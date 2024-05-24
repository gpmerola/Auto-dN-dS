# List of required R packages
required_packages <- c(
  "seqinr",
  "ape",
  "phylotools",
  "phangorn",
  "writexl",
  "openxlsx",
  "tidyverse",
  "dplyr",
  "readxl"
)

# Function to install missing packages
install_if_missing <- function(p) {
  if (!requireNamespace(p, quietly = TRUE)) {
    install.packages(p, repos='http://cran.rstudio.com/')
  }
}

# Install all required packages
invisible(lapply(required_packages, install_if_missing))
