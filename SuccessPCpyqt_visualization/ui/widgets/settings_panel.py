"""
设置面板组件
系统配置和参数设置
"""
import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QLineEdit, QSpinBox, QComboBox, QCheckBox,
                             QPushButton, QSlider, QTabWidget, QTextEdit,
                             QFileDialog, QMessageBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
import serial.tools.list_ports

class SettingsPanel(QWidget):
    """设置面板小部件"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 默认设置
        self.default_settings = {
            'serial': {
                'port': '/dev/ttyUSB0',
                'baudrate': 115200,
                'timeout': 1,
                'auto_connect': False
            },
            'display': {
                'update_rate': 20,
                'max_points': 500,
                'enable_3d': True,
                'theme': 'dark'
            },
            'recognition': {
                'confidence_threshold': 0.6,
                'stability_window': 5,
                'model_type': 'knn',
                'enable_filter': True
            },
            'recording': {
                'auto_label': True,
                'default_duration': 10,
                'sample_rate': 20,
                'file_format': 'csv'
            }
        }
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 串口设置选项卡
        serial_tab = self.create_serial_settings_tab()
        tab_widget.addTab(serial_tab, "串口设置")
        
        # 显示设置选项卡
        display_tab = self.create_display_settings_tab()
        tab_widget.addTab(display_tab, "显示设置")
        
        # 识别设置选项卡
        recognition_tab = self.create_recognition_settings_tab()
        tab_widget.addTab(recognition_tab, "识别设置")
        
        # 录制设置选项卡
        recording_tab = self.create_recording_settings_tab()
        tab_widget.addTab(recording_tab, "录制设置")
        
        layout.addWidget(tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("保存设置")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        load_button = QPushButton("加载设置")
        load_button.clicked.connect(self.load_settings_file)
        button_layout.addWidget(load_button)
        
        reset_button = QPushButton("恢复默认")
        reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_button)
        
        layout.addLayout(button_layout)
        
    def create_serial_settings_tab(self):
        """创建串口设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 串口连接设置
        connection_group = QGroupBox("连接设置")
        connection_layout = QVBoxLayout(connection_group)
        
        # 端口选择
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("串口:"))
        
        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        self.refresh_ports()
        port_layout.addWidget(self.port_combo)
        
        refresh_button = QPushButton("刷新")
        refresh_button.clicked.connect(self.refresh_ports)
        port_layout.addWidget(refresh_button)
        
        connection_layout.addLayout(port_layout)
        
        # 波特率设置
        baudrate_layout = QHBoxLayout()
        baudrate_layout.addWidget(QLabel("波特率:"))
        
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.setEditable(True)
        common_baudrates = ['9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600']
        self.baudrate_combo.addItems(common_baudrates)
        self.baudrate_combo.setCurrentText('115200')
        baudrate_layout.addWidget(self.baudrate_combo)
        
        connection_layout.addLayout(baudrate_layout)
        
        # 超时设置
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("超时(秒):"))
        
        self.timeout_spinbox = QDoubleSpinBox()
        self.timeout_spinbox.setRange(0.1, 10.0)
        self.timeout_spinbox.setSingleStep(0.1)
        self.timeout_spinbox.setValue(1.0)
        timeout_layout.addWidget(self.timeout_spinbox)
        
        connection_layout.addLayout(timeout_layout)
        
        # 自动连接选项
        self.auto_connect_checkbox = QCheckBox("启动时自动连接")
        connection_layout.addWidget(self.auto_connect_checkbox)
        
        layout.addWidget(connection_group)
        
        # 数据设置
        data_group = QGroupBox("数据设置")
        data_layout = QVBoxLayout(data_group)
        
        # 数据验证
        self.validate_data_checkbox = QCheckBox("启用数据验证")
        self.validate_data_checkbox.setChecked(True)
        data_layout.addWidget(self.validate_data_checkbox)
        
        # 数据缓冲
        buffer_layout = QHBoxLayout()
        buffer_layout.addWidget(QLabel("缓冲区大小:"))
        
        self.buffer_size_spinbox = QSpinBox()
        self.buffer_size_spinbox.setRange(100, 10000)
        self.buffer_size_spinbox.setValue(1000)
        buffer_layout.addWidget(self.buffer_size_spinbox)
        
        data_layout.addLayout(buffer_layout)
        
        layout.addWidget(data_group)
        
        return widget
        
    def create_display_settings_tab(self):
        """创建显示设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 图表设置
        chart_group = QGroupBox("图表设置")
        chart_layout = QVBoxLayout(chart_group)
        
        # 更新频率
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel("更新频率(FPS):"))
        
        self.update_rate_slider = QSlider(Qt.Horizontal)
        self.update_rate_slider.setRange(5, 60)
        self.update_rate_slider.setValue(20)
        self.update_rate_slider.valueChanged.connect(self.update_rate_changed)
        rate_layout.addWidget(self.update_rate_slider)
        
        self.update_rate_label = QLabel("20")
        rate_layout.addWidget(self.update_rate_label)
        
        chart_layout.addLayout(rate_layout)
        
        # 最大数据点
        points_layout = QHBoxLayout()
        points_layout.addWidget(QLabel("最大数据点:"))
        
        self.max_points_spinbox = QSpinBox()
        self.max_points_spinbox.setRange(100, 2000)
        self.max_points_spinbox.setValue(500)
        points_layout.addWidget(self.max_points_spinbox)
        
        chart_layout.addLayout(points_layout)
        
        # 3D可视化
        self.enable_3d_checkbox = QCheckBox("启用3D可视化")
        self.enable_3d_checkbox.setChecked(True)
        chart_layout.addWidget(self.enable_3d_checkbox)
        
        layout.addWidget(chart_group)
        
        # 主题设置
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout(theme_group)
        
        theme_selection_layout = QHBoxLayout()
        theme_selection_layout.addWidget(QLabel("主题:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light", "colorful"])
        theme_selection_layout.addWidget(self.theme_combo)
        
        theme_layout.addLayout(theme_selection_layout)
        
        # 字体大小
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("字体大小:"))
        
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 24)
        self.font_size_spinbox.setValue(12)
        font_layout.addWidget(self.font_size_spinbox)
        
        theme_layout.addLayout(font_layout)
        
        layout.addWidget(theme_group)
        
        return widget
        
    def create_recognition_settings_tab(self):
        """创建识别设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 识别参数
        recognition_group = QGroupBox("识别参数")
        recognition_layout = QVBoxLayout(recognition_group)
        
        # 置信度阈值
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("置信度阈值:"))
        
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(10, 95)
        self.confidence_slider.setValue(60)
        self.confidence_slider.valueChanged.connect(self.confidence_changed)
        confidence_layout.addWidget(self.confidence_slider)
        
        self.confidence_label = QLabel("0.60")
        confidence_layout.addWidget(self.confidence_label)
        
        recognition_layout.addLayout(confidence_layout)
        
        # 稳定性窗口
        stability_layout = QHBoxLayout()
        stability_layout.addWidget(QLabel("稳定性窗口:"))
        
        self.stability_spinbox = QSpinBox()
        self.stability_spinbox.setRange(3, 20)
        self.stability_spinbox.setValue(5)
        stability_layout.addWidget(self.stability_spinbox)
        
        recognition_layout.addLayout(stability_layout)
        
        # 模型类型
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("模型类型:"))
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["knn", "svm", "random_forest", "neural_network"])
        model_layout.addWidget(self.model_combo)
        
        recognition_layout.addLayout(model_layout)
        
        layout.addWidget(recognition_group)
        
        # 滤波设置
        filter_group = QGroupBox("数据滤波")
        filter_layout = QVBoxLayout(filter_group)
        
        self.enable_filter_checkbox = QCheckBox("启用数据滤波")
        self.enable_filter_checkbox.setChecked(True)
        filter_layout.addWidget(self.enable_filter_checkbox)
        
        # 滤波参数
        filter_params_layout = QHBoxLayout()
        filter_params_layout.addWidget(QLabel("滤波强度:"))
        
        self.filter_strength_slider = QSlider(Qt.Horizontal)
        self.filter_strength_slider.setRange(1, 10)
        self.filter_strength_slider.setValue(5)
        filter_params_layout.addWidget(self.filter_strength_slider)
        
        filter_layout.addLayout(filter_params_layout)
        
        layout.addWidget(filter_group)
        
        # 高级设置
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QVBoxLayout(advanced_group)
        
        # 模型路径
        model_path_layout = QHBoxLayout()
        model_path_layout.addWidget(QLabel("模型路径:"))
        
        self.model_path_edit = QLineEdit()
        model_path_layout.addWidget(self.model_path_edit)
        
        browse_model_button = QPushButton("浏览")
        browse_model_button.clicked.connect(self.browse_model_path)
        model_path_layout.addWidget(browse_model_button)
        
        advanced_layout.addLayout(model_path_layout)
        
        layout.addWidget(advanced_group)
        
        return widget
        
    def create_recording_settings_tab(self):
        """创建录制设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 录制参数
        recording_group = QGroupBox("录制参数")
        recording_layout = QVBoxLayout(recording_group)
        
        # 自动标签
        self.auto_label_checkbox = QCheckBox("自动标签模式")
        self.auto_label_checkbox.setChecked(True)
        recording_layout.addWidget(self.auto_label_checkbox)
        
        # 默认时长
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("默认录制时长(秒):"))
        
        self.default_duration_spinbox = QSpinBox()
        self.default_duration_spinbox.setRange(1, 300)
        self.default_duration_spinbox.setValue(10)
        duration_layout.addWidget(self.default_duration_spinbox)
        
        recording_layout.addLayout(duration_layout)
        
        # 采样率
        sample_rate_layout = QHBoxLayout()
        sample_rate_layout.addWidget(QLabel("目标采样率(Hz):"))
        
        self.sample_rate_spinbox = QSpinBox()
        self.sample_rate_spinbox.setRange(5, 100)
        self.sample_rate_spinbox.setValue(20)
        sample_rate_layout.addWidget(self.sample_rate_spinbox)
        
        recording_layout.addLayout(sample_rate_layout)
        
        layout.addWidget(recording_group)
        
        # 文件设置
        file_group = QGroupBox("文件设置")
        file_layout = QVBoxLayout(file_group)
        
        # 文件格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("默认格式:"))
        
        self.file_format_combo = QComboBox()
        self.file_format_combo.addItems(["csv", "json", "npy", "xlsx"])
        format_layout.addWidget(self.file_format_combo)
        
        file_layout.addLayout(format_layout)
        
        # 保存路径
        save_path_layout = QHBoxLayout()
        save_path_layout.addWidget(QLabel("默认保存路径:"))
        
        self.save_path_edit = QLineEdit()
        self.save_path_edit.setText(os.path.expanduser("~/Desktop"))
        save_path_layout.addWidget(self.save_path_edit)
        
        browse_save_button = QPushButton("浏览")
        browse_save_button.clicked.connect(self.browse_save_path)
        save_path_layout.addWidget(browse_save_button)
        
        file_layout.addLayout(save_path_layout)
        
        # 自动保存
        self.auto_save_checkbox = QCheckBox("录制完成后自动保存")
        self.auto_save_checkbox.setChecked(False)
        file_layout.addWidget(self.auto_save_checkbox)
        
        layout.addWidget(file_group)
        
        return widget
        
    def refresh_ports(self):
        """刷新可用串口列表"""
        self.port_combo.clear()
        
        # 获取可用串口
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            self.port_combo.addItem(f"{port.device} - {port.description}")
            
        # 如果没有找到串口，添加常见的默认端口
        if not ports:
            default_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', 'COM1', 'COM2', 'COM3']
            self.port_combo.addItems(default_ports)
            
    def update_rate_changed(self, value):
        """更新率改变"""
        self.update_rate_label.setText(str(value))
        
    def confidence_changed(self, value):
        """置信度阈值改变"""
        confidence = value / 100.0
        self.confidence_label.setText(f"{confidence:.2f}")
        
    def browse_model_path(self):
        """浏览模型路径"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择模型文件", "", 
            "Model files (*.pkl *.joblib *.h5);;All files (*)"
        )
        if file_path:
            self.model_path_edit.setText(file_path)
            
    def browse_save_path(self):
        """浏览保存路径"""
        path = QFileDialog.getExistingDirectory(
            self, "选择保存路径", self.save_path_edit.text()
        )
        if path:
            self.save_path_edit.setText(path)
            
    def get_settings(self):
        """获取当前设置"""
        settings = {
            'serial': {
                'port': self.get_serial_port(),
                'baudrate': self.get_baudrate(),
                'timeout': self.timeout_spinbox.value(),
                'auto_connect': self.auto_connect_checkbox.isChecked(),
                'validate_data': self.validate_data_checkbox.isChecked(),
                'buffer_size': self.buffer_size_spinbox.value()
            },
            'display': {
                'update_rate': self.update_rate_slider.value(),
                'max_points': self.max_points_spinbox.value(),
                'enable_3d': self.enable_3d_checkbox.isChecked(),
                'theme': self.theme_combo.currentText(),
                'font_size': self.font_size_spinbox.value()
            },
            'recognition': {
                'confidence_threshold': self.confidence_slider.value() / 100.0,
                'stability_window': self.stability_spinbox.value(),
                'model_type': self.model_combo.currentText(),
                'enable_filter': self.enable_filter_checkbox.isChecked(),
                'filter_strength': self.filter_strength_slider.value(),
                'model_path': self.model_path_edit.text()
            },
            'recording': {
                'auto_label': self.auto_label_checkbox.isChecked(),
                'default_duration': self.default_duration_spinbox.value(),
                'sample_rate': self.sample_rate_spinbox.value(),
                'file_format': self.file_format_combo.currentText(),
                'save_path': self.save_path_edit.text(),
                'auto_save': self.auto_save_checkbox.isChecked()
            }
        }
        return settings
        
    def apply_settings(self, settings):
        """应用设置"""
        try:
            # 串口设置
            if 'serial' in settings:
                s = settings['serial']
                if 'port' in s:
                    self.port_combo.setCurrentText(s['port'])
                if 'baudrate' in s:
                    self.baudrate_combo.setCurrentText(str(s['baudrate']))
                if 'timeout' in s:
                    self.timeout_spinbox.setValue(s['timeout'])
                if 'auto_connect' in s:
                    self.auto_connect_checkbox.setChecked(s['auto_connect'])
                if 'validate_data' in s:
                    self.validate_data_checkbox.setChecked(s['validate_data'])
                if 'buffer_size' in s:
                    self.buffer_size_spinbox.setValue(s['buffer_size'])
                    
            # 显示设置
            if 'display' in settings:
                s = settings['display']
                if 'update_rate' in s:
                    self.update_rate_slider.setValue(s['update_rate'])
                if 'max_points' in s:
                    self.max_points_spinbox.setValue(s['max_points'])
                if 'enable_3d' in s:
                    self.enable_3d_checkbox.setChecked(s['enable_3d'])
                if 'theme' in s:
                    self.theme_combo.setCurrentText(s['theme'])
                if 'font_size' in s:
                    self.font_size_spinbox.setValue(s['font_size'])
                    
            # 识别设置
            if 'recognition' in settings:
                s = settings['recognition']
                if 'confidence_threshold' in s:
                    self.confidence_slider.setValue(int(s['confidence_threshold'] * 100))
                if 'stability_window' in s:
                    self.stability_spinbox.setValue(s['stability_window'])
                if 'model_type' in s:
                    self.model_combo.setCurrentText(s['model_type'])
                if 'enable_filter' in s:
                    self.enable_filter_checkbox.setChecked(s['enable_filter'])
                if 'filter_strength' in s:
                    self.filter_strength_slider.setValue(s['filter_strength'])
                if 'model_path' in s:
                    self.model_path_edit.setText(s['model_path'])
                    
            # 录制设置
            if 'recording' in settings:
                s = settings['recording']
                if 'auto_label' in s:
                    self.auto_label_checkbox.setChecked(s['auto_label'])
                if 'default_duration' in s:
                    self.default_duration_spinbox.setValue(s['default_duration'])
                if 'sample_rate' in s:
                    self.sample_rate_spinbox.setValue(s['sample_rate'])
                if 'file_format' in s:
                    self.file_format_combo.setCurrentText(s['file_format'])
                if 'save_path' in s:
                    self.save_path_edit.setText(s['save_path'])
                if 'auto_save' in s:
                    self.auto_save_checkbox.setChecked(s['auto_save'])
                    
        except Exception as e:
            QMessageBox.warning(self, "警告", f"应用设置时出错: {str(e)}")
            
    def save_settings(self):
        """保存设置到文件"""
        settings = self.get_settings()
        
        config_dir = os.path.expanduser("~/.gesture_recognition")
        os.makedirs(config_dir, exist_ok=True)
        config_file = os.path.join(config_dir, "settings.json")
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
                
            QMessageBox.information(self, "成功", f"设置已保存到: {config_file}")
            self.settings_changed.emit(settings)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
            
    def load_settings(self):
        """从文件加载设置"""
        config_file = os.path.expanduser("~/.gesture_recognition/settings.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                self.apply_settings(settings)
                self.settings_changed.emit(settings)
                
            except Exception as e:
                QMessageBox.warning(self, "警告", f"加载设置失败: {str(e)}")
                self.apply_settings(self.default_settings)
        else:
            # 使用默认设置
            self.apply_settings(self.default_settings)
            
    def load_settings_file(self):
        """从文件加载设置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载设置文件", "", 
            "JSON files (*.json);;All files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                self.apply_settings(settings)
                self.settings_changed.emit(settings)
                QMessageBox.information(self, "成功", "设置已加载")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载设置失败: {str(e)}")
                
    def reset_to_defaults(self):
        """恢复默认设置"""
        reply = QMessageBox.question(
            self, "确认", "确定要恢复默认设置吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.apply_settings(self.default_settings)
            self.settings_changed.emit(self.default_settings)
            QMessageBox.information(self, "成功", "已恢复默认设置")
            
    def get_serial_port(self):
        """获取串口设置"""
        port_text = self.port_combo.currentText()
        # 如果文本包含描述信息，提取端口部分
        if " - " in port_text:
            return port_text.split(" - ")[0]
        return port_text
        
    def get_baudrate(self):
        """获取波特率设置"""
        try:
            return int(self.baudrate_combo.currentText())
        except ValueError:
            return 115200