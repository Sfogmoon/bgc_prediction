from bs4 import BeautifulSoup
from enum import Enum
import csv
import numpy as np

# should be more than 1. If 1 we take into account only leaves. If inf we take all levels equally, that will lead to disbalance in upper levels.
# TODO: select to increase dispersia
HIERARCHY_SPEED = 1.25
NUMBER_OF_SAMPLES_BOUND = 100000


class Input(Enum):
    REPORT = 1
    TSV = 2


LEVELS = {"superkingdom": 0,
          "phylum": 1,
          "class": 2,
          "order": 3,
          "family": 4,
          "genus": 5,
          "species": 6,
          "subspecies": 7,
          "leaf": 7}


class SampleBase:
    def __init__(self):
        self.samples = {}
        self.names = []
        self.info = {}

    def randomize(self):
        order = np.random.permutation(len(self.names))
        self.names = [self.names[i] for i in order]
        for info in self.info.keys():
            self.info[info] = [self.info[info][i] for i in order]

    def dbnames_to_dbids(self, ids_dict):
        for sample in self.samples.values():
            sample.dbnames_to_dbids(ids_dict)

    def load(self, filename, input_type):
        sample_to_leave = NUMBER_OF_SAMPLES_BOUND
        sample_data = {}
        if input_type == Input.REPORT:
            sample_names, sample_data = self.load_report(filename)
            self.names = sample_names[:sample_to_leave]

        if input_type == Input.TSV:
            sample_names, sample_data, sample_info = self.load_tsv(filename)
            self.names = sample_names[:sample_to_leave]
            self.info = sample_info
            for name in sample_info.keys():
                sample_info[name] = sample_info[name][:sample_to_leave]

        for name in self.names:
            self.samples[name] = Sample(name, sample_data[name])

    def load_report(self, report_filename):
        sample_name = report_filename.split(".")[0]
        sample_data = {sample_name: []}
        with open(report_filename) as tsv_file:
            reader = csv.reader(tsv_file, delimiter='\t')
            next(reader)
            for row in reader:
                if len(row) < 7:
                    continue
                if float(row[6]) == 0.0:
                    continue

                db_name = row[0]
                level_name = row[2]
                if level_name not in LEVELS:
                    print(level_name + " level not in predefined Levels")
                    continue
                level = LEVELS[level_name]
                while len(sample_data[sample_name]) <= level:
                    sample_data[sample_name].append({})
                sample_data[sample_name][level][db_name] = float(row[6])
        return [sample_name], sample_data

    def load_tsv(self, tsv_filename):
        with open(tsv_filename) as tsv_file:
            reader = csv.reader(tsv_file, delimiter='\t')

            # load sample names, create structs
            sample_names = next(reader)
            sample_data = {}
            sample_info = {}
            # for each sample create empty array for future levels of hierarchy
            for i in range(1, len(sample_names)):
                sample_data[sample_names[i]] = []

            # load data
            for row in reader:
                # check for row without bacteria info
                if "_" not in row[0]:
                    sample_info[row[0]] = row[1:]
                    continue

                # get bacteria name without prefix
                long_name = row[0].split("|")[-1]
                db_name = long_name
                if db_name.find("__") > 0:
                    db_name = db_name[3:]
                db_name = db_name.replace("_", " ")

                # level of hierarchy
                level = row[0].count("|")
                for i in range(1, len(row)):
                    if float(row[i]) != 0.0:
                        if len(sample_data[sample_names[i]]) <= level:
                            sample_data[sample_names[i]].append({})
                        sample_data[sample_names[i]][level][db_name] = float(row[i])
            return sample_names[1:], sample_data, sample_info


class Sample:
    def __init__(self):
        self.name = ""
        self.hierarchy = []
        self.environments = {}
        self.level_weights = []

    def __init__(self, sample_name, data):
        self.name = sample_name
        self.hierarchy = data
        self.environments = {}
        self.level_weights = []

    def get_vector_data(self):
        if self.level_weights == []:
            self.count_weight_of_levels()
        id = []
        id_weight = []
        id_level_weight = []
        for level in range(len(self.hierarchy)):
            for db_name in self.hierarchy[level]:
                id.append(db_name)
                id_weight.append(self.hierarchy[level][db_name])
                id_level_weight.append(self.level_weights[level])
        return id, id_weight, id_level_weight

    # change bacteria names by ids and remove unknown
    def dbnames_to_dbids(self, ids_dict):
        for level in range(len(self.hierarchy)):
            old_names = list(self.hierarchy[level].keys())
            for name in old_names:
                if name in ids_dict:
                    self.hierarchy[level][ids_dict[name]] = self.hierarchy[level][name]
                del self.hierarchy[level][name]

    def normalize_weights(self, rnorm=2):
        if rnorm <= 0:
            return

        # get norm
        norm_val = 0
        for level in range(len(self.hierarchy)):
            for db_name in self.hierarchy[level]:
                norm_val = norm_val + self.hierarchy[level][db_name] ** rnorm
        norm_val = 1 / (norm_val ** (1 / float(rnorm)))

        for level in range(len(self.hierarchy)):
            for db_name in self.hierarchy[level]:
                self.hierarchy[level][db_name] = self.hierarchy[level][db_name] * norm_val

    def count_weight_of_levels(self):
        # for no data
        if len(self.hierarchy) == 0:
            return

        # size of levels. It should be one in case of all data, but our data is not full
        level_sizes = []

        # get jsons and levels
        for level in range(len(self.hierarchy)):
            level_sizes.append(0)
            for db_name in self.hierarchy[level]:
                level_sizes[-1] = level_sizes[-1] + self.hierarchy[level][db_name]

        # print(level_sizes)
        # get weights of levels
        weight_of_levels = [0] * len(level_sizes)
        max_weight = level_sizes[-1] / HIERARCHY_SPEED
        for i in reversed(range(len(level_sizes) - 1)):
            if level_sizes[i] > max_weight:
                level_sizes[i] = level_sizes[i] - max_weight
                max_weight = max_weight + level_sizes[i] / HIERARCHY_SPEED
            else:
                level_sizes[i] = 0

        # print(level_sizes)
        sum_weights = sum(level_sizes)
        if sum_weights > 0:
            for i in range(len(level_sizes)):
                weight_of_levels[i] = level_sizes[i] / sum_weights
        # print(weight_of_levels)

        self.level_weights = weight_of_levels
