# coding=utf-8
import tensorflow as tf


class TensorflowLstm():
    batch_size = int
    time_step = int
    rnn_unit = int
    input_size = int
    output_size = int
    # learning rate
    lr = float
    # 输入层、输出层权重、偏置
    weights = {}
    biases = {}

    def __init__(self, batch_size=20, time_step=15,rnn_unit=10, input_size = 6, output_size=1, lr = 0.0002):
        self.batch_size = batch_size
        self.time_step = time_step
        self.rnn_unit = rnn_unit
        self.input_size = input_size
        self.output_size = output_size
        self.lr = lr
        self.weights= {
            # tf.Variable定义tensorflow图中的变量.
            # tf.random_normal(shape,mean=0.0,stddev=1.0,dtype=tf.float32,seed=None,name=None)
            # tf.truncated_normal(shape, mean=0.0, stddev=1.0, dtype=tf.float32, seed=None, name=None)
            # tf.random_uniform(shape,minval=0,maxval=None,dtype=tf.float32,seed=None,name=None)
            # 这几个都是用于生成随机数tensor的。尺寸是shape
            # random_normal: 正太分布随机数，均值mean,标准差stddev
            # truncated_normal:截断正态分布随机数，均值mean,标准差stddev,不过只保留[mean-2*stddev,mean+2*stddev]范围内的随机数
            # random_uniform:均匀分布随机数，范围为[minval,maxval]
            'in': tf.Variable(tf.random_normal([input_size, rnn_unit])),
            'out': tf.Variable(tf.random_normal([rnn_unit, 1]))
        }
        self.biases = {
            # tf.constant(value,dtype=None,shape=None,name=’Const’)
            # 创建一个常量tensor，按照给出value来赋值，可以用shape来指定其形状。value可以是一个数，也可以是一个list。
            # 如果是一个数，那么这个常亮中所有值的按该数来赋值。 如果是list,那么len(value)一定要小于等于shape展开后的长度。
            # 赋值时，先将value中的值逐个存入。不够的部分，则全部存入value的最后一个值。
            'in': tf.Variable(tf.constant(0.1, shape=[rnn_unit, ])),
            'out': tf.Variable(tf.constant(0.1, shape=[1, ]))
        }

    def lstm(self, X):
        # tf.shape(a)和a.get_shape()比较
        # 相同点：都可以得到tensor a的尺寸 不同点：tf.shape()中a 数据的类型可以是tensor, list, array
        # a.get_shape()中a的数据类型只能是tensor,且返回的是一个元组（tuple）
        batch_size = tf.shape(X)[0]
        time_step = tf.shape(X)[1]
        w_in = self.weights['in']
        b_in = self.biases['in']
        # 需要将tensor转成2维进行计算，计算后的结果作为隐藏层的输入
        input = tf.reshape(X, [-1, self.input_size])
        input_rnn = tf.matmul(input, w_in) + b_in
        # 将tensor转成3维，作为lstm cell的输入
        input_rnn = tf.reshape(input_rnn, [-1, time_step, self.rnn_unit])
        with tf.variable_scope('cell_def'):
            cell = tf.nn.rnn_cell.BasicLSTMCell(self.rnn_unit)
        init_state = cell.zero_state(batch_size, dtype=tf.float32)
        with tf.variable_scope('rnn_def', reuse=tf.AUTO_REUSE):
            # output_rnn是记录lstm每个输出节点的结果，final_states是最后一个cell的结果
            output_rnn, final_states = tf.nn.dynamic_rnn(cell, input_rnn,
                                                         initial_state=init_state,
                                                         dtype=tf.float32)
        # 作为输出层的输入
        output = tf.reshape(output_rnn, [-1, self.rnn_unit])
        w_out = self.weights['out']
        b_out = self.biases['out']
        pred = tf.matmul(output, w_out) + b_out

        return pred, final_states

    def fit(self, iteration=3, traindata=object):
        # tf.placeholder(dtype, shape=None, name=None) 此函数可以理解为形参，用于定义过程，在执行的时候再赋具体的值
        # 参数：dtype：数据类型。常用的是tf.float32,tf.float64等数值类型
        # shape：数据形状。默认是None，就是一维值，也可以是多维，比如[2,3], [None, 3]表示列是3，行不定
        # name：名称。
        X = tf.placeholder(tf.float32, shape=[None, self.time_step, self.input_size])
        Y = tf.placeholder(tf.float32, shape=[None, self.time_step, self.output_size])

        pred = self.lstm(X)
        # 损失函数
        loss = tf.reduce_mean(tf.square(tf.reshape(pred,[-1]) - tf.reshape(Y, [-1])))
        train_op = tf.train.AdadeltaOptimizer(self.lr).minimize(loss=loss)
        saver = tf.train.latest_checkpoint('model/stock')
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            # saver.restore(sess, module_file)
            # 重复训练
            for i in range(1, iteration + 2):
                for step in range(len(traindata.batch_index) - 1):
                    _, loss_ = sess.run([train_op, loss],feed_dict={
                        X:traindata.X[traindata.batch_index[step]:traindata.batch_index[step + 1]],
                        Y:traindata.Y[traindata.batch_index[step]:traindata.batch_index[step + 1]]})

                    if i % (iter // 2) == 0:
                        print("保存模型：", saver.save(sess, 'model/stock/stock.model', global_step=i))
























