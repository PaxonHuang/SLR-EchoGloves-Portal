"""
模型训练脚本
用于训练手势识别模型
"""
import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import joblib

def load_dataset():
    """加载数据集"""
    print("正在加载数据集...")
    
    # 尝试加载静态手势数据集
    dataset_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 
        'Datasets', 'Static Gestures', 'Dataset', 'dataset.csv'
    )
    
    if os.path.exists(dataset_path):
        print(f"找到数据集: {dataset_path}")
        df = pd.read_csv(dataset_path)
        
        # 假设最后一列是标签
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values
        
        print(f"数据集形状: {X.shape}")
        print(f"类别数量: {len(np.unique(y))}")
        print(f"类别: {np.unique(y)}")
        
        return X, y
    else:
        print(f"未找到数据集: {dataset_path}")
        print("将创建模拟数据集用于演示...")
        
        # 创建模拟数据
        np.random.seed(42)
        n_samples = 1000
        n_features = 30
        n_classes = 14
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, n_classes, n_samples)
        
        # 为每个类别添加一些特征模式
        for i in range(n_classes):
            mask = y == i
            X[mask] += np.random.randn(n_features) * 2
            
        # 转换标签为字符串
        gesture_names = [
            'Cash', 'Come Here', 'Excellent', 'Fingers crossed', 'Fist',
            'Five', 'Four', 'Go Away', 'One', 'Stop', 'Three', 
            'Thumbs Down', 'Thumbs Up', 'Two'
        ]
        y = np.array([gesture_names[i] for i in y])
        
        print(f"模拟数据集形状: {X.shape}")
        return X, y

def train_models(X, y):
    """训练多个模型并比较性能"""
    print("\\n开始训练模型...")
    
    # 数据分割
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 特征标准化
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 定义模型
    models = {
        'knn': KNeighborsClassifier(n_neighbors=5, weights='distance'),
        'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'svm': SVC(kernel='rbf', probability=True, random_state=42)
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\\n训练 {name.upper()} 模型...")
        
        # 训练模型
        if name == 'svm':
            # SVM需要标准化的数据
            model.fit(X_train_scaled, y_train)
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            y_pred = model.predict(X_test_scaled)
        else:
            # 其他模型可以使用原始数据
            model.fit(X_train, y_train)
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            y_pred = model.predict(X_test)
            
        # 交叉验证
        if name == 'svm':
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
        else:
            cv_scores = cross_val_score(model, X_train, y_train, cv=5)
            
        results[name] = {
            'model': model,
            'train_score': train_score,
            'test_score': test_score,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'predictions': y_pred
        }
        
        print(f"训练准确率: {train_score:.4f}")
        print(f"测试准确率: {test_score:.4f}")
        print(f"交叉验证: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # 选择最佳模型
    best_model_name = max(results.keys(), key=lambda x: results[x]['test_score'])
    best_model = results[best_model_name]['model']
    
    print(f"\\n最佳模型: {best_model_name.upper()}")
    print(f"测试准确率: {results[best_model_name]['test_score']:.4f}")
    
    # 详细分类报告
    print("\\n分类报告:")
    print(classification_report(y_test, results[best_model_name]['predictions']))
    
    return best_model, scaler, results

def save_model(model, scaler, model_name='gesture_model'):
    """保存模型"""
    model_dir = os.path.dirname(__file__)
    
    model_path = os.path.join(model_dir, f'{model_name}.pkl')
    scaler_path = os.path.join(model_dir, 'scaler.pkl')
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    print(f"\\n模型已保存到: {model_path}")
    print(f"缩放器已保存到: {scaler_path}")
    
    # 保存模型信息
    info_path = os.path.join(model_dir, 'model_info.txt')
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(f"模型类型: {type(model).__name__}\\n")
        f.write(f"训练时间: {pd.Timestamp.now()}\\n")
        f.write(f"特征数量: {model.n_features_in_ if hasattr(model, 'n_features_in_') else 'Unknown'}\\n")
        if hasattr(model, 'classes_'):
            f.write(f"类别: {', '.join(model.classes_)}\\n")
    
    print(f"模型信息已保存到: {info_path}")

def main():
    """主函数"""
    print("手势识别模型训练脚本")
    print("=" * 40)
    
    try:
        # 加载数据
        X, y = load_dataset()
        
        # 训练模型
        best_model, scaler, results = train_models(X, y)
        
        # 保存模型
        save_model(best_model, scaler)
        
        print("\\n训练完成！")
        
        # 显示所有模型的比较
        print("\\n模型性能比较:")
        print("-" * 50)
        for name, result in results.items():
            print(f"{name.upper():<15} | 测试准确率: {result['test_score']:.4f} | CV: {result['cv_mean']:.4f}±{result['cv_std']:.4f}")
        
    except Exception as e:
        print(f"训练过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()