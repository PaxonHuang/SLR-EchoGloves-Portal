
import serial
from time import sleep, time
import csv
import pandas as pd
import numpy as np

columnName = ['flex_1', 'flex_2', 'flex_3', 'flex_4', 'flex_5',
              'Qw', 'Qx', 'Qy', 'Qz',
              'GYRx', 'GYRy','GYRz',
              'ACCx', 'ACCy', 'ACCz',
              'ACCx_real', 'ACCy_real', 'ACCz_real',
              'ACCx_world', 'ACCy_world', 'ACCz_world',
              'GRAx', 'GRAy', 'GRAz',
              'ACCx_raw', 'ACCy_raw', 'ACCz_raw',
              'GYRx_raw', 'GYRy_raw', 'GYRz_raw']

data = []
# 修改前（错误路径）
# filename = 'E:\NJTS-Codeprojects-2023\NJTS-HandSignal-Cloud-sEMG\xhfPYQT666\version3\Hand-Gesture-Recognition-main\Datasets\testt.csv'

# 修改后（正确路径）
filename = r'E:\\NJTS-Codeprojects-2023\\NJTS-HandSignal-Cloud-sEMG\\xhfPYQT666\\version3\\Hand-Gesture-Recognition-main\Datasets\\testt.csv'
port = 'COM4'

ser = serial.Serial(port=port,
                    baudrate=115200,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=1,
                    xonxoff=0,
                    rtscts=0)

ser.dtr = False
sleep(1)
ser.reset_input_buffer()
ser.dtr = True

count = 0
recordData = True
recorditeration = 40
segmentLength = 180
interruptToken = False

print("Preparing Device... Please Wait")

while True:
    try:
        values = ser.readline().decode('utf-8').rstrip().split(',')
        values = list(map(float, values))
        if(recordData == True):
            interruptToken = False
            data.append(values)
            print("\nData Received... index: ", len(data)-1, end='')

        if ((len(data) % segmentLength) == 0) and (recordData == True) and (interruptToken == False):
            if recordData == True:
                recordData = False
                interruptToken = True
                count += 1
                print('\tSegment - ', count, ' finished')

            if count > recorditeration:
                df = pd.DataFrame(data,columns=columnName)
                df.to_csv(filename, index=False)
                print("\nData Writing Done... shape: ", df.shape)
                break


    except(KeyboardInterrupt):

        print("\n\nStart")

        if recordData == False:
            recordData = True

    except(ValueError):
        print(end='.')

    except:
        print("Something's Wrong... CHECK!!!")
