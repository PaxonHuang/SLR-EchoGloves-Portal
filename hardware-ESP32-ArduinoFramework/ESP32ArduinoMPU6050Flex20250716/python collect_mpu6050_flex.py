import serial
import pandas as pd
import time

# 配置参数
SERIAL_PORT = 'COM3'      # 修改为你的串口号，如'COM3'或'/dev/ttyACM0'
BAUD_RATE = 115200        # 与Arduino代码一致
CSV_FILE = 'mpu6050_flex_data.csv'

# 数据字段（需与Arduino输出顺序一致）
COLUMNS = [
    'timestamp',
    'flexADC', 'flexV', 'flexR', 'flexAngle',
    'ax', 'ay', 'az', 'gx', 'gy', 'gz'
]

def parse_line(line):
    # 解析Arduino输出的一行
    try:
        # 例：flexADC,123,flexV,2.345,flexR,45678.9,flexAngle,23.4,ax,123,ay,456,az,789,gx,12,gy,34,gz,56
        parts = line.strip().split(',')
        data = {}
        for i in range(0, len(parts)-1, 2):
            key = parts[i]
            value = parts[i+1]
            data[key] = float(value)
        return data
    except Exception as e:
        print(f"Parse error: {e} | line: {line}")
        return None

def main():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
    data_rows = []
    start_time = time.time()

    try:
        while True:
            line = ser.readline().decode('utf-8', errors='ignore')
            if not line.strip():
                continue
            parsed = parse_line(line)
            if parsed:
                timestamp = time.time() - start_time
                row = {
                    'timestamp': timestamp,
                    'flexADC': parsed.get('flexADC', None),
                    'flexV': parsed.get('flexV', None),
                    'flexR': parsed.get('flexR', None),
                    'flexAngle': parsed.get('flexAngle', None),
                    'ax': parsed.get('ax', None),
                    'ay': parsed.get('ay', None),
                    'az': parsed.get('az', None),
                    'gx': parsed.get('gx', None),
                    'gy': parsed.get('gy', None),
                    'gz': parsed.get('gz', None),
                }
                data_rows.append(row)
                print(row)
            # 每100行保存一次
            if len(data_rows) % 100 == 0:
                pd.DataFrame(data_rows, columns=COLUMNS).to_csv(CSV_FILE, index=False)
    except KeyboardInterrupt:
        print("采集结束，正在保存数据...")
    finally:
        pd.DataFrame(data_rows, columns=COLUMNS).to_csv(CSV_FILE, index=False)
        ser.close()
        print(f"数据已保存到 {CSV_FILE}")

if __name__ == '__main__':
    main()