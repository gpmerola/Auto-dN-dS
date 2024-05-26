import os

# Define mos_values to store Mean Overlap Scores (MOS)
mos_values = []

# Function to read sequences from a .fasta file and return them as a list of tuples
def read_fasta_file(file_path):
    sequences = []
    valid_characters = set("ACDEFGHIKLMNPQRSTVWY-")  # Set of valid amino acid characters and gap
    with open(file_path, "r") as file:
        current_sequence = ""
        sequence_id = ""
        for line in file:
            if line.startswith(">"):  # Start of a new sequence
                if current_sequence:
                    sequences.append((sequence_id, current_sequence))
                current_sequence = ""
                sequence_id = line.strip()[1:]  # Strip '>' and whitespace
            else:
                # Filter each line to include only valid characters
                cleaned_line = "".join(c for c in line.strip() if c in valid_characters)
                current_sequence += cleaned_line
        # Append the last read sequence to the list
        if current_sequence:
            sequences.append((sequence_id, current_sequence))
    return sequences

# Calculate the pairwise overlap score between two sequences
def pairwise_overlap_score(seq1, seq2):
    identical_positions = 0
    total_positions = 0

    for s1, s2 in zip(seq1, seq2):
        if s1 != '-' and s2 != '-':  # Ignore gaps
            total_positions += 1
            if s1 == s2:
                identical_positions += 1

    return identical_positions / total_positions if total_positions else 0  # Avoid division by zero

# Calculate the MOS for a set of sequences
def multiple_overlap_score(alignment):
    total_score = 0
    total_pairs = 0

    num_sequences = len(alignment)

    for i in range(num_sequences):
        for j in range(i+1, num_sequences):
            total_score += pairwise_overlap_score(alignment[i], alignment[j])
            total_pairs += 1

    return total_score / total_pairs if total_pairs else 0  # Average score or 0 if no pairs

# Main program
if __name__ == "__main__":
    initial_dir = os.getcwd()
    # Change to the temporary directory to read alignment folder name
    os.chdir(os.path.join("temp"))

    with open("alignfolder.txt", "r") as file:
        var = file.readline().strip()  # Read the folder name

    # Change to the results directory containing the alignment files
    os.chdir(os.path.join("..", "results", var))
    print(f"Current directory: {os.getcwd()}")

    mos_threshold = 0.8  # Define threshold for deciding whether to delete a file
    deleted_files_count = {}  # Track number of files deleted per directory
    investigated_directories = set()  # Track directories that have been processed

    # Process each directory in the current working directory
    for item in os.listdir('.'):
        if os.path.isdir(item):
            print(f"Processing directory: {item}")
            deleted_files_count[item] = 0  # Initialize deletion count

            for filename in os.listdir(item):
                if filename.endswith('.fasta'):
                    file_path = os.path.join(item, filename)
                    sequences = read_fasta_file(file_path)
                    investigated_directories.add(item)
                    
                    if sequences:
                        mos = multiple_overlap_score([s[1] for s in sequences])
                        mos_values.append(mos)  # Store MOS for reporting or analysis
                        print(f"File: {filename}, MOS: {mos}")
                        
                        # Delete files with an MOS below the threshold
                        if mos < mos_threshold:
                            os.remove(file_path)
                            deleted_files_count[item] += 1
                            print(f"Deleted file: {file_path}")

    # Report the number of files deleted from each directory
    if deleted_files_count:
        for directory, count in deleted_files_count.items():
            print(f"Deleted {count} fasta files from directory '{directory}'")
    else:
        print("Deleted 0 fasta files")
