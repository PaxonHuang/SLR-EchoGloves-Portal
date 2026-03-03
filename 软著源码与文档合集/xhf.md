# 数据手套系统 - Web管理平台开发

## 项目背景
你需要为一个数据手套手语翻译系统开发Web管理平台子模块。该系统整体架构包括：
- 硬件层：ESP32/STM32 + 传感器（弯曲传感器、应变片、IMU）
- Qt预处理应用
- 腾讯云IoT Hub
- 云端AI处理服务
- Unity移动端应用

## 技术要求
- 后端：Spring Boot 3.x + Spring Security + JWT
- 前端：Vue 3 + Element Plus + TypeScript
- 数据库：MySQL 8.0
- 缓存：Redis
- 文档：Swagger/OpenAPI 3.0

## 功能需求

### 用户角色设计
1. **管理员 (ADMIN)**
   - 系统配置管理
   - 用户管理
   - 设备管理
   - 数据分析和监控
   - 系统日志查看

2. **普通用户 (USER)**
   - 个人资料管理
   - 设备绑定/解绑
   - 手势数据查看
   - 学习记录查看

### 核心功能模块

#### 1. 认证授权模块
- 用户注册/登录（支持邮箱、手机号）
- JWT token管理
- 权限控制（RBAC）
- 密码找回
- 账户安全设置

#### 2. 用户管理模块
- 用户列表（管理员）
- 用户详情
- 账户状态管理
- 角色分配

#### 3. 设备管理模块
- 设备注册和认证
- 设备状态监控
- 设备配置管理
- 设备与用户绑定关系

#### 4. 数据管理模块
- 传感器数据查看
- 手势识别结果
- 数据统计分析
- 数据导出功能

## 数据库设计要求

### 用户相关表
```sql
-- 用户基础信息表
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(100),
    avatar_url VARCHAR(500),
    status ENUM('ACTIVE', 'INACTIVE', 'BANNED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_status (status)
);

-- 角色表
CREATE TABLE roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户角色关联表
CREATE TABLE user_roles (
    user_id BIGINT,
    role_id BIGINT,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);
设备相关表
sql

-- 设备信息表
CREATE TABLE devices (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    device_id VARCHAR(100) UNIQUE NOT NULL,
    device_name VARCHAR(100) NOT NULL,
    device_type ENUM('DATA_GLOVE') DEFAULT 'DATA_GLOVE',
    hardware_version VARCHAR(50),
    firmware_version VARCHAR(50),
    mac_address VARCHAR(17),
    status ENUM('ONLINE', 'OFFLINE', 'MAINTENANCE') DEFAULT 'OFFLINE',
    last_heartbeat TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_device_id (device_id),
    INDEX idx_status (status)
);

-- 用户设备绑定表
CREATE TABLE user_devices (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    device_id BIGINT NOT NULL,
    bind_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_device (user_id, device_id)
);
接口预留要求
1. 与IoT Hub集成接口
java

// 设备数据接收接口
@PostMapping("/api/v1/iot/device-data")
public ResponseEntity<?> receiveDeviceData(@RequestBody DeviceDataDTO data);

// 设备状态更新接口
@PostMapping("/api/v1/iot/device-status")
public ResponseEntity<?> updateDeviceStatus(@RequestBody DeviceStatusDTO status);
2. 与AI服务集成接口
java

// 手势识别结果接收接口
@PostMapping("/api/v1/ai/gesture-result")
public ResponseEntity<?> receiveGestureResult(@RequestBody GestureResultDTO result);

// 模型训练状态接口
@GetMapping("/api/v1/ai/training-status/{taskId}")
public ResponseEntity<TrainingStatusDTO> getTrainingStatus(@PathVariable String taskId);
3. 与Unity客户端集成接口
java

// 用户认证接口
@PostMapping("/api/v1/auth/mobile-login")
public ResponseEntity<AuthResponseDTO> mobileLogin(@RequestBody MobileLoginDTO loginDTO);

// 用户数据同步接口
@GetMapping("/api/v1/user/sync-data")
public ResponseEntity<UserSyncDataDTO> syncUserData();
安全性要求

密码安全
使用BCrypt加密
密码强度验证
密码历史记录（防止重复使用）

接口安全
JWT token认证
API限流
请求参数验证
SQL注入防护

数据安全
敏感数据加密存储
操作日志记录
数据访问审计

项目结构要求
code

data-glove-web/
├── backend/
│   ├── src/main/java/com/dataglove/web/
│   │   ├── config/          # 配置类
│   │   ├── controller/      # 控制器
│   │   ├── service/         # 业务服务
│   │   ├── repository/      # 数据访问
│   │   ├── entity/          # 实体类
│   │   ├── dto/             # 数据传输对象
│   │   ├── security/        # 安全配置
│   │   ├── integration/     # 外部系统集成
│   │   └── common/          # 通用工具
│   ├── src/main/resources/
│   │   ├── application.yml
│   │   ├── application-dev.yml
│   │   ├── application-prod.yml
│   │   └── db/migration/    # 数据库迁移脚本
│   └── pom.xml
├── frontend/
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   ├── components/      # 通用组件
│   │   ├── store/           # Vuex状态管理
│   │   ├── router/          # 路由配置
│   │   ├── api/             # API调用
│   │   ├── utils/           # 工具函数
│   │   └── types/           # TypeScript类型定义
│   ├── package.json
│   └── vite.config.ts
└── docs/
    ├── API.md               # API文档
    ├── DEPLOYMENT.md        # 部署文档
    └── DATABASE.md          # 数据库文档
扩展性预留

消息队列集成
预留RabbitMQ/Kafka接口
异步处理大量设备数据

多租户支持
预留租户隔离机制
支持企业级部署

国际化支持
前端i18n框架集成
后端消息国际化

监控和告警
预留监控指标接口
系统健康检查端点

开发要求

代码质量
遵循阿里巴巴Java开发规范
单元测试覆盖率≥80%
使用SonarQube代码质量检查

文档要求
完整的API文档
数据库设计文档
部署文档

版本控制
使用Git进行版本管理
遵循GitFlow工作流

请按照以上要求开发数据手套系统的Web管理平台，确保代码质量和扩展性，为后续集成其他子模块做好准备。