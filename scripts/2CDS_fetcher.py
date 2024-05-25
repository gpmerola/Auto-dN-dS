import ensembl_rest
import os
from tqdm import tqdm

def fetch_cds_sequence(symbol, species):
    """Fetch and save CDS sequence for given symbol and species."""
    try:
        data = ensembl_rest.symbol_post(species=species, params={'symbols': [symbol]})
        if symbol in data:
            canid = data[symbol]['canonical_transcript']
            canid_fasta = ensembl_rest.sequence_id(canid.split('.')[0], headers={'content-type': 'text/x-fasta'}, params={'type': 'cds'})

            header, sequence = canid_fasta.split('\n', 1)
            symbol_dir = os.path.join(output_dir, symbol)
            os.makedirs(symbol_dir, exist_ok=True)

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

# Read species and gene symbols
with open(list_file_path, 'r') as f:
    lines = f.read().splitlines()
    spc, listSymb = lines[0].split(', '), lines[1:]

# Set up output directory
output_dir = os.path.join(base_output_dir, f"Fetched CDS sequences for {'_'.join(spc)}")
os.makedirs(output_dir, exist_ok=True)

# Update folder name file
with open(os.path.join(base_path, '..', 'temp', 'alignfolder.txt'), 'w') as f:
    f.write(f"Fetched CDS sequences for {'_'.join(spc)}")

# Fetch and save CDS sequences
progress_bar = tqdm(total=len(spc) * len(listSymb), desc='Fetching CDS sequences')
for symbol in listSymb:
    for species in spc:
        desc = fetch_cds_sequence(symbol, species)
        progress_bar.set_description(desc)
        progress_bar.update(1)

progress_bar.close()
print("Finished!")
