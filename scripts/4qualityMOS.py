import os

# Define mos_values to store MOS values
mos_values = []

# Function to read .fasta files
def read_fasta_file(file_path):
    sequences = []
    valid_characters = set("ACDEFGHIKLMNPQRSTVWY-")
    with open(file_path, "r") as file:
        current_sequence = ""
        sequence_id = ""
        for line in file:
            if line.startswith(">"):
                if current_sequence:
                    sequences.append((sequence_id, current_sequence))
                current_sequence = ""
                sequence_id = line.strip()[1:]
            else:
                cleaned_line = "".join(c for c in line.strip() if c in valid_characters)
                current_sequence += cleaned_line
        if current_sequence:
            sequences.append((sequence_id, current_sequence))
    return sequences

# Function for pairwise overlap score
def pairwise_overlap_score(seq1, seq2):
    identical_positions = 0
    total_positions = 0

    for s1, s2 in zip(seq1, seq2):
        if s1 != '-' and s2 != '-':
            total_positions += 1
            if s1 == s2:
                identical_positions += 1

    return identical_positions / total_positions if total_positions else 0

# Function for multiple overlap score (MOS)
def multiple_overlap_score(alignment):
    total_score = 0
    total_pairs = 0

    num_sequences = len(alignment)

    for i in range(num_sequences):
        for j in range(i+1, num_sequences):
            total_score += pairwise_overlap_score(alignment[i], alignment[j])
            total_pairs += 1

    return total_score / total_pairs if total_pairs else 0

# Main program
if __name__ == "__main__":
    initial_dir = os.getcwd()
    # Navigate to the temp directory to read the variable file
    os.chdir(os.path.join("temp"))

    with open("alignments_dir_name.txt", "r") as file:
        var = file.readline().strip()

    # Navigate to the results directory
    os.chdir(os.path.join("..", "results", var))
    print(f"Current directory: {os.getcwd()}")

    mos_threshold = 0.8  # Threshold for MOS
    deleted_files_count = {}  # Dictionary to keep track of deleted files per directory
    investigated_directories = set()  # Set to keep track of directories containing investigated files

    # Iterate through all items in the current directory
    for item in os.listdir('.'):
        # Check if the item is a directory
        if os.path.isdir(item):
            print(f"Processing directory: {item}")

            # Initialize the deleted files count for this directory
            deleted_files_count[item] = 0
            
            # Iterate through files in the directory
            for filename in os.listdir(item):
                if filename.endswith('.fasta'):
                    file_path = os.path.join(item, filename)
                    sequences = read_fasta_file(file_path)
                    investigated_directories.add(item)
                    
                    if sequences:
                        mos = multiple_overlap_score([s[1] for s in sequences])
                        mos_values.append(mos)
                        print(f"File: {filename}, MOS: {mos}")
                        
                        # If the MOS is below the threshold, delete the file
                        if mos < mos_threshold:
                            os.remove(file_path)
                            deleted_files_count[item] += 1
                            print(f"Deleted file: {file_path}")

    # Print the number of deleted fasta files from each directory
    if deleted_files_count:
        for directory, count in deleted_files_count.items():
            print(f"Deleted {count} fasta files from directory '{directory}'")
    else:
        print("Deleted 0 fasta files")