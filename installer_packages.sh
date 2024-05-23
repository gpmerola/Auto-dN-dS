#!/bin/bash

# List of required Python packages
required_packages=(
    "requests"
    "concurrent.futures"
    "ensembl_rest"
    "tqdm"
    "biopython"
)

# Function to install a Python package
install_package() {
    package="$1"
    echo "Installing $package..."
    pip3 install --break-system-packages "$package"
}

# Main function to check and install required packages
check_and_install_packages() {
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" 2>/dev/null; then
            install_package "$package"
        else
            echo "$package is already installed."
        fi
    done
}

# Check and install packages
check_and_install_packages

echo "All required packages have been installed."

