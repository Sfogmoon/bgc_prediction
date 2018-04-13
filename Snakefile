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
        "clear_{sample}.fasta"
    output:
        "clear_{sample}/index.html"
    run:
        cmd = '''source activate antismash
        antismash {input}
        source deactivate antismash'''
        shell(cmd)

rule postprocess:
    input:
        "clear_{sample}/index.html"
    output:
        "clear_{sample}_BGCs.csv"
    run:
        cmd = '''source activate antismash
        python Postprocess.py {input}
        source deactivate antismash'''
        shell(cmd)