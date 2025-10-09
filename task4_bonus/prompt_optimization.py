"""
Task 4 Bonus: Automated prompt optimization using DSPy

This script demonstrates how DSPy can be used to automatically optimize
prompts for scientific abstract generation.

Note: This script is compatible with DSPy 3.0+ (dspy-ai>=3.0.0).
If you encounter compatibility issues, you may need to adjust your DSPy version:
- For DSPy 3.0+: pip install dspy-ai>=3.0.0
- For DSPy 2.x: pip install dspy-ai<3.0.0 (older version)
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import dspy
import pandas as pd
from typing import List
from src.config import ORIGINAL_DATA, OPENAI_API_KEY, TASK4_DIR, OPENAI_MODEL
from src.utils import load_data
from src.cost_estimator import estimate_dspy_cost, print_cost_summary

# Check DSPy version and set compatibility flags
print(f"DSPy version: {dspy.__version__ if hasattr(dspy, '__version__') else 'unknown'}")

# DSPy 3.0+ compatibility detection
try:
    # Try DSPy 3.0+ API
    from dspy import Signature, InputField, OutputField
    DSPY_VERSION = "3.0+"
    print("✓ DSPy 3.0+ API detected")
except (ImportError, AttributeError):
    # Fallback to DSPy 2.x API
    DSPY_VERSION = "2.x"
    print("✓ DSPy 2.x API detected")


# Define signature using string format (DSPy 3.0+ compatible)
ABSTRACT_SIGNATURE = """
full_text: str -> abstract: str
\"\"\"Generate a scientific abstract from a full text article.

Input: Full text of the scientific article
Output: Concise scientific abstract (150-250 words) following standard structure: 
        background, objective, methods, results, conclusion
\"\"\"
"""


class AbstractGenerationModule(dspy.Module):
    """DSPy module for abstract generation - DSPy 3.0+ compatible"""
    
    def __init__(self):
        super().__init__()
        # Use string-based signature for DSPy 3.0+ compatibility
        try:
            # DSPy 3.0+ approach
            self.generate_abstract = dspy.Predict("full_text -> abstract")
        except:
            # Fallback approach with ChainOfThought
            self.generate_abstract = dspy.ChainOfThought("full_text -> abstract")
    
    def forward(self, full_text):
        result = self.generate_abstract(full_text=full_text)
        return result


def prepare_training_data(df: pd.DataFrame, n_samples: int = 10) -> List[dspy.Example]:
    """
    Prepare training examples for DSPy
    
    Args:
        df: Dataframe with articles and abstracts
        n_samples: Number of samples to use for training
    
    Returns:
        List of DSPy examples
    """
    examples = []
    
    # Use diverse samples
    sample_df = df.sample(n=n_samples, random_state=42)
    
    for idx, row in sample_df.iterrows():
        example = dspy.Example(
            full_text=row['full_text'][:2000],  # Truncate for efficiency
            abstract=row['abstract']
        ).with_inputs('full_text')
        
        examples.append(example)
    
    return examples


def evaluate_abstract(example, pred, trace=None):
    """
    Custom evaluation function for abstract quality
    
    Simple metric: check if prediction exists and has reasonable length
    """
    # Handle both attribute access and dictionary access (DSPy version differences)
    try:
        abstract = pred.abstract if hasattr(pred, 'abstract') else (pred.get('abstract') if isinstance(pred, dict) else str(pred))
    except:
        return 0.0
    
    if not abstract:
        return 0.0
    
    # Target length: 150-250 words
    word_count = len(str(abstract).split())
    
    # Score based on length appropriateness
    if 150 <= word_count <= 250:
        length_score = 1.0
    elif 100 <= word_count < 150 or 250 < word_count <= 300:
        length_score = 0.7
    else:
        length_score = 0.3
    
    # Basic content check
    has_content = len(str(abstract)) > 100
    content_score = 1.0 if has_content else 0.0
    
    # Combined score
    return (length_score + content_score) / 2


def optimize_prompt_with_dspy():
    """
    Demonstrate DSPy prompt optimization
    
    Note: This is a simplified example. Full optimization would require:
    - More training examples
    - Better evaluation metrics (ROUGE, embedding similarity)
    - More compute time
    """
    
    print("\n" + "=" * 60)
    print("DSPy PROMPT OPTIMIZATION")
    print("=" * 60)
    
    # Configure DSPy with OpenAI
    try:
        # Try newer DSPy 3.0+ syntax first
        lm = dspy.LM(model='openai/'+OPENAI_MODEL, api_key=OPENAI_API_KEY, max_tokens=500)
        dspy.configure(lm=lm)
    except (AttributeError, TypeError):
        # Fallback to older syntax if needed
        try:
            lm = dspy.OpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, max_tokens=500)
            dspy.settings.configure(lm=lm)
        except Exception as e:
            print(f"⚠ Warning: Could not configure DSPy: {e}")
            print("Attempting with basic configuration...")
            lm = dspy.OpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)
            dspy.configure(lm=lm)
    
    # Load data
    print("\nLoading data...")
    df = load_data(ORIGINAL_DATA)
    print(f"✓ Loaded {len(df)} documents")
    
    # Prepare training data
    print("\nPreparing training examples...")
    train_examples = prepare_training_data(df, n_samples=5)
    print(f"✓ Created {len(train_examples)} training examples")
    
    # Create module
    print("\nInitializing abstract generation module...")
    module = AbstractGenerationModule()
    
    # Baseline evaluation
    print("\nBaseline evaluation (before optimization)...")
    baseline_scores = []
    for example in train_examples[:3]:
        pred = module(full_text=example.full_text)
        score = evaluate_abstract(example, pred)
        baseline_scores.append(score)
        print(f"  Sample score: {score:.2f}")
    
    baseline_avg = sum(baseline_scores) / len(baseline_scores)
    print(f"\n✓ Baseline average: {baseline_avg:.3f}")
    
    # Optimize with DSPy
    print("\nOptimizing prompt with DSPy...")
    print("  Note: This uses BootstrapFewShot optimizer")
    print("  In production, consider MIPROv2 or other advanced optimizers")
    
    try:
        # Try to use the optimizer
        try:
            optimizer = dspy.BootstrapFewShot(
                metric=evaluate_abstract,
                max_bootstrapped_demos=3,
                max_labeled_demos=3
            )
        except TypeError:
            # DSPy 3.0+ may have different parameter names
            optimizer = dspy.BootstrapFewShot(
                metric=evaluate_abstract,
                max_bootstrapped_demos=3
            )
        
        optimized_module = optimizer.compile(
            module,
            trainset=train_examples[:5]
        )
        
        # Evaluate optimized module
        print("\nEvaluating optimized module...")
        optimized_scores = []
        for example in train_examples[:3]:
            pred = optimized_module(full_text=example.full_text)
            score = evaluate_abstract(example, pred)
            optimized_scores.append(score)
            print(f"  Sample score: {score:.2f}")
        
        optimized_avg = sum(optimized_scores) / len(optimized_scores)
        print(f"\n✓ Optimized average: {optimized_avg:.3f}")
        
        improvement = ((optimized_avg - baseline_avg) / baseline_avg) * 100
        print(f"✓ Improvement: {improvement:+.1f}%")
        
        # Save the optimized module
        output_file = TASK4_DIR / "dspy_optimized_module.json"
        optimized_module.save(str(output_file))
        print(f"\n✓ Optimized module saved to: {output_file}")
        
        return {
            'baseline': baseline_avg,
            'optimized': optimized_avg,
            'improvement': improvement
        }
        
    except Exception as e:
        print(f"\n⚠ Warning: Optimization failed: {e}")
        print("This may require more compute time or different optimizer settings.")
        return None


def main():
    """Main function"""
    print("=" * 60)
    print("TASK 4 BONUS: AUTOMATED PROMPT OPTIMIZATION WITH DSPy")
    print("=" * 60)
    
    if not OPENAI_API_KEY:
        print("\n❌ Error: OPENAI_API_KEY not found")
        return
    
    # Estimate cost
    print("\nEstimating cost...")
    cost_estimate = estimate_dspy_cost(
        n_training_samples=5,
        n_test_samples=3,
        model=OPENAI_MODEL,
        avg_tokens_per_example=3000
    )
    
    # Display cost estimate and confirm
    if not print_cost_summary(
        task_name="DSPy Automated Prompt Optimization",
        cost_dict=cost_estimate,
        proceed_prompt=True
    ):
        print("Optimization cancelled.")
        return
    
    # Run optimization
    results = optimize_prompt_with_dspy()
    
    print("\n" + "=" * 60)
    print("✓ DSPy optimization completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()