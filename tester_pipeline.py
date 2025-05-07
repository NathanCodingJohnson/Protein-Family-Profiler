"""
tester_pipeline.py -
    Testing script for the full backend pipeline.
"""

from modules.main_pipeline import run_pipeline

# Step 1: Selecting training sequence input mode
# Options are 'family', 'ids', 'user_fasta'
input_mode = "family"

# Step 2: Providing input based on selected mode
if input_mode == "family":
    input_data = "Protein Kinase"  # Example family name from UniProt
elif input_mode == "ids":
    input_data = "test_data/ids.txt"  # Example file with UniProt accession IDs
elif input_mode == "user_fasta":
    input_data = "test_data/train_sequences.fasta"  # Local training FASTA path
else:
    raise ValueError("Invalid input mode. Choose 'family', 'ids', or 'user_fasta'.")

# Step 3: Provide path to query fasta file
query_fasta = "test_data/queries.fasta"  # Your multi-sequence user query file

# Step 4: Running the full backend pipeline
results = run_pipeline(
    input_mode=input_mode,
    input_data=input_data,
    query_fasta=query_fasta
)

# Step 5: Printing final annotated results
print("\nFinal Annotated Results:\n")
for res in results:
    print(f"Query: {res.get('query')}")
    print(f"  Verdict: {res.get('verdict')}")
    if "blast_annotation" in res:
        annotation = res["blast_annotation"]
        if annotation and "hit_id" in annotation:
            print(f"  BLAST Hit: {annotation.get('description')}")
            print(f"  BLAST Score: {annotation.get('score')}")
        else:
            print(f"  Note: {annotation.get('note')}")
    print("-" * 50)
