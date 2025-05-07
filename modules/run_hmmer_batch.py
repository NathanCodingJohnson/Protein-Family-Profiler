"""
run_hmmer_batch.py -
    This script builds a profile HMM from a set of training sequences,
    and uses it to search one or more query sequences.

    It works for both single queries and batch queries.
    Make sure HMMER is installed and can be run from the command line.
"""

import subprocess
import os


def hmm_build(msa_path, hmm_path):
    """
    Arguments:
        msa_path (str): Path to the multiple sequence alignment input.
        hmm_path (str): Path to the output HMM file.
    """
    try:
        command = ["hmmbuild", hmm_path, msa_path]
        print(f"Running HMMER build: {' '.join(command)}")

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            print("HMMER build failed.")
            print("Standard Error:", result.stderr.strip())
            return False

        print("HMMER build completed successfully.")
        print("Standard Output:", result.stdout.strip())
        print("HMM profile successfully created:", hmm_path)
        return True

    except FileNotFoundError:
        print("Error: 'hmmbuild' not found. Is HMMER installed and in your PATH?")
        return False

    except Exception as e:
        print(f"Unexpected error during HMM build: {e}")
        return False


def hmm_search(hmm_path, query_path, out_path):
    """
    Arguments:
        hmm_path (str): Path to the HMM model file.
        query_path (str): Path to the query FASTA file (single or multi-sequence).
        out_path (str): Path to save the hmmsearch output.
    """
    if not os.path.exists(hmm_path):
        print(f"Error: HMM file is not found at: {hmm_path}")
        return False

    if not os.path.exists(query_path):
        print(f"Error: Query file is not found at: {query_path}")
        return False

    try:
        command = ["hmmsearch", "--max", hmm_path, query_path]
        print("Starting HMMER search...")
        print("Running command:", " ".join(command))

        with open(out_path, "w") as output_file:
            result = subprocess.run(
                command,
                stdout=output_file,
                stderr=subprocess.PIPE,
                text=True
            )

        if result.returncode != 0:
            print("HMMER search failed.")
            print("Standard Error:", result.stderr.strip())
            return False

        print("HMMER search completed successfully.")
        print("Standard Error:", result.stderr.strip())
        print("HMM search completed. Output is saved to:", out_path)
        return True

    except FileNotFoundError:
        print("Error: 'hmmsearch' not found. Is HMMER installed and in your PATH?")
        return False

    except Exception as e:
        print(f"Unexpected error occurred during HMM search: {e}")
        return False
