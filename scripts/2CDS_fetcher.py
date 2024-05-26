import ensembl_rest
import os
from tqdm import tqdm

def fetch_cds_sequence(symbol, species):
    """Fetch and save CDS sequence for a given gene symbol and species using the Ensembl REST API."""
    try:
        # Retrieve gene data using the symbol from the Ensembl database for the specified species.
        data = ensembl_rest.symbol_post(species=species, params={'symbols': [symbol]})
        if symbol in data:
            # Extract canonical transcript ID and fetch its CDS sequence.
            canid = data[symbol]['canonical_transcript']
            canid_fasta = ensembl_rest.sequence_id(canid.split('.')[0], headers={'content-type': 'text/x-fasta'}, params={'type': 'cds'})

            # Split FASTA format into header and sequence components.
            header, sequence = canid_fasta.split('\n', 1)
            symbol_dir = os.path.join(output_dir, symbol)
            os.makedirs(symbol_dir, exist_ok=True)  # Ensure the directory for the symbol exists.

            # Write the CDS sequence to a file.
            output_file = os.path.join(symbol_dir, f'{symbol}_{species}.fasta')
            with open(output_file, 'w') as f:
                f.write(f'>{symbol}_{species}_{canid.split(".")[0]}\n' + sequence)

            return f"CDS sequence fetched for {symbol} in {species}"
        else:
            return f"No CDS data found for {symbol} in {species}"
    except Exception as e:
        return f"Error processing {symbol}: {e}"

# Setup paths and directories
base_path = os.path.dirname(os.path.abspath(__file__))
list_file_path = os.path.join(base_path, '..', 'temp', 'list.txt')
base_output_dir = os.path.join(base_path, '..', 'results')

# Read species and gene symbols from a file.
with open(list_file_path, 'r') as f:
    lines = f.read().splitlines()
    spc, listSymb = lines[0].split(', '), lines[1:]

# Set up the output directory based on species names.
output_dir = os.path.join(base_output_dir, f"Fetched CDS sequences for {'_'.join(spc)}")
os.makedirs(output_dir, exist_ok=True)

# Write the output directory path to a file for potential future use.
with open(os.path.join(base_path, '..', 'temp', 'alignfolder.txt'), 'w') as f:
    f.write(f"Fetched CDS sequences for {'_'.join(spc)}")

# Initialize the progress bar for tracking CDS sequence fetching.
progress_bar = tqdm(total=len(spc) * len(listSymb), desc='Fetching CDS sequences')
for symbol in listSymb:
    for species in spc:
        desc = fetch_cds_sequence(symbol, species)  # Fetch and process each CDS sequence.
        progress_bar.set_description(desc)  # Update progress bar description with the current task.
        progress_bar.update(1)  # Increment the progress bar.

progress_bar.close()
print("Finished!")  # Signal the end of the process.
