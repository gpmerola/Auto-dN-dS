# Auto-dN-dS
A package to automate the retrieval, alignment, and dN/dS calculation of the whole CDS sequences across species.

## Overview of scripts
  1) mastercode.py: main script, it allows users to select and run specific scripts or all available scripts in a directory.

  2) 1list.py: this script retrieves common protein-coding genes shared between human and a single specified species from Ensembl database using multithreading and writes them to a file. It then saves the list in "list.txt" in the "temp" directory.

  3) 2CDS_fetcher.py: this script fetches and saves coding sequences (CDS) for all gene symbols contained in the list.txt file in the "temp" directory, utilizing the ensembl_rest library, in the "results" folder.

  4) 3align.py: this script aligns the fetched CDS using the MACSE tool in parallel processes and saves the aligned sequences, also logging any errors encountered during the process in the "temp" directory. It then saves the alignments in a separate subfolder within "results".

  5) 4qualityMOS.py: this script performs QC, calculating the multiple overlap score (MOS) for each set of aligned sequences in a directory, then deleting files with an MOS below a specified threshold (default 0.8).

  6) 5kaks.py: this R script processes sequence alignment files to calculate dN/dS values for human versus other species pairs, stores the results in Excel files, and then calculates summary statistics from those Excel files. All results are saved in "results".

  7) macse_v2.07.jar: is an executable JAR file containing the MACSE program, which aligns protein-coding nucleotide sequences while accounting for frameshifts and stop codons (https://www.agap-ge2pop.org/macse/).


## Setup
First of all, download the Github package and navigate in the package directory:

```console
git clone https://github.com/gpmerola/Auto-dN-dS.git
cd Auto-dN-dS
```

Then, install the R and Python dependecies.
To install the required R packages, run the following command:

```console
Rscript requirements.R
```
To install the required Python packages, run the following command:

```console
pip install -r requirements.txt
```

### R Packages
- seqinr, phangorn: Phylogenetic and sequence analysis.
  
- writexl, readxl: Reading and writing Excel files.
  
- tidyverse, dplyr: Data manipulation and visualization.

### Python Libraries:
- requests, ensembl_rest: Web and database interaction.

- concurrent.futures, tqdm: Asynchronous execution and progress tracking.

- biopython: Computational biology tools.

## Usage
Run the main code:

```console
python mastercode.py
```

Provide input regarding which parts of the code to run; type "all" if you want the whole code to run (see the above section "Overview of scripts" to understand the functioning of each part). Then, input the species name (common or scientific, see https://www.ensembl.org/info/about/species.html for acceptable inputs). Use "d" for debug mode (few genes only, human and mouse).
      
The parts must be run in order, with "3" being the most computationally intensive step. Only step "1" and "2" require an internet connection to function.

## Output
The following output files are generated by the script during the analysis workflow. Each file serves a specific purpose in the overall analysis process, from preprocessing and modeling to visualization and correlation analysis. These files are saved in the new working directory created and set at the beginning of the script, provided through the console command.

  1) "dir.txt": Contains the working directory name. It helps share the information between the .R and the .py script.

  2) "LDSC_main.rds": Contains the LDSC output data.

  3) "SNP_files.rds": Contains the sumstats for the SNPs, harmonized.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
