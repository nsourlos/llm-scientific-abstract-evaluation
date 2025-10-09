"""
Utility functions for the LLM evaluation project
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np


def load_data(file_path: Path) -> pd.DataFrame:
    """Load pickled dataframe"""
    df = pd.read_pickle(file_path)
    print(f"Dataset shape: {df.shape}")
    print(f"\nColumns: {df.columns.tolist()}")
    return df


def save_data(df: pd.DataFrame, file_path: Path) -> None:
    """Save dataframe as pickle"""
    df.to_pickle(file_path)
    df.to_excel(file_path.with_suffix('.xlsx'), index=False, engine='openpyxl')


def load_prompt(file_path: Path) -> str:
    """Load prompt from text file"""
    with open(file_path, 'r') as f:
        return f.read().strip()


def save_prompt(prompt: str, file_path: Path) -> None:
    """Save prompt to text file"""
    with open(file_path, 'w') as f:
        f.write(prompt)


def calculate_summary_stats(scores: List[float]) -> Dict[str, float]:
    """Calculate summary statistics for a list of scores"""
    return {
        'mean': np.mean(scores),
        'median': np.median(scores),
        'std': np.std(scores),
        'min': np.min(scores),
        'max': np.max(scores)
    }


def format_scores_table(df: pd.DataFrame, metrics: List[str]) -> str:
    """Format metrics dataframe as markdown table"""
    summary_stats = {}
    for metric in metrics:
        if metric in df.columns:
            summary_stats[metric] = calculate_summary_stats(df[metric].tolist())
    
    # Create markdown table
    table = "| Metric | Mean | Median | Std | Min | Max |\n"
    table += "|--------|------|--------|-----|-----|-----|\n"
    for metric, stats in summary_stats.items():
        table += f"| {metric} | {stats['mean']:.4f} | {stats['median']:.4f} | {stats['std']:.4f} | {stats['min']:.4f} | {stats['max']:.4f} |\n"
    
    return table


def get_sample_indices(df: pd.DataFrame, n_samples: int = 5, strategy: str = "diverse") -> List[int]:
    """
    Get sample indices for qualitative review
    
    Args:
        df: Dataframe with metrics
        n_samples: Number of samples to select
        strategy: 'diverse', 'best', 'worst', or 'random'
    
    Returns:
        List of indices
    """
    if strategy == "random":
        return df.sample(n=n_samples, random_state=42).index.tolist()
    elif strategy == "best":
        return df.nlargest(n_samples, 'rouge1').index.tolist()
    elif strategy == "worst":
        return df.nsmallest(n_samples, 'rouge1').index.tolist()
    elif strategy == "diverse":
        # Select samples from different score ranges
        quantiles = [0.1, 0.3, 0.5, 0.7, 0.9]
        indices = []
        for q in quantiles[:n_samples]:
            idx = (df['rouge1'] - df['rouge1'].quantile(q)).abs().idxmin()
            indices.append(idx)
        return indices
    else:
        raise ValueError(f"Unknown strategy: {strategy}")