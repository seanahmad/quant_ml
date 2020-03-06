from unittest import TestCase
from keras import backend as K

from quant_ml.util import one_hot
from quant_ml.keras.loss import tailed_categorical_crossentropy, DifferentiableArgmax, normal_penalized_crossentropy, \
    parabolic_crossentropy
import numpy as np

import pandas as pd
import os
import dill as pickle

df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "SPY.csv"), index_col='Date')
os.environ["CUDA_VISIBLE_DEVICES"] = ""


def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


class TestKerasLoss(TestCase):

    def test__differentiable_argmax(self):
        """given"""
        args = 10
        argmax = DifferentiableArgmax(args)

        """when"""
        res = np.array([K.eval(argmax(K.variable(one_hot(i, args)))) for i in range(args)])

        """then"""
        print(res)
        np.testing.assert_array_almost_equal(res, np.arange(0, args))

    def test__parabolic_crossentropy(self):
        """when"""
        categories = 11
        loss_function = parabolic_crossentropy(categories, 1)

        """then"""
        for truth in range(categories):
            losses = []
            for prediction in range(categories):
                loss = K.eval(loss_function(K.variable(one_hot(truth, categories)),
                                            K.variable(one_hot(prediction, categories))))
                losses.append(loss)

            # all predictions left of truth need to increase
            for i in range(1, truth):
                self.assertGreater(losses[i - 1], losses[i])

            # right of truth need to decrease
            for i in range(truth, categories - 1):
                self.assertLess(losses[i], losses[i + 1])

            if truth > 0 and truth < categories - 1:
                if truth > categories / 2:
                    # right tail:
                    self.assertGreater(losses[truth - 1], losses[truth + 1])
                else:
                    # left tail
                    self.assertGreater(losses[truth + 1], losses[truth - 1])

    def test__tailed_categorical_crossentropy(self):
        """when"""
        categories = 11
        loss = tailed_categorical_crossentropy(categories, 1)

        """then"""
        l = K.eval(loss(K.variable(one_hot(3, 11)), K.variable(one_hot(6, 11))))
        pickle

        """then"""
        self.assertGreater(l, 0)
        save_object(loss, '/tmp/test__tailed_categorical_crossentropy.dill')

    def test_normal_penalized_crossentropy(self):
        """when"""
        loss = normal_penalized_crossentropy(11)

        """then"""
        for i in range(11):
            self.assertLess(K.eval(loss(K.variable(one_hot(i, 11)), K.variable(one_hot(i, 11)))), 0.00001)

        self.assertLess(K.eval(loss(K.variable(one_hot(7, 11)), K.variable(one_hot(8, 11)))),
                        K.eval(loss(K.variable(one_hot(7, 11)), K.variable(one_hot(6, 11)))))

        self.assertLess(K.eval(loss(K.variable(one_hot(6, 11)), K.variable(one_hot(7, 11)))),
                        K.eval(loss(K.variable(one_hot(6, 11)), K.variable(one_hot(5, 11)))))

        self.assertLess(K.eval(loss(K.variable(one_hot(3, 11)), K.variable(one_hot(2, 11)))),
                        K.eval(loss(K.variable(one_hot(3, 11)), K.variable(one_hot(4, 11)))))


