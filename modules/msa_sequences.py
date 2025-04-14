"""
msa_sequences.py -
    Takes a validated fasta file, runs Clustal Omega locally, and saves the aligned output fasta file.

Requirements:
    - Clustal Omega should be installed locally and accessible when the 'clustalo' command is used in the system.
      (For the web application version, we will need to install the Clustal Omega on the server or bundle it in a docker container for deployment.)
    - Input must be a valid fasta file.
"""

import subprocess
import os

def run_clustalo(in_path, out_path):
    """
    Running Clustal Omega on the validated fasta file to get a multiple sequence alignment (MSA).

    Arguments:
        :param in_path: path to the input validated fasta file.
        :param out_path: path where the aligned fasta file should be saved.
    """
    try:
        command = ["clustalo", "-i", in_path, "-o", out_path, "--force", "--outfmt", "fasta"]

        print(f"Running Clustal Omega: {' '.join(command)}")
        output = subprocess.run(command, capture_output=True, text=True)

        if output.returncode != 0:
            print(f"Clustal Omega failed: {output.stderr}")
            return False

        print("MSA done. Output is saved to:", out_path)
        return True

    except FileNotFoundError:
        print("clustalo is not found, please ensure that it is installed properly and is in path.")
        return False

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
