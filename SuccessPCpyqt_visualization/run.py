#!/usr/bin/env python3
"""
手势识别可视化系统启动脚本
"""
import os
import sys
import subprocess

def check_dependencies():
    """检查依赖项"""
    print("检查依赖项...")
    
    required_packages = [
        'PyQt5', 'pyqtgraph', 'numpy', 'pandas', 
        'scikit-learn', 'pyserial', 'joblib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下依赖项:")
        for package in missing_packages:
            print(f"  - {package}")
        
        print("\\n请运行以下命令安装依赖项:")
        print("pip install -r requirements.txt")
        return False
    
    print("所有依赖项已安装")
    return True

def train_model_if_needed():
    """如果需要则训练模型"""
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'gesture_model.pkl')
    
    if not os.path.exists(model_path):
        print("未找到预训练模型，开始训练...")
        
        train_script = os.path.join(os.path.dirname(__file__), 'models', 'train_model.py')
        
        try:
            subprocess.run([sys.executable, train_script], check=True)
            print("模型训练完成")
        except subprocess.CalledProcessError as e:
            print(f"模型训练失败: {e}")
            print("将使用默认模型配置")
    else:
        print("找到预训练模型")

def main():
    """主函数"""
    print("手势识别可视化系统")
    print("=" * 40)
    
    # 检查依赖项
    if not check_dependencies():
        return
    
    # 训练模型（如果需要）
    train_model_if_needed()
    
    # 启动应用程序
    print("\\n启动应用程序...")
    
    try:
        from main import main as app_main
        app_main()
    except Exception as e:
        print(f"启动应用程序失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()