"""
blast_annotate.py -
    We made this module to handle BLAST annotation for confident query sequences.

    This script takes a protein sequence, submits it to the NCBI BLAST server,
    and tries to find the top matching protein from the SwissProt database.

    It saves the BLAST result as an XML file for checking later if needed,
    and pulls out basic information like the top hit ID, description, and bit score.
"""

import requests
import time
import xml.etree.ElementTree as ET

def blast_annotate(sequence, program="blastp", database="swissprot", retries=30, delay=6):
    """
    Arguments:
        sequence (str): The protein sequence to search with (amino acids only).
        program (str): The BLAST program to use (default is "blastp").
        database (str): The database to search against (default is SwissProt).
        retries (int): How many times to check if the BLAST result is ready.
        delay (int): How long to wait between retries (in seconds).

    It returns a dictionary with the hit ID, description, and bit score
    if a match is found, or None if no match or if something goes wrong.
    """
    base_url = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"

    payload = {
        "CMD": "Put",
        "PROGRAM": program,
        "DATABASE": database,
        "QUERY": sequence
    }

    response = requests.post(base_url, data=payload)
    if "RID =" not in response.text:
        print("Failed to submit the BLAST request.")
        return None

    rid = response.text.split("RID =")[1].splitlines()[0].strip()
    print(f"RID received: {rid}")

    for attempt in range(retries):
        print(f"Waiting for the BLAST result... (trial {attempt+1})")
        status = requests.get(base_url, params={"CMD": "Get", "RID": rid, "FORMAT_OBJECT": "SearchInfo"})
        if "Status=READY" in status.text:
            break
        time.sleep(delay)
    else:
        print("BLAST server took too long to respond. Please try again later.")
        return None

    result = requests.get(base_url, params={"CMD": "Get", "RID": rid, "FORMAT_TYPE": "XML"})
    if result.status_code != 200:
        print("Failed to retrieve the result.")
        return None

    try:
        # Saving raw XML for manual inspection
        with open("blast_debug.xml", "w") as f:
            f.write(result.text)
        print("Saved the BLAST XML output to blast_debug.xml for debugging if neeeded.")

        # Proceeding with normal parsing
        root = ET.fromstring(result.text)
        hit = root.find(".//Hit")
        if hit is None:
            print("No top hit found.")
            return None

        hsp = hit.find(".//Hsp")
        if hsp is None:
            print("No HSP found.")
            return None

        score = float(hsp.findtext("Hsp_bit-score"))

        return {
            "hit_id": hit.findtext("Hit_accession"),
            "description": hit.findtext("Hit_def"),
            "score": score
        }

    except Exception as e:
        print(f"Error parsing the BLAST XML: {e}")
        return None
