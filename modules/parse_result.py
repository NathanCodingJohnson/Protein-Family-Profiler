"""
parse_result.py -
    Reading and interpreting the hmmsearch output file.
    Extracting whether a match was found, score, e-value, and also giving relevant biological interpretation.
"""

def parses_result(out_path):
    """
    Parses the output from hmmsearch and returns a dictionary.

    Argument:
        :param out_path: path to the HMMER output file.
    """
    match = False
    e_val = None
    score = None
    exp = "The query sequence did not show significant similarity to the trained protein family. This may mean that it is unrelated or highly divergent."

    with open(out_path) as f:
        lines = f.readlines()

    for i, l in enumerate(lines):
        if l.strip().startswith("Scores for complete sequences"):
            for j in range(i+3, len(lines)):
                line = lines[j].strip()
                if line == "" or line.startswith("------"):
                    continue
                if line.startswith("[No hits detected that satisfy reporting thresholds]"):
                    exp = "No hits passed HMMER's statistical thresholds. The sequence likely does nit contain conserved motifs or domains that are typical of the family."
                    break

                parts = line.split()
                if len(parts) >= 6:
                    try:
                        score = float(parts[1])
                        e_val = float(parts[0])
                        match = True
                        exp = "A strong hit was detected with a low e-value and high score, indicating high similarity to the trained protein family."
                    except ValueError:
                        continue
                    break
            break

    final_verdict = (
        "High-confidence match. This sequence is strongly related to the trained family."
        if match and e_val is not None and e_val < 1e-5 else
        "Borderline similarity detected. Further review recommended."
        if match and e_val is not None and e_val < 1e-2 else
        "No significant match detected."
    )

    return {
        "match": match,
        "e-value": e_val,
        "score": score,
        "verdict": final_verdict,
        "explanation": exp
    }