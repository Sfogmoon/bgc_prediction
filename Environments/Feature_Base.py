import math
from enum import Enum


class Tf(Enum):
    ONE = 1
    MAX = 2
    MAX_SQRT = 3
    SUM = 4


class Idf(Enum):
    ONE = 1
    COUNT_SQRT = 2
    COUNT_LOG = 3


CURRENT_TF = Tf.ONE
CURRENT_IDF = Idf.ONE
NO_VALUE = 1.0


class FeatureBase:
    def __init__(self):
        self.features = {}

    def __str__(self):
        return str(self.features)

    def get_measure(self, id, tf=CURRENT_TF, idf=CURRENT_IDF):
        if id not in self.features:
            return NO_VALUE
        return self.features[id].get_measure(tf, idf)

    def add_environments_data(self, envs):
        for env in envs.environments.values():
            self.add_environment_data(env)

    def add_environment_data(self, env):
        for id in env.dbid_weights.keys():
            if id not in self.features:
                self.features[id] = Feature(id)
            self.features[id].add_data(env.dbid_weights[id])


class Feature:
    def __init__(self, id_name):
        self.name = id_name
        self.env_values = []
        self.measure = None

    def __str__(self):
        return str(self.env_values)

    def add_data(self, value):
        if value > 0:
            self.env_values.append(value)

    def get_measure(self, tf=CURRENT_TF, idf=CURRENT_IDF):
        if self.measure != None:
            return self.measure

        self.measure = self.count_tf(tf) * self.count_idf(idf)
        return self.measure

    def count_tf(self, tf):
        if len(self.env_values) == 0:
            return 1.0
        if tf == Tf.ONE:
            return 1.0
        if tf == Tf.MAX:
            return 1 / max(self.env_values)
        if tf == Tf.MAX_SQRT:
            return 1 / (max(self.env_values) ** 0.5)
        if tf == Tf.SUM:
            return 1 / sum(self.env_values)
        return 1.0

    def count_idf(self, idf):
        if idf == Idf.ONE:
            return 1.0
        if idf == Idf.COUNT_SQRT:
            return 1.0 / ((len(self.env_values) + 1) ** 0.5)
        if idf == Idf.COUNT_LOG:
            return 1.0 / math.log(len(self.env_values) + 2)
        return 1.0
