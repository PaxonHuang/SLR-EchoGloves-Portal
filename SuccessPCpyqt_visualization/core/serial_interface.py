"""
串口通信接口模块
基于原有serialDataAcquisition.py，提供线程安全的数据接收功能
"""
import serial
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox

class SerialInterface(QObject):
    """串口通信接口类"""
    
    # 信号定义
    data_received = pyqtSignal(list)  # 数据接收信号
    connection_changed = pyqtSignal(bool)  # 连接状态变化信号
    error_occurred = pyqtSignal(str)  # 错误信号
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.is_connected_flag = False
        self.is_reading = False
        self.read_thread = None
        
        # 数据列名 - 与原始代码保持一致
        self.column_names = [
            'flex_1', 'flex_2', 'flex_3', 'flex_4', 'flex_5',
            'Qw', 'Qx', 'Qy', 'Qz',
            'GYRx', 'GYRy','GYRz',
            'ACCx', 'ACCy', 'ACCz',
            'ACCx_real', 'ACCy_real', 'ACCz_real',
            'ACCx_world', 'ACCy_world', 'ACCz_world',
            'GRAx', 'GRAy', 'GRAz',
            'ACCx_raw', 'ACCy_raw', 'ACCz_raw',
            'GYRx_raw', 'GYRy_raw', 'GYRz_raw'
        ]
        
        # 数据缓冲
        self.data_buffer = []
        self.max_buffer_size = 1000
        
    def connect(self, port='COM4', baudrate=115200):
        """连接串口设备"""
        try:
            if self.is_connected_flag:
                self.disconnect()
                
            # 创建串口连接 - 使用与原始代码相同的参数
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
                xonxoff=0,
                rtscts=0
            )
            
            # 重置设备 - 与原始代码保持一致
            self.serial_port.dtr = False
            time.sleep(1)
            self.serial_port.reset_input_buffer()
            self.serial_port.dtr = True
            
            self.is_connected_flag = True
            self.connection_changed.emit(True)
            
            # 启动数据读取线程
            self.start_reading()
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"连接串口失败: {str(e)}")
            return False
            
    def disconnect(self):
        """断开串口连接"""
        try:
            self.stop_reading()
            
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                
            self.is_connected_flag = False
            self.connection_changed.emit(False)
            
        except Exception as e:
            self.error_occurred.emit(f"断开串口失败: {str(e)}")
            
    def start_reading(self):
        """开始读取数据"""
        if not self.is_reading and self.is_connected_flag:
            self.is_reading = True
            self.read_thread = threading.Thread(target=self._read_data_loop, daemon=True)
            self.read_thread.start()
            
    def stop_reading(self):
        """停止读取数据"""
        self.is_reading = False
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2)
            
    def _read_data_loop(self):
        """数据读取循环（在独立线程中运行）"""
        while self.is_reading and self.is_connected_flag:
            try:
                if self.serial_port and self.serial_port.is_open:
                    # 读取一行数据
                    line = self.serial_port.readline().decode('utf-8').rstrip()
                    
                    if line:
                        # 解析数据 - 与原始代码保持一致
                        values = line.split(',')
                        
                        # 确保数据长度正确
                        if len(values) == len(self.column_names):
                            try:
                                # 转换为浮点数
                                float_values = list(map(float, values))
                                
                                # 添加到缓冲区
                                self._add_to_buffer(float_values)
                                
                                # 发射数据信号
                                self.data_received.emit(float_values)
                                
                            except ValueError:
                                # 数据格式错误，忽略这一行
                                continue
                                
            except Exception as e:
                if self.is_reading:  # 只有在仍在读取时才报告错误
                    self.error_occurred.emit(f"读取数据错误: {str(e)}")
                break
                
        # 读取结束
        if self.is_connected_flag:
            self.disconnect()
            
    def _add_to_buffer(self, data):
        """添加数据到缓冲区"""
        self.data_buffer.append(data)
        
        # 保持缓冲区大小
        if len(self.data_buffer) > self.max_buffer_size:
            self.data_buffer.pop(0)
            
    def get_recent_data(self, count=100):
        """获取最近的数据"""
        return self.data_buffer[-count:] if len(self.data_buffer) >= count else self.data_buffer.copy()
        
    def clear_buffer(self):
        """清空数据缓冲"""
        self.data_buffer.clear()
        
    def is_connected(self):
        """检查连接状态"""
        return self.is_connected_flag and self.serial_port and self.serial_port.is_open
        
    def get_available_ports(self):
        """获取可用的串口列表"""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
        
    def get_data_info(self):
        """获取数据信息"""
        return {
            'column_names': self.column_names,
            'column_count': len(self.column_names),
            'buffer_size': len(self.data_buffer),
            'max_buffer_size': self.max_buffer_size
        }