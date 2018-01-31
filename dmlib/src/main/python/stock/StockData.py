# coding=utf-8
import numpy as np


class StockData():

    def __init__(self, data, featurebegin=1,featureend=7, ylabel=4, time_step=15,
                 batch_size=20, T=1, normalize=True, isPercent=False, isTest=False):
        self.code = str
        self.name = str
        self.time_step = time_step
        self.X = []
        self.Y = []
        self.batch_index = []
        self.normalize = normalize
        self.ylabel = ylabel
        self.T = T

        # numpy.mean(a, axis=None, dtype=None, out=None, keepdims=<class numpy._globals._NoValue at 0x40b6a26c>)[source]
        # Compute the arithmetic mean along the specified axis.
        # 经常操作的参数为axis，以m * n矩阵举例：axis 不设置值，对 m*n 个数求均值，返回一个实数
        # axis = 0：压缩行，对各列求均值，返回 1* n 矩阵axis =1 ：压缩列，对各行求均值，返回 m *1 矩阵
        # np.std求标准差
        newdata = data.iloc[:, featurebegin:featureend].values

        if isPercent:
            newdata1 = newdata[1:]
            newdata2 = newdata[0:len(newdata) - 1]
            newdata = (newdata1 - newdata2) / newdata2 * 10

        self.mean = np.mean(newdata, axis=0)
        self.std = np.std(newdata, axis=0)  # 标准化
        if normalize:
            # 取第1-6列
            newdata = (newdata - self.mean) / self.std

        # X collect data from 0 util newdata's length - T using time_step
        # Y collect data from T util newdata's length using time_step
        # so len(X) == len(Y)
        for i in range(len(newdata) - time_step - T):
            if i % batch_size == 0:
                self.batch_index.append(i)
            x = newdata[i:i + time_step, :]
            y = newdata[i + T:i + time_step + T, ylabel, np.newaxis]
            self.X.append(x.tolist())
            self.Y.append(y.tolist())

        if isTest:
            # X collect data from 0 util newdata's length using time_step
            # Y collect data from T util newdata's length using time_step
            # so len(X) - len(Y) = T
            for i in range(len(newdata) - time_step - T, len(newdata) - time_step):
                if i % batch_size == 0:
                    self.batch_index.append(i)
                x = newdata[i:i + time_step, :]
                self.X.append(x.tolist())

        self.batch_index.append((len(newdata) - time_step - T + 1))






