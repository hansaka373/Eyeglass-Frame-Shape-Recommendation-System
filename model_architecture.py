#!/usr/bin/python3


from tensorflow.keras import backend as K
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Lambda, Dense, Dropout
from shufflenet_and_gans.shufflenetv2 import ShuffleNetV2


def build_network(input_shape, embedding_size):

    inputs, outputs = ShuffleNetV2(include_top=False, input_shape=input_shape,
                                   bottleneck_ratio=0.35, num_shuffle_units=[2, 2, 2])
    outputs = Dropout(0.0)(outputs)
    outputs = Dense(embedding_size, activation=None,
                    kernel_initializer='he_uniform')(outputs)
    # force the encoding to live on the d-dimentional hypershpere
    outputs = Lambda(lambda x: K.l2_normalize(x, axis=-1))(outputs)
    return Model(inputs, outputs)
