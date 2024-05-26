import requests
import concurrent.futures
import threading
from requests.adapters import HTTPAdapter
import os

debug_mode = False  # Initialize the debug mode flag as False

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))
temp_directory = os.path.join(current_directory, '..', 'temp')

# Ensure the "temp" directory exists; if not, create it
if not os.path.exists(temp_directory):
    os.makedirs(temp_directory)

# Input prompt to the user for species or debug mode activation
input_value = input("Please enter the species, separated by commas (e.g., 'mouse,rat') or 'd' for debug mode: ")
species_input = ["mouse"] if input_value.lower() == 'd' else [species.strip() for species in input_value.split(',')]
debug_mode = input_value.lower() == 'd'  # Update debug mode based on user input

# Dictionary mapping human chromosomes to their respective lengths in base pairs
chromosome_lengths = {
    '1': 248956422, '2': 242193529, '3': 198295559, '4': 190214555, '5': 181538259,
    '6': 170805979, '7': 159345973, '8': 145138636, '9': 138394717, '10': 133797422,
    '11': 135086622, '12': 133275309, '13': 114364328, '14': 107043718, '15': 101991189,
    '16': 90338345, '17': 83257441, '18': 80373285, '19': 58617616, '20': 64444167,
    '21': 46709983, '22': 50818468, 'X': 156040895, 'Y': 57227415
}

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

successful_retrieval = 0  # Counter for successful gene retrievals
lock = threading.Lock()  # Lock for thread-safe operations

def safe_request(url):
    """ Perform a safe HTTP GET request with error handling. """
    response = session.get(url, timeout=10, headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        return response.json()
    return None

def gene_exists_in_species(gene_symbol, species):
    """ Check if a given gene symbol exists in a specified species using the Ensembl API. """
    url = f"https://rest.ensembl.org/xrefs/symbol/{species}/{gene_symbol}?content-type=application/json"
    response = safe_request(url)
    return bool(response)

def print_progress_bar():
    """ Update and print the progress bar in the console. """
    bar_length = 50
    progress_fraction = completed_chunks / total_chunks
    arrow = '=' * int(round(progress_fraction * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    print(f"\rProgress: [{arrow + spaces}] {int(progress_fraction * 100)}% - Successful retrievals: {successful_retrieval}", end="")

def fetch_genes_from_region(chromosome, chrom_length):
    """ Fetch genes from a specified region of a chromosome and check if they are common across specified species. """
    global successful_retrieval, completed_chunks
    CHUNK_SIZE = 5000000  # Define size of chromosome chunks to process
    common_genes = []
    start = 1
    end = CHUNK_SIZE

    while start < chrom_length:
        with lock:
            if debug_mode and successful_retrieval >= 5:
                return common_genes

        url = f"https://rest.ensembl.org/overlap/region/human/{chromosome}:{start}-{end}?feature=gene;content-type=application/json"
        genes = safe_request(url)
        
        if genes:
            for gene in genes:
                with lock:
                    if debug_mode and successful_retrieval >= 5:
                        return common_genes
                    if gene.get('biotype') == 'protein_coding' and 'external_name' in gene:
                        if all(gene_exists_in_species(gene['external_name'], species) for species in species_input):
                            print(f"Processing gene: {gene['external_name']}")  # Output the gene being processed
                            common_genes.append(gene['external_name'])
                            successful_retrieval += 1
                            print_progress_bar()

        start, end = end + 1, min(end + CHUNK_SIZE, chrom_length)
        with lock:
            completed_chunks += 1
            print_progress_bar()

    return common_genes

def main():
    """ Main function to orchestrate the gene fetching and file writing process. """
    global total_chunks, completed_chunks
    total_chunks = sum((length // 5000000 + (length % 5000000 > 0)) for length in chromosome_lengths.values())
    completed_chunks = 0
    all_common_genes = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_genes_from_region, chromosome, length) for chromosome, length in chromosome_lengths.items()]
        for future in concurrent.futures.as_completed(futures):
            all_common_genes.extend(future.result())

    formatted_species_names = "Human, " + ', '.join(species.title() for species in species_input)
    with open(os.path.join(temp_directory, "list.txt"), 'w') as f:
        f.write(formatted_species_names + "\n")
        f.write('\n'.join(sorted(all_common_genes)))


if __name__ == "__main__":
    main()
