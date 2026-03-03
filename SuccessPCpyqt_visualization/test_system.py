#!/usr/bin/env python3
"""
快速功能测试脚本
"""
import sys
import os

def test_imports():
    """测试所有重要模块的导入"""
    print("测试模块导入...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5基础模块")
        
        from ui.widgets.sensor_plots import SensorPlotsWidget
        print("✓ 传感器可视化组件")
        
        from ui.widgets.gesture_display import GestureDisplayWidget
        print("✓ 手势显示组件")
        
        from ui.widgets.data_manager import DataManagerWidget
        print("✓ 数据管理组件")
        
        from ui.widgets.settings_panel import SettingsPanel
        print("✓ 设置面板组件")
        
        from core.serial_interface import SerialInterface
        print("✓ 串口接口")
        
        from core.gesture_classifier import GestureClassifier
        print("✓ 手势分类器")
        
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_ui_creation():
    """测试UI组件创建"""
    print("\n测试UI组件创建...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        import sys
        
        app = QApplication(sys.argv)
        
        from ui.widgets.sensor_plots import SensorPlotsWidget
        sensor_widget = SensorPlotsWidget()
        print("✓ 传感器可视化组件创建成功")
        
        from ui.widgets.gesture_display import GestureDisplayWidget
        gesture_widget = GestureDisplayWidget()
        print("✓ 手势显示组件创建成功")
        
        from ui.widgets.settings_panel import SettingsPanel
        settings_widget = SettingsPanel()
        print("✓ 设置面板组件创建成功")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"✗ UI创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_core_modules():
    """测试核心模块"""
    print("\n测试核心模块...")
    
    try:
        from core.serial_interface import SerialInterface
        serial_interface = SerialInterface()
        print("✓ 串口接口创建成功")
        
        from core.gesture_classifier import GestureClassifier
        classifier = GestureClassifier()
        print("✓ 手势分类器创建成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 核心模块测试失败: {e}")
        return False

def main():
    print("手势识别可视化系统 - 功能测试")
    print("=" * 50)
    
    success = True
    
    success &= test_imports()
    success &= test_core_modules()
    success &= test_ui_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ 所有测试通过！系统可以正常运行。")
        print("\n启动应用程序:")
        print("python3 start.py")
    else:
        print("✗ 部分测试失败，请检查错误信息。")
    
    return success

if __name__ == "__main__":
    main()