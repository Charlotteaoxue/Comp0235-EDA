import sys
from Bio import SeqIO

def read_ids(file_path):
    with open(file_path, 'r') as file:
        return set(line.strip().split('|')[1] for line in file)

def select_ids(id_file, fasta_file, output_file):
    
    ids = read_ids(id_file)
    selected_records = []
    
    for record in SeqIO.parse(fasta_file, "fasta"):
        uniprot_id = record.id.split('|')[1]
       
        if uniprot_id in ids:
            selected_records.append(record)

    SeqIO.write(selected_records, output_file, "fasta")

if __name__ == "__main__":
    
    if len(sys.argv) < 4:
        print("Usage: python script.py <ID_FILE> <FASTA_FILE> <OUTPUT_FILE>")
        sys.exit(1)
    
    id_file = sys.argv[1]
    fasta_file = sys.argv[2]
    output_file = sys.argv[3]

    select_ids(id_file, fasta_file, output_file)