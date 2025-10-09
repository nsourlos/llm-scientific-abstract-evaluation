"""
Task 1: Compute Quantitative Metrics

This script computes:
1. String-overlap metric: ROUGE scores (ROUGE-1, ROUGE-2, ROUGE-L)
2. Embedding-based metric: Cosine similarity using sentence transformers
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
from src.config import ORIGINAL_DATA, TASK1_DIR, EMBEDDING_MODEL, ROUGE_METRICS
from src.utils import load_data, format_scores_table


def compute_rouge_scores(reference: str, generated: str, metrics: list = None) -> dict:
    """
    Compute ROUGE scores between reference and generated text
    
    Args:
        reference: Reference/ground truth text
        generated: Generated text to evaluate
        metrics: List of ROUGE metrics to compute
    
    Returns:
        Dictionary with ROUGE scores
    """
    if metrics is None:
        metrics = ROUGE_METRICS
    
    scorer = rouge_scorer.RougeScorer(metrics, use_stemmer=True)
    scores = scorer.score(reference, generated)
    
    # Extract F1 scores
    result = {}
    for metric in metrics:
        result[metric] = scores[metric].fmeasure
    
    return result


def compute_embedding_similarity(reference: str, generated: str, model) -> float:
    """
    Compute cosine similarity between embeddings of reference and generated text
    
    Args:
        reference: Reference/ground truth text
        generated: Generated text to evaluate
        model: SentenceTransformer model
    
    Returns:
        Cosine similarity score
    """
    # Encode texts
    ref_embedding = model.encode(reference, convert_to_tensor=True)
    gen_embedding = model.encode(generated, convert_to_tensor=True)
    
    # Compute cosine similarity
    similarity = util.cos_sim(ref_embedding, gen_embedding).item()
    
    return similarity


def compute_all_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all metrics for the entire dataframe
    
    Args:
        df: Dataframe with 'abstract' and 'generated_abstract' columns
    
    Returns:
        Dataframe with additional metric columns
    """
    print("Loading embedding model...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    
    print("Computing metrics for each sample...")
    
    # Initialize lists to store scores
    rouge1_scores = []
    rouge2_scores = []
    rougeL_scores = []
    embedding_scores = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        reference = row['abstract']
        generated = row['generated_abstract']
        
        # Compute ROUGE scores
        rouge_scores = compute_rouge_scores(reference, generated)
        rouge1_scores.append(rouge_scores['rouge1'])
        rouge2_scores.append(rouge_scores['rouge2'])
        rougeL_scores.append(rouge_scores['rougeL'])
        
        # Compute embedding similarity
        emb_score = compute_embedding_similarity(reference, generated, embedding_model)
        embedding_scores.append(emb_score)
    
    # Add scores to dataframe
    df['rouge1'] = rouge1_scores
    df['rouge2'] = rouge2_scores
    df['rougeL'] = rougeL_scores
    df['embedding_similarity'] = embedding_scores
    
    return df


def save_results(df: pd.DataFrame, output_dir: Path):
    """Save results to CSV and generate analysis report"""
    # Save detailed results
    results_file = output_dir / "results_original.csv"
    df[['doi', 'title', 'abstract', 'full_text', 'generated_abstract', 'rouge1', 'rouge2', 'rougeL', 'embedding_similarity']].to_csv(
        results_file, index=False
    )
    
    # Generate summary statistics table
    metrics = ['rouge1', 'rouge2', 'rougeL', 'embedding_similarity']
    summary_table = format_scores_table(df, metrics)
    
    # Create analysis report
    analysis_content = f"""# Task 1: Quantitative Metrics Analysis

## Summary Statistics

{summary_table}

## Interpretation

### String-Overlap Metrics (ROUGE Scores)

**ROUGE-1 (Unigram Overlap):**
- Mean: {df['rouge1'].mean():.4f}
- The ROUGE-1 score measures the overlap of individual words between the reference and generated abstracts.
- This score indicates that the generated abstracts share {df['rouge1'].mean()*100:.1f}% word-level overlap with the original abstracts.

**ROUGE-2 (Bigram Overlap):**
- Mean: {df['rouge2'].mean():.4f}
- ROUGE-2 measures the overlap of two-word sequences, which better captures phrase-level similarity (local coherence).
- The ROUGE-2 score being lower than ROUGE-1 shows that matching exact phrases is more challenging than matching individual words.

**ROUGE-L (Longest Common Subsequence):**
- Mean: {df['rougeL'].mean():.4f}
- ROUGE-L measures the longest common subsequence, which captures sentence-level structure.
- This score reflects the degree to which the generated abstracts preserve the sequential structure of the originals.


**Note:** Additional metrics like BLEU score and Jaccard similarity index could provide complementary perspectives but were not included in this analysis.



### Embedding-Based Metric (Semantic Similarity)

**Cosine Similarity:**
- Mean: {df['embedding_similarity'].mean():.4f}
- This metric uses embeddings from `{EMBEDDING_MODEL}` to measure semantic similarity. We used the implementation from `sentence transformers` library and not from `sklearn` to make the code faster in case GPU is available.
- The cosine similarity score ranges from 0 to 1, where 1 indicates perfect semantic alignment.
- This metric is crucial for scientific abstracts as it measures meaning preservation rather than exact wording.
- The model is one of the best performing models under 1B parameters according to the MTEB leaderboard, balancing quality and efficiency.
- Other strong alternatives include BAAI/bge-small-en-v1.5 (best under 100M parameters) and OpenAI's text-embedding-3-small but it does not disclose parameter count.

## Key Findings

1. **Low ROUGE-1, 2 and L values:**
.......

2. **Embedding similarity vs. ROUGE:**
.....

"""
    
    analysis_file = output_dir / "analysis.md"
    with open(analysis_file, 'w') as f:
        f.write(analysis_content)
    print(f"✓ Analysis report saved to: {analysis_file}")


def main():
    """Main function to compute metrics"""
    print("=" * 60)
    print("TASK 1: QUANTITATIVE METRICS COMPUTATION")
    print("=" * 60)
    
    # Load data
    print(f"\nLoading data from: {ORIGINAL_DATA}")
    df = load_data(ORIGINAL_DATA)
    print(f"✓ Loaded {len(df)} documents")
    
    # Save as Excel for easy viewing
    excel_file = ORIGINAL_DATA.parent / "scientific_documents_and_generations.xlsx"
    print(f"\nSaving original data to Excel: {excel_file}")
    df.to_excel(excel_file, index=False, engine='openpyxl')
    print(f"✓ Excel file saved")
    
    # Compute metrics
    df_with_metrics = compute_all_metrics(df)
    
    # Save results
    save_results(df_with_metrics, TASK1_DIR)
    
    print("\n" + "=" * 60)
    print("✓ Task 1 completed successfully!")
    print("=" * 60)
    
    return df_with_metrics


if __name__ == "__main__":
    main()

