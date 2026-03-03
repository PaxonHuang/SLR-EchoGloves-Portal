#include <Wire.h>
#include <MPU6050.h>

#define FLEX_PIN A0

// Flex传感器参数（可根据实际调整）
const float VCC = 5.0; // 供电电压
const float R_DIV = 20000.0; // 分压电阻20KΩ
const float STRAIGHT_RESISTANCE = 37300.0; // 平直时电阻
const float BEND_RESISTANCE = 90000.0; // 90度弯曲时电阻

MPU6050 mpu;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed!");
    while (1);
  }
  pinMode(FLEX_PIN, INPUT);
  Serial.println("Setup complete.");
}

void loop() {
  // 1. 读取Flex传感器
  int flexADC = analogRead(FLEX_PIN);
  float flexV = flexADC * VCC / 1023.0;
  float flexR = R_DIV * (VCC / flexV - 1.0);
  float flexAngle = map(flexR, STRAIGHT_RESISTANCE, BEND_RESISTANCE, 0, 90);

  // 2. 读取MPU6050数据
  int16_t ax, ay, az, gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  // 3. 串口输出（CSV格式，方便后续训练用）
  Serial.print("flexADC,"); Serial.print(flexADC);
  Serial.print(",flexV,"); Serial.print(flexV, 3);
  Serial.print(",flexR,"); Serial.print(flexR, 1);
  Serial.print(",flexAngle,"); Serial.print(flexAngle, 1);
  Serial.print(",ax,"); Serial.print(ax);
  Serial.print(",ay,"); Serial.print(ay);
  Serial.print(",az,"); Serial.print(az);
  Serial.print(",gx,"); Serial.print(gx);
  Serial.print(",gy,"); Serial.print(gy);
  Serial.print(",gz,"); Serial.println(gz);

  delay(20); // 50Hz采样
}

// Arduino的map函数只支持整数，这里自定义一个float版本
float map(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}