"""
传感器数据可视化组件
实时显示来自ESP32数据手套的传感器数据
"""
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QLabel, QCheckBox, QGroupBox)
from PyQt5.QtCore import pyqtSignal
import pyqtgraph as pg
from collections import deque

# 尝试导入OpenGL支持
try:
    import pyqtgraph.opengl as gl
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL支持不可用，3D可视化将被禁用")

class SensorPlotsWidget(QWidget):
    """传感器数据可视化小部件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # 数据缓冲区
        self.max_points = 500
        self.time_buffer = deque(maxlen=self.max_points)
        
        # 传感器数据缓冲区
        self.flex_buffers = [deque(maxlen=self.max_points) for _ in range(5)]
        self.gyro_buffers = [deque(maxlen=self.max_points) for _ in range(3)]
        self.acc_buffers = [deque(maxlen=self.max_points) for _ in range(3)]
        self.quaternion_buffers = [deque(maxlen=self.max_points) for _ in range(4)]
        
        self.current_time = 0
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 弯曲传感器选项卡
        self.flex_tab = self.create_flex_sensor_tab()
        self.tab_widget.addTab(self.flex_tab, "弯曲传感器")
        
        # IMU传感器选项卡
        self.imu_tab = self.create_imu_sensor_tab()
        self.tab_widget.addTab(self.imu_tab, "IMU传感器")
        
        # 3D可视化选项卡（如果支持OpenGL）
        if OPENGL_AVAILABLE:
            self.viz_3d_tab = self.create_3d_visualization_tab()
            self.tab_widget.addTab(self.viz_3d_tab, "3D可视化")
        else:
            # 创建简化的信息选项卡
            self.info_tab = self.create_info_tab()
            self.tab_widget.addTab(self.info_tab, "数据信息")
        
        layout.addWidget(self.tab_widget)
        
    def create_flex_sensor_tab(self):
        """创建弯曲传感器选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 创建绘图区域
        self.flex_plot_widget = pg.PlotWidget(title="弯曲传感器数据")
        self.flex_plot_widget.setLabel('left', '弯曲值')
        self.flex_plot_widget.setLabel('bottom', '时间 (s)')
        self.flex_plot_widget.addLegend()
        
        # 创建绘图曲线
        colors = ['red', 'green', 'blue', 'yellow', 'magenta']
        self.flex_curves = []
        
        for i in range(5):
            curve = self.flex_plot_widget.plot(
                pen=pg.mkPen(color=colors[i], width=2),
                name=f'Flex {i+1}'
            )
            self.flex_curves.append(curve)
            
        layout.addWidget(self.flex_plot_widget)
        
        # 添加控制选项
        control_group = QGroupBox("显示选项")
        control_layout = QHBoxLayout(control_group)
        
        self.flex_checkboxes = []
        for i in range(5):
            checkbox = QCheckBox(f"Flex {i+1}")
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_flex_visibility)
            control_layout.addWidget(checkbox)
            self.flex_checkboxes.append(checkbox)
            
        layout.addWidget(control_group)
        
        return widget
        
    def create_imu_sensor_tab(self):
        """创建IMU传感器选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 陀螺仪数据
        self.gyro_plot_widget = pg.PlotWidget(title="陀螺仪数据")
        self.gyro_plot_widget.setLabel('left', '角速度 (rad/s)')
        self.gyro_plot_widget.setLabel('bottom', '时间 (s)')
        self.gyro_plot_widget.addLegend()
        
        # 陀螺仪曲线
        gyro_colors = ['red', 'green', 'blue']
        gyro_labels = ['X轴', 'Y轴', 'Z轴']
        self.gyro_curves = []
        
        for i in range(3):
            curve = self.gyro_plot_widget.plot(
                pen=pg.mkPen(color=gyro_colors[i], width=2),
                name=f'陀螺仪{gyro_labels[i]}'
            )
            self.gyro_curves.append(curve)
            
        layout.addWidget(self.gyro_plot_widget)
        
        # 加速度计数据
        self.acc_plot_widget = pg.PlotWidget(title="加速度计数据")
        self.acc_plot_widget.setLabel('left', '加速度 (m/s²)')
        self.acc_plot_widget.setLabel('bottom', '时间 (s)')
        self.acc_plot_widget.addLegend()
        
        # 加速度计曲线
        self.acc_curves = []
        for i in range(3):
            curve = self.acc_plot_widget.plot(
                pen=pg.mkPen(color=gyro_colors[i], width=2),
                name=f'加速度{gyro_labels[i]}'
            )
            self.acc_curves.append(curve)
            
        layout.addWidget(self.acc_plot_widget)
        
        return widget
        
    def create_info_tab(self):
        """创建信息选项卡（当OpenGL不可用时）"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 四元数显示
        quat_group = QGroupBox("四元数数据")
        quat_layout = QHBoxLayout(quat_group)
        
        self.quat_labels = []
        for component in ['W', 'X', 'Y', 'Z']:
            label = QLabel(f"{component}: 0.000")
            quat_layout.addWidget(label)
            self.quat_labels.append(label)
            
        layout.addWidget(quat_group)
        
        # 数据统计
        stats_group = QGroupBox("传感器统计")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("等待数据...")
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_group)
        
        return widget
        
    def create_3d_visualization_tab(self):
        """创建3D可视化选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 3D绘图区域
        self.gl_widget = gl.GLViewWidget()
        self.gl_widget.setCameraPosition(distance=30)
        
        # 添加坐标轴
        axis = gl.GLAxisItem()
        self.gl_widget.addItem(axis)
        
        # 添加网格
        grid = gl.GLGridItem()
        self.gl_widget.addItem(grid)
        
        # 手部模型（简化的5个点代表5个手指）
        self.hand_model = self.create_hand_model()
        self.gl_widget.addItem(self.hand_model)
        
        layout.addWidget(self.gl_widget)
        
        # 四元数显示
        quat_group = QGroupBox("四元数数据")
        quat_layout = QHBoxLayout(quat_group)
        
        self.quat_labels = []
        for component in ['W', 'X', 'Y', 'Z']:
            label = QLabel(f"{component}: 0.000")
            quat_layout.addWidget(label)
            self.quat_labels.append(label)
            
        layout.addWidget(quat_group)
        
        return widget
        
    def create_hand_model(self):
        """创建简化的手部模型"""
        if not OPENGL_AVAILABLE:
            return None
            
        # 创建5个点代表5个手指
        pos = np.array([
            [0, 0, 0],      # 拇指
            [1, 0, 0],      # 食指
            [2, 0, 0],      # 中指
            [3, 0, 0],      # 无名指
            [4, 0, 0]       # 小指
        ])
        
        color = np.array([
            [1, 0, 0, 1],   # 红色
            [0, 1, 0, 1],   # 绿色
            [0, 0, 1, 1],   # 蓝色
            [1, 1, 0, 1],   # 黄色
            [1, 0, 1, 1]    # 紫色
        ])
        
        scatter = gl.GLScatterPlotItem(
            pos=pos, 
            color=color, 
            size=10,
            pxMode=False
        )
        
        return scatter
        
    def update_data(self, sensor_data):
        """更新传感器数据"""
        if len(sensor_data) < 29:
            return
            
        self.current_time += 0.05  # 假设50ms间隔
        self.time_buffer.append(self.current_time)
        
        # 更新弯曲传感器数据
        for i in range(5):
            self.flex_buffers[i].append(sensor_data[i])
            
        # 更新IMU数据
        quaternion = sensor_data[5:9]
        gyro_data = sensor_data[9:12]
        acc_data = sensor_data[12:15]
        
        for i in range(4):
            self.quaternion_buffers[i].append(quaternion[i])
            
        for i in range(3):
            self.gyro_buffers[i].append(gyro_data[i])
            self.acc_buffers[i].append(acc_data[i])
            
        # 更新图表
        self.update_plots()
        self.update_3d_visualization(sensor_data)
        
    def update_plots(self):
        """更新2D图表"""
        if len(self.time_buffer) < 2:
            return
            
        time_data = np.array(self.time_buffer)
        
        # 更新弯曲传感器图表
        for i, curve in enumerate(self.flex_curves):
            if self.flex_checkboxes[i].isChecked():
                flex_data = np.array(self.flex_buffers[i])
                curve.setData(time_data, flex_data)
            else:
                curve.clear()
                
        # 更新陀螺仪图表
        for i, curve in enumerate(self.gyro_curves):
            gyro_data = np.array(self.gyro_buffers[i])
            curve.setData(time_data, gyro_data)
            
        # 更新加速度计图表
        for i, curve in enumerate(self.acc_curves):
            acc_data = np.array(self.acc_buffers[i])
            curve.setData(time_data, acc_data)
            
    def update_3d_visualization(self, sensor_data):
        """更新3D可视化"""
        if len(sensor_data) < 9:
            return
            
        # 更新四元数显示
        quaternion = sensor_data[5:9]
        for i, label in enumerate(self.quat_labels):
            label.setText(f"{['W', 'X', 'Y', 'Z'][i]}: {quaternion[i]:.3f}")
            
        # 如果有OpenGL支持，更新3D模型
        if OPENGL_AVAILABLE and hasattr(self, 'hand_model') and self.hand_model:
            # 根据弯曲传感器数据更新手指位置
            flex_data = sensor_data[:5]
            pos = np.array([
                [0, 0, 0],
                [1, -flex_data[1] * 0.1, 0],
                [2, -flex_data[2] * 0.1, 0],
                [3, -flex_data[3] * 0.1, 0],
                [4, -flex_data[4] * 0.1, 0]
            ])
            
            self.hand_model.setData(pos=pos)
        
    def update_flex_visibility(self):
        """更新弯曲传感器可见性"""
        self.update_plots()
        
    def clear_data(self):
        """清空数据"""
        self.time_buffer.clear()
        for buffer in self.flex_buffers:
            buffer.clear()
        for buffer in self.gyro_buffers:
            buffer.clear()
        for buffer in self.acc_buffers:
            buffer.clear()
        for buffer in self.quaternion_buffers:
            buffer.clear()
            
        self.current_time = 0
        
        # 清空图表
        for curve in self.flex_curves:
            curve.clear()
        for curve in self.gyro_curves:
            curve.clear()
        for curve in self.acc_curves:
            curve.clear()