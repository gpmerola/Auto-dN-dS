# Auto-dN-dS
Auto-dN-dS is a package designed to automate the retrieval, alignment, and dN/dS calculation of coding sequences (CDS) across species. This package downloads the entire CDS of humans and a user-selected species, aligning these sequences, performing quality control, and calculating the dN/dS ratio [(Hurst, 2002)](https://pubmed.ncbi.nlm.nih.gov/12175810/) in order to estimate the level of purifying or positive selection.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)
- [Output Files](#output-files)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview
  - mastercode.py: main script, it allows users to select and run specific scripts or all available scripts in a directory.

  - 1list.py: this script retrieves common protein-coding genes shared between human and a single specified species from the Ensembl database using multithreading and writes them to a file. It then saves the list in "list.txt" in the "temp" directory.

  - 2CDS_fetcher.py: this script fetches and saves CDS for all gene symbols contained in the list.txt file in the "temp" directory, utilizing the ensembl_rest library, in the "results" folder.

  - 3align.py: this script aligns the fetched CDS using the MACSE tool in parallel processes and saves the aligned sequences, also logging any errors encountered during the process in the "temp" directory. It then saves the alignments in a separate subfolder within "results".

  - 4qualityMOS.py: this script performs QC, calculating the multiple overlap score [(Mos; Lassmann et Sonnhammer, 2005)](https://academic.oup.com/nar/article/33/22/7120/1333952) for each set of aligned sequences in a directory, then deleting files with an MOS below a specified threshold (default 0.8).

  - 5kaks.py: this R script processes sequence alignment files to calculate dN/dS values for human versus other species pairs, stores the results in Excel files, and then calculates summary statistics from those Excel files. All results are saved in "results".

  - macse_v2.07.jar: is an executable JAR file containing the MACSE program, which aligns protein-coding nucleotide sequences while accounting for frameshifts and stop codons [(Ranwez et al., 2011)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0022594).

## Prerequisites
  - Python 3.6 or higher
  - R 3.6 or higher
  - Java 1.8.0 or higher
  - Git

## Setup
First of all, download the Github package and navigate in the package directory:

```console
git clone https://github.com/gpmerola/Auto-dN-dS.git
cd Auto-dN-dS
```

Install the R and Python dependencies:

```console
Rscript requirements.R
pip install -r requirements.txt
```

## Usage
Run the main code:

```console
python mastercode.py
```

Provide input regarding which parts of the code to run; type "all" if you want the whole code to run (see the above section "Overview of scripts" to understand the functioning of each part). Then, input the species name (common or scientific, see https://www.ensembl.org/info/about/species.html for acceptable inputs). Use "d" for debug mode (few genes only, human and mouse).
      
The parts must be run in order, with "3" being the most computationally intensive step. Only step "1" and "2" require an internet connection to function.

## Output Files

### "results" directory
This directory contains the main results.

  - list.txt: Contains the species names and the list of gene symbols that are common across the specified species and humans.

  - Fetched CDS sequences for <species>.fasta/: Directory containing FASTA files for the CDS sequences for each gene symbol.

  - 1Alignments_Human_{species}/: Directory containing alignment FASTA files for each gene.

  - output_results.xlsx: An Excel file containing the Ka/Ks ratios for each gene. This file provides a wide-format table where each row represents a gene, and columns represent different species pairs.

  - summary.xlsx: An Excel file summarizing the statistics of the Ka/Ks ratios for each gene. This file includes mean, standard deviation, and count of valid Ka/Ks ratios for each gene.

### "temp" directory
This directory contains log files and necessary intermediate files.

  - alignfolder.txt: A text file containing the name of the directory where the alignment files are stored. This is used for reference in subsequent steps.

  - log.txt: A log file containing messages and any errors encountered during the processing of gene alignments.

  - combined_{gene_name}.fasta: Combined FASTA files for each gene (before alignment).

## Troubleshooting
Ensure that all dependencies are installed correctly.
Check log.txt for any error messages during the processing steps.
Verify that the species name provided is acceptable as per Ensembl's list.

## Contributing
Contributions are welcome. Please submit a pull request or open an issue to discuss any changes or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
