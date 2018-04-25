# Post processing for BGC finding. Extracting data from html, creating csv file with BGCs
import sys
from bs4 import BeautifulSoup
import pandas as pd
import os

def html_to_csv(html_file):
    # Open file
    file = open(html_file, "r")
    text = file.read()

    # Get file path to save result
    original_path = os.path.abspath(html_file)
    dir_name = os.path.dirname(original_path)
    try:
        # Parse html
        soup = BeautifulSoup(text, "lxml")
        # Find first table in html. It should be table with clusters
        html_table = soup.find('table')
        # Parse html with pandas. There should be only one table, take it
        pd_table = pd.read_html(str(html_table))[0]
        # Drop the first unrelevant row
        # pd_table = pd_table.drop([0])
        with open(dir_name + "_BGCs.csv", "w+") as outfile:
            outfile.write("\t".join(list(pd_table.columns.values)) + "\n")
            seq = "sequence 0 "
            for row in list(pd_table.values):
                if len(row) < 1:
                    continue
                if "sequence" in row[0]:
                    seq = row[0][row[0].find("sequence"):-1] + " "
                    continue
                row[0] = seq + str(row[0])
                outfile.write("\t".join([str(i) for i in row]) + "\n")
        # pd_table.to_csv(dir_name + "_BGCs.csv", sep='\t')
    except:
        print(sys.exc_info())
        # Create empty file with no results
        with open(dir_name + "_BGCs.csv", "w+") as output_file:
            pass

userParameters = sys.argv[1:]
if len(userParameters) == 1:
    html_to_csv(userParameters[0])
else:
    print("There is a problem!")