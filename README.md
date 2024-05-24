# GSEM Dual Subtraction
A package to automate the retrieval, alignment, and dN/dS calculation of the whole CDS sequences across species.

## Overview of scripts
  1) mastercode.py: main script, with a customizable part at the beginning to set up variables and inputs.

  2) 1list.py: main script, with a customizable part at the beginning to set up variables and inputs.

  3) 1list.py: main script, with a customizable part at the beginning to set up variables and inputs.

  4) 1list.py: main script, with a customizable part at the beginning to set up variables and inputs.

  5) 1list.py: main script, with a customizable part at the beginning to set up variables and inputs.

  6) 1list.py: main script, with a customizable part at the beginning to set up variables and inputs.

## Setup
This README file provides instructions on how to set up the project environment by installing the required dependencies for both R and Python.

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

## Usage
  1) Prepare Input Files: Ensure your input files are in the correct format and located in the appropriate directory.

  2) Choose Input Settings: The first argument contains the name of the directory you want your output files to be stored in. Add numbers from "1" to "6", or "r", to the input as shown below to run specific parts of the code:

      1: Preprocessing and Preparation - Performs munging, LD score regression, and prepares SNP files.
      
      2: Model Fitting - Fits the specified structural equation model using the input data.
      
      3: GSEM - Performs the most computationally intensive step, running a synthethic GWAS on the latent variables specified in the model. Including "r" runs the GWAS in a test mode, using only chromosome 2.
      
      4: Plots and Post-Munging - Generates Manhattan and QQ plots, performs post-munging, and computes LD score regression for the new phenotype.
      
      5: Genetic Correlation - Computes genetic correlation between the new phenotype and the input traits.
      
      6: Matrix Generation - Generates a matrix of genetic correlations and performs significance testing between the new phenotype and input traits.```

The parts must be run in order, with "3" being the most computationally intensive step.

  3) Run the Script: Execute the main script to perform the subtraction by navigating to the scripts directory and running the following command ("r" is optional):

```console
cd scripts
Rscript main.R  "working_directory" 1 2 3 4 5 6 "r"
```

  4) Plotting: If needed, the plotting script for genetic correlation can be run:

```console
python plot.py
```

### Settings
These variables are located at the top of the main.R file and can be edited to modify them:

      1: files_input: List of file paths to cleaned GWAS summary statistics files, 3 elements in the vector. The third one represents the phenotype from which the subtraction is conducted.

      2: ref_file: File path to the reference panel.

      3: hm3: File path to the HapMap 3 SNP list.

      4: paths_corr: Directory path for the files for the correlation (see the "Correlation_input.csv" file, and the section below).

      5: ld: Directory path to the linkage disequilibrium (LD) reference data.

      6: wld: Directory path the weighted linkage disequilibrium (LD) reference data, if relevant. Otherwise set equal to "ld".

      7: traitnames: Names of traits for analysis, 3 elements in the vector. Has to follow the same order as "files_input". Make sure that the third file in "traitnames" correspond to the first element in the "trait" column in "Correlation_input.csv"). 

      8: latentnames: Names of latent variables corresponding to the traits, 3 elements in the vector. Has to follow the same order as "files_input".

      9: output_name: Name of the output for the synthetic phenotype file.

      10: infofilter: Information score filter threshold.

      11: maffilter: Minor allele frequency filter threshold.

      12: sample.prev: Vector of sample prevalence for each trait, 3 elements in the vector. Has to follow the same order as "files_input".

      13: population.prev: Vector of population prevalence for each trait, 3 elements in the vector. Has to follow the same order as "files_input".

      14: se.logit_vector: Logical vector indicating if standard error of logit transformation should be used (https://github.com/GenomicSEM/GenomicSEM/wiki/2.-Important-resources-and-key-information for reference), 3 elements in the vector. Has to follow the same order as "files_input".

      15: OLS_vector: Logical vector indicating if Ordinary Least Squares (OLS) regression should be used (https://github.com/GenomicSEM/GenomicSEM/wiki/2.-Important-resources-and-key-information for reference), 3 elements in the vector. Has to follow the same order as "files_input".

      16: linprob_vector: Logical vector indicating if linear probability model should be used (https://github.com/GenomicSEM/GenomicSEM/wiki/2.-Important-resources-and-key-information for reference), 3 elements in the vector. Has to follow the same order as "files_input".

      17: ncores: Number of CPU cores to use for computation.

Additionally, the Correlation_input.csv file contains important information necessary for the genetic correlation analysis. Each column in the file is used to define specific parameters for the traits being analyzed. An example of the Correlation_input.csv file might look like this:

```csv
trait,code,sampleprev,popprev,Cluster
SCZ,SCHI06,0.425,0.01,A
MDD,DEPR14,0.346,0.10,B
BD,BIPO03,0.1013,0.02,C
```

  1) trait: The name of the trait.

  2) code: A unique identifier or code for each trait used, for file path construction (see "paths_corr" in the section above).

  3) sampleprev: The sample prevalence.

  4) popprev: The population prevalence.

  5) Cluster: This column lists the cluster information for each trait, used to group traits into clusters based on their genetic correlation patterns. The cluster information only affects the graphical representation in the analysis output.

Ensure that the data in Correlation_input.csv matches the order wanted in the final plot (with the exception of the first trait, which must be the one from which the subtraction is conducted). The file should be placed in the same directory as the .R file and the .py file.

## Output
The following output files are generated by the script during the analysis workflow. Each file serves a specific purpose in the overall analysis process, from preprocessing and modeling to visualization and correlation analysis. These files are saved in the new working directory created and set at the beginning of the script, provided through the console command.

  1) "dir.txt": Contains the working directory name. It helps share the information between the .R and the .py script.

  2) "LDSC_main.rds": Contains the LDSC output data.

  3) "SNP_files.rds": Contains the sumstats for the SNPs, harmonized.

  4) "model_LD.csv": Contains the factor loadings, SEs and p-values from the GSEM model.

  5) "SEMplot.png": The GSEM plot saved as a PNG image.

  6) "outputMANN.png": The Manhattan plot saved as a PNG image.

  7) "outputQQ.png": The QQ plot saved as a PNG image.

  8) "[latentname3]_gwas.gz": The GSEM results file for the synthetic phenotype.

  9) "trait_correlation_data.csv": Contains the trait correlation data. It helps share the information between the .R and the .py script.

  10) "Correlation_output.rds": Contains the correlation output data. It helps share the information between the .R and the .py script.

  11) "trait_correlation_plot_with_clusters_background.png": PNG image of the correlation plot with cluster backgrounds.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
