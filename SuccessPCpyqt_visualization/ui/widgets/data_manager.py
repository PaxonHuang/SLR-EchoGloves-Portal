"""
数据管理组件
负责数据的录制、保存和导出
"""
import os
import csv
import json
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QLabel, QLineEdit, QSpinBox,
                             QFileDialog, QMessageBox, QTextEdit, QComboBox,
                             QCheckBox, QProgressBar, QTabWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
import pandas as pd
import numpy as np

class DataManagerWidget(QWidget):
    """数据管理小部件"""
    
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    data_exported = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # 录制状态
        self.is_recording_flag = False
        self.recorded_data = []
        self.recording_start_time = None
        self.current_label = "unknown"
        
        # 数据统计
        self.total_samples = 0
        self.recording_duration = 0
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 录制选项卡
        recording_tab = self.create_recording_tab()
        tab_widget.addTab(recording_tab, "数据录制")
        
        # 导出选项卡
        export_tab = self.create_export_tab()
        tab_widget.addTab(export_tab, "数据导出")
        
        # 统计选项卡
        stats_tab = self.create_statistics_tab()
        tab_widget.addTab(stats_tab, "数据统计")
        
        layout.addWidget(tab_widget)
        
    def create_recording_tab(self):
        """创建录制选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 录制控制区域
        control_group = QGroupBox("录制控制")
        control_layout = QVBoxLayout(control_group)
        
        # 手势标签设置
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("手势标签:"))
        
        self.label_combo = QComboBox()
        self.label_combo.setEditable(True)
        
        # 添加预定义的手势标签
        predefined_gestures = [
            'Cash', 'Come Here', 'Excellent', 'Fingers crossed', 'Fist',
            'Five', 'Four', 'Go Away', 'One', 'Stop', 'Three', 
            'Thumbs Down', 'Thumbs Up', 'Two', 'Painting', 'Thank You', 'Sorry'
        ]
        self.label_combo.addItems(predefined_gestures)
        
        label_layout.addWidget(self.label_combo)
        control_layout.addLayout(label_layout)
        
        # 录制时长设置
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("录制时长(秒):"))
        
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(1, 300)
        self.duration_spinbox.setValue(10)
        duration_layout.addWidget(self.duration_spinbox)
        
        self.auto_stop_checkbox = QCheckBox("自动停止")
        self.auto_stop_checkbox.setChecked(True)
        duration_layout.addWidget(self.auto_stop_checkbox)
        
        control_layout.addLayout(duration_layout)
        
        # 录制按钮
        button_layout = QHBoxLayout()
        
        self.record_button = QPushButton("开始录制")
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                background-color: #27ae60;
                color: white;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """
        )
        button_layout.addWidget(self.record_button)
        
        self.save_button = QPushButton("保存数据")
        self.save_button.clicked.connect(self.save_recorded_data)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)
        
        self.clear_button = QPushButton("清除数据")
        self.clear_button.clicked.connect(self.clear_recorded_data)
        self.clear_button.setEnabled(False)
        button_layout.addWidget(self.clear_button)
        
        control_layout.addLayout(button_layout)
        
        layout.addWidget(control_group)
        
        # 录制状态显示
        status_group = QGroupBox("录制状态")
        status_layout = QVBoxLayout(status_group)
        
        # 状态信息
        self.status_label = QLabel("未录制")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ecf0f1;
            }
        """
        )
        status_layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        
        self.samples_label = QLabel("样本数: 0")
        stats_layout.addWidget(self.samples_label)
        
        self.duration_label = QLabel("时长: 0s")
        stats_layout.addWidget(self.duration_label)
        
        self.rate_label = QLabel("采样率: 0 Hz")
        stats_layout.addWidget(self.rate_label)
        
        status_layout.addLayout(stats_layout)
        
        layout.addWidget(status_group)
        
        # 录制预览
        preview_group = QGroupBox("数据预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 10px;
                background-color: #2c3e50;
                color: #27ae60;
                border: 1px solid #34495e;
            }
        """
        )
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        # 录制定时器
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_status)
        
        return widget
        
    def create_export_tab(self):
        """创建导出选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 导出设置
        settings_group = QGroupBox("导出设置")
        settings_layout = QVBoxLayout(settings_group)
        
        # 文件格式选择
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("文件格式:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "JSON", "NPY", "Excel"])
        format_layout.addWidget(self.format_combo)
        
        settings_layout.addLayout(format_layout)
        
        # 文件路径选择
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("保存路径:"))
        
        self.path_edit = QLineEdit()
        self.path_edit.setText(os.path.expanduser("~/Desktop"))
        path_layout.addWidget(self.path_edit)
        
        browse_button = QPushButton("浏览")
        browse_button.clicked.connect(self.browse_export_path)
        path_layout.addWidget(browse_button)
        
        settings_layout.addLayout(path_layout)
        
        # 文件名设置
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("文件名:"))
        
        self.filename_edit = QLineEdit()
        self.filename_edit.setText(f"gesture_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        name_layout.addWidget(self.filename_edit)
        
        settings_layout.addLayout(name_layout)
        
        layout.addWidget(settings_group)
        
        # 导出选项
        options_group = QGroupBox("导出选项")
        options_layout = QVBoxLayout(options_group)
        
        self.include_timestamp_checkbox = QCheckBox("包含时间戳")
        self.include_timestamp_checkbox.setChecked(True)
        options_layout.addWidget(self.include_timestamp_checkbox)
        
        self.include_metadata_checkbox = QCheckBox("包含元数据")
        self.include_metadata_checkbox.setChecked(True)
        options_layout.addWidget(self.include_metadata_checkbox)
        
        self.compress_checkbox = QCheckBox("压缩文件")
        self.compress_checkbox.setChecked(False)
        options_layout.addWidget(self.compress_checkbox)
        
        layout.addWidget(options_group)
        
        # 导出按钮
        export_button_layout = QHBoxLayout()
        
        self.export_current_button = QPushButton("导出当前数据")
        self.export_current_button.clicked.connect(self.export_current_data)
        export_button_layout.addWidget(self.export_current_button)
        
        self.export_all_button = QPushButton("导出所有数据")
        self.export_all_button.clicked.connect(self.export_all_data)
        export_button_layout.addWidget(self.export_all_button)
        
        layout.addLayout(export_button_layout)
        
        return widget
        
    def create_statistics_tab(self):
        """创建统计选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 数据概览
        overview_group = QGroupBox("数据概览")
        overview_layout = QVBoxLayout(overview_group)
        
        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        self.overview_text.setMaximumHeight(200)
        overview_layout.addWidget(self.overview_text)
        
        refresh_button = QPushButton("刷新统计")
        refresh_button.clicked.connect(self.update_statistics)
        overview_layout.addWidget(refresh_button)
        
        layout.addWidget(overview_group)
        
        return widget
        
    def toggle_recording(self):
        """切换录制状态"""
        if not self.is_recording_flag:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        """开始录制"""
        self.is_recording_flag = True
        self.recorded_data = []
        self.recording_start_time = datetime.now()
        self.current_label = self.label_combo.currentText()
        
        # 更新UI
        self.record_button.setText("停止录制")
        self.record_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        
        self.status_label.setText(f"录制中 - {self.current_label}")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border: 2px solid #e74c3c;
                border-radius: 5px;
                background-color: #fadbd8;
                color: #e74c3c;
            }
        """
        )
        
        # 如果启用自动停止，设置定时器
        if self.auto_stop_checkbox.isChecked():
            duration = self.duration_spinbox.value() * 1000  # 转换为毫秒
            self.progress_bar.setMaximum(duration // 100)
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            
            QTimer.singleShot(duration, self.stop_recording)
            
        # 启动状态更新定时器
        self.recording_timer.start(100)  # 每100ms更新一次
        
        self.recording_started.emit()
        
    def stop_recording(self):
        """停止录制"""
        self.is_recording_flag = False
        self.recording_timer.stop()
        
        # 更新UI
        self.record_button.setText("开始录制")
        self.record_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                background-color: #27ae60;
                color: white;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """
        )
        
        sample_count = len(self.recorded_data)
        self.status_label.setText(f"录制完成 - {sample_count} 个样本")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border: 2px solid #27ae60;
                border-radius: 5px;
                background-color: #d5f4e6;
                color: #27ae60;
            }
        """
        )
        
        self.progress_bar.setVisible(False)
        
        # 启用保存和清除按钮
        self.save_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        
        # 更新预览
        self.update_preview()
        
        self.recording_stopped.emit()
        
    def add_data_point(self, data):
        """添加数据点"""
        if self.is_recording_flag:
            timestamp = datetime.now()
            data_point = {
                'timestamp': timestamp,
                'data': data.copy(),
                'label': self.current_label
            }
            self.recorded_data.append(data_point)
            
    def update_recording_status(self):
        """更新录制状态"""
        if not self.is_recording_flag:
            return
            
        # 更新统计信息
        sample_count = len(self.recorded_data)
        self.samples_label.setText(f"样本数: {sample_count}")
        
        if self.recording_start_time:
            duration = (datetime.now() - self.recording_start_time).total_seconds()
            self.duration_label.setText(f"时长: {duration:.1f}s")
            
            if duration > 0:
                rate = sample_count / duration
                self.rate_label.setText(f"采样率: {rate:.1f} Hz")
                
        # 更新进度条
        if self.progress_bar.isVisible() and self.auto_stop_checkbox.isChecked():
            duration_ms = (datetime.now() - self.recording_start_time).total_seconds() * 1000
            progress = min(int(duration_ms / 100), self.progress_bar.maximum())
            self.progress_bar.setValue(progress)
            
    def update_preview(self):
        """更新数据预览"""
        if not self.recorded_data:
            self.preview_text.clear()
            return
            
        # 显示最后几个数据点
        preview_lines = []
        for i, data_point in enumerate(self.recorded_data[-10:]):
            timestamp = data_point['timestamp'].strftime('%H:%M:%S.%f')[:-3]
            data_str = ', '.join([f"{x:.3f}" for x in data_point['data'][:5]])  # 只显示前5个值
            preview_lines.append(f"[{timestamp}] {data_str}...")
            
        self.preview_text.setText('\\n'.join(preview_lines))
        
    def save_recorded_data(self):
        """保存录制的数据"""
        if not self.recorded_data:
            QMessageBox.warning(self, "警告", "没有数据可保存")
            return
            
        # 选择保存文件
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存录制数据", 
            f"{self.current_label}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV files (*.csv);;JSON files (*.json);;All files (*)"
        )
        
        if file_path:
            try:
                self.save_data_to_file(self.recorded_data, file_path)
                QMessageBox.information(self, "成功", f"数据已保存到: {file_path}")
                self.data_exported.emit(file_path)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存数据失败: {str(e)}")
                
    def save_data_to_file(self, data, file_path):
        """保存数据到文件"""
        if file_path.endswith('.csv'):
            # 保存为CSV格式
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                if not data:
                    return
                    
                # 写入表头
                fieldnames = ['timestamp', 'label'] + [f'sensor_{i}' for i in range(len(data[0]['data']))]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # 写入数据
                for data_point in data:
                    row = {
                        'timestamp': data_point['timestamp'].isoformat(),
                        'label': data_point['label']
                    }
                    for i, value in enumerate(data_point['data']):
                        row[f'sensor_{i}'] = value
                    writer.writerow(row)
                    
        elif file_path.endswith('.json'):
            # 保存为JSON格式
            json_data = []
            for data_point in data:
                json_data.append({
                    'timestamp': data_point['timestamp'].isoformat(),
                    'label': data_point['label'],
                    'data': data_point['data']
                })
                
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)
                
    def clear_recorded_data(self):
        """清除录制的数据"""
        self.recorded_data = []
        self.save_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.preview_text.clear()
        
        self.status_label.setText("未录制")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ecf0f1;
            }
        """
        )
        
        self.samples_label.setText("样本数: 0")
        self.duration_label.setText("时长: 0s")
        self.rate_label.setText("采样率: 0 Hz")
        
    def browse_export_path(self):
        """浏览导出路径"""
        path = QFileDialog.getExistingDirectory(self, "选择导出路径", self.path_edit.text())
        if path:
            self.path_edit.setText(path)
            
    def export_current_data(self):
        """导出当前数据"""
        if not self.recorded_data:
            QMessageBox.warning(self, "警告", "没有数据可导出")
            return
            
        self.export_data(self.recorded_data)
        
    def export_all_data(self):
        """导出所有数据"""
        # 这里可以实现导出所有历史数据的功能
        QMessageBox.information(self, "提示", "导出所有数据功能待实现")
        
    def export_data(self, data):
        """导出数据"""
        if not data:
            return
            
        export_path = self.path_edit.text()
        filename = self.filename_edit.text()
        file_format = self.format_combo.currentText().lower()
        
        full_path = os.path.join(export_path, f"{filename}.{file_format}")
        
        try:
            self.save_data_to_file(data, full_path)
            QMessageBox.information(self, "成功", f"数据已导出到: {full_path}")
            self.data_exported.emit(full_path)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出数据失败: {str(e)}")
            
    def update_statistics(self):
        """更新统计信息"""
        if not self.recorded_data:
            self.overview_text.setText("暂无数据")
            return
            
        # 计算统计信息
        total_samples = len(self.recorded_data)
        
        if self.recording_start_time:
            duration = (datetime.now() - self.recording_start_time).total_seconds()
        else:
            duration = 0
            
        # 按标签统计
        label_counts = {}
        for data_point in self.recorded_data:
            label = data_point['label']
            label_counts[label] = label_counts.get(label, 0) + 1
            
        # 生成统计报告
        stats_text = f"""数据统计报告
==================
总样本数: {total_samples}
录制时长: {duration:.2f} 秒
平均采样率: {total_samples/duration:.2f} Hz (如果duration > 0)

按标签分组:
{'-' * 20}
"""
        
        for label, count in label_counts.items():
            percentage = (count / total_samples) * 100
            stats_text += f"{label}: {count} 样本 ({percentage:.1f}%)\\n"
            
        self.overview_text.setText(stats_text)
        
    def is_recording(self):
        """检查是否正在录制"""
        return self.is_recording_flag
        
    def get_recorded_data(self):
        """获取录制的数据"""
        return self.recorded_data.copy()