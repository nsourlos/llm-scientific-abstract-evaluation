"""
Task 1: Visualize quantitative metrics results

This script generates comprehensive visualizations for the computed metrics.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.config import TASK1_DIR, EMBEDDING_MODEL

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10


def create_distribution_plots(df: pd.DataFrame, output_dir: Path):
    """Create distribution plots for ROUGE-L and Embedding Similarity"""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # ROUGE-L Distribution
    ax1 = axes[0, 0]
    rouge_mean = df['rougeL'].mean()
    ax1.hist(df['rougeL'], bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    ax1.axvline(rouge_mean, color='red', linestyle='--', linewidth=2, label=f'Mean: {rouge_mean:.3f}')
    ax1.set_xlabel('ROUGE-L Score', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.set_title('Distribution of ROUGE-L Scores', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Embedding Similarity Distribution
    ax2 = axes[0, 1]
    emb_mean = df['embedding_similarity'].mean()
    ax2.hist(df['embedding_similarity'], bins=20, color='lightgreen', edgecolor='black', alpha=0.7)
    ax2.axvline(emb_mean, color='red', linestyle='--', linewidth=2, label=f'Mean: {emb_mean:.3f}')
    ax2.set_xlabel('Embedding Similarity Score', fontsize=12)
    ax2.set_ylabel('Frequency', fontsize=12)
    ax2.set_title('Distribution of Embedding Similarity Scores', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # Box Plot Comparison
    ax3 = axes[1, 0]
    box_data = [df['rougeL'], df['embedding_similarity']]
    bp = ax3.boxplot(box_data, labels=['ROUGE-L', 'Embedding Sim'], patch_artist=True,
                     showmeans=True, meanline=True)
    bp['boxes'][0].set_facecolor('skyblue')
    bp['boxes'][1].set_facecolor('lightgreen')
    ax3.set_ylabel('Score', fontsize=12)
    ax3.set_title('Box Plot Comparison', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Correlation Scatter Plot
    ax4 = axes[1, 1]
    correlation = df['rougeL'].corr(df['embedding_similarity'])
    ax4.scatter(df['rougeL'], df['embedding_similarity'], alpha=0.6, s=100, color='steelblue')
    ax4.set_xlabel('ROUGE-L Score', fontsize=12)
    ax4.set_ylabel('Embedding Similarity Score', fontsize=12)
    ax4.set_title(f'Correlation: ROUGE-L vs Embedding Similarity\nCorrelation: {correlation:.3f}', 
                  fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # Add trend line
    z = np.polyfit(df['rougeL'], df['embedding_similarity'], 1)
    p = np.poly1d(z)
    ax4.plot(df['rougeL'], p(df['rougeL']), "r--", alpha=0.5, linewidth=2)
    
    plt.tight_layout()
    
    # Save
    output_file = output_dir / "metrics_visualization.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved visualization to: {output_file}")
    plt.close()


def create_all_metrics_plot(df: pd.DataFrame, output_dir: Path):
    """Create comprehensive plot with all ROUGE metrics"""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    metrics = ['rouge1', 'rouge2', 'rougeL', 'embedding_similarity']
    titles = ['ROUGE-1 (Unigram)', 'ROUGE-2 (Bigram)', 'ROUGE-L (LCS)', 'Embedding Similarity']
    colors = ['lightcoral', 'lightskyblue', 'lightgreen', 'plum']
    
    for idx, (metric, title, color) in enumerate(zip(metrics, titles, colors)):
        ax = axes[idx // 2, idx % 2]
        mean_val = df[metric].mean()
        
        ax.hist(df[metric], bins=15, color=color, edgecolor='black', alpha=0.7)
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, 
                   label=f'Mean: {mean_val:.3f}')
        ax.set_xlabel(f'{title} Score', fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        ax.set_title(f'Distribution of {title}', fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_file = output_dir / "all_metrics_distribution.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved all metrics plot to: {output_file}")
    plt.close()


def create_summary_statistics_plot(df: pd.DataFrame, output_dir: Path):
    """Create summary statistics visualization"""
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    metrics = ['rouge1', 'rouge2', 'rougeL', 'embedding_similarity']
    metric_names = ['ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'Embedding\nSimilarity']
    
    stats_data = {
        'Mean': [df[m].mean() for m in metrics],
        'Median': [df[m].median() for m in metrics],
        'Std Dev': [df[m].std() for m in metrics]
    }
    
    x = np.arange(len(metrics))
    width = 0.25
    
    bars1 = ax.bar(x - width, stats_data['Mean'], width, label='Mean', 
                   color='steelblue', alpha=0.8)
    bars2 = ax.bar(x, stats_data['Median'], width, label='Median', 
                   color='lightcoral', alpha=0.8)
    bars3 = ax.bar(x + width, stats_data['Std Dev'], width, label='Std Dev', 
                   color='lightgreen', alpha=0.8)
    
    ax.set_xlabel('Metric', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Summary Statistics Across Metrics', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metric_names, fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    output_file = output_dir / "summary_statistics.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved summary statistics to: {output_file}")
    plt.close()


def generate_detailed_interpretation(df: pd.DataFrame, output_dir: Path):
    """Generate detailed interpretation with visualizations"""
    
    metrics = {
        'rouge1': 'ROUGE-1 (Unigram Overlap)',
        'rouge2': 'ROUGE-2 (Bigram Overlap)',
        'rougeL': 'ROUGE-L (Longest Common Subsequence)',
        'embedding_similarity': 'Embedding Similarity (Semantic)'
    }
    
    interpretation = """# Detailed Metrics Interpretation

## Visual Analysis Summary

Based on the generated visualizations, here's a comprehensive interpretation of the results:

---

"""
    
    for metric_key, metric_name in metrics.items():
        mean = df[metric_key].mean()
        median = df[metric_key].median()
        std = df[metric_key].std()
        min_val = df[metric_key].min()
        max_val = df[metric_key].max()
        
        interpretation += f"""## {metric_name}

**Statistics:**
- Mean: {mean:.4f}
- Median: {median:.4f}
- Std Dev: {std:.4f}
- Range: [{min_val:.4f}, {max_val:.4f}]

"""
        
        # Add specific interpretation
        if metric_key == 'rouge1':
            interpretation += f"""**What it measures:**
  ROUGE-1 measures unigram (individual word) overlap between generated and reference abstracts.
  It captures vocabulary similarity at the word level.

**Interpretation:**
  {get_score_interpretation(mean, 'rouge1')}

**Implications:**
  - Higher scores indicate better word choice alignment
  - Sensitive to paraphrasing and word substitutions
  - Good for capturing topic coverage

"""
        
        elif metric_key == 'rouge2':
            interpretation += f"""**What it measures:**
  ROUGE-2 measures bigram (two consecutive words) overlap.
  It captures phrase-level similarity and word order.

**Interpretation:**
  {get_score_interpretation(mean, 'rouge2')}

**Implications:**
  - Stricter than ROUGE-1 (requires matching word pairs)
  - Better captures phrasing and structure
  - More sensitive to variations in expression

"""
        
        elif metric_key == 'rougeL':
            interpretation += f"""**What it measures:**
  ROUGE-L measures longest common subsequence overlap between texts.
  It captures word order and structure similarity.

**Interpretation:**
  {get_score_interpretation(mean, 'rougeL')}

**Implications:**
  - Captures sentence-level structure
  - More robust to insertions and deletions
  - Good indicator of overall similarity

"""
        
        elif metric_key == 'embedding_similarity':
            interpretation += f"""**What it measures:**
  Embedding similarity measures semantic similarity using neural embeddings ({EMBEDDING_MODEL}).
  It captures meaning even with different wording.

**Interpretation:**
  {get_score_interpretation(mean, 'embedding')}

**Implications:**
  - More robust to paraphrasing than ROUGE
  - Captures semantic equivalence
  - Model: `{EMBEDDING_MODEL}`
  - Higher scores indicate better meaning preservation

"""
        
        interpretation += "---\n\n"
    
    # Add correlation analysis
    corr = df['rougeL'].corr(df['embedding_similarity'])
    interpretation += f"""## Correlation Analysis

**ROUGE-L vs Embedding Similarity: {corr:.3f}**

"""
    
    if corr > 0.6:
        interpretation += """✓ **Strong positive correlation** suggests that lexical and semantic similarity align well.
  This indicates that abstracts with similar wording also have similar meaning.

"""
    elif corr > 0.3:
        interpretation += """→ **Moderate positive correlation** suggests partial alignment between lexical and semantic similarity.
  Some abstracts may express similar meaning with different words.

"""
    else:
        interpretation += """⚠ **Weak correlation** suggests lexical and semantic similarity are somewhat independent.
  Generated abstracts may use different words while preserving (or changing) meaning.

"""
    
    # Add distribution insights
    interpretation += f"""## Distribution Insights

### Variability Analysis

**ROUGE-L Standard Deviation: {df['rougeL'].std():.4f}**
{get_variability_interpretation(df['rougeL'].std())}

**Embedding Similarity Standard Deviation: {df['embedding_similarity'].std():.4f}**
{get_variability_interpretation(df['embedding_similarity'].std())}

### Quality Consistency

"""
    
    rouge_cv = df['rougeL'].std() / df['rougeL'].mean()
    emb_cv = df['embedding_similarity'].std() / df['embedding_similarity'].mean()
    
    interpretation += f"""**Coefficient of Variation:**
- ROUGE-L: {rouge_cv:.3f}
- Embedding Similarity: {emb_cv:.3f}

"""
    
    if rouge_cv < 0.3:
        interpretation += "✓ Low variability indicates consistent quality across documents.\n"
    elif rouge_cv < 0.5:
        interpretation += "→ Moderate variability suggests some inconsistency in performance.\n"
    else:
        interpretation += "⚠ High variability indicates significant quality differences across documents.\n"
    
    interpretation += """
---

## Key Findings

"""
    
    # Determine overall assessment
    overall_rouge = df['rougeL'].mean()
    overall_emb = df['embedding_similarity'].mean()
    
    interpretation += f"""### Overall Performance

1. **Lexical Similarity (ROUGE-L): {overall_rouge:.3f}**
   {get_overall_assessment(overall_rouge, 'rouge')}

2. **Semantic Similarity (Embedding): {overall_emb:.3f}**
   {get_overall_assessment(overall_emb, 'embedding')}

### Primary Issues Identified

"""
    
    if overall_rouge < 0.25:
        interpretation += "1. ⚠ **Low lexical overlap** - Generated abstracts use significantly different wording\n"
    if overall_emb < 0.75:
        interpretation += "2. ⚠ **Moderate semantic alignment** - Meaning preservation could be improved\n"
    if df['rouge2'].mean() < 0.15:
        interpretation += "3. ⚠ **Poor phrase-level similarity** - Sentence structure differs substantially\n"
    if df['rougeL'].std() > 0.15:
        interpretation += "4. ⚠ **High variability** - Inconsistent quality across different documents\n"
    
    interpretation += """
### Recommendations for Improvement

Based on the visual and statistical analysis:

1. **Structure Enhancement:**
   - Add explicit structure guidelines to prompt
   - Specify standard abstract format (IMRAD)
   - Include section markers (Background, Methods, Results, Conclusion)

2. **Content Specificity:**
   - Instruct model to preserve key technical terms
   - Request inclusion of specific methodological details
   - Emphasize results and findings

3. **Consistency Improvement:**
   - Provide clearer length constraints
   - Add examples of well-formatted abstracts (few-shot learning)
   - Standardize style and tone requirements

4. **Semantic Alignment:**
   - Add instructions to preserve all key findings
   - Emphasize importance of factual accuracy
   - Request verbatim inclusion of critical results

---

## Files Generated

- `metrics_visualization.png` - Main 4-plot visualization
- `all_metrics_distribution.png` - All metrics distributions
- `summary_statistics.png` - Statistical comparison
- `detailed_interpretation.md` - This file

---

**Generated by:** Task 1 Visualization Script
**Date:** [Auto-generated]
"""
    
    output_file = output_dir / "detailed_interpretation.md"
    with open(output_file, 'w') as f:
        f.write(interpretation)
    
    print(f"✓ Saved detailed interpretation to: {output_file}")


def get_score_interpretation(score: float, metric_type: str) -> str:
    """Get interpretation based on score and metric type"""
    
    if metric_type == 'rouge1':
        if score > 0.4:
            return "✓ **Good vocabulary overlap** - Generated abstracts use similar words as references."
        elif score > 0.25:
            return "→ **Moderate vocabulary overlap** - Some word choices differ from references."
        else:
            return "⚠ **Low vocabulary overlap** - Generated abstracts use substantially different words."
    
    elif metric_type == 'rouge2':
        if score > 0.25:
            return "✓ **Good phrase preservation** - Bigrams are well maintained."
        elif score > 0.15:
            return "→ **Moderate phrase similarity** - Some phrases match, others differ."
        else:
            return "⚠ **Low phrase similarity** - Generated abstracts rephrase substantially."
    
    elif metric_type == 'rougeL':
        if score > 0.35:
            return "✓ **Good structural alignment** - Sentence structure is well preserved."
        elif score > 0.2:
            return "→ **Moderate structural similarity** - Some structural alignment exists."
        else:
            return "⚠ **Low structural similarity** - Significant differences in wording and structure."
    
    elif metric_type == 'embedding':
        if score > 0.85:
            return "✓ **Excellent semantic alignment** - Meaning is very well preserved."
        elif score > 0.75:
            return "✓ **Good semantic similarity** - Core meaning is captured."
        elif score > 0.65:
            return "→ **Moderate semantic alignment** - Some meaning preserved, room for improvement."
        else:
            return "⚠ **Low semantic similarity** - Meaning differs substantially from reference."
    
    return "→ Requires further analysis"


def get_variability_interpretation(std: float) -> str:
    """Interpret standard deviation"""
    if std < 0.1:
        return "✓ **Low variability** - Consistent performance across all documents."
    elif std < 0.15:
        return "→ **Moderate variability** - Some inconsistency in quality."
    else:
        return "⚠ **High variability** - Significant quality differences across documents."


def get_overall_assessment(score: float, metric_type: str) -> str:
    """Get overall assessment"""
    if metric_type == 'rouge':
        if score > 0.3:
            return "   Performance is acceptable but has room for improvement."
        elif score > 0.2:
            return "   Performance is below optimal. Prompt engineering recommended."
        else:
            return "   Performance is poor. Significant improvements needed."
    else:  # embedding
        if score > 0.8:
            return "   Semantic preservation is good."
        elif score > 0.7:
            return "   Semantic preservation is moderate."
        else:
            return "   Semantic preservation needs improvement."


def main():
    """Main function"""
    print("=" * 60)
    print("TASK 1: VISUALIZE RESULTS")
    print("=" * 60)
    
    # Load results
    results_file = TASK1_DIR / "results_original.csv"
    
    if not results_file.exists():
        print("\n❌ Error: Results file not found!")
        print(f"   Expected: {results_file}")
        print("\n   Please run Task 1 first:")
        print("   python task1_quantitative_metrics/compute_metrics.py")
        return
    
    print(f"\nLoading results from: {results_file}")
    df = pd.read_csv(results_file)
    print(f"✓ Loaded {len(df)} documents")
    
    # Create visualizations
    print("\nGenerating visualizations...")
    create_distribution_plots(df, TASK1_DIR)
    create_all_metrics_plot(df, TASK1_DIR)
    create_summary_statistics_plot(df, TASK1_DIR)
    
    # Generate interpretation
    # print("\nGenerating detailed interpretation...")
    # generate_detailed_interpretation(df, TASK1_DIR)
    
    print("\n" + "=" * 60)
    print("✓ Visualization completed successfully!")
    print("=" * 60)
    print(f"\nGenerated files:")
    print(f"  - {TASK1_DIR}/metrics_visualization.png")
    print(f"  - {TASK1_DIR}/all_metrics_distribution.png")
    print(f"  - {TASK1_DIR}/summary_statistics.png")
    # print(f"  - {TASK1_DIR}/detailed_interpretation.md")


if __name__ == "__main__":
    main()