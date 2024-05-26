library(seqinr)
library(phangorn)
library(writexl)
library(tidyverse)
library(dplyr)
library(readxl)

# Set the working directory to the script's location or one level above if necessary.
set_working_directory <- function() {
  # Check if we can use rstudioapi to find the script's path within RStudio
  if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
    setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
  } else {
    # Try to get the script path from command line arguments if not run within RStudio
    args <- commandArgs(trailingOnly = FALSE)
    file.arg <- "--file="
    script.path <- sub(file.arg, "", args[grep(file.arg, args)])
    if (length(script.path) > 0) {
      setwd(dirname(script.path))
    } else {
      stop("Cannot determine the script's location.")
    }
  }
  setwd("..")  # Move up one directory level
}

set_working_directory()

# Extract species and gene name from sequence name
extract_info <- function(seq_name) {
  parts <- unlist(strsplit(seq_name, "_"))
  list(species = parts[2] %||% NA, gene = parts[1] %||% NA)
}

# Function to calculate Ka/Ks ratio for genes in a FASTA file
ka <- function(file_path) {
  gene_name <- tools::file_path_sans_ext(basename(file_path))
  alignment <- read.alignment(file_path, format = "fasta")
  
  # Error handling for Ka/Ks calculation
  gene_results <- tryCatch({
    kaks_result <- kaks(alignment)
    kadf <- as.data.frame(as.matrix(kaks_result$ka))
    ksdf <- as.data.frame(as.matrix(kaks_result$ks))
    kratio <- kadf / ksdf
    
    gene_results <- list()
    for (i in 1:nrow(kratio)) {
      for (j in 1:ncol(kratio)) {
        species_1_info <- extract_info(rownames(kratio)[i])
        species_2_info <- extract_info(colnames(kratio)[j])
        species_1 <- species_1_info$species
        species_2 <- species_2_info$species
        
        if (!(species_1 == "Human")) {
          next
        }
        
        if (!is.na(kratio[i, j]) && is.numeric(kratio[i, j])) {
          key <- paste("HUMAN", species_2, sep = "-")
          gene_results[[key]] <- round(kratio[i, j], 3)
        }
      }
    }
    gene_results
  }, error = function(e) {
    print(paste("Error processing:", gene_name, "with message:", e$message))
    list()
  })
  return(gene_results)
}

# Process all FASTA files in a directory and compile Ka/Ks results
process_directory <- function(directory_path) {
  setwd(directory_path)
  cat("Current working directory:", getwd(), "\n")
  
  fasta_files <- list.files(pattern = "\\.fa$|\\.fasta$", full.names = TRUE)
  
  results <- setNames(vector("list", length(fasta_files)), basename(fasta_files))
  
  for (file_path in fasta_files) {
    file_name <- tools::file_path_sans_ext(basename(file_path))
    results[[file_name]] <- ka(file_path)
  }
  
  output_df_long <- bind_rows(
    lapply(names(results), function(gene_name) {
      gene_results <- results[[gene_name]]
      if(length(gene_results) == 0) return(NULL)
      data.frame(
        gene = rep(gene_name, length(gene_results)),
        species_pair = names(gene_results),
        ka_ks = unlist(gene_results),
        stringsAsFactors = FALSE
      )
    }),
    .id = "gene_id"
  ) %>% filter(!is.na(ka_ks))
  
  output_df_wide <- output_df_long %>%
    pivot_wider(names_from = species_pair, values_from = ka_ks) %>%
    mutate(across(where(is.numeric), ~ifelse(. == Inf | is.infinite(.) | . < 0 | . > 50, NA_real_, .))) %>%
    mutate(across(where(is.character), ~ifelse(. == "Inf", NA_character_, .))) %>%
    select(gene, everything())
  
  output_file_name <- "output_results.xlsx"
  setwd("..")
  write_xlsx(output_df_wide, output_file_name)
  cat("Results file created:", output_file_name, "\n")
  
  return(output_df_wide)
}

# Calculate basic statistics from the data in an Excel file
calculate_stats <- function(filepath) {
  data <- read_excel(filepath)
  
  if (ncol(data) < 3) {
    stop("The file ", filepath, " does not have a third column.")
  }
  
  mean_val <- mean(data[[3]], na.rm = TRUE)
  sd_val <- sd(data[[3]], na.rm = TRUE)
  count_val <- sum(!is.na(data[[3]]))
  
  return(list(mean = mean_val, sd = sd_val, count = count_val))
}

# Main execution block
setwd("temp")
alignfolder <- readLines("alignfolder.txt", warn = FALSE)
output_df_wide <- process_directory(file.path(getwd(), "..", "results", alignfolder))

files <- list.files(pattern = "\\.xlsx$", full.names = TRUE)

results <- list()

for (file in files) {
  stats <- calculate_stats(file)
  stats$name <- basename(file)
  results[[length(results) + 1]] <- stats
}

summary_df <- do.call(rbind, lapply(results, as.data.frame))
row.names(summary_df) <- NULL

write_xlsx(summary_df, "summary.xlsx")

cat("Summary file created with", nrow(summary_df), "rows.\n")
