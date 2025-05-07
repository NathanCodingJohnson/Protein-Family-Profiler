import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from modules.get_sequences import get_sequences_family, get_sequences_ids
from modules.fasta_validation import valid_fasta
from modules.run_hmmer_batch import hmm_build, hmm_search
from modules.parse_result_batch import parses_result_batch
from modules.msa_sequences import run_clustalo
from modules.extract_confident_query import extract_confident_query  # Import added
from modules.blast_annotate import blast_annotate  # Import added
from modules.visualize_results import plot_hmmer_scores, plot_evalue_vs_score, annotate_confident_matches  # Import added

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for headless environments
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')

# Ensure the uploads directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/upload_fasta_page', methods=['GET'])
def upload_fasta_page():
    return render_template('upload_fasta.html')

@app.route('/fetch_sequences_page', methods=['GET'])
def fetch_sequences_page():
    return render_template('fetch_sequences.html')

@app.route('/fetch_by_family_page', methods=['GET'])
def fetch_by_family_page():
    return render_template('fetch_by_family.html')

@app.route('/fetch_by_ids_page', methods=['GET'])
def fetch_by_ids_page():
    return render_template('fetch_by_ids.html')

@app.route('/upload_fasta', methods=['POST'])
def upload_fasta():
    fasta_file = request.files.get('fasta_file')
    if fasta_file and fasta_file.filename.endswith('.fasta'):
        fasta_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(fasta_file.filename))
        fasta_file.save(fasta_path)

        if valid_fasta(fasta_path):
            # Step 1: Generate MSA file using Clustal Omega
            msa_path = os.path.join(app.config['UPLOAD_FOLDER'], "aligned_sequences.msa")
            if not run_clustalo(fasta_path, msa_path):
                error_message = "Failed to generate MSA file. Please ensure Clustal Omega is installed and accessible."
                return render_template('index.html', error=error_message)

            # Step 2: Build HMM profile using the MSA file
            hmm_path = os.path.join(app.config['UPLOAD_FOLDER'], "profile.hmm")
            if not hmm_build(msa_path, hmm_path):
                error_message = "Failed to build HMM profile. Please check the input MSA file."
                return render_template('index.html', error=error_message)

            # Step 3: Prompt user to upload a query FASTA file for HMM search
            return render_template('upload_query.html', hmm_path=hmm_path)

        else:
            os.remove(fasta_path)  # Remove invalid file
            error_message = "Invalid fasta file. Please upload a properly formatted .fasta file."
            return render_template('index.html', error=error_message)
    error_message = "Invalid file. Please upload a .fasta file."
    return render_template('index.html', error=error_message)

@app.route('/perform_hmm_search', methods=['POST'])
def perform_hmm_search():
    hmm_path = request.form.get('hmm_path')
    query_file = request.files.get('query_file')

    if query_file and query_file.filename.endswith('.fasta'):
        query_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(query_file.filename))
        query_file.save(query_path)

        if valid_fasta(query_path):
            # Step 4: Perform HMM search
            raw_search_output = os.path.join(app.config['UPLOAD_FOLDER'], "hmmsearch_result.txt")
            parsed_search_output = os.path.join(app.config['UPLOAD_FOLDER'], "parsed_search_results.json")

            if not hmm_search(hmm_path, query_path, raw_search_output):
                error_message = "Failed to perform HMM search. Please check the HMM profile and query file."
                return render_template('upload_query.html', hmm_path=hmm_path, error=error_message)

            # Step 5: Parse the HMM search results
            parsed_results = parses_result_batch(raw_search_output, query_path)

            # Step 6: Annotate high-confidence matches using BLAST
            blast_success = False
            blast_timeout = False
            for result in parsed_results:
                if result.get("verdict") == "High-confidence match":
                    query_id = result.get("match")
                    sequence = extract_confident_query(query_path, query_id)
                    if sequence:
                        annotation = blast_annotate(sequence)
                        if annotation == "timeout":  # Check if BLAST timed out
                            blast_timeout = True
                            result["blast_annotation"] = {"note": "BLAST timed out. Please try again later."}
                        elif annotation:
                            result["blast_annotation"] = annotation
                            blast_success = True
                        else:
                            result["blast_annotation"] = {"note": "No hit found"}
                    else:
                        result["blast_annotation"] = {"note": "Sequence not found"}

            # Save parsed results with annotations
            try:
                with open(parsed_search_output, "w") as output_file:
                    import json
                    json.dump(parsed_results, output_file, indent=4)
                print(f"Parsed results with annotations saved to: {parsed_search_output}")
            except Exception as e:
                error_message = f"Failed to save parsed results: {e}"
                return render_template('upload_query.html', hmm_path=hmm_path, error=error_message)

            # Step 7: Generate visualizations
            static_dir = os.path.join(app.root_path, "static", "images")
            os.makedirs(static_dir, exist_ok=True)
            hmmer_plot_path = os.path.join(static_dir, "hmmer_scores.png")
            scatter_plot_path = os.path.join(static_dir, "scatter_plot.png")
            plot_hmmer_scores(parsed_results, hmmer_plot_path)

            # Only generate the scatter plot if BLAST annotations were successful
            if blast_success:
                plot_evalue_vs_score(parsed_results, scatter_plot_path)
            else:
                scatter_plot_path = None

            # Step 8: Display the results on a new page
            return render_template(
                'results.html',
                results=parsed_results,
                hmmer_plot="images/hmmer_scores.png",
                scatter_plot="images/scatter_plot.png" if scatter_plot_path else None,
                blast_timeout=blast_timeout  # Pass the timeout flag to the template
            )

        else:
            os.remove(query_path)  # Remove invalid file
            error_message = "Invalid query fasta file. Please upload a properly formatted .fasta file."
            return render_template('upload_query.html', hmm_path=hmm_path, error=error_message)

    error_message = "Invalid file. Please upload a .fasta file."
    return render_template('upload_query.html', hmm_path=hmm_path)

@app.route('/fetch_by_ids', methods=['POST'])
def fetch_by_ids():
    ids_file = request.files.get('ids_file')
    if ids_file and ids_file.filename.endswith('.txt'):
        ids_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(ids_file.filename))
        ids_file.save(ids_path)

        fasta_path = os.path.join(app.config['UPLOAD_FOLDER'], "fetched_sequences.fasta")

        # Step 1: Fetch sequences from UniProt using accession IDs
        get_sequences_ids(ids_path, out_file=fasta_path)

        # Step 2: Validate the fetched fasta file
        if not valid_fasta(fasta_path):
            os.remove(fasta_path)  # Remove invalid file
            error_message = "Fetched fasta file is invalid. Please check the accession IDs file."
            return render_template('fetch_sequences.html', error=error_message)

        # Step 3: Generate MSA file using Clustal Omega
        msa_path = os.path.join(app.config['UPLOAD_FOLDER'], "aligned_sequences.msa")
        if not run_clustalo(fasta_path, msa_path):
            error_message = "Failed to generate MSA file. Please ensure Clustal Omega is installed and accessible."
            return render_template('fetch_sequences.html', error=error_message)

        # Step 4: Build HMM profile using the MSA file
        hmm_path = os.path.join(app.config['UPLOAD_FOLDER'], "profile.hmm")
        if not hmm_build(msa_path, hmm_path):
            error_message = "Failed to build HMM profile. Please check the input MSA file."
            return render_template('fetch_sequences.html', error=error_message)

        # Redirect to upload_query.html for query FASTA upload
        return render_template('upload_query.html', hmm_path=hmm_path)

    error_message = "Invalid file. Please upload a .txt file with accession IDs."
    return render_template('fetch_sequences.html', error=error_message)

@app.route('/fetch_by_family', methods=['POST'])
def fetch_by_family():
    family_name = request.form.get('family_name')
    size = request.form.get('size', 25, type=int)

    # Server-side validation for family name
    if not family_name or not all(c.isalnum() or c in ['_', ' '] for c in family_name):
        error_message = "Invalid family name. Please use only letters, numbers, underscores, and spaces."
        return render_template('fetch_sequences.html', error=error_message)

    # Replace spaces with underscores for file naming
    sanitized_family_name = family_name.replace(" ", "_")
    fasta_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{sanitized_family_name}_sequences.fasta")

    # Step 1: Fetch sequences from UniProt
    get_sequences_family(family_name, size=size, out_file=fasta_path)

    # Step 2: Validate the fetched fasta file
    if not valid_fasta(fasta_path):
        os.remove(fasta_path)  # Remove invalid file
        error_message = "Fetched fasta file is invalid. Please try again with a different family name or size."
        return render_template('fetch_sequences.html', error=error_message)

    # Step 3: Generate MSA file using Clustal Omega
    msa_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{sanitized_family_name}_aligned_sequences.msa")
    if not run_clustalo(fasta_path, msa_path):
        error_message = "Failed to generate MSA file. Please ensure Clustal Omega is installed and accessible."
        return render_template('fetch_sequences.html', error=error_message)

    # Step 4: Build HMM profile using the MSA file
    hmm_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{sanitized_family_name}_profile.hmm")
    if not hmm_build(msa_path, hmm_path):
        error_message = "Failed to build HMM profile. Please check the input MSA file."
        return render_template('fetch_sequences.html', error=error_message)

    # Redirect to upload_query.html for query FASTA upload
    return render_template('upload_query.html', hmm_path=hmm_path)

@app.route('/results', methods=['GET'])
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True)