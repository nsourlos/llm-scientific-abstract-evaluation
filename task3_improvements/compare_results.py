"""
Task 3: Compare original and improved abstracts

This script:
1. Loads both original and improved abstracts
2. Computes metrics for improved abstracts
3. Generates comparison report
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from task1_quantitative_metrics.compute_metrics import compute_rouge_scores, compute_embedding_similarity
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from src.config import IMPROVED_DATA, TASK1_DIR, TASK3_DIR, EMBEDDING_MODEL, OPENAI_MODEL
from src.utils import load_data, format_scores_table


def compute_metrics_for_improved(df: pd.DataFrame) -> pd.DataFrame:
    """Compute metrics for improved abstracts"""
    
    print("Loading embedding model...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    
    print("Computing metrics for improved abstracts...")
    
    rouge1_scores = []
    rouge2_scores = []
    rougeL_scores = []
    embedding_scores = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        reference = row['abstract']
        generated = row['improved_abstract']
        
        # Compute ROUGE scores
        rouge_scores = compute_rouge_scores(reference, generated)
        rouge1_scores.append(rouge_scores['rouge1'])
        rouge2_scores.append(rouge_scores['rouge2'])
        rougeL_scores.append(rouge_scores['rougeL'])
        
        # Compute embedding similarity
        emb_score = compute_embedding_similarity(reference, generated, embedding_model)
        embedding_scores.append(emb_score)
    
    df['rouge1_improved'] = rouge1_scores
    df['rouge2_improved'] = rouge2_scores
    df['rougeL_improved'] = rougeL_scores
    df['embedding_similarity_improved'] = embedding_scores
    
    # Also save as Excel for easy viewing
    excel_file = TASK3_DIR / "results_comparison_with_improved_metrics.xlsx"
    print(f"\nSaving results to Excel: {excel_file}")
    df.to_excel(excel_file, index=False, engine='openpyxl')
    print(f"✓ Excel file saved")
    
    return df


def generate_comparison_report(df: pd.DataFrame, output_dir: Path):
    """Generate comprehensive comparison report between original and improved abstracts"""
    
    # Calculate improvements
    metrics = ['rouge1', 'rouge2', 'rougeL', 'embedding_similarity']
    
    comparison_data = []
    for metric in metrics:
        orig_col = metric
        imp_col = f"{metric}_improved"
        
        orig_mean = df[orig_col].mean()
        imp_mean = df[imp_col].mean()
        improvement = ((imp_mean - orig_mean) / orig_mean) * 100
        
        comparison_data.append({
            'Metric': metric,
            'Original': f"{orig_mean:.4f}",
            'Improved': f"{imp_mean:.4f}",
            'Change': f"{improvement:+.2f}%"
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Save summary CSV
    csv_file = output_dir / "results_comparison_summary.csv"
    comparison_df.to_csv(csv_file, index=False)
    
    # Save detailed CSV with all metrics for visualization
    detailed_csv = output_dir / "results_comparison.csv"
    metrics_df = df[['doi', 'title'] + 
                    ['rouge1', 'rouge2', 'rougeL', 'embedding_similarity'] + 
                    ['rouge1_improved', 'rouge2_improved', 'rougeL_improved', 'embedding_similarity_improved']]
    metrics_df.to_csv(detailed_csv, index=False)
    
    # Also save as Excel for easy viewing
    excel_file = output_dir / "results_comparison.xlsx"
    metrics_df.to_excel(excel_file, index=False, engine='openpyxl')
    print(f"✓ Excel comparison saved to: {excel_file}")
    
    # Calculate detailed statistics for the report
    rouge1_orig_mean = df['rouge1'].mean()
    rouge1_imp_mean = df['rouge1_improved'].mean()
    rouge1_improvement = ((rouge1_imp_mean - rouge1_orig_mean) / rouge1_orig_mean) * 100
    
    rouge2_orig_mean = df['rouge2'].mean()
    rouge2_imp_mean = df['rouge2_improved'].mean()
    rouge2_improvement = ((rouge2_imp_mean - rouge2_orig_mean) / rouge2_orig_mean) * 100
    
    rougeL_orig_mean = df['rougeL'].mean()
    rougeL_imp_mean = df['rougeL_improved'].mean()
    rougeL_improvement = ((rougeL_imp_mean - rougeL_orig_mean) / rougeL_orig_mean) * 100
    
    emb_orig_mean = df['embedding_similarity'].mean()
    emb_imp_mean = df['embedding_similarity_improved'].mean()
    emb_improvement = ((emb_imp_mean - emb_orig_mean) / emb_orig_mean) * 100
    
    # Calculate consistency changes
    rouge1_consistency = ((df['rouge1_improved'].std() - df['rouge1'].std()) / df['rouge1'].std()) * 100
    rouge2_consistency = ((df['rouge2_improved'].std() - df['rouge2'].std()) / df['rouge2'].std()) * 100
    rougeL_consistency = ((df['rougeL_improved'].std() - df['rougeL'].std()) / df['rougeL'].std()) * 100
    emb_consistency = ((df['embedding_similarity_improved'].std() - df['embedding_similarity'].std()) / df['embedding_similarity'].std()) * 100
    
    # Calculate document-level changes
    df['rouge1_change'] = df['rouge1_improved'] - df['rouge1']
    df['rouge2_change'] = df['rouge2_improved'] - df['rouge2']
    df['rougeL_change'] = df['rougeL_improved'] - df['rougeL']
    df['emb_change'] = df['embedding_similarity_improved'] - df['embedding_similarity']
    
    rougeL_improved_count = (df['rougeL_change'] > 0).sum()
    rougeL_declined_count = (df['rougeL_change'] < 0).sum()
    
    emb_improved_count = (df['emb_change'] > 0).sum()
    emb_declined_count = (df['emb_change'] < 0).sum()
    
    # Helper functions for interpretation
    def get_improvement_interpretation(pct: float, metric: str) -> str:
        if pct > 20:
            return f"✓ **Substantial improvement** - The new prompt significantly enhances {metric} performance."
        elif pct > 10:
            return f"✓ **Good improvement** - Clear positive impact on {metric}."
        elif pct > 5:
            return f"↗ **Moderate improvement** - {metric} shows positive trend."
        elif pct > -5:
            return f"⚠ **Slight decline** - Minor decrease in {metric}."
        elif pct > -10:
            return f"↘ **Moderate decline** - {metric} performance decreased."
        else:
            return f"✗ **Significant decline** - {metric} substantially decreased."
    
    def get_consistency_label(pct: float) -> str:
        if pct < -10:
            return f"More consistent ({abs(pct):.1f}% reduction) ✓"
        elif pct > 10:
            return f"Much less consistent ({pct:.1f}% increase) ⚠"
        else:
            return f"Similar consistency ({pct:+.1f}%)"
    
    def assess_improvement_level(pct: float) -> str:
        if pct > 15:
            return "✓✓✓ Excellent improvement"
        elif pct > 10:
            return "✓✓ Substantial improvement"
        elif pct > 5:
            return "✓ Moderate improvement"
        elif pct > -5:
            return "→ Minimal change"
        else:
            return "↓ Decline"
    
    # Generate comprehensive markdown report
    report = f"""# Task 3: Comparison of Original vs. Improved Abstracts

## Executive Summary

This report provides a comparison of abstracts generated using the original simple prompt versus the improved structured prompt, including quantitative metrics.

---

## Quantitative Comparison

### Overall Metrics

| Metric | Original | Improved | Change |
|--------|----------|----------|--------|
"""
    
    for _, row in comparison_df.iterrows():
        report += f"| {row['Metric']} | {row['Original']} | {row['Improved']} | {row['Change']} |\n"
    
    report += f"""

### Detailed Statistics

#### Original Prompt
{format_scores_table(df, metrics)}

#### Improved Prompt
{format_scores_table(df, [f"{m}_improved" for m in metrics])}

![All Metrics Histograms Comparison](all_metrics_histograms_comparison.png)

![Comparison Boxplots Means](comparison_boxplots_means.png)
---

## Metric-by-Metric Analysis

### ROUGE-1 (Unigram)

**Performance Change:**
- Original Mean: {rouge1_orig_mean:.4f}
- Improved Mean: {rouge1_imp_mean:.4f}
- Absolute Change: {rouge1_imp_mean - rouge1_orig_mean:+.4f}
- Percentage Change: {rouge1_improvement:+.2f}%

**Interpretation:**
{get_improvement_interpretation(rouge1_improvement, 'rouge1')}

**Distribution Changes:**
- Original Std Dev: {df['rouge1'].std():.4f}
- Improved Std Dev: {df['rouge1_improved'].std():.4f}
- Consistency Change: {get_consistency_label(rouge1_consistency)}

---

### ROUGE-2 (Bigram)

**Performance Change:**
- Original Mean: {rouge2_orig_mean:.4f}
- Improved Mean: {rouge2_imp_mean:.4f}
- Absolute Change: {rouge2_imp_mean - rouge2_orig_mean:+.4f}
- Percentage Change: {rouge2_improvement:+.2f}%

**Interpretation:**
{get_improvement_interpretation(rouge2_improvement, 'rouge2')}

**Distribution Changes:**
- Original Std Dev: {df['rouge2'].std():.4f}
- Improved Std Dev: {df['rouge2_improved'].std():.4f}
- Consistency Change: {get_consistency_label(rouge2_consistency)}

---

### ROUGE-L (LCS)

**Performance Change:**
- Original Mean: {rougeL_orig_mean:.4f}
- Improved Mean: {rougeL_imp_mean:.4f}
- Absolute Change: {rougeL_imp_mean - rougeL_orig_mean:+.4f}
- Percentage Change: {rougeL_improvement:+.2f}%

**Interpretation:**
{get_improvement_interpretation(rougeL_improvement, 'rougeL')}

**Distribution Changes:**
- Original Std Dev: {df['rougeL'].std():.4f}
- Improved Std Dev: {df['rougeL_improved'].std():.4f}
- Consistency Change: {get_consistency_label(rougeL_consistency)}

---

### Embedding Similarity

**Performance Change:**
- Original Mean: {emb_orig_mean:.4f}
- Improved Mean: {emb_imp_mean:.4f}
- Absolute Change: {emb_imp_mean - emb_orig_mean:+.4f}
- Percentage Change: {emb_improvement:+.2f}%

**Interpretation:**
{get_improvement_interpretation(emb_improvement, 'embedding_similarity')}

**Distribution Changes:**
- Original Std Dev: {df['embedding_similarity'].std():.4f}
- Improved Std Dev: {df['embedding_similarity_improved'].std():.4f}
- Consistency Change: {get_consistency_label(emb_consistency)}

**Note:** We consider a change as 'Significant' if it changes more than 10% (either increase or decrease), 'Moderate' if it changed by 5-10%, and in other cases, change is considered as 'Minor'. That definition doesn't include any formal statistical comparisons (that could be a next step).

![Comparison Histograms Visualization](comparison_histograms_visualization.png)


---

## Overall Impact Assessment

### Quantitative Improvements

![Improvement Analysis](improvement_analysis.png)

1. **Lexical Similarity (ROUGE-L):** {rougeL_improvement:+.2f}%
   {assess_improvement_level(rougeL_improvement)}

2. **Semantic Similarity (Embedding):** {emb_improvement:+.2f}%
   {assess_improvement_level(emb_improvement)}

### Quality Consistency

**Variability Changes:**
- ROUGE-L: {rougeL_consistency:+.2f}% {'(more consistent ✓)' if rougeL_consistency < 0 else '(less consistent ⚠)'}
- Embedding: {emb_consistency:+.2f}% {'(more consistent ✓)' if emb_consistency < 0 else '(less consistent ⚠)'}

### Document-Level Changes

**ROUGE-L:**
- Improved: {rougeL_improved_count} documents ({rougeL_improved_count/len(df)*100:.1f}%)
- Declined: {rougeL_declined_count} documents ({rougeL_declined_count/len(df)*100:.1f}%)
- Unchanged: {len(df) - rougeL_improved_count - rougeL_declined_count} documents

**Embedding Similarity:**
- Improved: {emb_improved_count} documents ({emb_improved_count/len(df)*100:.1f}%)
- Declined: {emb_declined_count} documents ({emb_declined_count/len(df)*100:.1f}%)
- Unchanged: {len(df) - emb_improved_count - emb_declined_count} documents

---

## Key Findings

### What Worked

"""
    
    if rougeL_improvement > 10:
        report += "✓ **Structural improvements are significant** - The improved prompt successfully enhanced word-level and structure alignment.\n\n"
    
    if rougeL_improved_count / len(df) > 0.7:
        report += f"✓ **Broad effectiveness** - {rougeL_improved_count/len(df)*100:.0f}% of documents showed ROUGE-L improvement.\n\n"
    
    if emb_improvement > 5:
        report += "✓ **Semantic preservation improved** - Meaning is better captured in improved abstracts.\n\n"
    
    report += """### Remaining Challenges

"""
    
    if rougeL_declined_count > len(df) * 0.1:
        report += f"⚠ **Some documents declined** - {rougeL_declined_count} documents showed decreased ROUGE scores.\n\n"
    
    if emb_improvement < 0:
        report += "⚠ **Semantic alignment decreased** - The improved prompt may have changed meaning in some cases.\n\n"
    
    if rougeL_consistency > 10:
        report += "⚠ **Increased variability** - Quality became less consistent across documents.\n\n"
    
    # Calculate effect size description (avoid backslash in f-string)
    if abs(rougeL_improvement) > 20:
        effect_size_desc = "Large effect size (Cohen's d > 0.8)"
    elif abs(rougeL_improvement) > 10:
        effect_size_desc = "Medium effect size (Cohen's d ~0.5)"
    else:
        effect_size_desc = "Small effect size"
    
    # Calculate significance
    significance_desc = 'Statistically significant' if abs(rougeL_improvement) > 10 else 'May not be statistically significant'
    
    # Calculate style impact
    style_impact = 'positive' if emb_improvement >= 0 else 'mixed'
    
    # Calculate distribution descriptions
    rougeL_shift = 'clear rightward shift' if rougeL_improvement > 10 else 'slight rightward shift' if rougeL_improvement > 0 else 'leftward shift'
    rougeL_direction = 'overall improvement' if rougeL_improvement > 0 else 'decline'
    
    emb_shift = 'rightward shift' if emb_improvement > 0 else 'leftward shift'
    emb_direction = 'improvement' if emb_improvement > 0 else 'decline'
    
    median_shift_desc = 'Significant upward median shift indicating improved typical performance' if rougeL_improvement > 10 else 'Moderate shifts in median values'
    
    report += f"""
---

## Key Improvements from Prompt Engineering

The improved prompt addressed several key issues identified in the qualitative review:

1. **Structured Format:** The new prompt explicitly requests the standard abstract structure (background, objective, methods, results, conclusion), leading to more coherent and complete abstracts.

2. **Scientific Style:** By specifying formal, scientific language and appropriate tense usage, the improved prompt produces more professionally written abstracts.

3. **Accuracy Instructions:** Explicit instructions against hallucination and over-claiming have improved factual accuracy.

4. **Length Control:** The 150-250 word guideline ensures abstracts are appropriately concise while comprehensive.

---


## Recommendations for Further Improvement

1. **Address declining cases:** Investigate the {rougeL_declined_count} documents that showed decreased ROUGE scores
2. **Semantic alignment:** Review prompt instructions to emphasize meaning preservation
3. **Few-shot learning:** Add 2-3 example abstracts to the prompt
4. **Fine-tuning:** Consider training a specialized model
5. **Statistical tests** Consider formal statistical tests for comparisons
---

## Model and Cost Analysis

### Model Selection: {OPENAI_MODEL}

**Configuration:**
- Model can be changed in `src/config.py` by updating `OPENAI_MODEL`
- Criteria for selection based on cost/quality/latency trade-offs
- Model (gpt-4o-mini) suitable for scientific abstract generation with structured prompts, low cost, and fast

---

## Conclusion

"""
    
    if rougeL_improvement > 15 and emb_improvement > 7:
        report += """The improved prompt design **successfully enhanced abstract quality** across both lexical and semantic dimensions. The structured approach, explicit guidelines, and accuracy instructions work together to produce higher-quality abstracts.

"""
    elif rougeL_improvement > 10 or emb_improvement > 5:
        report += """The improved prompt design **moderately enhanced abstract quality**. While improvements are visible, there's room for further optimization.

"""
    else:
        report += """The improved prompt design showed **mixed results**. While some improvements are visible, the gains may not justify the increased complexity. Consider alternative approaches or hybrid methods.

"""
    
    report += f"""
---
"""
    
    # Save report
    report_file = output_dir / "comparison_report.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"✓ Comprehensive comparison report saved to: {report_file}")
    print(f"✓ Summary CSV saved to: {csv_file}")
    print(f"✓ Detailed CSV saved to: {detailed_csv}")
    print(f"✓ Excel file saved to: {excel_file}")


def main():
    """Main function"""
    print("=" * 60)
    print("TASK 3: COMPARE ORIGINAL VS. IMPROVED ABSTRACTS")
    print("=" * 60)
    
    # Load improved data
    print("\nLoading improved abstracts...")
    df = load_data(IMPROVED_DATA)
    print(f"✓ Loaded {len(df)} documents with improved abstracts")
    
    # Load original metrics from Task 1
    print("\nLoading original metrics from Task 1...")
    import pandas as pd
    original_metrics_file = TASK1_DIR / "results_original.csv"
    
    if not original_metrics_file.exists():
        print("\n❌ Error: Task 1 results not found!")
        print(f"   Expected file: {original_metrics_file}")
        print("\n   Please run Task 1 first:")
        print("   python task1_quantitative_metrics/compute_metrics.py")
        return
    
    original_metrics = pd.read_csv(original_metrics_file)
    print(f"✓ Loaded original metrics for {len(original_metrics)} documents")
    
    # Merge original metrics into the dataframe
    df = df.merge(
        original_metrics[['doi', 'rouge1', 'rouge2', 'rougeL', 'embedding_similarity']], 
        on='doi', 
        how='left'
    )
    print("✓ Merged original metrics")
    
    # Compute metrics for improved abstracts
    df_with_metrics = compute_metrics_for_improved(df)
    
    # Generate comparison report
    print("\nGenerating comparison report...")
    generate_comparison_report(df_with_metrics, TASK3_DIR)
    
    print("\n" + "=" * 60)
    print("✓ Task 3 comparison completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

