"""
手势显示组件
实时显示识别到的手势及其置信度
"""
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QGroupBox, QLCDNumber, QListWidget,
                             QListWidgetItem, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QPen
from collections import deque
import numpy as np

class GestureDisplayWidget(QWidget):
    """手势显示小部件"""
    
    gesture_selected = pyqtSignal(str)  # 手势选择信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # 手势历史记录
        self.gesture_history = deque(maxlen=50)
        self.confidence_history = deque(maxlen=100)
        
        # 当前手势状态
        self.current_gesture = "未知"
        self.current_confidence = 0.0
        
        # 手势稳定性检测
        self.stable_gesture_buffer = deque(maxlen=10)
        self.min_stable_count = 5
        self.min_confidence_threshold = 0.6
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 当前手势显示区域
        current_group = QGroupBox("当前识别手势")
        current_layout = QVBoxLayout(current_group)
        
        # 手势名称显示
        self.gesture_label = QLabel("未知")
        self.gesture_label.setAlignment(Qt.AlignCenter)
        self.gesture_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }
        """
        )
        current_layout.addWidget(self.gesture_label)
        
        # 置信度显示
        confidence_layout = QHBoxLayout()
        
        confidence_layout.addWidget(QLabel("置信度:"))
        
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        self.confidence_bar.setValue(0)
        self.confidence_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """
        )
        confidence_layout.addWidget(self.confidence_bar)
        
        self.confidence_lcd = QLCDNumber(4)
        self.confidence_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.confidence_lcd.setStyleSheet("""
            QLCDNumber {
                background-color: #2c3e50;
                color: #27ae60;
                border: 1px solid #34495e;
                border-radius: 5px;
            }
        """
        )
        confidence_layout.addWidget(self.confidence_lcd)
        
        current_layout.addLayout(confidence_layout)
        
        layout.addWidget(current_group)
        
        # 手势图像显示（可选）
        image_group = QGroupBox("手势示意图")
        image_layout = QVBoxLayout(image_group)
        
        self.gesture_image_label = QLabel()
        self.gesture_image_label.setAlignment(Qt.AlignCenter)
        self.gesture_image_label.setMinimumSize(200, 150)
        self.gesture_image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """
        )
        image_layout.addWidget(self.gesture_image_label)
        
        layout.addWidget(image_group)
        
        # 统计信息
        stats_group = QGroupBox("识别统计")
        stats_layout = QVBoxLayout(stats_group)
        
        # 手势计数
        self.gesture_count_label = QLabel("总识别次数: 0")
        stats_layout.addWidget(self.gesture_count_label)
        
        # 准确率指示
        self.accuracy_label = QLabel("平均置信度: 0.00%")
        stats_layout.addWidget(self.accuracy_label)
        
        # 稳定性指示
        self.stability_label = QLabel("手势稳定性: 低")
        stats_layout.addWidget(self.stability_label)
        
        layout.addWidget(stats_group)
        
        # 历史记录
        history_group = QGroupBox("识别历史")
        history_layout = QVBoxLayout(history_group)
        
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(150)
        history_layout.addWidget(self.history_list)
        
        # 清除历史按钮
        clear_btn = QPushButton("清除历史")
        clear_btn.clicked.connect(self.clear_history)
        history_layout.addWidget(clear_btn)
        
        layout.addWidget(history_group)
        
        # 设置伸缩因子
        layout.setStretchFactor(current_group, 3)
        layout.setStretchFactor(image_group, 2)
        layout.setStretchFactor(stats_group, 1)
        layout.setStretchFactor(history_group, 2)
        
    def update_gesture(self, gesture, confidence):
        """更新识别到的手势"""
        self.current_gesture = gesture
        self.current_confidence = confidence
        
        # 添加到稳定性缓冲区
        self.stable_gesture_buffer.append((gesture, confidence))
        
        # 检查手势稳定性
        stable_gesture = self.get_stable_gesture()
        
        if stable_gesture:
            # 只有稳定的手势才显示
            self.display_gesture(stable_gesture[0], stable_gesture[1])
            
            # 添加到历史记录
            self.add_to_history(stable_gesture[0], stable_gesture[1])
            
        # 更新统计信息
        self.update_statistics()
        
    def get_stable_gesture(self):
        """获取稳定的手势"""
        if len(self.stable_gesture_buffer) < self.min_stable_count:
            return None
            
        # 检查最近的手势是否一致
        recent_gestures = list(self.stable_gesture_buffer)[-self.min_stable_count:]
        gesture_names = [g[0] for g in recent_gestures]
        confidences = [g[1] for g in recent_gestures]
        
        # 检查手势一致性和置信度
        if (len(set(gesture_names)) == 1 and 
            all(c >= self.min_confidence_threshold for c in confidences)):
            
            avg_confidence = np.mean(confidences)
            return gesture_names[0], avg_confidence
            
        return None
        
    def display_gesture(self, gesture, confidence):
        """显示手势"""
        # 更新手势标签
        self.gesture_label.setText(gesture)
        
        # 根据置信度设置颜色
        if confidence >= 0.8:
            color = "#27ae60"  # 绿色
        elif confidence >= 0.6:
            color = "#f39c12"  # 橙色
        else:
            color = "#e74c3c"  # 红色
            
        self.gesture_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {color};
                background-color: #ecf0f1;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }}
        """
        )
        
        # 更新置信度显示
        confidence_percent = int(confidence * 100)
        self.confidence_bar.setValue(confidence_percent)
        self.confidence_lcd.display(f"{confidence:.3f}")
        
        # 更新手势图像
        self.update_gesture_image(gesture)
        
    def update_gesture_image(self, gesture):
        """更新手势示意图"""
        # 查找手势图像文件
        image_path = self.find_gesture_image(gesture)
        
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # 缩放图像以适应标签
            scaled_pixmap = pixmap.scaled(
                self.gesture_image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.gesture_image_label.setPixmap(scaled_pixmap)
        else:
            # 如果没有找到图像，显示文本
            self.gesture_image_label.clear()
            self.gesture_image_label.setText(f"手势: {gesture}")
            
    def find_gesture_image(self, gesture):
        """查找手势图像文件"""
        # 查找项目中的手势图像
        base_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 
            'Figures', 'Static Gestures', 'Individual'
        )
        
        # 可能的文件名格式
        possible_names = [
            f"{gesture}.jpg",
            f"{gesture}.png",
            f"{gesture.lower()}.jpg",
            f"{gesture.lower()}.png",
            f"{gesture.replace(' ', '')}.jpg",
            f"{gesture.replace(' ', '')}.png"
        ]
        
        for name in possible_names:
            full_path = os.path.join(base_path, name)
            if os.path.exists(full_path):
                return full_path
                
        return None
        
    def add_to_history(self, gesture, confidence):
        """添加到历史记录"""
        self.gesture_history.append((gesture, confidence))
        self.confidence_history.append(confidence)
        
        # 更新历史列表显示
        item_text = f"{gesture} ({confidence:.3f})"
        item = QListWidgetItem(item_text)
        
        # 根据置信度设置颜色
        if confidence >= 0.8:
            item.setBackground(QColor("#d5f4e6"))  # 浅绿色
        elif confidence >= 0.6:
            item.setBackground(QColor("#fdeaa7"))  # 浅黄色
        else:
            item.setBackground(QColor("#fab1a0"))  # 浅红色
            
        self.history_list.insertItem(0, item)
        
        # 限制历史记录显示数量
        if self.history_list.count() > 20:
            self.history_list.takeItem(self.history_list.count() - 1)
            
    def update_statistics(self):
        """更新统计信息"""
        # 总识别次数
        total_count = len(self.gesture_history)
        self.gesture_count_label.setText(f"总识别次数: {total_count}")
        
        # 平均置信度
        if self.confidence_history:
            avg_confidence = np.mean(self.confidence_history)
            self.accuracy_label.setText(f"平均置信度: {avg_confidence:.2%}")
        else:
            self.accuracy_label.setText("平均置信度: 0.00%")
            
        # 稳定性评估
        stability = self.assess_stability()
        self.stability_label.setText(f"手势稳定性: {stability}")
        
    def assess_stability(self):
        """评估手势稳定性"""
        if len(self.confidence_history) < 10:
            return "评估中"
            
        recent_confidences = list(self.confidence_history)[-10:]
        std_dev = np.std(recent_confidences)
        mean_confidence = np.mean(recent_confidences)
        
        if std_dev < 0.1 and mean_confidence > 0.8:
            return "高"
        elif std_dev < 0.2 and mean_confidence > 0.6:
            return "中"
        else:
            return "低"
            
    def clear_history(self):
        """清除历史记录"""
        self.gesture_history.clear()
        self.confidence_history.clear()
        self.history_list.clear()
        self.update_statistics()
        
    def reset_display(self):
        """重置显示"""
        self.gesture_label.setText("未知")
        self.gesture_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }
        """
        )
        
        self.confidence_bar.setValue(0)
        self.confidence_lcd.display(0.0)
        self.gesture_image_label.clear()
        self.gesture_image_label.setText("等待手势识别...")
        
        self.stable_gesture_buffer.clear()
        
    def get_gesture_statistics(self):
        """获取手势统计信息"""
        if not self.gesture_history:
            return {}
            
        # 统计各手势出现次数
        gesture_counts = {}
        for gesture, _ in self.gesture_history:
            gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1
            
        # 计算各手势平均置信度
        gesture_confidences = {}
        for gesture, confidence in self.gesture_history:
            if gesture not in gesture_confidences:
                gesture_confidences[gesture] = []
            gesture_confidences[gesture].append(confidence)
            
        gesture_avg_confidence = {}
        for gesture, confidences in gesture_confidences.items():
            gesture_avg_confidence[gesture] = np.mean(confidences)
            
        return {
            'counts': gesture_counts,
            'avg_confidences': gesture_avg_confidence,
            'total_recognitions': len(self.gesture_history),
            'overall_avg_confidence': np.mean(self.confidence_history) if self.confidence_history else 0
        }