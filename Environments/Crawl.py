# Crawling microbedb website for the data
import requests
import os
import time
import sys
from multiprocessing import Pool as ThreadPool

NUM_THREADS = 5
# DESTINATION_FOLDER = "C:/Work/Data/tax_id"
DESTINATION_FOLDER = "C:/Work/Data/meo_id_16s"
LINK = "https://beta.microbedb.jp/stanza/environment_taxonomy_composition_of_meta16s?referer=https://beta.microbedb.jp&meo_id="


# LINK = "https://beta.microbedb.jp/stanza/environment_taxonomy_composition_of_metagenome?referer=https://beta.microbedb.jp&meo_id="
# LINK = "http://togostanza.org/stanza/environment_taxonomic_composition/resources/taxonomy_sunburst?meo_id="

def get_list_tax_id(ncbi_file):
    ids_arr = ["1"]
    with open(ncbi_file, "r") as ids_file:
        lines = ids_file.readlines()
        for line in lines:
            new_id = line.split("\t")[0]
            if new_id == ids_arr[-1]:
                continue
            ids_arr.append(new_id)

    print(len(ids_arr))
    return ids_arr


def get_list_env_id(data_file):
    ids_arr = []
    with open(data_file, "r") as ids_file:
        lines = ids_file.readlines()
        for line in lines:
            new_id = line.strip()[1:]
            ids_arr.append(new_id)

    print(len(ids_arr))
    return ids_arr


def get_last_id(destination_folder):
    max_id = ""
    for file in sorted(os.listdir(destination_folder)):
        max_id = max(max_id, file.split(".")[0])
    return max_id


def process_id(i):
    print(i)
    counter = 0
    while (True):
        # time.sleep(1)
        json_text = ""
        try:
            r = requests.get(
                LINK + str(
                    i))
            # print(r.text)
            # json_text = r.json()
            json_text = r.text
            if str(r) == "<Response [200]>":
                counter += 1
            else:
                time.sleep(NUM_THREADS * 5)
                print(str(r))
                continue
        except:
            time.sleep(NUM_THREADS * 5)
            print(sys.exc_info()[0])
            continue

        if len(str(json_text)) < 100 and counter < 1:
            continue
        if len(str(json_text)) > 100:
            with open(os.path.join(DESTINATION_FOLDER, str(i) + ".json"), "w+") as output_file:
                # print("write file " + str(i))
                output_file.write(str(json_text))
        break
    return


def process_ids(ids):
    numThreads = min(len(ids), 10)
    # print("START")
    # print(ids)
    pool = ThreadPool(numThreads)
    pool.imap_unordered(process_id, ids)
    pool.close()
    pool.join()
    # print("END")
    return


if __name__ == '__main__':
    # ids_filename = "C:/Users/Sfogmoon/Downloads/names.dmp"
    ids_filename = "C:/Users/Sfogmoon/Dropbox/WQ Work/Cornell/meo.txt"
    ids_arr = sorted(get_list_env_id(ids_filename))

    max_id = get_last_id(DESTINATION_FOLDER)
    print(max_id)

    num_threads = 10
    small_arr = []
    # for i in range(1):
    for i in range(len(ids_arr)):
        if str(ids_arr[i]) < str(max_id):
            continue
        if i % 1000 == 0:
            print(ids_arr[i])
        small_arr.append(ids_arr[i])
        if len(small_arr) >= num_threads:
            process_ids(small_arr)
            small_arr = []
            continue
        # process_id(i)
    if len(small_arr) > 0:
        process_ids(small_arr)
