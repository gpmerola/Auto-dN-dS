library(seqinr)
library(ape)
library(phylotools)
library(phangorn)
library(writexl)
library(openxlsx)
library(tidyverse)
library(dplyr)
library(readxl)

if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
  setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
} else {
  args <- commandArgs(trailingOnly = FALSE)
  file.arg <- "--file="
  script.path <- sub(file.arg, "", args[grep(file.arg, args)])
  if (length(script.path) > 0) {
    setwd(dirname(script.path))
  } else {
    stop("Cannot determine the script's location.")
  }
}
setwd("..")
setwd(file.path(getwd(), "results"))


# Extract species and gene name from sequence name
extract_info <- function(seq_name) {
  parts <- unlist(strsplit(seq_name, "_"))
  list(species = parts[2] %||% NA, gene = parts[1] %||% NA)
}

# Define the ka function
ka <- function(file_path) {
  gene_name <- tools::file_path_sans_ext(basename(file_path))
  alignment <- read.alignment(file_path, format = "fasta")
  
  # Perform error handling for kaks calculation
  tryCatch({
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
        
        if (!(species_1 == "Human")) 
        {
          next
        }
        
        # Collect Ka/Ks values for humans vs other species
        if (!is.na(kratio[i, j]) && is.numeric(kratio[i, j])) {
          key <- paste("HUMAN", species_2, sep = "-")
          gene_results[[key]] <- round(kratio[i, j], 3)
        }
      }
    }
    results[[gene_name]] <- gene_results
  }, error = function(e) {
    print(paste("Error processing:", gene_name, "with message:", e$message))
  })
  return(gene_results)
}

directories <- list.dirs(path = ".", full.names = TRUE, recursive = FALSE)

# Loop over each directory and process the files
for (dir in directories) {
  message("Processing directory: ", dir)
  
  # Get all .fa or .fasta files in the current directory
  fasta_files <- list.files(path = dir, pattern = "\\.fa$|\\.fasta$", full.names = TRUE)
  # Skip the directory if no files are found
  if(length(fasta_files) == 0) {
    message("No FASTA files detected in ", dir)
    next
  }
  
  # Initialize a list to store results for this directory
  dir_results <- setNames(vector("list", length(fasta_files)), basename(fasta_files))
  
  # Process each .fa or .fasta file and store the results
  for (file_path in fasta_files) {
    file_name <- tools::file_path_sans_ext(basename(file_path))
    dir_results[[file_name]] <- ka(file_path)
  }
  
  # Combine results into a single data frame in long format
  output_df_long <- bind_rows(
    lapply(names(dir_results), function(gene_name) {
      gene_results <- dir_results[[gene_name]]
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
  
  # If there are no results, skip the file writing
  if (nrow(output_df_long) == 0) {
    message("No results for directory: ", dir)
    next
  }
  
  # Convert 'long' format to 'wide' format and clean up the data
  output_df_wide <- output_df_long %>%
    pivot_wider(names_from = species_pair, values_from = ka_ks) %>%
    mutate(across(where(is.numeric), ~ifelse(. == Inf | is.infinite(.) | . < 0 | . > 50, NA_real_, .))) %>%
    mutate(across(where(is.character), ~ifelse(. == "Inf", NA_character_, .)))
  
  # Reorder the data frame to ensure gene name is the first column
  if("gene" %in% names(output_df_wide)) {
    output_df_wide <- output_df_wide %>% 
      select(gene, everything())
  }
  
  # Create a unique filename for each directory
  output_file_name <- paste0("output_results_", basename(dir), "_", ".xlsx")
  write_xlsx(output_df_wide, output_file_name)
}















calculate_stats <- function(filepath) {
  data <- read_excel(filepath)
  
  # Check if the third column exists
  if (ncol(data) < 3) {
    stop("The file ", filepath, " does not have a third column.")
  }
  
  # Calculate statistics
  mean_val <- mean(data[[3]], na.rm = TRUE)
  sd_val <- sd(data[[3]], na.rm = TRUE)
  count_val <- sum(!is.na(data[[3]]))
  
  # Return as a named list
  return(list(mean = mean_val, sd = sd_val, count = count_val))
}

# Get a list of all .xlsx files in the current directory
files <- list.files(pattern = "\\.xlsx$", full.names = TRUE)

# Initialize a list to store results
results <- list()

# Loop through files and calculate statistics
for (file in files) {
  stats <- calculate_stats(file)
  stats$name <- basename(file) # Add the filename to the stats list
  results[[length(results) + 1]] <- stats
}

# Combine all results into a data frame
summary_df <- do.call(rbind, lapply(results, as.data.frame))
row.names(summary_df) <- NULL

# Write the summary to a new Excel file
write_xlsx(summary_df, "summary.xlsx")

# Output to console to indicate completion
cat("Summary file created with", nrow(summary_df), "rows.\n")

