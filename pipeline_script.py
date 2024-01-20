import sys
from subprocess import Popen, PIPE
from Bio import SeqIO

import os
import pandas as pd
import time

"""
usage: python pipeline_script.py INPUT.fasta  
approx 5min per analysis
"""

def run_parser(hhr_file):
    """
    Run the results_parser.py over the hhr file to produce the output summary
    """

    cmd = ['python', '/home/ec2-user/data/pdb70/results_parser.py', hhr_file]

    print(f'STEP 4: RUNNING PARSER: {" ".join(cmd)}')
    p = Popen(cmd, stdin=PIPE,stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    print(err)
    # print(out.decode("utf-8"))

def run_hhsearch(a3m_file):
    """
    Run HHSearch to produce the hhr file
    """

    cmd = ['/home/ec2-user/data/myvenv/bin/hhsearch',
           '-i', a3m_file, '-cpu', '1', '-d', 
           '/home/ec2-user/data/pdb70/pdb70']

    print(f'STEP 3: RUNNING HHSEARCH: {" ".join(cmd)}')
    p = Popen(cmd, stdin=PIPE,stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    print(err)


def read_horiz(tmp_file, horiz_file, a3m_file):
    """
    Parse horiz file and concatenate the information to a new tmp a3m file
    """
    pred = ''
    conf = ''
    print("STEP 2: REWRITING INPUT FILE TO A3M")
    with open(horiz_file) as fh_in:
        for line in fh_in:
            if line.startswith('Conf: '):
                conf += line[6:].rstrip()
            if line.startswith('Pred: '):
                pred += line[6:].rstrip()
    with open(tmp_file) as fh_in:
        contents = fh_in.read()
    with open(a3m_file, "w") as fh_out:
        fh_out.write(f">ss_pred\n{pred}\n>ss_conf\n{conf}\n")
        fh_out.write(contents)

def run_s4pred(input_file, out_file):
    """
    Runs the s4pred secondary structure predictor to produce the horiz file
    """

    cmd = ['/home/ec2-user/data/myvenv/bin/python3', '/home/ec2-user/data/s4pred/run_model.py',
           '-t', 'horiz', '-T', '1', input_file]

    print(f'STEP 1: RUNNING S4PRED: {" ".join(cmd)}')
    p = Popen(cmd, stdin=PIPE,stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()

    with open(out_file, "w") as fh_out:
        fh_out.write(out.decode("utf-8"))

def read_input(file):
    """
    Function reads a fasta formatted file of protein sequences
    """
    print("READING FASTA FILES")
    sequences = {}
    ids = []
    for record in SeqIO.parse(file, "fasta"):
        sequences[record.id] = record.seq
        ids.append(record.id)

    return(sequences)

def store_analysis_info(hhr_output_file, output_csv):
    header = "query_id,best_hit,best_evalue,best_score,score_mean,score_std,score_gmean"

    if os.path.getsize(output_csv) == 0:
        with open(output_csv, "w") as csv_fh:
            csv_fh.write(header + "\n")

    with open(hhr_output_file, "r") as hhr_fh:
        hhr_content = hhr_fh.readlines()[1:]

    if hhr_content:
        with open(output_csv, "a") as csv_fh:
            csv_fh.writelines(hhr_content)
            
    files_to_remove = ["tmp.fas", "tmp.horiz", "tmp.a3m", "tmp.hhr", "hhr_parse.out"]
    
    for file in files_to_remove:
        os.remove(file)


if __name__ == "__main__":
  
    sequences = read_input(sys.argv[1])
    output_csv = sys.argv[2]

    tmp_file = "tmp.fas"
    horiz_file = "tmp.horiz"
    a3m_file = "tmp.a3m"
    hhr_file = "tmp.hhr"

    for k, v in sequences.items():
        print(k)
        
        with open(tmp_file, "w") as fh_out:
            fh_out.write(f">{k}\n")
            fh_out.write(f"{v}\n")

        run_s4pred(tmp_file, horiz_file) #
        read_horiz(tmp_file, horiz_file, a3m_file) 
        run_hhsearch(a3m_file)
        run_parser(hhr_file)

        while not os.path.exists("hhr_parse.out"):
            time.sleep(1)  

        store_analysis_info("hhr_parse.out", output_csv)