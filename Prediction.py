# BGC finding. Running antismash on several files
import sys
import os
import subprocess
from multiprocessing import Pool
from shutil import copyfile

def process_fasta(fasta):
    file_name = os.path.basename(fasta)
    file_path = os.path.abspath(fasta)
    file_dir = os.path.dirname(file_path)
    name = file_name.split(".")[0]
    if os.path.exists(os.path.join(file_dir, name, "index.html")):
        return (fasta + " Exists")

    bashCommand = "antismash " + fasta
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return fasta

# need a copy for the next step of pipeline
def copy_control_file(control_file):
    original_path = os.path.abspath(control_file)
    file_name = os.path.basename(original_path)
    name = file_name.split(".")[0] + "_finished"
    extension = "." + ".".join(file_name.split(".")[1:])
    copyfile(original_path, os.path.join(os.path.dirname(original_path), name + extension))

def run_antismash(control_file):

    file = open(control_file, "r")
    fasta_files = [x.strip() for x in file.readlines() if len(x.strip()) > 0]
    file.close()

    # change dir to file
    temp = os.getcwd()
    # to save antismash files in own dir
    os.chdir(os.path.dirname(os.path.abspath(control_file)))

    pool = Pool(min(len(fasta_files), 10))
    for i in pool.imap_unordered(process_fasta, fasta_files):
        print(i)
    pool.close()

    os.chdir(temp)

userParameters = sys.argv[1:]

if len(userParameters) == 1:
    control_filename = userParameters[0]
    run_antismash(control_filename)
    copy_control_file(control_filename)
else:
    print("There is a problem!")