#!/usr/bin/env python3
"""
手势识别可视化系统启动脚本
"""
import os
import sys

def main():
    """主函数"""
    print("手势识别可视化系统")
    print("=" * 40)
    
    # 启动应用程序
    print("启动应用程序...")
    
    try:
        from main import main as app_main
        app_main()
    except Exception as e:
        print(f"启动应用程序失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()