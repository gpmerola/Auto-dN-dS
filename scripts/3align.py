import os
import subprocess
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from Bio import SeqIO

max_workers = 8

def ensure_log_dir_exists(log_file_path):
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

def process_gene_dir(args):
    gene_dir, jar_path, alignments_dir, log_file_path = args
    gene_name = os.path.basename(gene_dir)
    aligned_file_name = f"alignment_{gene_name}.fasta"
    new_name = os.path.join(alignments_dir, aligned_file_name)

    upper_dir = os.path.abspath(os.path.join(gene_dir, os.pardir))

    fasta_files = [f for f in os.listdir(gene_dir) if f.endswith('.fasta')]
    output_file = os.path.join(upper_dir, 'combined.fasta')
    with open(output_file, 'w') as outfile:
        for fname in fasta_files:
            with open(os.path.join(gene_dir, fname)) as infile:
                outfile.write(infile.read())
                outfile.write('\n')

    try:
        align_fasta_file(output_file, jar_path, new_name)
    except Exception as e:
        log_error(log_file_path, gene_name, e)
        delete_aa_files(gene_dir)
        return gene_name, False

    delete_aa_files(gene_dir)
    return gene_name, True

def align_fasta_file(fasta_path, jar_path, aligned_file):
    remove_asterisk_from_fasta(fasta_path)
    cmd = ['java', '-jar', jar_path, '-prog', 'alignSequences', '-seq', fasta_path, '-out_NT', aligned_file]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)

def remove_asterisk_from_fasta(fasta_path):
    sequences = list(SeqIO.parse(fasta_path, "fasta"))
    for record in sequences:
        if record.seq.endswith("*"):
            record.seq = record.seq[:-1]
    SeqIO.write(sequences, fasta_path, "fasta")

def delete_aa_files(directory):
    for file_name in os.listdir(directory):
        if "_AA" in file_name:
            os.remove(os.path.join(directory, file_name))

def log_error(log_file_path, gene_name, error):
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"Error processing {gene_name}: {str(error)}\n")

def main():
    current_directory = os.getcwd()
    relative_path = os.path.join(current_directory, '..', 'temp', 'output_folder_name.txt')
    folder_name_file_path = os.path.abspath(relative_path)

    relative_path = os.path.join(current_directory, '..', 'temp', 'log.txt')
    log_file_path = os.path.abspath(relative_path)

    ensure_log_dir_exists(log_file_path)

    start_time = datetime.now()
    print(f"Number of CPU cores available: {os.cpu_count()}")
    print(f"Number of max_workers: {max_workers}")
    print(f"Process started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    with open(folder_name_file_path, 'r') as f:
        fetched_directory = f.readline().strip()

    relative_path = os.path.join(current_directory, '..')
    root_dir = os.path.abspath(relative_path)
    
    relative_path = os.path.join(root_dir, 'results', fetched_directory)
    gene_dirs_path = os.path.abspath(relative_path)

    gene_dirs = [os.path.join(gene_dirs_path, d) for d in os.listdir(gene_dirs_path) if os.path.isdir(os.path.join(gene_dirs_path, d))]
    alignments_dir_name = "1Alignments_" + "_".join(fetched_directory.split()[4:])
    alignments_dir = os.path.join(root_dir, 'results', alignments_dir_name)
    if not os.path.exists(alignments_dir):
        os.makedirs(alignments_dir)

    jar_path = os.path.join(current_directory, 'macse_v2.07.jar')

    tasks = [(gene_dir, jar_path, alignments_dir, log_file_path) for gene_dir in gene_dirs]

    successfully_aligned = 0
    gene_counter = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(process_gene_dir, tasks)

        for gene_name, success in results:
            gene_counter += 1
            if success:
                successfully_aligned += 1
                print(f"{gene_counter}) Successfully aligned {gene_name}")
            else:
                print(f"{gene_counter}) Failed to align {gene_name}")

    print(f"\nAlignment process completed. {successfully_aligned}/{gene_counter} genes aligned successfully.")
    end_time = datetime.now()
    print(f"Process ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {end_time - start_time}")

    relative_path = os.path.join(current_directory, '..', 'temp', 'alignfolder.txt')
    outputfolder = os.path.abspath(relative_path)

    with open(outputfolder, "w") as file:
        os.makedirs(os.path.dirname(file.name), exist_ok=True)
        file.write(alignments_dir_name)

if __name__ == "__main__":
    main()
