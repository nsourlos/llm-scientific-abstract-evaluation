"""
Merge Reports Script

This script merges all generated markdown reports into one comprehensive document.
It also fixes relative image paths to ensure they work from the root directory.

Usage:
    python merge_reports.py
"""

import sys
import re
from pathlib import Path
from datetime import datetime

# Define paths to all report files
REPORTS = {
    "Task 1: Quantitative Metrics": "task1_quantitative_metrics/analysis.md",
    "Task 2: Qualitative Review": "task2_qualitative_review/qualitative_report.md",
    "Task 3: Comparison of Improvements": "task3_improvements/comparison_report.md",
    "Task 4A: LLM-as-Judge Evaluation": "task4_bonus/llm_evaluation_report.md",
    # "Task 4B: DSPy Prompt Optimization": "task4_bonus/dspy_optimization_report.md",
}

OUTPUT_FILE = "FINAL_REPORT.md"


def read_report(filepath: Path) -> str:
    """Read a report file if it exists"""
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def fix_image_paths(content: str, source_dir: str) -> tuple[str, int]:
    """
    Fix relative image paths in markdown content.
    
    Converts:
        ![alt text](image.png) -> ![alt text](task1_quantitative_metrics/image.png)
        ![alt text](./image.png) -> ![alt text](task1_quantitative_metrics/image.png)
    
    Args:
        content: The markdown content
        source_dir: The directory where the original markdown file is located
        
    Returns:
        Tuple of (content with fixed image paths, number of paths fixed)
    """
    # Pattern to match markdown images: ![alt text](path)
    # Captures: ![...](path)
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    fixes_count = 0
    
    def replace_path(match):
        nonlocal fixes_count
        alt_text = match.group(1)
        img_path = match.group(2)
        
        # Don't modify absolute URLs (http:// or https://)
        if img_path.startswith(('http://', 'https://', '/')):
            return match.group(0)  # Return original
        
        # Remove leading ./ if present
        img_path = img_path.lstrip('./')
        
        # Prepend the source directory
        new_path = f"{source_dir}/{img_path}"
        fixes_count += 1
        
        return f"![{alt_text}]({new_path})"
    
    # Replace all image references
    fixed_content = re.sub(image_pattern, replace_path, content)
    
    return fixed_content, fixes_count


def merge_reports():
    """Merge all available reports into one comprehensive document"""
    
    print("=" * 60)
    print("MERGING ALL REPORTS")
    print("=" * 60)
    
    # Start building the merged report
    #**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    merged_content = f"""# Comprehensive Evaluation Report
## LLM-Generated Scientific Abstracts

## Table of Contents

"""
    
    # Check which reports exist and build TOC
    available_reports = {}
    report_directories = {}  # Store directory for each report
    toc_entries = []
    total_image_fixes = 0
    
    for task_name, filepath in REPORTS.items():
        report_path = Path(filepath)
        content = read_report(report_path)
        if content:
            # Get the directory path (e.g., "task1_quantitative_metrics")
            source_dir = str(report_path.parent)
            
            # Fix image paths in the content
            content, fixes_count = fix_image_paths(content, source_dir)
            total_image_fixes += fixes_count
            
            available_reports[task_name] = content
            report_directories[task_name] = source_dir
            
            # Create TOC entry
            toc_id = task_name.lower().replace(" ", "-").replace(":", "")
            toc_entries.append(f"- [{task_name}](#{toc_id})")
            
            if fixes_count > 0:
                print(f"✓ Found: {filepath} ({fixes_count} image path(s) fixed)")
            else:
                print(f"✓ Found: {filepath}")
        else:
            print(f"⚠ Skipped: {filepath} (not found)")
    
    # Add TOC
    merged_content += "\n".join(toc_entries)
    merged_content += "\n\n---\n\n"
    
    # Add each report
    for task_name, content in available_reports.items():
        merged_content += f"# {task_name}\n\n"
        
        # Remove the first header from content if it exists (avoid duplicate headers)
        lines = content.split('\n')
        if lines and lines[0].startswith('#'):
            # Skip the first line (the title)
            content = '\n'.join(lines[1:])
        
        merged_content += content
        merged_content += "\n\n" + "\n\n"
    
    # Add footer
    merged_content += f"""---



---

## Design Choices & Technical Decisions

### 1. Metric Selection

**ROUGE Scores (String Overlap)**
- **Rationale:** Industry-standard for text generation evaluation
- **Coverage:** ROUGE-1 (unigrams), ROUGE-2 (bigrams), ROUGE-L (longest common subsequence)
- **Advantages:** Fast, deterministic, interpretable
- **Limitations:** Doesn't capture semantic meaning

**Embedding Similarity (Semantic)**
- **Model:** Configured in `src/config.py` (supports HuggingFace models)
- **Rationale:** Captures semantic similarity beyond exact word matching
- **Advantages:** Robust to paraphrasing, domain-aware embeddings available
- **Limitations:** Computationally expensive, requires model download

### 2. Model Selection for Generation

**Primary Model:** Configured via `OPENAI_MODEL` in `src/config.py`
- **Current Default:** GPT-4o-mini
- **Rationale:** Best cost/performance/latency balance
- **Alternatives:** GPT-4o, GPT-5-nano, GPT-5-mini

**Design Philosophy:**
- Configuration-driven (easy to change models)
- Cost-conscious (default to cheap models)

### 3. Evaluation Framework

**Multi-Level Approach:**
1. **Quantitative (Task 1):** Automated metrics for all documents
2. **Qualitative (Task 2):** Manual review of 5 representative samples
3. **Comparative (Task 3):** Before/after analysis with improved prompts
4. **Advanced (Task 4):** LLM-as-judge and automated optimization

**Rationale:**
- Quantitative metrics alone miss nuanced quality issues
- Manual review provides actionable insights
- Comparison shows real-world improvement impact

### 4. Prompt Engineering Strategy

**Structured Approach:**
- Explicit format requirements (background, methods, results, conclusion)
- Length constraints (150-250 words)
- Scientific style guidelines
- Anti-hallucination instructions

**Iteration Process:**
1. Baseline metrics (Task 1)
2. Manual failure analysis (Task 2)
3. Targeted improvements (Task 3)
4. Validation and refinement (Task 4)

---

## Next Steps & Recommendations

**1. Address Edge Cases**
- Investigate the 3 documents with declining ROUGE-L scores
- Analyze failure modes for low-performing abstracts
- Create document-type-specific prompts if needed

**2. Expand Test Coverage**
- Run evaluation on larger dataset (100+ documents)
- Test across different scientific domains
- Validate with expert reviewers

**3. Cost Optimization**
- Benchmark alternative models
- Consider batch processing for efficiency

**4. Prompt Enhancement**
- **Few-shot Learning:** Add 2-3 high-quality examples to the prompt
- **Domain Adaptation:** Create field-specific prompts (medical, CS, physics)
- **Style Templates:** Provide structural templates for consistency

**5. Automation**
- Set up continuous evaluation pipeline
- Automated alerts for quality assements

**6. Advanced Techniques**
- **Retrieval-Augmented Generation (RAG):** Use source paper as context

**7. Specialized Fine-tuning**
- Fine-tune on domain-specific scientific abstracts
- Create field-specific models (biomedical, CS, physics)

---

## Report Information

**Reports Merged:** {len(available_reports)} of {len(REPORTS)}

**Available Tasks:**
"""
    
    for task_name in available_reports.keys():
        merged_content += f"- ✓ {task_name}\n"
    
    for task_name, filepath in REPORTS.items():
        if task_name not in available_reports:
            merged_content += f"- ✗ {task_name} (not run)\n"
    
    merged_content += f"""
**Generated by:** `merge_reports.py`
---
"""
    
    # Write the merged report
    output_path = Path(OUTPUT_FILE)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(merged_content)
    
    print(f"\n✓ Merged report saved to: {output_path}")
    print(f"  Total reports merged: {len(available_reports)}")
    print(f"  Total size: {len(merged_content):,} characters")
    if total_image_fixes > 0:
        print(f"  Image paths fixed: {total_image_fixes}")
    
    print("\n" + "=" * 60)
    print("MERGE COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nView the report: {OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        merge_reports()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

