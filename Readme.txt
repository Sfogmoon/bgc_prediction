Unfortunately snakemake and antismash refers to different python.
Snakemake -> python3
Antismash -> python2

Snakemake setup:
http://snakemake.readthedocs.io/en/stable/tutorial/setup.html

Here I will describe the same as in link.

Envinment.yaml file:
channels:
  - conda-forge
  - bioconda
  - r
  - defaults
dependencies:
  - bcftools=1.3.1
  - bwa=0.7.12
  - graphviz=2.38.0
  - python=3.5.1
  - samtools=1.3.1
  - snakemake=3.11.0
  - pyyaml=3.11

Steps:
First you have to install conda
Second you should run this comand:
conda env create --name snakemake-tutorial --file environment.yaml


Antismash setup:
First you have to install conda
Second you should run these comands:
conda create -n antismash antismash
source activate antismash
download-antismash-databases
source deactivate antismash

To run pipeline you should activate snakemake-tutorial:
source activate snakemake-tutorial
To run for Ecoli.fasta:
snakemake clear_Ecoli_BGCs.csv