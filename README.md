# Protein-Family-Profiler
By Nathan Johnson and Rama Krishna Pudota (Team NatKris)


Protein sequence analysis is very crucial in understanding a protein's structure, function, and even its evolution. A lot of sequence analysis tools that are available either require command-line skills or are not so flexible and usable. Tools like HMMER and BLAST are used for profiling sequences and homology detection. So, we decided to try and develop a web-based protein family profiler tool that makes sequence profiling more accessible and easy to use. Our project uses UniProt API, Clustal Omega, HMMER, and BLAST API. Our idea was to build an automated workflow that anyone, who is a beginner and has an interest in bioinformatics research, can easily use to perform protein sequence analysis. 


# Installation Guide

**It is important to note that at the current time, running this project on Windows is not possible as two of the important modules (HMMER and clustalo) are not available on Windows machines. We got around this issue by utilizing a local Linux installation to run the webapp for testing.**

## Environment Management

This project uses a Conda environment for package and dependency management. It is recommended to install Miniconda before proceeding. Miniconda is a lightweight installer for Conda and is available for macOS, Linux, and Windows.

On Linux:
```
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

    bash Miniconda3-latest-Linux-x86_64.sh
```
Then restart your Linux terminal using:
```
    source ~/.bashrc
```

## Installing the Environment (Recommended Method)

An environment.yml file is provided with the project, containing all necessary dependencies and their versions.
To create the environment from this file:
```
    conda env create -f environment.yml

    conda activate bioenv_x86
```

### Alternative Manual Setup (If environment.yml Fails)
In case the environment.yml file does not work due to platform-specific issues (for example, package availability for osx-64 or osx-arm64), follow the steps below to manually set up the environment:

Step 1: Create a new Conda environment

conda create -n protein_family_profiler python=3.10

conda activate protein_family_profiler

Step 2: Install Required Packages

Install the required Python libraries and bioinformatics tools:

conda install -c conda-forge biopython matplotlib seaborn pandas requests flask

conda install -c bioconda hmmer

conda install -c bioconda clustalo

Note:

If a specific package (like hmmer or clustalo) is unavailable in the suggested channel for your platform, please:
Visit the Anaconda Package Search website. https://anaconda.org/
Search for the package (e.g., "clustalo") and check which channels and platforms are supported.

Install it by specifying the correct channel.
For example:
conda install -c <channel_name> <package_name>
Example:
conda install -c etetoolkit clustalo
(if bioconda version is not available for your platform).

## Run the program!

to run the program, simply run the following command in the project folder:
```
    python main.py
```

Once the project is running, navigate to: http://127.0.0.1:5000/ to view our webapp


# Testing the project
In order to test our project, we have provided some test data files with expected results.
First, select which method you would like to use to provide protein sequences to train the HMM.
- Uploading a fasta file directly
    - Select "Upload a .fasta File" from the home page
    - Choose "proteinkinase_familiy.fasta" from the test data directory within the project folder
    - Press "Upload"
- Fetching from UniProt by searching by protein family name
    - Select "Fetch by Protein Family" from the home page
    - Type "protein kinase" into the field under "Enter a Protein Family Name:" and leace the number of sequences blank
    - Press "Fetch Sequences"
- Fetching from UniProt using a text file list of accession IDs
    - Select "Fetch by Accession IDs" from the home page
    - Choose "proteinkinase_familiy_ids.txt" from the test data directory within the project folder
    - Press "Fetch Sequences"

_Wait while the protein sequences are validated, aligned, and used to train an HMM. It should only take a minute_

- Once you have reached the upload query fasta file page
    - Choose "proteinkinase_queries.fasta" from the test data directory within the project folder
    - Press "Upload"

_Please wait while the uploaded query sequences are scanned against the HMM you just created and BLAST API calls are made for any high-confidence matches. This may take a very long time (for this test file, at worst, it should only take up to 9 minutes if the BLAST API is too busy and you are unlucky)_

- Once the BLAST API calls are finished, you will see the results page!
    - You should see that the first 3 queries are high-confidence matches
    - The last two queries should be low-confidence matches
    - The bar graph should look like this:
        - ![image](https://github.com/user-attachments/assets/f5c80e0f-b4b3-4832-a7d0-635e058da63d)

    - If the BLAST API calls were successful, the high confidence matches will have extra information from BLAST and there will be a scatter plot with E value vs BLAST Score
