# LLM Scientific Abstract Evaluation

> A comprehensive framework for evaluating and improving LLM-generated scientific abstracts using ROUGE metrics, semantic embeddings, and LLM-as-judge techniques.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Results](#results)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Tasks Overview](#tasks-overview)
- [Metrics & Evaluation](#metrics--evaluation)
- [Configuration](#configuration)
- [Cost Analysis](#cost-analysis)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This project provides a **multi-level evaluation framework** for assessing and improving the quality of LLM-generated scientific abstracts. It combines:

- **Quantitative metrics** (ROUGE scores, semantic similarity)
- **Qualitative review** (manual assessment of samples)
- **Comparative analysis** (before/after prompt improvements)
- **Advanced evaluation** (LLM-as-judge with DeepEval, automated optimization with DSPy)

> **Note:** For comprehensive results and analysis, see [FINAL_REPORT.md](FINAL_REPORT.md)

---

## ✨ Key Features

### 📊 Comprehensive Evaluation
- **ROUGE Metrics:** String-overlap evaluation (ROUGE-1, ROUGE-2, ROUGE-L)
- **Semantic Similarity:** Embedding-based similarity using state-of-the-art models
- **LLM-as-Judge:** Advanced evaluation with DeepEval (coherence, accuracy, faithfulness, relevancy)
- **Manual Review:** Structured qualitative assessment framework

### 🤖 Advanced Techniques
- **DeepEval Integration:** G-Eval, Faithfulness, Answer Relevancy, Hallucination, Summarization metrics
- **DSPy Optimization:** Automated prompt refinement using BootstrapFewShot
- **Visualizations:** Comprehensive plots for all metrics

---

## 📁 Repository Structure

```
llm-scientific-abstract-evaluation/
├── data/                           # Dataset and generated outputs
│   ├── prompt.txt                  # Original prompt
│   └── scientific_documents_and_generations.pkl
│
├── src/                            # Core utilities
│   ├── config.py                   # Centralized configuration
│   ├── utils.py                    # Shared helper functions
│   └── cost_estimator.py           # API cost estimation
│
├── task1_quantitative_metrics/     # Quantitative evaluation
│   ├── compute_metrics.py          # ROUGE & embedding metrics
│   ├── visualize_results.py        # Generate visualizations
│   ├── analysis.md                 # Results report
│   └── *.png                       # Generated plots
│
├── task2_qualitative_review/       # Manual quality assessment
│   ├── select_samples.py           # Sample selection logic
│   └── qualitative_report.md       # Review template & findings
│
├── task3_improvements/             # Prompt engineering & comparison
│   ├── generate_abstracts.py       # Generate with improved prompt
│   ├── compare_results.py          # Compare original vs improved
│   ├── visualize_comparison.py     # Comparison visualizations
│   ├── comparison_report.md        # Comparison analysis
│   └── *.png                       # Comparison plots
│
├── task4_bonus/                    # Advanced evaluation techniques
│   ├── llm_evaluation.py           # DeepEval LLM-as-judge
│   ├── prompt_optimization.py      # DSPy automated optimization
│   └── llm_evaluation_report.md    # LLM evaluation results
│
├── merge_reports.py                # Merge all reports into one
├── run_all_tasks.py                # Main orchestration script
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project metadata for uv
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── QUICK_START.md                  # Quick start guide
├── FINAL_REPORT.md                 # Comprehensive merged report
└── README.md                       # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- OpenAI API key (for Tasks 3 and 4)

### Installation

```bash
# Clone the repository
git clone https://github.com/nsourlos/llm-scientific-abstract-evaluation.git
cd llm-scientific-abstract-evaluation

# Install uv (fast Python package manager)
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows:
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Create environment and install dependencies
uv venv --python 3.12 venv_llm_scientific_eval
source venv_llm_scientific_eval/bin/activate  # On Windows: venv_llm_scientific_eval\Scripts\activate
uv pip install -e .

# Alternative (if you prefer pip):
# pip install -r requirements.txt
```

### Configuration

```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env

# (Optional) Customize configuration
# Edit src/config.py to change models, metrics, etc.
```

### Run Initial Analysis (No API Needed)

```bash
# Compute metrics and generate visualizations
python task1_quantitative_metrics/compute_metrics.py
python task1_quantitative_metrics/visualize_results.py

# Select samples for manual review
python task2_qualitative_review/select_samples.py
```

### Run Full Pipeline (API Required)

```bash
# Generate improved abstracts
python task3_improvements/generate_abstracts.py

# Compare and visualize results
python task3_improvements/compare_results.py
python task3_improvements/visualize_comparison.py

# (Optional) Advanced evaluation
python task4_bonus/llm_evaluation.py
python task4_bonus/prompt_optimization.py

# Merge all reports into one
python merge_reports.py
```

**For detailed instructions, see [QUICK_START.md](QUICK_START.md)**

---

## 📝 Tasks Overview

### Task 1: Quantitative Metrics
**Purpose:** Establish baseline performance using automated metrics

**Metrics:**
- ROUGE-1, ROUGE-2, ROUGE-L (string overlap)
- Semantic similarity (embedding-based)

**Cost:** FREE (no API calls)

**Output:** 
- `analysis.md` - Statistical analysis
- Visualizations (histograms, distributions, correlations)

---

### Task 2: Qualitative Review
**Purpose:** Manual assessment to identify concrete quality issues

**Process:**
1. Select 5 representative samples (best, worst, median)
2. Evaluate on clarity, coherence, factuality, safety/ethics
3. Document failure modes and improvement opportunities

**Cost:** FREE (no API calls)

**Output:**
- `qualitative_report.md` - Findings and recommendations

---

### Task 3: Improvements & Comparison
**Purpose:** Apply prompt engineering and measure improvements

**Features:**
- Structured prompt design (format, style, accuracy guidelines)
- Generate new abstracts with improved prompt
- Side-by-side comparison with original
- Comprehensive visualizations

**Output:**
- `comparison_report.md` - Detailed analysis
- Comparison visualizations

---

### Task 4: Advanced Evaluation

#### Part A: LLM-as-Judge (DeepEval)
**Purpose:** Scale qualitative assessment using LLM judges

**Metrics:**
- G-Eval (coherence, scientific accuracy)
- Faithfulness, Answer Relevancy
- Hallucination detection, Summarization quality

---

#### Part B: Automated Optimization (DSPy)
**Purpose:** Data-driven prompt optimization

**Features:**
- BootstrapFewShot optimizer
- Automated prompt refinement
- Performance validation

---

## 📊 Metrics & Evaluation

### Quantitative Metrics

**ROUGE Scores** (String Overlap)
- **ROUGE-1:** Unigram overlap (individual words)
- **ROUGE-2:** Bigram overlap (phrase-level similarity)
- **ROUGE-L:** Longest common subsequence (structural similarity)

**Semantic Similarity**
- Cosine similarity using sentence embeddings
- Model: Configurable (default: `Qwen/Qwen3-Embedding-0.6B`)
- Captures meaning beyond exact wording

### Qualitative Dimensions

- **Clarity:** Is the abstract easy to understand?
- **Coherence:** Does it flow logically?
- **Factuality:** Is information accurate to the source?
- **Safety/Ethics:** Any problematic content?
- **Completeness:** Are key elements present?

### LLM-as-Judge Metrics

- **Coherence:** Logical flow and organization
- **Scientific Accuracy:** Factual correctness, no over-claiming
- **Faithfulness:** Consistency with source document
- **Relevancy:** Appropriate summarization
- **Hallucination:** Identification of fabricated information
- **Summarization Quality:** Coverage of key elements

---

## ⚙️ Configuration

All configuration is centralized in `src/config.py`:

```python
# Model Configuration
OPENAI_MODEL = "gpt-4o-mini"  # Change model here
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"  # Change embeddings

# Metric Configuration
ROUGE_METRICS = ["rouge1", "rouge2", "rougeL"]

# Random Seed (for reproducibility)
RANDOM_SEED = 42
```

### Supported Models

**Generation:**
- `gpt-4o-mini` (recommended - best cost/speed)

**Embeddings:**
- `Qwen/Qwen3-Embedding-0.6B` (recommended <1B params)
- `BAAI/bge-small-en-v1.5` (recommended <100M params)
- `sentence-transformers/all-MiniLM-L6-v2` (fast, lightweight)

---

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Fast setup and usage guide
- **[FINAL_REPORT.md](FINAL_REPORT.md)** - Comprehensive results and analysis
- **Individual Task Reports** - Detailed findings in each task directory
- **Inline Documentation** - Code comments and docstrings

---

## 🛠️ Technology Stack

- **Language:** Python 3.12+
- **LLM API:** OpenAI (GPT-4o-mini)
- **Metrics:** rouge-score, sentence-transformers
- **Evaluation:** DeepEval, DSPy
- **Visualization:** matplotlib, seaborn
- **Package Management:** uv (recommended) or pip
- **Data:** pandas, numpy

---

## 🔬 Use Cases

- **Research:** Evaluate LLM capabilities on scientific text generation
- **Publishing:** Automated abstract generation for papers
- **Education:** Teach prompt engineering and evaluation techniques
- **Benchmarking:** Compare different models/prompts

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional metrics (BERTScore, BLEU, etc.)
- Domain-specific prompts (medical, CS, physics)
- Fine-tuning capabilities

Please open an issue or submit a pull request.


---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Happy Evaluating! 🚀**

