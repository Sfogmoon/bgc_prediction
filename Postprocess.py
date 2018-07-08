# Post processing for BGC finding. Extracting data from html, creating csv file with BGCs
import sys
from bs4 import BeautifulSoup
import pandas as pd
import os

def recount_BGCs(table):
    for i in range(1, len(table)):
        if len(table[i]) > 1:
            n = table[i][0].split()[0]
            table[i][0] = n + " Cluster " + str(i)

def files_to_csv(control_file):
    # Open file
    file = open(control_file, "r")
    files = file.readlines()
    file.close()

    # Get file path to save result
    original_path = os.path.abspath(control_file)
    dir_name = os.path.dirname(original_path)

    out = []
    for file in files:
        file_name = os.path.basename(file)
        file_path = os.path.abspath(file)
        file_dir = os.path.dirname(file_path)
        name = file_name.split(".")[0]

        new = html_to_text(os.path.join(file_dir, name, "index.html"))
        if len(out) > 0:
            new = new[1:]
        out.extend(new)

    recount_BGCs(out)

    with open(dir_name + "_BGCs.csv", "w+") as outfile:
        for line in out:
            outfile.write("\t".join(line) + "\n")

def html_to_text(html_file):
    try:
        # Open file
        file = open(html_file, "r")
        text = file.read()

        # Parse html
        soup = BeautifulSoup(text, "lxml")
        # Find first table in html. It should be table with clusters
        html_table = soup.find('table')
        # Parse html with pandas. There should be only one table, take it
        pd_table = pd.read_html(str(html_table))[0]
        # Drop the first unrelevant row
        out = []
        out.append(list(pd_table.columns.values))
        seq = "sequence 0 "
        for row in list(pd_table.values):
            if len(row) < 1:
                continue
            if "sequence" in row[0]:
                seq = row[0][row[0].find("sequence"):-1] + " "
                continue
            row[0] = seq + str(row[0])
            out.append([str(i) for i in row])
        return out
    except:
        print(sys.exc_info())
        return []

userParameters = sys.argv[1:]
if len(userParameters) == 1:
    files_to_csv(userParameters[0])
else:
    print("There is a problem!")