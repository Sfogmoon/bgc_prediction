# Pre processing for BGC finding. Removing short contigs and long names of contigs
import sys
import os
from Bio import SeqIO


def sequence_cleaner(fasta_file, min_length=0):
    # Create our array to add the sequences
    sequences = []

    # Using the Biopython fasta parse we can read our fasta input
    for seq_record in SeqIO.parse(fasta_file, "fasta"):
        # Take the current sequence
        sequence = str(seq_record.seq).upper()
        # Check if the current sequence is according to the user parameters
        if (len(sequence) >= min_length):
            sequences.append(sequence)

    # Create a file in the same directory where you ran this script
    original_path = os.path.abspath(fasta_file)
    dir_name = os.path.dirname(original_path)
    file_name = os.path.basename(original_path)
    with open(os.path.join(dir_name, "clear_" + file_name), "w+") as output_file:
        # Just read the hash table and write on the file as a fasta format
        counter = 0
        for sequence in sequences:
            output_file.write(">sequence_" + str(counter) + "\n" + sequence + "\n")
            counter += 1

    print("CLEAN!!!\nPlease check " + os.path.join(dir_name, "clear_" + file_name))


userParameters = sys.argv[1:]

try:
    if len(userParameters) == 1:
        sequence_cleaner(userParameters[0])
    elif len(userParameters) == 2:
        sequence_cleaner(userParameters[0], int(userParameters[1]))
    else:
        print("There is a problem!")
except:
    print("There is a problem!")
