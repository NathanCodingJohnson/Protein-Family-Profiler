"""
extract_confident_query.py -
    We made this script to pull out a specific sequence from a FASTA file.

    It's used after we find that a query sequence got a "High-confidence match"
    in the HMMER search, and we want to use it for BLAST annotation.

    Basically, it just looks through the FASTA file and finds the sequence
    for the given query ID.
"""

from Bio import SeqIO

def extract_confident_query(fasta_path, query_id):
    """
    Arguments:
        fasta_path (str): Path to the FASTA file we want to search in.
        query_id (str): The ID of the sequence we’re looking for (without the '>').

    It returns the sequence as a plain string if found, or None if it's not there.
"""
    try:
        for record in SeqIO.parse(fasta_path, "fasta"):
            if record.id == query_id:
                return str(record.seq)
        print(f"Query '{query_id}' is not found in {fasta_path}")
        return None
    except Exception as e:
        print(f"Error reading the FASTA file: {e}")
        return None
