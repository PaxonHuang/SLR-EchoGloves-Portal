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

filename = 'data_21062020/bla.csv'
port = '/dev/ttyUSB0'

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
recorditeration = 0

print("Preparing Device... Please Wait")

while True:
    try:
        values = ser.readline().decode('utf-8').rstrip().split(',')
        values = list(map(float, values))
        if(recordData == True):
            data.append(values)
            print("\nData Received... index: ", len(data)-1, end='')

    except(KeyboardInterrupt):

        print("\n\nKeyboard Interrupt")

        if recordData == True:
            recordData = False
            count += 1
        elif recordData == False:
            recordData = True

        if count > recorditeration:
            df = pd.DataFrame(data,columns=columnName)
            df.to_csv(filename, index=False)
            print("\nData Writing Done... shape: ", df.shape)
            break

    except(ValueError):
        print(end='.')

    except:
        print("Something's Wrong... CHECK!!!")
