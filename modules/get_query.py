"""
get_query.py
    We made this script to save the query sequence(s) uploaded by the user.

    It just saves the file as it is — we are not checking if the format is correct here.
"""


def save_uploaded_query_fasta(file_object, out_path="iofiles/query.fasta"):
    """
    Arguments:
    file_object: The uploaded file (from the user form).
    out_path (str): Where to save the file.

    Returns True if the file was saved successfully, False otherwise.
    """
    try:
        file_object.save(out_path)
        print(f"Query FASTA file is saved to: {out_path}")
        return True

    except Exception as e:
        print(f"Error occurred while saving query FASTA: {e}")
        return False
