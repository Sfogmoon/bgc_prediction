from enum import Enum

import numpy as np
from scipy import spatial
import Feature_Base
from sklearn.metrics.pairwise import cosine_similarity
import heapq
from tabulate import tabulate
from scipy.stats import rankdata


class Measure(Enum):
    COSINE = 1
    BRAYCURTIS = 2
    CORRELATION = 3
    RANKCORRELATION = 4
    EUCLIDIAN = 5


CURRENT_MEASURE = Measure.COSINE


def count_all_similarity(sample, environments, feature_base):
    print(sample.name)
    env_scores = {}
    for env_key in environments.environments.keys():
        env_scores[env_key] = count_similarity(sample, environments.environments[env_key], feature_base)
    sample.environments = env_scores
    # k_keys_sorted = heapq.nlargest(5, env_scores, key=env_scores.get)
    # header = ["Environment", "Score"]
    # lines = []
    # for env_id in k_keys_sorted:
    #     lines.append([env_id, env_scores[env_id]])
    # print(tabulate(lines, headers=header))

    std = np.std(list(env_scores.values()))
    return std


def count_similarity(sample, environment, feature_base):
    ids, id_weight, id_level_weight = sample.get_vector_data()
    env_weight = []
    for id in ids:
        if id in environment.dbid_weights:
            env_weight.append(float(environment.dbid_weights[id]))
        else:
            env_weight.append(0)

    id_weight = normalize_vector(id_weight)
    env_weight = normalize_vector(env_weight)

    id_weight = id_weight * np.array(id_level_weight)
    env_weight = env_weight * np.array(id_level_weight)

    id_weight = normalize_vector(id_weight)
    env_weight = normalize_vector(env_weight)

    id_weight = apply_feature_transform(ids, id_weight, feature_base)
    env_weight = apply_feature_transform(ids, env_weight, feature_base)

    id_weight = normalize_vector(id_weight)
    env_weight = normalize_vector(env_weight)

    return similarity(id_weight, env_weight)


def normalize_vector(vec):
    vec = np.array(vec)
    measure = (np.sum(vec * vec) ** 0.5)
    if measure == 0:
        return vec
    return vec / measure


def similarity(a, b):
    measure = min(np.sum(a * a), np.sum(b * b))
    if measure == 0:
        return 0

    if CURRENT_MEASURE == Measure.COSINE:
        return 1.0 - spatial.distance.cosine(a, b)
    # if CURRENT_MEASURE == Measure.CITYBLOCK:
    #     return 1.0 - spatial.distance.cityblock(a, b) / ((2 * len(a)) ** 0.5)
    if CURRENT_MEASURE == Measure.BRAYCURTIS:
        return 1.0 - spatial.distance.braycurtis(a, b)
    if CURRENT_MEASURE == Measure.CORRELATION:
        return (2.0 - spatial.distance.correlation(a, b)) / 2
    if CURRENT_MEASURE == Measure.RANKCORRELATION:
        return (2.0 - spatial.distance.correlation(rankdata(a), rankdata(b))) / 2
    if CURRENT_MEASURE == Measure.EUCLIDIAN:
        return 1.0 - spatial.distance.euclidean(a, b) / (2 ** 0.5)


def apply_feature_transform(ids, a, feature_base):
    for i in range(len(ids)):
        a[i] = a[i] * feature_base.get_measure(ids[i], Feature_Base.CURRENT_TF, Feature_Base.CURRENT_IDF)
    return a
