// 定义ADC引脚
const int adcPins[5] = {34, 35, 32, 33, 36};  // 5个ADC输入引脚
const float maxVoltage = 3.3;  // 最大电压（平放，0度）
const float midVoltage = 1.65; // 90度对应的电压
const float angleRange = 90.0; // 最大角度范围为90度

void setup() {
  Serial.begin(115200);  // 初始化串口
  delay(1000);           // 等待串口初始化
}

// 将电压值转换为角度
float voltageToAngle(float voltage) {
  if (voltage > midVoltage) {
    // 从90度到0度范围
    return 90.0 - ((voltage - midVoltage) / (maxVoltage - midVoltage) * angleRange);
  } else {
    // 从0度到90度范围
    return (midVoltage - voltage) / midVoltage * angleRange;
  }
}

void loop() {
  float angles[5];  // 存储5个传感器的角度数据

  // 读取每个传感器的电压并转换为角度
  for (int i = 0; i < 5; i++) {
    int adcValue = analogRead(adcPins[i]);
    float voltage = (adcValue / 4095.0) * maxVoltage;
    angles[i] = voltageToAngle(voltage);
  }

  // 清空串口缓存，以确保数据实时更新
  while (Serial.available()) {
    Serial.read();
  }

  // 输出5个传感器的角度数据
  Serial.print("Angles:");
  for (int i = 0; i < 5; i++) {
    Serial.print(angles[i]);
    Serial.print(i < 4 ? "," : "\n");  // 以逗号分隔，最后一个数据换行
  }

  delay(50); // 每50ms发送一次数据
}
