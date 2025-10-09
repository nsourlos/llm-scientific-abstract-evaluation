"""
Configuration management for the LLM evaluation project
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TASK1_DIR = PROJECT_ROOT / "task1_quantitative_metrics"
TASK2_DIR = PROJECT_ROOT / "task2_qualitative_review"
TASK3_DIR = PROJECT_ROOT / "task3_improvements"
TASK4_DIR = PROJECT_ROOT / "task4_bonus"

# Data files
ORIGINAL_DATA = DATA_DIR / "scientific_documents_and_generations.pkl"
ORIGINAL_PROMPT = DATA_DIR / "prompt.txt"
IMPROVED_PROMPT = DATA_DIR / "improved_prompt.txt"
IMPROVED_DATA = DATA_DIR / "scientific_documents_with_improved_abstracts.pkl"

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"  # gpt-5-nano is the best cost/quality tradeoff. 
#Other options could be gpt5mini or gpt-4o-mini (faster and cheaper)

# Metric configurations
ROUGE_METRICS = ["rouge1", "rouge2", "rougeL"]
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"  
# Best model <1B is Qwen/Qwen3-Embedding-0.6B and best <100M is BAAI/bge-small-en-v1.5 (https://huggingface.co/spaces/mteb/leaderboard)
# Only from the models that mention parameters. Otherwise, text-embedding-3-small seems also very good

# Random seed for reproducibility
RANDOM_SEED = 42

