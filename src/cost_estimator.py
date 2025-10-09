"""
Cost estimation utilities for OpenAI API calls
"""

from typing import Dict, Optional
import pandas as pd


# Pricing per 1M tokens (as of October 2024)
PRICING = {
    'gpt-4o-mini': {'input': 0.150, 'output': 0.600},
    'gpt-5-nano': {'input': 0.050, 'output': 0.400},
    'gpt-5-mini': {'input': 0.250, 'output': 2.000},
}


def estimate_tokens(text: str) -> int:
    """
    Estimate number of tokens in text.
    
    Rule of thumb: 1 token ≈ 4 characters for English text
    
    Args:
        text: Input text
    
    Returns:
        Estimated token count
    """
    return len(text) // 4


def estimate_generation_cost(
    df: pd.DataFrame,
    prompt_template: str,
    model: str = 'gpt-4o-mini',
    max_output_tokens: int = 500,
    n_samples: Optional[int] = None,
    full_text_col: str = 'full_text'
) -> Dict[str, float]:
    """
    Estimate API cost for generating abstracts.
    
    Args:
        df: DataFrame with papers
        prompt_template: Prompt template with {full_text} placeholder
        model: Model name
        max_output_tokens: Maximum output tokens per request
        n_samples: Number of samples (None = all)
        full_text_col: Column name for full text
    
    Returns:
        Dictionary with cost estimates
    """
    if model not in PRICING:
        return {
            'error': f'Pricing not available for model {model}',
            'samples': n_samples or len(df)
        }
    
    # Select subset
    if n_samples is not None:
        df_subset = df.head(n_samples)
    else:
        df_subset = df
    
    # Estimate tokens for a sample
    sample_row = df_subset.iloc[0]
    sample_prompt = prompt_template.format(
        full_text=sample_row[full_text_col]#[:5000]  # Limit to first 5000 chars for estimation
    )
    
    avg_input_tokens = estimate_tokens(sample_prompt)
    avg_output_tokens = max_output_tokens
    
    total_input_tokens = avg_input_tokens * len(df_subset)
    total_output_tokens = avg_output_tokens * len(df_subset)
    
    input_cost = (total_input_tokens / 1_000_000) * PRICING[model]['input']
    output_cost = (total_output_tokens / 1_000_000) * PRICING[model]['output']
    total_cost = input_cost + output_cost
    
    return {
        'model': model,
        'samples': len(df_subset),
        'estimated_input_tokens': int(total_input_tokens),
        'estimated_output_tokens': int(total_output_tokens),
        'estimated_input_cost_usd': round(input_cost, 4),
        'estimated_output_cost_usd': round(output_cost, 4),
        'estimated_total_cost_usd': round(total_cost, 4)
    }


def estimate_evaluation_cost(
    n_samples: int,
    model: str = 'gpt-4o-mini',
    n_metrics: int = 3,
    avg_input_tokens: int = 2000,
    avg_output_tokens: int = 200
) -> Dict[str, float]:
    """
    Estimate cost for LLM-based evaluation.
    
    Args:
        n_samples: Number of samples to evaluate
        model: Model name
        n_metrics: Number of evaluation metrics
        avg_input_tokens: Average input tokens per evaluation
        avg_output_tokens: Average output tokens per evaluation
    
    Returns:
        Dictionary with cost estimates
    """
    if model not in PRICING:
        return {
            'error': f'Pricing not available for model {model}',
            'samples': n_samples
        }
    
    # Total evaluations = samples × metrics
    total_evaluations = n_samples * n_metrics
    
    total_input_tokens = avg_input_tokens * total_evaluations
    total_output_tokens = avg_output_tokens * total_evaluations
    
    input_cost = (total_input_tokens / 1_000_000) * PRICING[model]['input']
    output_cost = (total_output_tokens / 1_000_000) * PRICING[model]['output']
    total_cost = input_cost + output_cost
    
    return {
        'model': model,
        'samples': n_samples,
        'n_metrics': n_metrics,
        'total_evaluations': total_evaluations,
        'estimated_input_tokens': int(total_input_tokens),
        'estimated_output_tokens': int(total_output_tokens),
        'estimated_input_cost_usd': round(input_cost, 4),
        'estimated_output_cost_usd': round(output_cost, 4),
        'estimated_total_cost_usd': round(total_cost, 4)
    }


def estimate_dspy_cost(
    n_training_samples: int,
    n_test_samples: int = 3,
    model: str = 'gpt-4o-mini',
    avg_tokens_per_example: int = 3000
) -> Dict[str, float]:
    """
    Estimate cost for DSPy optimization.
    
    Args:
        n_training_samples: Number of training samples
        n_test_samples: Number of test samples
        model: Model name
        avg_tokens_per_example: Average tokens per example
    
    Returns:
        Dictionary with cost estimates
    """
    if model not in PRICING:
        return {
            'error': f'Pricing not available for model {model}',
            'training_samples': n_training_samples
        }
    
    # DSPy typically needs:
    # - Initial generation for each training example
    # - Bootstrap attempts (3-5 per example)
    # - Test evaluations
    
    bootstrap_multiplier = 4
    total_generations = (n_training_samples * bootstrap_multiplier) + n_test_samples
    
    # Assume input/output split 70/30
    total_tokens = avg_tokens_per_example * total_generations
    input_tokens = int(total_tokens * 0.7)
    output_tokens = int(total_tokens * 0.3)
    
    input_cost = (input_tokens / 1_000_000) * PRICING[model]['input']
    output_cost = (output_tokens / 1_000_000) * PRICING[model]['output']
    total_cost = input_cost + output_cost
    
    return {
        'model': model,
        'training_samples': n_training_samples,
        'test_samples': n_test_samples,
        'estimated_generations': total_generations,
        'estimated_input_tokens': input_tokens,
        'estimated_output_tokens': output_tokens,
        'estimated_input_cost_usd': round(input_cost, 4),
        'estimated_output_cost_usd': round(output_cost, 4),
        'estimated_total_cost_usd': round(total_cost, 4)
    }


def format_cost_estimate(cost_dict: Dict[str, float]) -> str:
    """
    Format cost estimate as readable string.
    
    Args:
        cost_dict: Cost dictionary from estimation functions
    
    Returns:
        Formatted string
    """
    if 'error' in cost_dict:
        return f"❌ {cost_dict['error']}"
    
    # Handle different formats (regular vs DSPy)
    if 'samples' in cost_dict:
        samples_str = f"   Samples: {cost_dict['samples']}\n"
    elif 'training_samples' in cost_dict and 'test_samples' in cost_dict:
        samples_str = f"   Training Samples: {cost_dict['training_samples']}\n   Test Samples: {cost_dict['test_samples']}\n"
    elif 'n_samples' in cost_dict:
        samples_str = f"   Samples: {cost_dict['n_samples']}\n"
    else:
        samples_str = ""
    
    output = f"""
💰 Cost Estimate:
   Model: {cost_dict['model']}
{samples_str}   
   Estimated Tokens:
   - Input:  {cost_dict['estimated_input_tokens']:,} tokens
   - Output: {cost_dict['estimated_output_tokens']:,} tokens
   
   Estimated Cost:
   - Input:  ${cost_dict['estimated_input_cost_usd']:.4f}
   - Output: ${cost_dict['estimated_output_cost_usd']:.4f}
   - Total:  ${cost_dict['estimated_total_cost_usd']:.4f}
"""
    return output


def print_cost_summary(
    task_name: str,
    cost_dict: Dict[str, float],
    proceed_prompt: bool = True
) -> bool:
    """
    Print cost summary and optionally ask for confirmation.
    
    Args:
        task_name: Name of the task
        cost_dict: Cost dictionary
        proceed_prompt: Whether to ask for confirmation
    
    Returns:
        True if user confirms, False otherwise (or True if no prompt)
    """
    print("\n" + "=" * 60)
    print(f"COST ESTIMATE: {task_name}")
    print("=" * 60)
    print(format_cost_estimate(cost_dict))
    
    if proceed_prompt and 'error' not in cost_dict:
        response = input("Proceed with API calls? (y/n): ")
        return response.lower() == 'y'
    
    return True

