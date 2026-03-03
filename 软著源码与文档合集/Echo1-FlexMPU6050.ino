// File Name: MPU6050.ino
// Author: Puchenghuang
// Version: 1.0
// Date: 2025-03-16
// Description: MPU6050的Arduino代码
// License: MIT
'''
  版本：1.0
  日期：2025-03-16
  作者：Puchenghuang
  版权：MIT
  功能：
  1.通过MPU6050读取加速度计和陀螺仪数据
  2.通过AD转换读取传感器数据
  3.通过蓝牙模块将数据发送到手机APP
  4.通过矩阵按键控制LED灯
  5.通过串口打印数据
  6.通过串口控制LED灯
  7.通过串口控制MPU6050
  8.通过串口控制AD转换
  9.通过串口控制蓝牙模块
  10.通过串口控制矩阵按键
'''
#include <Wire.h>
#include <JY901.h>
#include <math.h>
const int FLEX_PIN0 = A0; // 模拟量A0口
const int FLEX_PIN1 = A1; // 模拟量A1口
const int FLEX_PIN2 = A2; // 模拟量A2口
const int FLEX_PIN3 = A3; // 模拟量A3口
const int FLEX_PIN4 = A4; // 模拟量A4口

const int KEY1 = 3;    // 连接矩阵按键的引脚
const int KEY2 = 4;    // 连接矩阵按键的引脚
const int LED_PIN = 5;
const float VCC = 3.30; // Android开发板上5V实测电压4.98V
const float R_DIV = 47000.0; // Measured resistance of 3.3k resistor


const int adcPins[5] = {34, 35, 32, 33, 36};  // 5个ADC输入引脚
const float maxVoltage = 3.3;  // 最大电压（平放，0度）
const float midVoltage = 1.65; // 90度对应的电压
const float angleRange = 90.0; // 最大角度范围为90度

float STRAIGHT_RESISTANCE0;
float STRAIGHT_RESISTANCE1;
float STRAIGHT_RESISTANCE2;
float STRAIGHT_RESISTANCE3;
float STRAIGHT_RESISTANCE4;

float BEND_RESISTANCE0;
float BEND_RESISTANCE1;
float BEND_RESISTANCE2;
float BEND_RESISTANCE3;
float BEND_RESISTANCE4;

float flexV0;
float flexV1;
float flexV2;
float flexV3;
float flexV4;

float flexR0;
float flexR1;
float flexR2;
float flexR3;
float flexR4;

int angle0;
int angle1;
int angle2;
int angle3;
int angle4;

int flexADC0;
int flexADC1;
int flexADC2;
int flexADC3;
int flexADC4;

int numdata[8] = {0};

void setup() 
{
  Serial.begin(115200);  // 初始化串口
  delay(1000);           // 等待串口初始化
  Serial.begin(115200);
  pinMode(FLEX_PIN0, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(KEY1, INPUT_PULLUP);
  pinMode(KEY2, INPUT_PULLUP);
  delay(5000);
  Serial.println("First init is starting!");
  LED_BLINK(5);
  Fist_init();
  digitalWrite(LED_PIN,LOW);
  if(STRAIGHT_RESISTANCE0!=0)
  {
    Serial.println("First init is ok!");
    Serial.println("Second init is starting!");
    LED_BLINK(5);
    Second_init();
    if(BEND_RESISTANCE0!=0 && BEND_RESISTANCE0>STRAIGHT_RESISTANCE0)
    {
      Serial.println("All init is ok!");
      digitalWrite(LED_PIN,HIGH);
    }
  } 
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

void serialEvent() 
{
  while (Serial.available()) 
  {
    JY901.CopeSerialData(Serial.read()); //Call JY901 data cope function
  }
}

void loop() 
{
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
  if (digitalRead(KEY2) == 0 && digitalRead(KEY1) == 1) 
  { 
    Read_ADC();
    Serial.print(angle4);Serial.print(",");
    Serial.print(angle3);Serial.print(",");
    Serial.print(angle2);Serial.print(",");
    Serial.print(angle1);Serial.print(",");
    Serial.print(angle0);Serial.print(",");
    Serial.print((int)((float)JY901.stcAngle.Angle[0]/32768*180));Serial.print(",");
    Serial.print((int)((float)JY901.stcAngle.Angle[1]/32768*180));Serial.print(",");
    Serial.println((int)((float)JY901.stcAngle.Angle[2]/32768*180));
    delay(80);
  }
  if(digitalRead(KEY1) == 0 && digitalRead(KEY2) == 1)
  {
    Read_ADC();
    numdata[0] = map(angle4,0,90,2500.,500);
    numdata[1] = map(angle3,0,90,500.,2500);
    numdata[2] = map(angle2,0,90,500.,2500);
    numdata[3] = map(angle1,0,90,500.,2500);
    numdata[4] = map(angle0,0,90,500.,2500);
    numdata[5] = map((int)((float)JY901.stcAngle.Angle[1]/32768*180),-90,90,2400,600);
    numdata[6] = map((int)((float)JY901.stcAngle.Angle[0]/32768*180),-90,90,2400,600);
    numdata[5] = constrain(numdata[5],600,2400);
    numdata[6] = constrain(numdata[6],600,2400);
    String order = "#1P" + (String)numdata[6] + "#2P" + (String)numdata[5] + "#3P" + (String)numdata[0] + "#4P" + (String)numdata[1] + "#5P" + (String)numdata[2] + "#6P" + (String)numdata[3] + "#7P" + (String)numdata[4] + "T100"; 
    Serial.println(order);
    for(int i = 0; i < 8; i++)
    {
      numdata[i] = 0;
    }
  }
  if(digitalRead(KEY2) == 1 && digitalRead(KEY1) == 1)
  {
    Serial.println("Only one model can be chosen!");  
  }
  if(digitalRead(KEY2) == 0 && digitalRead(KEY1) == 0)
  {
    Serial.println("Only one model can be chosen!");  
  }
  delay(20);
}
void Read_ADC()
{
  flexADC0 = analogRead(FLEX_PIN0);
  flexADC1 = analogRead(FLEX_PIN1);
  flexADC2 = analogRead(FLEX_PIN2);
  flexADC3 = analogRead(FLEX_PIN3);
  flexADC4 = analogRead(FLEX_PIN4);
  //A0
  flexV0 = flexADC0 * VCC / 1023.0;//计算电压
  flexR0 = R_DIV * (VCC / flexV0 - 1.0);//计算电阻值
  angle0 = map(flexR0, STRAIGHT_RESISTANCE0, BEND_RESISTANCE0,0,90.0);
  //A1
  flexV1 = flexADC1 * VCC / 1023.0;//计算电压
  flexR1 = R_DIV * (VCC / flexV1 - 1.0);//计算电阻值
  angle1 = map(flexR1, STRAIGHT_RESISTANCE1, BEND_RESISTANCE1,0,90.0);
  //A2
  flexV2 = flexADC2 * VCC / 1023.0;//计算电压
  flexR2 = R_DIV * (VCC / flexV2 - 1.0);//计算电阻值
  angle2 = map(flexR2, STRAIGHT_RESISTANCE2, BEND_RESISTANCE2,0,90.0);
  //A3
  flexV3 = flexADC3 * VCC / 1023.0;//计算电压
  flexR3 = R_DIV * (VCC / flexV3 - 1.0);//计算电阻值
  angle3 = map(flexR3, STRAIGHT_RESISTANCE3, BEND_RESISTANCE3,0,90.0);
  //A4
  flexV4 = flexADC4 * VCC / 1023.0;//计算电压
  flexR4 = R_DIV * (VCC / flexV4 - 1.0);//计算电阻值
  angle4 = map(flexR4, STRAIGHT_RESISTANCE4, BEND_RESISTANCE4,0,90.0);  
}

void LED_BLINK(int BTime)
{
  delay(3000);
  for(int i = 0;i<=BTime;i++)
  {
    digitalWrite(LED_PIN,LOW);
    delay(200);
    digitalWrite(LED_PIN,HIGH);
    delay(200);
  }
}

void Fist_init()
{
  int flexADC0 = analogRead(FLEX_PIN0);
  int flexADC1 = analogRead(FLEX_PIN1);
  int flexADC2 = analogRead(FLEX_PIN2);
  int flexADC3 = analogRead(FLEX_PIN3);
  int flexADC4 = analogRead(FLEX_PIN4);
  for(int i = 0;i<11;i++)
  {
    //A0
    float flexV0 = flexADC0 * VCC / 1023.0;//计算电压
    float flexR0 = R_DIV * (VCC / flexV0 - 1.0);//计算电阻值
    STRAIGHT_RESISTANCE0 = flexR0;
    //A1
    float flexV1 = flexADC1 * VCC / 1023.0;//计算电压
    float flexR1 = R_DIV * (VCC / flexV1 - 1.0);//计算电阻值
    STRAIGHT_RESISTANCE1 = flexR1;
    //A2
    float flexV2 = flexADC2 * VCC / 1023.0;//计算电压
    float flexR2 = R_DIV * (VCC / flexV2 - 1.0);//计算电阻值
    STRAIGHT_RESISTANCE2 = flexR2;
    //A3
    float flexV3 = flexADC3 * VCC / 1023.0;//计算电压
    float flexR3 = R_DIV * (VCC / flexV3 - 1.0);//计算电阻值
    STRAIGHT_RESISTANCE3 = flexR3;
    //A4
    float flexV4 = flexADC4 * VCC / 1023.0;//计算电压
    float flexR4 = R_DIV * (VCC / flexV4 - 1.0);//计算电阻值
    STRAIGHT_RESISTANCE4 = flexR4;
    delay(50);
  }
}


void Second_init()
{
  int flexADC0 = analogRead(FLEX_PIN0);
  int flexADC1 = analogRead(FLEX_PIN1);
  int flexADC2 = analogRead(FLEX_PIN2);
  int flexADC3 = analogRead(FLEX_PIN3);
  int flexADC4 = analogRead(FLEX_PIN4);
  for(int i = 0;i<11;i++)
  {
    //A0
    float flexV0 = flexADC0 * VCC / 1023.0;//计算电压
    float flexR0 = R_DIV * (VCC / flexV0 - 1.0);//计算电阻值
    BEND_RESISTANCE0 = flexR0;
    //A1
    float flexV1 = flexADC1 * VCC / 1023.0;//计算电压
    float flexR1 = R_DIV * (VCC / flexV1 - 1.0);//计算电阻
    BEND_RESISTANCE1 = flexR1;
    //A2
    float flexV2 = flexADC2 * VCC / 1023.0;//计算电压
    float flexR2 = R_DIV * (VCC / flexV2 - 1.0);//计算电阻值
    BEND_RESISTANCE2 = flexR2;
    //A3
    float flexV3 = flexADC3 * VCC / 1023.0;//计算电压
    float flexR3 = R_DIV * (VCC / flexV3 - 1.0);//计算电阻值
    BEND_RESISTANCE3 = flexR3;
    //A4
    float flexV4 = flexADC4 * VCC / 1023.0;//计算电压
    float flexR4 = R_DIV * (VCC / flexV4 - 1.0);//计算电阻值
    BEND_RESISTANCE4 = flexR4;
    delay(500);
  }
}
