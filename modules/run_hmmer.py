"""
run_hmmer.py -
    Building a profile HMM using a 'hmmbuild'
    Searching a query fasta using 'hmmsearch'

Requirements:
    HMMER is properly installed and is accessible in the system path.
"""
import subprocess

def hmm_build(msa_path, hmm_path):
    """
    Build a profile HMM using the aligned fasta file.

    Arguments:
        :param msa_path: path to aligned fasta input.
        :param hmm_path: path to output .hmm profile file.
    """

    try:
        command = ["hmmbuild", hmm_path, msa_path]
        print(f"Running HMMER build: {' '.join(command)}")
        output = subprocess.run(command, capture_output=True, text=True)

        if output.returncode != 0:
            print(f"HMMER build failed: {output.stderr}")
            return False

        print("HMM profile created:", hmm_path)
        return True

    except FileNotFoundError:
        print("HMMER is not found. Please ensure 'hmmbuild' is installed properly and is in path.")
        return False


def hmm_search(hmmbuild_opath, query_path, out_path):
    """
    Searching a query sequence against a trained HMM using hmmsearch.

    Arguments:
        :param hmmbuild_opath: path to the .hmm model file.
        :param query_path: path to the query sequence in fasta format.
        :param out_path: path to save the hmmsearch result.
    """
    try:
        command = ["hmmsearch", hmmbuild_opath, query_path]
        print(f"Running HMMER search: {' '.join(command)}")

        with open(out_path, "w") as f:
            output = subprocess.run(command, stdout=f, stderr=subprocess.PIPE, text=True)

        if output.returncode != 0:
            print(f"HMMER search failed: {output.stderr}")
            return False

        print("HMM search completed. Output is saved to:", out_path)
        return True

    except FileNotFoundError:
        print("HMMER not found. Please ensure 'HMMER' is installed properly and in path.")
        return False


