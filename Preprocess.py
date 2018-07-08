# Pre processing for BGC finding. Removing short contigs and long names of contigs. Separating long files to several
import sys
import os
import shutil
from Bio import SeqIO

def sequence_cleaner(fasta_file, min_length=0, max_length=5000000):
    # Create our array to add the sequences
    files = []
    sequences = []
    sequence_ids = []
    file_length = 0
    counter = -1

    # Using the Biopython fasta parse we can read our fasta input
    for seq_record in SeqIO.parse(fasta_file, "fasta"):
        counter += 1
        # Take the current sequence
        sequence = str(seq_record.seq).upper()
        # Check if the current sequence is according to the user parameters
        if (len(sequence) >= min_length):
            sequence_ids.append(counter)
            sequences.append(sequence)
            file_length += len(sequence)
            if file_length > max_length:
                files.append(sequences)
                sequences = []
                file_length = 0
    files.append(sequences)

    # Create files in the directory with this filename same as input file
    original_path = os.path.abspath(fasta_file)
    file_name = os.path.basename(original_path)
    name = file_name.split(".")[0]
    extension = "." + ".".join(file_name.split(".")[1:])
    new_dir_name = os.path.join(os.path.dirname(original_path), name)
    control_file_text = []

    # Empty dir
    if os.path.exists(new_dir_name):
        shutil.rmtree(new_dir_name)
    os.makedirs(new_dir_name)

    counter = 0
    for i in range(len(files)):
        new_file_name = name + "_" + str(i) + extension
        control_file_text.append(os.path.join(new_dir_name, new_file_name))
        with open(os.path.join(new_dir_name, new_file_name), "w+") as output_file:
            for sequence in files[i]:
                output_file.write(">sequence_" + str(sequence_ids[counter]) + "\n" + sequence + "\n")
                counter += 1
    with open(os.path.join(new_dir_name, name + ".txt"), "w+") as output_file:
        for line in control_file_text:
            output_file.write(line + "\n")

    print("CLEAN!!!\nPlease check " + os.path.join(new_dir_name, name + ".txt"))

userParameters = sys.argv[1:]

try:
    if len(userParameters) == 1:
        sequence_cleaner(userParameters[0])
    elif len(userParameters) == 2:
        sequence_cleaner(userParameters[0], int(userParameters[1]))
    elif len(userParameters) == 3:
        sequence_cleaner(userParameters[0], int(userParameters[1]), int(userParameters[2]))
    else:
        print("There is a problem!")
except Exception as ErrorMessage:
    print(ErrorMessage)
    print("There is a problem!")
