"""
Task 2: Select samples for qualitative review
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from src.config import TASK1_DIR, TASK2_DIR
from src.utils import get_sample_indices


def select_and_export_samples(n_samples: int = 5) -> pd.DataFrame:
    """
    Select diverse samples for qualitative review
    
    Args:
        n_samples: Number of samples to select
    
    Returns:
        DataFrame with selected samples
    """
    # Load results from Task 1
    results_file = TASK1_DIR / "results_original.csv"
    df = pd.read_csv(results_file)
    
    # Load full data for abstracts
    from src.config import ORIGINAL_DATA
    from src.utils import load_data
    full_df = load_data(ORIGINAL_DATA)
    
    # Merge metrics with full data
    df_full = full_df.merge(df[['doi', 'rouge1', 'rouge2', 'rougeL', 'embedding_similarity']], 
                            on='doi', how='left')

    # Select diverse samples
    indices = get_sample_indices(df_full, n_samples=n_samples, strategy="diverse")
    
    selected = df_full.loc[indices]
    
    # Save selected samples for reference
    output_file = TASK2_DIR / "selected_samples.csv"
    selected[['doi', 'title', 'abstract', 'full_text', 'generated_abstract', 'rouge1', 'rouge2', 'rougeL', 'embedding_similarity']].to_csv(
        output_file, index=False
    )
    
    print(f"✓ Selected {len(selected)} samples for qualitative review")
    print(f"✓ Saved to: {output_file}")
    
    # Print summary
    print("\nSelected Samples:")
    for idx, row in selected.iterrows():
        print(f"\n{idx}. {row['title'][:60]}...")
        print(f"   ROUGE-1: {row['rouge1']:.3f}, Embedding: {row['embedding_similarity']:.3f}")
    
    return selected


def generate_qualitative_report_template(selected: pd.DataFrame):
    """Generate a template for qualitative review"""
    
    report = """# Task 2: Qualitative Review Report

## Methodology

This qualitative review analyzes 5 carefully selected examples from the dataset, chosen to represent diverse quality levels based on ROUGE-1 scores. 
We chose samples from the 10th, 30th, 50th, 70th, and 90th percentiles of ROUGE-1 scores  to ensure that we cover low, average and high values of it. 
That way, we get diverse samples from different quality levels.
For each example, we evaluate based on anstracts:

1. **Clarity & Coherence:** Is the abstract readable, well-structured, and logically organized?
2. **Factuality:** Does the abstract accurately represent the scientific document without hallucinations?
3. **Safety/Ethics:** Are there any over-claiming, misleading statements, or ethical concerns?
4. **Failure Modes:** What specific issues exist compared to the reference abstract?
5. **Improvement Opportunities:** What concrete changes would enhance quality?

---

"""
    
    for idx, (i, row) in enumerate(selected.iterrows(), 1):
        report += f"""## Example {idx}: {row['title']}

**Metrics:**
- ROUGE-1: {row['rouge1']:.3f}
- ROUGE-2: {row['rouge2']:.3f}
- ROUGE-L: {row['rougeL']:.3f}
- Embedding Similarity: {row['embedding_similarity']:.3f}

### Reference Abstract
```
{row['abstract']}
```

### Generated Abstract
```
{row['generated_abstract']}
```

### Analysis

#### Clarity, Coherence & Factuality
[Analysis to be added after manual review]

#### Safety/Ethics
[Analysis to be added after manual review]

#### Failure Modes
[Analysis to be added after manual review]

#### Specific Improvements
[Analysis to be added after manual review]

---

"""
    
    report += """## Overall Findings

### Common Patterns Across Samples

1. **Strengths:**
   - [To be filled after review]

2. **Weaknesses:**
   - [To be filled after review]

3. **Critical Issues:**
   - [To be filled after review]

### Key Improvement Recommendations

Based on the above, the following improvements should be implemented:

1. **[Improvement 1]:** [Description]
2. **[Improvement 2]:** [Description]
3. **[Improvement 3]:** [Description]
"""
    
    output_file = TASK2_DIR / "qualitative_report_template.md"
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\n✓ Qualitative report template saved to: {output_file}")
    
    return report


def main():
    """Main function"""
    print("=" * 60)
    print("TASK 2: QUALITATIVE REVIEW - SAMPLE SELECTION")
    print("=" * 60)
    
    selected = select_and_export_samples(n_samples=5)
    generate_qualitative_report_template(selected)
    
    print("\n" + "=" * 60)
    print("✓ Task 2 sample selection completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()