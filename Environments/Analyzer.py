# Processing samples and finding most similar environments
import os
import Environment_Base
import Feature_Base
import Sample_Base
import Measure_Environments
import Components_Extractor
import pickle
import numpy as np
import csv
import pylab as pl

from bs4 import BeautifulSoup

JSON_FOLDER = "C:/Work/Data/tax_id"


def load_available_ids(ncbi_file, data_folder):
    ids_dict = {}
    with open(ncbi_file, "r") as ids_file:
        for line in ids_file.readlines():
            new_id = line.split("\t")[0]
            json_filename = os.path.join(data_folder, str(new_id) + ".json")
            if not os.path.isfile(json_filename):
                continue
            name = line.split("\t")[2]
            ids_dict[name] = new_id

    return ids_dict


def load_all_ids(ncbi_file):
    ids_dict = {}
    duplicates = {}
    with open(ncbi_file, "r") as ids_file:
        for line in ids_file.readlines():
            new_id = line.split("\t")[0]
            name = line.split("\t")[2]
            if name in duplicates:
                continue
            if name in ids_dict:
                del ids_dict[name]
                duplicates[name] = 1
            ids_dict[name] = new_id

    print(len(ids_dict))
    return ids_dict


def create_filtered_ncbi(old_ncbi_file, new_ncbi_file, environment_base):
    used_id = {}
    for env_key in environment_base.environments.keys():
        env = environment_base.environments[env_key]
        for dbid in env.dbid_weights.keys():
            used_id[dbid] = env_key

    with open(old_ncbi_file, "r") as ids_file, open(new_ncbi_file, "w+") as new_ids_file:
        for line in ids_file.readlines():
            new_id = line.split("\t")[0]
            new_name = line.split("\t")[2]
            if new_id not in used_id:  # and new_name not in used_id:
                continue
            # if new_name in used_id:
            #     print(new_name, used_id[new_name])
            # else:
            #     print(new_id, used_id[new_id])
            new_ids_file.write(line)


def load_environmets():
    var_names = ["Domain", "Phylum", "Class", "Order", "Family", "Genus"]
    type_names = ["16s", "genome"]
    envs = Environment_Base.EnvironmentBase()
    for type_name in type_names:
        for var_name in var_names:
            envs.add_data("C:/Work/Data/meo_id_" + type_name, Environment_Base.Input.ENV_HTML, var_name + "Array", "", "")
            envs.filter_empty()

    envs.add_data("C:/Work/Data/meo_id_togo", Environment_Base.Input.ENV_JSON, "taxonomy_sunburst", "tax_label", "")
    envs.filter_empty()

    # envs.add_dbid_data("C:/Work/Data/tax_id")
    # envs.filter_empty()

    return envs


if __name__ == '__main__':
    # print("Load all environments data")
    # envs = load_environmets()
    # print("Load prefiltered ncbi data")
    # ids_dict = load_all_ids("C:/Users/Sfogmoon/Dropbox/WQ Work/Cornell/filtered_names3.dmp") # "C:/Users/Sfogmoon/Downloads/names.dmp"
    # print("Go from names to ncbi ids in the data")
    # envs.dbnames_to_dbids(ids_dict)
    # print("Load available environment names")
    # envs.meoids_to_ttl("C:/Users/Sfogmoon/Dropbox/WQ Work/Cornell/meo.ttl")
    #
    # print("Normalize environment data")
    # envs.normalize(2)
    #
    # print("Load samples file")
    # sample_base = Sample_Base.SampleBase()
    # sample_base.load("C:/Users/Sfogmoon/Dropbox/WQ Work/Cornell/pathomap_metaphlan2.txt", Sample_Base.Input.TSV)
    # sample_base.dbnames_to_dbids(ids_dict)
    #
    # print("Calculate features (bacterias) stats")
    # feature_base = Feature_Base.FeatureBase()
    # feature_base.add_environments_data(envs)
    #
    # print("Predict environments")
    # counter = 0
    # for sample in sample_base.samples.values():
    #     if counter % 10 == 0:
    #         print(".", end="", flush=True)
    #     counter += 1
    #     measure = Measure_Environments.count_all_similarity(sample, envs, feature_base)
    #
    # with open('C:/Users/Sfogmoon/Dropbox/WQ Work/Cornell/pathomap_metaphlan2.pkl', 'wb') as output:
    #     pickle.dump(sample_base, output, pickle.HIGHEST_PROTOCOL)
    with open('C:/Users/Sfogmoon/Dropbox/WQ Work/Cornell/pathomap_metaphlan2.pkl', 'rb') as input:
        sample_base = pickle.load(input)

    # env_vector = []
    # env_sum = []
    # for sample in sample_base.samples.values():
    #     env_sample = []
    #     for env in sample.environments.values():
    #         env_vector.append(env)
    #         env_sample.append(env)
    #     env_sum.append(sum(env_sample) / 698)
    #
    # pl.figure()
    # pl.hist(env_vector, normed=True, bins=10)  # use this to draw histogram of your data
    # pl.title('Histogram of all measure output')
    #
    # pl.figure()
    # pl.hist(env_sum, normed=True, bins=10)  # use this to draw histogram of your data
    # pl.title('Histogram of avg measures for samples')
    # pl.show()

    print("\nMaking PCA & LDA")
    lda = []
    svm = []
    for i in range(1):
        # sample_base.randomize()
        x, y = Components_Extractor.extract_components(sample_base)
        lda.append(x)
        svm.append(y)
    print(np.mean(lda), np.mean(svm))

    # a = zip(*csv.reader(open("C:/Users/Sfogmoon/Dropbox/WQ Work/Cornell/pathomap_metaphlan2_transposed.txt"), delimiter='\t'))
    # csv.writer(open("C:/Users/Sfogmoon/Dropbox/WQ Work/Cornell/pathomap_metaphlan2.txt", "wt")).writerows(a)

    # create_filtered_ncbi("C:/Users/Sfogmoon/Downloads/names.dmp", "C:/Users/Sfogmoon/Dropbox/WQ Work/Cornell/filtered_names3.dmp", envs)
