"""
主窗口类 - PyQt手势识别可视化系统的核心界面
"""
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QMenuBar, QStatusBar, QAction, 
                             QToolBar, QSplitter, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from ui.widgets.sensor_plots import SensorPlotsWidget
from ui.widgets.gesture_display import GestureDisplayWidget
from ui.widgets.data_manager import DataManagerWidget
from ui.widgets.settings_panel import SettingsPanel
from core.serial_interface import SerialInterface
from core.gesture_classifier import GestureClassifier

class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 自定义信号
    data_received = pyqtSignal(list)  # 传感器数据接收信号
    gesture_recognized = pyqtSignal(str, float)  # 手势识别信号
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("手势识别可视化系统")
        self.setGeometry(100, 100, 1400, 900)
        
        # 初始化核心组件
        self.serial_interface = SerialInterface()
        self.gesture_classifier = GestureClassifier()
        
        # 设置UI
        self.setup_ui()
        self.setup_connections()
        self.setup_status_bar()
        
        # 初始化定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建中央小部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建分割器
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：传感器数据可视化
        self.sensor_plots = SensorPlotsWidget()
        main_splitter.addWidget(self.sensor_plots)
        
        # 右侧：手势显示和控制面板
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 手势识别显示
        self.gesture_display = GestureDisplayWidget()
        right_layout.addWidget(self.gesture_display)
        
        # 选项卡组件
        tab_widget = QTabWidget()
        
        # 数据管理选项卡
        self.data_manager = DataManagerWidget()
        tab_widget.addTab(self.data_manager, "数据管理")
        
        # 设置选项卡
        self.settings_panel = SettingsPanel()
        tab_widget.addTab(self.settings_panel, "系统设置")
        
        right_layout.addWidget(tab_widget)
        main_splitter.addWidget(right_widget)
        
        # 设置分割器比例
        main_splitter.setSizes([800, 600])
        
        main_layout.addWidget(main_splitter)
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        # 连接串口
        connect_action = QAction('连接设备', self)
        connect_action.setShortcut('Ctrl+C')
        connect_action.triggered.connect(self.connect_device)
        file_menu.addAction(connect_action)
        
        # 断开串口
        disconnect_action = QAction('断开设备', self)
        disconnect_action.setShortcut('Ctrl+D')
        disconnect_action.triggered.connect(self.disconnect_device)
        file_menu.addAction(disconnect_action)
        
        file_menu.addSeparator()
        
        # 导出数据
        export_action = QAction('导出数据', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        # 开始/停止可视化
        self.start_action = QAction('开始可视化', self)
        self.start_action.setShortcut('Space')
        self.start_action.triggered.connect(self.toggle_visualization)
        view_menu.addAction(self.start_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 连接设备按钮
        self.connect_btn = toolbar.addAction("连接设备")
        self.connect_btn.triggered.connect(self.connect_device)
        
        # 断开设备按钮
        self.disconnect_btn = toolbar.addAction("断开设备")
        self.disconnect_btn.triggered.connect(self.disconnect_device)
        
        toolbar.addSeparator()
        
        # 开始/停止按钮
        self.toggle_btn = toolbar.addAction("开始")
        self.toggle_btn.triggered.connect(self.toggle_visualization)
        
        # 录制按钮
        self.record_btn = toolbar.addAction("录制数据")
        self.record_btn.triggered.connect(self.toggle_recording)
        
    def setup_connections(self):
        """设置信号连接"""
        # 串口数据接收
        self.serial_interface.data_received.connect(self.on_data_received)
        
        # 连接状态变化
        self.serial_interface.connection_changed.connect(self.on_connection_changed)
        
        # 设置面板信号
        self.settings_panel.settings_changed.connect(self.on_settings_changed)
        
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.connection_status = "未连接"
        self.recording_status = "未录制"
        self.update_status_bar()
        
    def update_status_bar(self):
        """更新状态栏"""
        status_text = f"连接状态: {self.connection_status} | 录制状态: {self.recording_status}"
        self.status_bar.showMessage(status_text)
        
    def connect_device(self):
        """连接设备"""
        try:
            port = self.settings_panel.get_serial_port()
            baudrate = self.settings_panel.get_baudrate()
            
            if self.serial_interface.connect(port, baudrate):
                self.connection_status = "已连接"
                self.update_status_bar()
                QMessageBox.information(self, "成功", f"成功连接到 {port}")
            else:
                QMessageBox.warning(self, "错误", "连接设备失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接设备时发生错误: {str(e)}")
            
    def disconnect_device(self):
        """断开设备"""
        try:
            self.serial_interface.disconnect()
            self.connection_status = "未连接"
            self.update_status_bar()
            QMessageBox.information(self, "成功", "已断开设备连接")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"断开设备时发生错误: {str(e)}")
            
    def toggle_visualization(self):
        """切换可视化状态"""
        if self.update_timer.isActive():
            self.update_timer.stop()
            self.start_action.setText("开始可视化")
            self.toggle_btn.setText("开始")
        else:
            if self.serial_interface.is_connected():
                self.update_timer.start(50)  # 20 FPS更新
                self.start_action.setText("停止可视化")
                self.toggle_btn.setText("停止")
            else:
                QMessageBox.warning(self, "警告", "请先连接设备")
                
    def toggle_recording(self):
        """切换录制状态"""
        if self.data_manager.is_recording():
            self.data_manager.stop_recording()
            self.record_btn.setText("录制数据")
            self.recording_status = "未录制"
        else:
            self.data_manager.start_recording()
            self.record_btn.setText("停止录制")
            self.recording_status = "录制中"
        self.update_status_bar()
        
    def export_data(self):
        """导出数据"""
        self.data_manager.export_data()
        
    def on_data_received(self, data):
        """处理接收到的传感器数据"""
        try:
            # 更新传感器可视化
            self.sensor_plots.update_data(data)
            
            # 进行手势识别
            if len(data) >= 27:  # 确保数据完整
                gesture, confidence = self.gesture_classifier.predict(data)
                self.gesture_display.update_gesture(gesture, confidence)
                
            # 记录数据（如果在录制模式）
            if self.data_manager.is_recording():
                self.data_manager.add_data_point(data)
                
        except Exception as e:
            print(f"处理数据时出错: {str(e)}")
            
    def on_connection_changed(self, connected):
        """处理连接状态变化"""
        if connected:
            self.connection_status = "已连接"
        else:
            self.connection_status = "未连接"
            if self.update_timer.isActive():
                self.toggle_visualization()
        self.update_status_bar()
        
    def on_settings_changed(self, settings):
        """处理设置变化"""
        # 更新串口设置
        if self.serial_interface.is_connected():
            # 如果设置变化需要重新连接
            self.disconnect_device()
            
    def update_display(self):
        """定时更新显示"""
        # 这里可以添加定期更新的逻辑
        pass
        
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
                         "手势识别可视化系统 v1.0\n\n"
                         "基于ESP32数据手套的实时手势识别与可视化系统\n"
                         "支持14种静态手势和3种动态手势识别")
        
    def closeEvent(self, event):
        """关闭事件处理"""
        # 停止所有活动
        if self.update_timer.isActive():
            self.update_timer.stop()
            
        # 断开串口连接
        if self.serial_interface.is_connected():
            self.serial_interface.disconnect()
            
        # 停止录制
        if self.data_manager.is_recording():
            self.data_manager.stop_recording()
            
        event.accept()