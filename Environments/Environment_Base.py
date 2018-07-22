from bs4 import BeautifulSoup
from enum import Enum
import os
import ast
import sys
import json
from rdflib import Graph


class Input(Enum):
    MICROBE_JSON = 1
    ENV_JSON = 2
    ENV_HTML = 3


class EnvironmentBase:
    def __init__(self):
        self.environments = {}

    def dbnames_to_dbids(self, ids_dict):
        for env in self.environments.values():
            env.dbnames_to_dbids(ids_dict)

    # change ids with ids+names using ttl file with environment base
    def meoids_to_ttl(self, ttl_file):
        with open(ttl_file, "r") as file:
            meo_id = ""
            meo_name = ""
            for line in file.readlines():
                if line.startswith(":MEO_"):
                    meo_id = line[1:].strip()
                    continue
                if line.startswith("  rdfs:label"):
                    meo_name = line.split("\"")[1]
                    if meo_id in self.environments:
                        self.environments[meo_id + " " + meo_name] = self.environments[meo_id]
                        del self.environments[meo_id]

    # change ids with ids+names using txt file with environment base
    def meoids_to_names(self, meo_file):
        with open(meo_file, "r") as file:
            for line in file.readlines():
                split = line.split("\t")
                if len(split) < 2:
                    continue
                meo_id = split[0].split("/")[-1].strip()
                meo_name = split[1].strip()
                if meo_id in self.environments:
                    self.environments[meo_name] = self.environments[meo_id]
                    del self.environments[meo_id]

    def normalize(self, rnorm):
        for env in self.environments.values():
            env.normalize_self(rnorm)

    def add_data(self, data_folder, input_type, main_key, id_key, weight_key):
        for filename in os.listdir(data_folder):
            env_id = filename.split(".")[0]
            if env_id not in self.environments:
                self.environments[env_id] = Environment()
            self.environments[env_id].add_data(os.path.join(data_folder, filename), input_type, main_key, id_key, weight_key)

    def add_dbid_data(self, data_folder, normalize_input=True):
        jsons = {}
        env_data = {}
        for filename in os.listdir(data_folder):
            json_data = get_struct_from_json(open(os.path.join(data_folder, filename)).read())
            jsons[filename.split(".")[0]] = json_data
            for item in json_data['taxonomy_composition_via_meta16s']:
                env_data[item['envid']] = {}

        for dbid in jsons.keys():
            json_data = jsons[dbid]['taxonomy_composition_via_meta16s']
            max_value = float(json_data[0]['sum'])
            norm_value = 1.0
            # norm to make max value 1.0
            if normalize_input and (max_value > 0):
                norm_value = 1.0 / max_value

            for item in json_data:
                if float(item['sum']) > 0:
                    env_data[item['envid']][dbid] = float(item['sum']) * norm_value

        for env_id in env_data.keys():
            if env_id not in self.environments:
                self.environments[env_id] = Environment()
            self.environments[env_id].add_parsed_data(env_data[env_id])

    # remove environments without data
    def filter_empty(self):
        to_remove = []
        for env_key in self.environments.keys():
            if len(self.environments[env_key].dbid_weights) == 0:
                to_remove.append(env_key)
        for env_key in to_remove:
            del self.environments[env_key]

    def environments_to_csv(self, outfile):
        env_ids = sorted(self.environments.keys())
        dbids = {}
        for env_id in env_ids:
            for dbid in self.environments[env_id].dbid_weights.keys():
                dbids[dbid] = 1

        with open(outfile, "w+") as out:
            out.write("ncbi_id\t" + "\t".join(env_ids) + "\n")
            for dbid in sorted(dbids.keys()):
                scores = []
                for env_id in env_ids:
                    if dbid in self.environments[env_id].dbid_weights:
                        scores.append(str(self.environments[env_id].dbid_weights[dbid]))
                    else:
                        scores.append("0.0")
                out.write(str(dbid) + "\t" + "\t".join(scores) + "\n")


class Environment:
    def __init__(self):
        self.dbid_weights = {}

    # change bacteria names by ids and remove unknown
    def dbnames_to_dbids(self, ids_dict):
        new_data = {}
        old_names = list(self.dbid_weights.keys())
        for name in old_names:
            if name.isdigit():
                continue
            if name in ids_dict:
                new_data[ids_dict[name]] = self.dbid_weights[name]
            del self.dbid_weights[name]
        self.add_parsed_data(new_data, False)

    def add_data(self, data_file, input_type, main_key, id_key, weight_key):
        data = {}
        if input_type == Input.ENV_JSON:
            data = self.__get_json_data(data_file, main_key, id_key, weight_key)
        if input_type == Input.ENV_HTML:
            data = self.__get_html_data(data_file, main_key, id_key, weight_key)
        self.add_parsed_data(data)
        return

    def add_parsed_data(self, data, normalize=True):
        if normalize:
            self.__normalize_data(data, 1)
        # merge old and new structures
        for key in data.keys():
            if key not in self.dbid_weights:
                self.dbid_weights[key] = 0
            self.dbid_weights[key] += data[key]
        return

    def normalize_self(self, rnorm):
        self.__normalize_data(self.dbid_weights, rnorm)

    def __normalize_data(self, data, rnorm):
        norm_sum = 0
        for dbid_score in data.values():
            norm_sum += dbid_score ** (rnorm)
        norm_sum = norm_sum ** (1 / rnorm)
        for dbid in data.keys():
            data[dbid] = data[dbid] / norm_sum

    def __get_json_data(elf, json_file, main_key, id_key, weight_key=""):
        data = {}
        response_json = open(json_file).read()
        struct = get_struct_from_json(response_json)

        json_data = struct[main_key]
        for item in json_data:
            dbid = item[id_key]
            if dbid == "root":
                continue
            data[dbid] = 1.0
            if weight_key != "":
                data[dbid] = item[weight_key]

        return data

    def __get_html_data(self, html_file, main_key, id_key, weight_key=""):
        struct = {}

        soup = BeautifulSoup(open(html_file).read(), 'lxml')
        all_data = soup.find_all("script")
        string_data = ""
        for script in all_data:
            if main_key in str(script):
                # find variable
                string_data = str(script)[str(script).find(main_key):]
                # find value
                string_data = string_data[string_data.find("["):string_data.find(";")]
                # remove unnecessary parts
                string_data = string_data.replace("\n", "").replace(" ", "")
                string_data = string_data.replace("unescapeHTML(", "").replace(")", "")
                break

        if string_data == "":
            return struct

        # from string to list
        data = ast.literal_eval(string_data)
        # from list to dict. skip first line
        for i in range(1, len(data)):
            struct[data[i][0]] = data[i][1]
        # print(struct)
        return struct


def get_struct_from_json(response_json):
    struct = {}
    try:
        string_data = str(response_json)
        json_data = string_data.split("\"")
        for i in range(len(json_data)):
            if i % 2 == 0:
                continue
            json_data[i] = json_data[i].replace('\'', '')
        string_data = "\'".join(json_data)
        dataform = string_data.strip("'<>() ").replace('\'', '\"').replace("None", "null")
        struct = json.loads(dataform)
    except:
        print(response_json)
        print(sys.exc_info())
    return struct


if __name__ == '__main__':
    print("HI")
    var_names = ["Domain", "Phylum", "Class", "Order", "Family", "Genus"]
    type_names = ["16s", "genome"]
    # for type_name in type_names:
    #     for var_name in var_names:
    #         envs = EnvironmentBase()
    #         envs.add_data("C:/Work/Data/meo_id_" + type_name, Input.ENV_HTML, var_name + "Array", "", "")
    #         envs.filter_empty()
    #         envs.environments_to_csv("C:/Work/Data/meta" + type_name + "_" + var_name + ".csv")

    envs = EnvironmentBase()
    envs.add_data("C:/Work/Data/meo_id_togo", Input.ENV_JSON, "taxonomy_sunburst", "tax_label", "")
    envs.filter_empty()
    envs.environments_to_csv("C:/Work/Data/togo.csv")

    # env1 = Environment()
    # env1.add_data("C:/Work/Data/meo_id_genome/MEO_0000002.json", Input.ENV_HTML, "PhylumArray", "", "")
#     exit()
