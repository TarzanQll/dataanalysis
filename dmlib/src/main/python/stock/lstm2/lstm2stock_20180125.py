# coding=gbk
'''
Created on 2018��1��23��
@author: ningyongheng
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import os

np.seterr(divide='ignore', invalid='ignore')


class StockLstm():
    # stock name
    name = object
    # stock code
    code = object
    # stock code
    data = object

    # �������������������������������������������������������������������������������������
    # ���峣��
    # hidden layer units
    rnn_unit = 10
    input_size = 6
    output_size = 1
    lr = 0.0006  # ѧϰ��
    # ����㡢�����Ȩ�ء�ƫ��
    weights = {
        # tf.Variable����tensorflowͼ�еı���.
        # tf.random_normal(shape,mean=0.0,stddev=1.0,dtype=tf.float32,seed=None,name=None)
        # tf.truncated_normal(shape, mean=0.0, stddev=1.0, dtype=tf.float32, seed=None, name=None)
        # tf.random_uniform(shape,minval=0,maxval=None,dtype=tf.float32,seed=None,name=None)
        # �⼸�������������������tensor�ġ��ߴ���shape
        # random_normal: ��̫�ֲ����������ֵmean,��׼��stddev
        # truncated_normal:�ض���̬�ֲ����������ֵmean,��׼��stddev,����ֻ����[mean-2*stddev,mean+2*stddev]��Χ�ڵ������
        # random_uniform:���ȷֲ����������ΧΪ[minval,maxval]
        'in': tf.Variable(tf.random_normal([input_size, rnn_unit])),
        'out': tf.Variable(tf.random_normal([rnn_unit, 1]))
    }
    biases = {
        # tf.constant(value,dtype=None,shape=None,name=��Const��)
        # ����һ������tensor�����ո���value����ֵ��������shape��ָ������״��value������һ������Ҳ������һ��list��
        # �����һ��������ô�������������ֵ�İ���������ֵ�� �����list,��ôlen(value)һ��ҪС�ڵ���shapeչ����ĳ��ȡ�
        # ��ֵʱ���Ƚ�value�е�ֵ������롣�����Ĳ��֣���ȫ������value�����һ��ֵ��
        'in': tf.Variable(tf.constant(0.1, shape=[rnn_unit, ])),
        'out': tf.Variable(tf.constant(0.1, shape=[1, ]))
    }

    batch_size = int
    time_step = int
    train_begin = int
    train_end = int
    ylabel = int
    test_begin = int

    def __init__(self, batch_size = 20, time_step = 15,
                 train_begin = 1, train_end = 40000,
                 ylabel = 4, test_begin = 401):
        self.batch_size = batch_size
        self.time_step = time_step
        self.train_begin = train_begin
        self.train_end = train_end
        self.iter = iter
        self.ylabel = ylabel
        self.test_begin = test_begin

    def get_all_data(self, filepath, feturebeginindex, fetureendindex):
        # �������������������������������������������ݡ�������������������������������������������
        f = open(filepath)
        df = pd.read_csv(f)  # �����Ʊ����
        self.data = df.iloc[:, feturebeginindex:fetureendindex].values  # ȡ��1-6��

    # ��ȡѵ����
    def get_train_data(self, input_size, batch_size, time_step, train_begin, train_end, ylabel):
        batch_index = []
        data_train = self.data[train_begin:train_end]
        # numpy.mean(a, axis=None, dtype=None, out=None, keepdims=<class numpy._globals._NoValue at 0x40b6a26c>)[source]
        # Compute the arithmetic mean along the specified axis.
        # ���������Ĳ���Ϊaxis����m * n���������axis ������ֵ���� m*n �������ֵ������һ��ʵ��
        # axis = 0��ѹ���У��Ը������ֵ������ 1* n ����axis =1 ��ѹ���У��Ը������ֵ������ m *1 ����
        # np.std���׼��
        normalized_train_data = (data_train - np.mean(data_train, axis=0)) / np.std(data_train, axis=0)  # ��׼��
        # normalized_train_data = data_train
        train_x, train_y = [], []  # ѵ����
        for i in range(len(normalized_train_data) - time_step):
            if i % batch_size == 0:
                batch_index.append(i)
            x = normalized_train_data[i:i + time_step, :input_size]
            y = normalized_train_data[i + 1:i + time_step + 1, ylabel, np.newaxis]
            train_x.append(x.tolist())
            train_y.append(y.tolist())
        batch_index.append((len(normalized_train_data) - time_step))
        return batch_index, train_x, train_y

    # ��ȡ���Լ�
    def get_test_data(self, input_size, time_step, test_begin, ylabel):
        data_test = self.data[test_begin:]
        mean = np.mean(data_test, axis=0)
        std = np.std(data_test, axis=0)
        normalized_test_data = (data_test - mean) / std  # ��׼��
        # normalized_test_data = data_test
        size = (len(normalized_test_data) + time_step - 1) // time_step  # ��size��sample
        test_x, test_y = [], []
        for i in range(len(normalized_test_data) - time_step - 1):
            # x = normalized_test_data[i * time_step:(i + 1) * time_step, :input_size]
            # y = normalized_test_data[i * time_step + 1:(i + 1) * time_step + 1, ylabel]
            # test_x.append(x.tolist())
            # test_y.append(y.tolist)
            x = normalized_test_data[i:i + time_step, :input_size]
            y = normalized_test_data[i + 1:i + time_step + 1, ylabel, np.newaxis]
            test_x.append(x.tolist())
            test_y.append(y.tolist())
        # test_x.append((normalized_test_data[len(data_test) // time_step * time_step:len(data_test) - 2, :input_size]).tolist())
        # test_y.extend((normalized_test_data[len(data_test) // time_step + 1:, ylabel]).tolist())
        return mean, std, test_x, test_y

    # �������������������������������������������������������������������������������������
    def lstm(self, X):
        batch_size = tf.shape(X)[0]
        time_step = tf.shape(X)[1]
        w_in = self.weights['in']
        b_in = self.biases['in']
        # ��Ҫ��tensorת��2ά���м��㣬�����Ľ����Ϊ���ز������
        input = tf.reshape(X, [-1, self.input_size])
        input_rnn = tf.matmul(input, w_in) + b_in
        # ��tensorת��3ά����Ϊlstm cell������
        input_rnn = tf.reshape(input_rnn, [-1, time_step, self.rnn_unit])
        with tf.variable_scope('cell_def', reuse=tf.AUTO_REUSE):
            cell = tf.nn.rnn_cell.BasicLSTMCell(self.rnn_unit)
        init_state = cell.zero_state(batch_size, dtype=tf.float32)
        with tf.variable_scope('rnn_def', reuse=tf.AUTO_REUSE):
            # output_rnn�Ǽ�¼lstmÿ������ڵ�Ľ����final_states�����һ��cell�Ľ��
            output_rnn, final_states = tf.nn.dynamic_rnn(cell, input_rnn,
                                                         initial_state=init_state,
                                                         dtype=tf.float32)
        output = tf.reshape(output_rnn, [-1, self.rnn_unit])  # ��Ϊ����������
        w_out = self.weights['out']
        b_out = self.biases['out']
        pred = tf.matmul(output, w_out) + b_out
        return pred, final_states

    # ������������������������������������ѵ��ģ�͡�����������������������������������
    def train_lstm(self, iter = 3):
        # tf.placeholder(dtype, shape=None, name=None) �˺����������Ϊ�βΣ����ڶ�����̣���ִ�е�ʱ���ٸ������ֵ
        # ������dtype���������͡����õ���tf.float32,tf.float64����ֵ����
        # shape��������״��Ĭ����None������һάֵ��Ҳ�����Ƕ�ά������[2,3], [None, 3]��ʾ����3���в���
        # name�����ơ�
        X = tf.placeholder(tf.float32, shape=[None, self.time_step, self.input_size])
        Y = tf.placeholder(tf.float32, shape=[None, self.time_step, self.output_size])
        batch_index, train_x, train_y = self.get_train_data(self.input_size, self.batch_size,
                                                            self.time_step, self.train_begin,
                                                            self.train_end, self.ylabel)
        pred, _ = self.lstm(X)
        # ��ʧ����
        loss = tf.reduce_mean(tf.square(tf.reshape(pred, [-1]) - tf.reshape(Y, [-1])))
        train_op = tf.train.AdamOptimizer(self.lr).minimize(loss)
        saver = tf.train.Saver(tf.global_variables(), max_to_keep=15)
        module_file = tf.train.latest_checkpoint('model')
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            # saver.restore(sess, module_file)
            # �ظ�ѵ��
            for i in range(1, iter + 2):
                for step in range(len(batch_index) - 1):
                    _, loss_ = sess.run([train_op, loss],
                                        feed_dict={X: train_x[batch_index[step]:batch_index[step + 1]],
                                                   Y: train_y[batch_index[step]:batch_index[step + 1]]})
                    # print(i, loss_)
                if i % (iter //2) == 0:
                    print("����ģ�ͣ�", saver.save(sess, 'model/stock2.model', global_step=i))

    # ��������������������������������Ԥ��ģ�͡���������������������������������������
    def predictionDays(self):
        X = tf.placeholder(tf.float32, shape=[None, self.time_step, self.input_size])
        # Y=tf.placeholder(tf.float32, shape=[None,time_step,output_size])
        mean, std, test_x, test_y = self.get_test_data(self.input_size, self.time_step, self.test_begin, self.ylabel)
        pred, _ = self.lstm(X)
        saver = tf.train.Saver(tf.global_variables())
        with tf.Session() as sess:
            # �����ָ�
            module_file = tf.train.latest_checkpoint('model')
            saver.restore(sess, module_file)
            test_predict = []
            test_true = []
            for step in range(len(test_x) - 1):
                prob = sess.run(pred, feed_dict={X: [test_x[step]]})[0]
                predict = prob.reshape((-1))
                test_predict.extend(predict)
                test_true.extend(test_y[step][0])
            # Ԥ�����time_step��
            prob = sess.run(pred, feed_dict={X: [test_x[len(test_x) - 1]]})
            predict = prob.reshape((-1))
            test_predict.extend(predict)
            for i in range(self.time_step):
                test_true.extend(test_y[len(test_y) - 1][i])

            test_true = np.array(test_true) * float(std[self.ylabel]) + mean[self.ylabel]
            test_predict = np.array(test_predict) * std[self.ylabel] + mean[self.ylabel]
            acc = np.average(np.abs(test_predict - test_true[:len(test_predict)])
                             / test_true[:len(test_predict)])  # ƫ��
            # ������ͼ��ʾ���
            plt.figure()
            plt.plot(list(range(len(test_predict))), test_predict, color='b')
            plt.plot(list(range(len(test_true))), test_true, color='r')
            plt.show()

    # ��������������������������������Ԥ��ģ�͡���������������������������������������
    def predictionDay(self, test_x):
        X = tf.placeholder(tf.float32, shape=[None, self.time_step, self.input_size])
        mean = np.mean(test_x, axis=0)
        std = np.std(test_x, axis=0)
        normalized_test_data = (test_x - mean) / std  # ��׼��
        pred, _ = self.lstm(X)
        saver = tf.train.Saver(tf.global_variables())
        with tf.Session() as sess:
            # �����ָ�
            module_file = tf.train.latest_checkpoint('model')
            saver.restore(sess, module_file)
            prob = sess.run(pred, feed_dict={X: [normalized_test_data]})
            predict = prob.reshape((-1))
            print("predict :  " + str(predict[self.time_step - 1]
                                   * std[self.ylabel] + mean[self.ylabel]))


if __name__ == '__main__':
    os.chdir("/home/nyh/work/workspace/dataanalysis/dmlib/")
    np.seterr(divide='ignore')

    lstmstock = StockLstm()
    filepath = 'data/stock/000977.SZ.csv'
    feturebeginindex = 1
    fetureendindex = 7
    lstmstock.get_all_data(filepath, feturebeginindex, fetureendindex)
    train_end = 496

    # ============train============
    # lstmstock.train_lstm(iter=10000)

    # ============predict===========
    lstmstock.predictionDays()

    # test_x = lstmstock.data[len(lstmstock.data) - lstmstock.time_step:len(lstmstock.data)]
    # lstmstock.predictionDay(test_x = test_x)
    # print("true = " + str(lstmstock.data[lstmstock.train_end + 2][lstmstock.ylabel]))