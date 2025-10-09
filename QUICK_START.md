# Quick Start Guide

## ⚡ 5-Minute Quick Start

### 1. Install Dependencies
```bash
cd any-empty-folder

# Install uv if not already installed
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows:
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Create environment and install dependencies
uv venv --python 3.12 venv_llm_scientific_eval
source venv_llm_scientific_eval/bin/activate  # On Windows: .venv_llm_scientific_eval\Scripts\activate
uv pip install -e .
```

**Alternative (if you prefer pip):**
```bash
pip install -r requirements.txt
```

### 2. Run Initial Analysis (No API needed)
```bash
python run_all_tasks.py --no-api
```

This runs Task 1 (metrics) and Task 2 (sample selection) without any API calls.

Alternatively:

```bash
python task1_quantitative_metrics/compute_metrics.py
```
Then generate visualizations with:
```
python task1_quantitative_metrics/visualize_results.py
```

And perform quantitive analysis with:

```bash
python task2_qualitative_review/select_samples.py
```
---

## 📊 To Generate Improved Abstracts

### 1. Generate New Abstracts
```bash
python task3_improvements/generate_abstracts.py
# Confirm when prompted
```

### 2. Compare Results
```bash
python task3_improvements/compare_results.py
```

### 3. View Comparison
```bash
# Generate comparison visualizations 
python task3_improvements/visualize_comparison.py
```

---

## 🎯 To Run Everything at Once (not tested yet)

```bash
python run_all_tasks.py --all
# Confirm at each step when prompted
```

---

## 🚀 Task 4 Bonus: Advanced Evaluation

### Part A: LLM-as-Judge Evaluation
```bash
# Uses GPT-4o-mini to evaluate abstract quality
python task4_bonus/llm_evaluation.py
```
### Part B: DSPy Automated Optimization
```bash
# Automatically optimizes prompts using DSPy
python task4_bonus/prompt_optimization.py
```

### Or Run Both via Runner (not tested)
```bash
python run_all_tasks.py --task 4
```

---

## 📑 Merge All Reports

After running tasks, merge all markdown reports into one comprehensive document:

```bash
python merge_reports.py
```

This creates `MERGED_REPORT.md` containing:
- Task 1: Quantitative Metrics
- Task 2: Qualitative Review
- Task 3: Comparison of Improvements
- Task 4A: LLM-as-Judge Evaluation (if run)

---

## 🎓 Understanding the Solution

### The Pipeline

```
Original Data → Task 1: Metrics → Task 2: Manual Review
                                          ↓
                                    Identify Issues
                                          ↓
Task 3: Improved Prompt → Generate New Abstracts → Compare
                                          ↓
                            Task 4: Advanced Evaluation
```

### What Each Task Does

- **Task 1:** Computes ROUGE and semantic similarity for baseline (FREE)
- **Task 2:** Manual review of 5 samples to find concrete issues (FREE)
- **Task 3:** Creates better prompt, generates new abstracts, compares new and old ones
- **Task 4A:** LLM-as-judge evaluation with DeepEval
- **Task 4B:** Automated prompt optimization with DSPy

---

## 📞 Need Help?

- **Assignment questions:** Contact thomas.vandongen@springernature.com

---