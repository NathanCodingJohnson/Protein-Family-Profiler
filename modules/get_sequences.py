"""
get_sequences.py -

Three Methods -
    I. Fetching sequences by the protein family name. Users are given an option to choose a common protein family (dropdown selection).
    II. Fetching by a list of UniProt accession IDs (.txt file).
        The text file should be in this format:
            - One UniProt Accession ID per line
            - No commas, tabs, or other separators
            - No headers
            - No extra whitespace
    III. Saving the user-uploaded fasta file.
        The fasta file that user uploads should be in this format:
            - One protein sequence per entry
            - Each entry must begin with a header line starting with '>'
            - Sequence must follow immediately with no empty lines between entries
            - Only amino acid characters allowed (A, C, D, E, F, G, etc.)

        Example:
            >seq1
            MAVLVVVFTAILFSSALA
            >seq2
            MAGRTQVVRSLFPNLR
"""

import requests

def get_sequences_family(family_name, size=25, out_file="iofiles/train_seqs.fasta"):
    """
    Fetching sequences by the protein family name selected by user in the dropdown.

    Arguments:
        family_name: Name of the protein family.
        size: Number of protein sequences to fetch.
        out_file: Path to save the compiled fasta file.
    """

    query = f'family:"{family_name}" AND reviewed:true'
    url = "https://rest.uniprot.org/uniprotkb/search"
    parameters = {"query": query, "format": "fasta", "size": str(size)}

    print(f"Fetching {size} sequences for the {family_name} family.")
    responses = requests.get(url, params=parameters)

    if responses.status_code == 200:
        with open(out_file, "w") as a:
            a.write(responses.text)
        print(f"Sequences saved to {out_file}")
    else:
        print(f"Failed to fetch protein family sequences (status code: {responses.status_code}.")


def get_sequences_ids(ids_file, out_file="iofiles/train_seqs.fasta"):
    """
    Fetching sequences from UniProt using their accession IDs list (txt file) given by the user.

    Arguments:
        ids_file: Path to .txt file with accession IDs.
        out_file: Path to save the compiled fasta file.
    """

    count = 0

    with open(ids_file) as a:
        accession_ids = [l.strip() for l in a if l.strip()]
    print(f"Parsed accessions: {accession_ids}.")

    with open(out_file, "w") as o:
        for acc in accession_ids:
            url = f"https://rest.uniprot.org/uniprotkb/{acc}?format=fasta"
            responses = requests.get(url, allow_redirects=True)
            if responses.status_code == 200:
                o.write(responses.text)
                count += 1
            else:
                print(f"Failed to fetch {acc} (status: {responses.status_code}) (URL: {url}).")

    print(f"Fetched {count} out of {len(accession_ids)} sequences.")
    print(f"Sequences are saved to {out_file}")

import shutil

def user_fasta(file_object, out_file="iofiles/training_sequences.fasta"):
    """
    Saving the user-uploaded fasta file or copying a local fasta file during testing.

    Arguments:
        file_object: This can be a Flask uploaded file object or a file path (string).
        out_file (str): Path where the file should be saved.
    """

    if isinstance(file_object, str):
        # It's a local path string for testing, copying the file
        shutil.copy(file_object, out_file)
    else:
        # It's a Flask file upload, saving it
        file_object.save(out_file)

    print(f"Training fasta file saved to {out_file}.")
