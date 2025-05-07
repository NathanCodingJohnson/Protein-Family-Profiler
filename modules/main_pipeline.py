"""
main_pipeline.py -
    Tying together the full backend pipeline for Protein Family Profiler.
    This script is made to handle training sequence input, query input, HMM building, searching, annotation, visualization, and result aggregation.
"""

# Importing necessary modules
from modules.get_sequences import get_sequences_family, get_sequences_ids, user_fasta
from modules.msa_sequences import run_clustalo
from modules.run_hmmer_batch import hmm_build
from modules.run_hmmer_batch import hmm_search
from modules.parse_result_batch import parses_result_batch
from modules.extract_confident_query import extract_confident_query
from modules.blast_annotate import blast_annotate
from modules.visualize_results import plot_evalue_vs_score, plot_hmmer_scores

import os

def prepare_training_sequences(input_mode, input_data, output_fasta):
    """
    Preparing training sequences based on input method.
    """
    if input_mode == 'family':
        get_sequences_family(family_name=input_data, out_file=output_fasta)
    elif input_mode == 'ids':
        get_sequences_ids(ids_file=input_data, out_file=output_fasta)
    elif input_mode == 'user_fasta':
        user_fasta(file_object=input_data, out_file=output_fasta)
    else:
        raise ValueError(f"Invalid input_mode: {input_mode}")


def build_hmm(training_fasta, msa_output, hmm_output):
    """
    Building an HMM profile from training sequences.
    """
    run_clustalo(in_path=training_fasta, out_path=msa_output)
    hmm_build(msa_path=msa_output, hmm_path=hmm_output)


def search_queries(hmm_file, query_fasta, search_output):
    """
    Running hmmsearch against the query sequences.
    """
    hmm_search(hmm_file, query_fasta, search_output)


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


def run_pipeline(input_mode, input_data, query_fasta, working_dir="iofiles"):
    """
    Main runner function for the full pipeline.

    It returns list of annotated results.
    """

    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    training_fasta = os.path.join(working_dir, "training_sequences.fasta")
    msa_output = os.path.join(working_dir, "training_alignment.fasta")
    hmm_output = os.path.join(working_dir, "trained_model.hmm")
    search_output = os.path.join(working_dir, "search_results.txt")

    prepare_training_sequences(input_mode, input_data, training_fasta)
    build_hmm(training_fasta, msa_output, hmm_output)
    search_queries(hmm_output, query_fasta, search_output)

    # Parsing and printing HMMER results before annotation
    parsed_results = parses_result_batch(search_output)
    print("\nParsed HMMER Results:\n")
    for result in parsed_results:
        print(f"Query: {result.get('query')}")
        print(f"  Match: {result.get('match')}")
        print(f"  E-value: {result.get('e-value')}")
        print(f"  Score: {result.get('score')}")
        print(f"  Verdict: {result.get('verdict')}")
        print(f"  Explanation: {result.get('explanation')}")
        print("-" * 50)

    # Proceeding to BLAST annotation for confident matches
    annotated_results = annotate_confident_matches(search_output, query_fasta)

    # Creating visualizations
    plot_evalue_vs_score(annotated_results)
    plot_hmmer_scores(annotated_results)

    return annotated_results
