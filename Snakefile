rule preprocess:
    input:
        "{sample}.fasta"
    output:
        "clear_{sample}.fasta"
    run:
        cmd = '''source activate antismash
        python Preprocess.py {input} 1000
        source deactivate antismash'''
        shell(cmd)

rule antismash:
    input:
        "{sample}/{sample}.txt"
    output:
        "{sample}/{sample}_finished.txt"
    run:
        cmd = '''source activate antismash
        antismash {input}
        source deactivate antismash'''
        shell(cmd)

rule postprocess:
    input:
        "{sample}/{sample}_finished.txt"
    output:
        "{sample}_BGCs.csv"
    run:
        cmd = '''source activate antismash
        python Postprocess.py {input}
        source deactivate antismash'''
        shell(cmd)