"""
parse_result_batch.py -
    This script is made to parse hmmsearch output when multiple query sequences are searched.
    It Extracts hit information such as query ID, e-value, bit score, and we give a verdict based on custom threshold.
"""

from Bio import SeqIO

def parses_result_batch(out_path, query_fasta):
    """
    Parse the HMMER search output file and extract results.

    Arguments:
        out_path (str): Path to the HMMER output file.
        query_fasta (str): Path to the input query FASTA file.

    Returns:
        list: A list of dictionaries, one per query sequence.
    """
    results = []
    queries = {record.id: {"query": record.id, "match": None, "e-value": None, "score": None, "verdict": "No match found", "explanation": "No match found in HMMER search."} for record in SeqIO.parse(query_fasta, "fasta")}

    try:
        with open(out_path, "r") as file:
            lines = file.readlines()

        current_query = None
        in_scores_section = False

        for i, line in enumerate(lines):
            # Identify the query
            if line.startswith("Query:"):
                current_query = line.split()[1]
                print(f"Current query: {current_query}")

            # Identify the start of the "Scores for complete sequences" section
            elif line.strip().startswith("Scores for complete sequences"):
                in_scores_section = True
                print("Entering 'Scores for complete sequences' section.")

            # Parse matches in the "Scores for complete sequences" section
            elif in_scores_section:
                if line.strip() == "" or line.startswith("Domain annotation"):
                    # End of the scores section
                    in_scores_section = False
                    print("Exiting 'Scores for complete sequences' section.")
                elif line.strip().startswith("E-value") or line.strip().startswith("---"):
                    # Skip the header line or separator line
                    continue
                else:
                    # Extract E-value, Score, and Match
                    parts = line.split()
                    if len(parts) >= 9:  # Ensure there are enough columns
                        try:
                            e_value = float(parts[0])
                            score = float(parts[1])
                            match = parts[8]
                            verdict = "Low-confidence match"
                            explanation = "No significant match detected."

                            # Determine if the match is high confidence
                            if e_value < 1e-5:  # Example threshold for high confidence
                                verdict = "High-confidence match"
                                explanation = "Strong similarity to the HMM profile."

                            print(f"Query: {current_query}, Match: {match}, E-value: {e_value}, Score: {score}, Verdict: {verdict}")
                            queries[match] = {
                                "query": current_query,
                                "match": match,
                                "e-value": e_value,
                                "score": score,
                                "verdict": verdict,
                                "explanation": explanation
                            }
                        except ValueError as ve:
                            print(f"Skipping line due to parsing error: {line.strip()} - {ve}")

        # Add all queries to the results
        results = list(queries.values())
        return results

    except Exception as e:
        print(f"Error parsing HMMER output: {e}")
        return []
