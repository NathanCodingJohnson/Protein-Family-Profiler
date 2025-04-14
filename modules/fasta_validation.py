"""
fasta_validation.py -
    Validate fasta files submitted by the user.
    Ensure all sequence inputs are correctly formatted and the file contains a sufficient number of protein sequences.

Note:
    We assume that all uploaded FASTA files contain only protein sequences.
    Users are expected to upload protein FASTA files only.
    DNA or mixed sequences may result in incorrect alignments or low-quality predictions.
"""

def valid_fasta(fpath):
    """
    Checking if the uploaded file is a valid fasta file.
    A valid fasta file must have at least one header line starting with '>' and at least one sequence line after each header.

    The output is 'True' is the file is valid, otherwise it's 'False'.

    Argument:
        :param fpath: path to the saved fasta file.
    """
    try:
        with open(fpath, "r") as f:
            lines = [l.strip() for l in f if l.strip()]

        if not lines:
            return False

        header = False
        for i, l in enumerate(lines):
            if l.startswith(">"):
                header = True
            elif not header:
                return False   #Sequence line appeared before the header

        return header

    except Exception as e:
        print(f"Error occurred during fasta file validation: {e}.")
        return False


def sequence_count(fpath):
    """
    Counting the number of sequences in the fasta file.
    Identifying each sequence by the line starting with '>'.

    Argument:
        :param fpath: path to the saved fasta file.
    """
    try:
        with open(fpath, "r") as f:
            return sum(1 for l in f if l.startswith(">"))

    except Exception as e:
        print(f"Error occurred when counting sequences: {e}.")
        return 0