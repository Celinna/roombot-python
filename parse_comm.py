import numpy as np
import pandas as pd
import glob, os
import matplotlib.pyplot as plt
from dataclasses import dataclass


datapath = "./data/test_bat"
plot = False
qos = "qos0"
N = 55000
dfs = []
cdfs = []
data = {
        # "13": None, 
        # "15": None,
        # "16": None,
        "19": None
        }
modules = list(data.keys())
X = []
Y = []

@dataclass
class Info:
    name:       str
    avg_time_all:   float
    avg_time:   float
    std_time:   float
    cnt_timeout: int
    # cnt_error:   int
    cnt_valid:    int


for file in os.listdir(datapath):
    if file.endswith(".csv"):
        if qos in file:
            temp = pd.read_csv(os.path.join(datapath, file))
            # temp = temp.truncate(before=20000, after=75000)
            temp.drop(columns=['trial', "Unnamed: 0"], inplace=True)
            dfs.append(temp)

            # cdf
            intervals = temp["interval (ms)"]
            x = np.sort(intervals)
            x = x[0:54900]
            
            y = np.arange(N) / float(N)
            y = y[0:54900]
            Y.append(y)
            X.append(x)
            

            # extract data
            avg_time_all = temp["interval (ms)"].mean()
            # std_time = temp["interval (ms)"].std()
            avg_time = temp.loc[temp['state'] == 1, 'interval (ms)'].mean()
            std_time = temp.loc[temp['state'] == 1, 'interval (ms)'].std()
            cnt_timeout = temp["state"].value_counts()[0]
            cnt_valid = temp["state"].value_counts()[1]
            # cnt_error = temp["state"].value_counts()[2]

            stats = Info(qos, avg_time_all, avg_time, std_time, cnt_timeout, cnt_valid)

        
            for m in modules:
                if m in file:
                    data[m] = stats

            print(file, data)

if (plot):
    for i in range(len(X)):
        # plotting  CDF
        # plt.plot(bins_count[1:], l, label="CDF")
        plt.plot(X[i], Y[i], marker='o', label=modules[i])
        

    plt.xlabel('Time (ms)')
    plt.ylabel('CDF (%)')

    plt.title('CDF using sorting the data')
    plt.legend()
    plt.show()



