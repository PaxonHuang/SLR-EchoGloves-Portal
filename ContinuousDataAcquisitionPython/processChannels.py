
#!/usr/bin/env python
# coding: utf-8
# In[62]:


import os
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

gestureFiles = ['bad', 'deaf', 'fine', 'good', 'hello', 'hi', 'howareyou', 'no',
                'please', 'sorry', 'thankyou', 'yes']

storePath = 'data_21062020/channels/'
sourcePath = 'data_21062020/'

segmentLength = 180


# In[65]:


for file in gestureFiles:
    os.mkdir(storePath + file)
    source = pd.read_csv(sourcePath + file + '.csv')
    for channel in columnName:
        temp = source[channel].to_numpy()
        arr = np.expand_dims(temp, axis=0).reshape(-1,segmentLength)
        np.savetxt(storePath + file + '/' + channel + '.csv', arr, delimiter=",")


# In[67]:


print(pd.read_csv(storePath + file + '/' + 'flex_1' + '.csv', header=None))
