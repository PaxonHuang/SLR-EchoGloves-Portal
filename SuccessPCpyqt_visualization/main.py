#!/usr/bin/env python3
"""
PyQt手势识别可视化系统 - 主程序入口
基于现有的ESP32手势识别项目，提供实时数据可视化和手势识别界面
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow

def main():
    # 创建QApplication实例，设置高DPI支持必须在创建之前
    import sys
    sys.argv += ['--style', 'Fusion']  # 使用Fusion样式以获得更好的跨平台外观
    
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("手势识别可视化系统")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Hand Gesture Recognition")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行事件循环
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()