"""
visualize_results.py -
    Create a scatter plot of E-value vs BLAST score using Seaborn.

This version uses a simple static plot (not interactive).
"""

import seaborn as sns
import matplotlib.pyplot as plt
import math
from modules.extract_confident_query import extract_confident_query
from modules.blast_annotate import blast_annotate
from modules.parse_result_batch import parses_result_batch

def annotate_confident_matches(search_output, query_fasta):
    """
    Parsing hmmsearch output and annotating high-confidence matches using BLAST.

    It returns List of dictionaries containing enriched results.
    """
    results = parses_result_batch(search_output)

    for result in results:
        if result.get("verdict") == "High-confidence match":
            query_id = result.get("query")
            sequence = extract_confident_query(fasta_path=query_fasta, query_id=query_id)

            if sequence:
                annotation = blast_annotate(sequence)
                result["blast_annotation"] = annotation if annotation else {"note": "No hit found"}
            else:
                result["blast_annotation"] = {"note": "Sequence not found"}

    return results

def plot_hmmer_scores(results, output_path="hmmer_scores.png"):
    """
    Create a bar plot showing HMMER scores for each query.

    Arguments:
        results (list): List of result dictionaries (parsed HMMER output).
        output_path (str): File path to save the plot image.
    """
    query_ids = []
    hmmer_scores = []

    for entry in results:
        if entry.get("match") and entry.get("score") is not None:
            try:
                query_ids.append(entry.get("match"))  # Use the match ID as the label
                hmmer_scores.append(float(entry.get("score")))
            except ValueError:
                continue

    if not query_ids or not hmmer_scores:
        print("No valid HMMER matches to plot.")
        return

    # Create the bar plot
    plt.figure(figsize=(10, 6))
    sns.barplot(x=query_ids, y=hmmer_scores, palette="Blues_r")

    plt.xlabel("Query ID")
    plt.ylabel("HMMER Score")
    plt.title("HMMER Match Scores by Query")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

    # Save the plot
    plt.savefig(output_path)
    print(f"HMMER Score plot saved to {output_path}")
    plt.close()

def plot_evalue_vs_score(results, output_path="scatter_plot.png"):
    """
    This function is used to create a scatter plot from annotated query results using Seaborn.

    Arguments:
        results (list): List of result dictionaries.
        output_path (str): File path to save the plot image.
    """

    # Preparing data
    query_ids = []
    log_e_values = []
    scores = []

    for entry in results:
        if entry.get("verdict") == "High-confidence match" and "blast_annotation" in entry:
            annotation = entry["blast_annotation"]
            if annotation and annotation.get("score") and annotation.get("hit_id"):
                try:
                    e_val = float(entry.get("e-value"))
                    score = float(annotation.get("score"))

                    if e_val > 0:
                        query_ids.append(entry.get("query"))
                        log_e_values.append(math.log10(e_val))
                        scores.append(score)

                except ValueError:
                    continue  # Skips if parsing fails

    if not query_ids:
        print("No valid data to plot.")
        return

    # Creating the scatter plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=log_e_values, y=scores, hue=query_ids, s=100, palette="deep")

    plt.xlabel("log10(E-value)")
    plt.ylabel("BLAST Score")
    plt.title("E-value vs BLAST Score for High-Confidence Matches")
    plt.legend(title="Query ID", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()

    # Saving the plot
    plt.savefig(output_path)
    print(f"Scatter plot saved to {output_path}")

    # Optionally showing the plot directly
    plt.show()

