#!/bin/bash

# Update package lists
sudo apt-get update

# Upgrade existing packages
sudo apt-get upgrade -y

# Install Python3 and pip if they are not installed
sudo apt-get install python3 python3-pip -y

# Install necessary Python libraries
pip3 install cryptography requests jwt numpy pandas schedule

echo "All necessary libraries have been installed."
