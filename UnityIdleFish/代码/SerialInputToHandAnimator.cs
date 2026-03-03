using UnityEngine;
using System.IO.Ports; // 串口通信库
using System;

public class SerialReceiver : MonoBehaviour
{
    public string portName = "COM9";  // 你的串口号
    public int baudRate = 115200;     // 波特率
    private SerialPort serialPort;
    private string incomingData = "";  // 缓存接收到的数据
    public Transform[] fingerBones;  // 五个手指的骨骼 Transform 数组
    public float maxAngle = 90f;      // 最大旋转角度
    public float minAngle = 0f;       // 最小旋转角度

    void Start()
    {
        TryOpenSerialPort();
    }
    
    // 尝试打开串口
    void TryOpenSerialPort()
    {
        try
        {
            // 打开串口通信
            serialPort = new SerialPort(portName, baudRate);
            serialPort.ReadTimeout = 1000;   // 设置读取超时时间（毫秒）
            serialPort.Open();
            Debug.Log("串口已打开");
        }
        catch (Exception e)
        {
            Debug.LogError($"打开串口失败: {e.Message}");
        }
    }
    
    void Update()
    {
        if (serialPort != null && serialPort.IsOpen)
        {
            try
            {
                // 读取串口数据
                if (serialPort.BytesToRead > 0)
                {
                    // 读取串口字符
                    char incomingChar = (char)serialPort.ReadByte();
    
                    // 如果读取到换行符，则认为数据接收完成
                    if (incomingChar == '\n')
                    {
                        // 显示接收到的数据
                        Debug.Log($"接收到的数据: {incomingData.Trim()}");
    
                        // 将接收到的数据按逗号分割
                        string[] values = incomingData.Split(',');
    
                        // 如果接收到的数据是五个角度值
                        if (values.Length == 5)
                        {
                            // 为每个手指骨骼计算角度，并进行旋转
                            for (int i = 0; i < 5; i++)
                            {
                                // 将每个接收到的角度值转换为 float
                                float sensorAngle;
                                if (float.TryParse(values[i].Trim(), out sensorAngle))
                                {
                                    // 限制角度范围，确保角度在 minAngle 和 maxAngle 之间
                                    sensorAngle = Mathf.Clamp(sensorAngle, minAngle, maxAngle);
    
                                    // 设置手指骨骼的旋转，假设是绕 X 轴旋转
                                    fingerBones[i].localRotation = Quaternion.Euler(sensorAngle, 0, 0);
                                }
                                else
                                {
                                    Debug.LogError($"无效的数据: {values[i].Trim()}");
                                }
                            }
                        }
                        else
                        {
                            Debug.LogWarning("接收到的数据不是五个角度值");
                        }
    
                        // 清空数据缓冲区，准备接收下一组数据
                        incomingData = "";
                    }
                    else
                    {
                        // 累积接收到的字符
                        incomingData += incomingChar;
                    }
                }
            }
            catch (TimeoutException)
            {
                Debug.LogWarning("串口读取超时");
            }
            catch (Exception e)
            {
                Debug.LogError($"读取串口数据失败: {e.Message}");
            }
        }
    }
    
    void OnApplicationQuit()
    {
        if (serialPort != null && serialPort.IsOpen)
        {
            serialPort.Close();
            Debug.Log("串口已关闭");
        }
    }

}