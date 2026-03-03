"""
手势分类器模块
基于机器学习算法进行实时手势识别
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

class GestureClassifier:
    """手势分类器类"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # 手势标签
        self.static_gestures = [
            'Cash', 'Come Here', 'Excellent', 'Fingers crossed', 'Fist',
            'Five', 'Four', 'Go Away', 'One', 'Stop', 'Three', 
            'Thumbs Down', 'Thumbs Up', 'Two'
        ]
        
        self.dynamic_gestures = ['Painting', 'Thank You', 'Sorry']
        
        self.all_gestures = self.static_gestures + self.dynamic_gestures
        
        # 特征窗口大小
        self.window_size = 180
        self.feature_buffer = []
        
        # 尝试加载预训练模型
        self._try_load_model()
        
    def _try_load_model(self):
        """尝试加载预训练的模型"""
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models')
        
        try:
            if os.path.exists(os.path.join(model_path, 'gesture_model.pkl')):
                self.model = joblib.load(os.path.join(model_path, 'gesture_model.pkl'))
                self.scaler = joblib.load(os.path.join(model_path, 'scaler.pkl'))
                self.is_trained = True
                print("成功加载预训练模型")
        except Exception as e:
            print(f"加载模型失败: {str(e)}")
            self._create_default_model()
            
    def _create_default_model(self):
        """创建默认模型"""
        # 使用KNN作为默认模型，基于论文结果
        self.model = KNeighborsClassifier(n_neighbors=5, weights='distance')
        print("创建默认KNN模型")
        
    def extract_features(self, sensor_data):
        """从传感器数据提取特征"""
        if len(sensor_data) < 27:
            return None
            
        # 分离不同类型的传感器数据
        flex_data = sensor_data[:5]          # 弯曲传感器
        quaternion = sensor_data[5:9]        # 四元数
        gyro_data = sensor_data[9:12]        # 陀螺仪
        acc_data = sensor_data[12:15]        # 加速度计
        acc_real = sensor_data[15:18]        # 真实加速度
        acc_world = sensor_data[18:21]       # 世界坐标系加速度
        gravity = sensor_data[21:24]         # 重力
        acc_raw = sensor_data[24:27]         # 原始加速度
        
        features = []
        
        # 弯曲传感器特征
        features.extend(flex_data)  # 原始值
        features.append(np.mean(flex_data))  # 均值
        features.append(np.std(flex_data))   # 标准差
        features.append(np.max(flex_data) - np.min(flex_data))  # 范围
        
        # 四元数特征
        features.extend(quaternion)
        quat_magnitude = np.sqrt(sum(q**2 for q in quaternion))
        features.append(quat_magnitude)
        
        # 陀螺仪特征
        features.extend(gyro_data)
        features.append(np.linalg.norm(gyro_data))  # 幅值
        
        # 加速度特征
        features.extend(acc_data)
        features.append(np.linalg.norm(acc_data))
        
        # 真实加速度特征
        features.extend(acc_real)
        features.append(np.linalg.norm(acc_real))
        
        # 世界坐标系加速度特征
        features.extend(acc_world)
        
        # 重力特征
        features.extend(gravity)
        
        # 如果有额外的传感器数据
        if len(sensor_data) > 27:
            gyro_raw = sensor_data[27:30] if len(sensor_data) >= 30 else sensor_data[27:]
            features.extend(gyro_raw)
            
        return np.array(features)
        
    def predict(self, sensor_data):
        """预测手势"""
        if not self.is_trained:
            return "未知", 0.0
            
        try:
            # 提取特征
            features = self.extract_features(sensor_data)
            if features is None:
                return "数据不完整", 0.0
                
            # 添加到特征缓冲区
            self.feature_buffer.append(features)
            
            # 保持缓冲区大小
            if len(self.feature_buffer) > 10:
                self.feature_buffer.pop(0)
                
            # 使用最近的特征进行预测
            if len(self.feature_buffer) >= 3:
                # 使用滑动窗口的平均特征
                avg_features = np.mean(self.feature_buffer[-3:], axis=0)
                features_scaled = self.scaler.transform([avg_features])
                
                # 预测
                prediction = self.model.predict(features_scaled)[0]
                
                # 如果模型支持概率预测
                if hasattr(self.model, 'predict_proba'):
                    probabilities = self.model.predict_proba(features_scaled)[0]
                    confidence = max(probabilities)
                    
                    # 获取最高概率对应的手势
                    gesture_idx = np.argmax(probabilities)
                    if gesture_idx < len(self.all_gestures):
                        gesture = self.all_gestures[gesture_idx]
                    else:
                        gesture = str(prediction)
                else:
                    gesture = str(prediction)
                    confidence = 0.8  # 默认置信度
                    
                return gesture, confidence
            else:
                return "准备中", 0.0
                
        except Exception as e:
            print(f"预测错误: {str(e)}")
            return "错误", 0.0
            
    def train_model(self, dataset_path=None):
        """训练模型"""
        try:
            if dataset_path is None:
                # 使用项目中的数据集
                static_dataset_path = os.path.join(
                    os.path.dirname(__file__), '..', '..', 
                    'Datasets', 'Static Gestures', 'Dataset', 'dataset.csv'
                )
                
                if not os.path.exists(static_dataset_path):
                    print("未找到训练数据集")
                    return False
                    
                # 加载静态手势数据
                df = pd.read_csv(static_dataset_path)
                
                # 假设最后一列是标签
                X = df.iloc[:, :-1].values
                y = df.iloc[:, -1].values
                
            else:
                # 使用指定的数据集
                df = pd.read_csv(dataset_path)
                X = df.iloc[:, :-1].values
                y = df.iloc[:, -1].values
                
            # 数据预处理
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # 标准化特征
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # 训练KNN模型（基于论文最佳结果）
            self.model = KNeighborsClassifier(n_neighbors=5, weights='distance')
            self.model.fit(X_train_scaled, y_train)
            
            # 评估模型
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            print(f"训练集准确率: {train_score:.4f}")
            print(f"测试集准确率: {test_score:.4f}")
            
            self.is_trained = True
            
            # 保存模型
            self._save_model()
            
            return True
            
        except Exception as e:
            print(f"训练模型错误: {str(e)}")
            return False
            
    def _save_model(self):
        """保存模型"""
        try:
            model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
            os.makedirs(model_dir, exist_ok=True)
            
            joblib.dump(self.model, os.path.join(model_dir, 'gesture_model.pkl'))
            joblib.dump(self.scaler, os.path.join(model_dir, 'scaler.pkl'))
            
            print("模型保存成功")
        except Exception as e:
            print(f"保存模型错误: {str(e)}")
            
    def get_gesture_list(self):
        """获取支持的手势列表"""
        return self.all_gestures.copy()
        
    def is_model_trained(self):
        """检查模型是否已训练"""
        return self.is_trained