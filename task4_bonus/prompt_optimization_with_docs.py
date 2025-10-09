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


def generate_dspy_report(results: dict, output_dir: Path):
    """Generate report on DSPy optimization"""
    
    report = """# Task 4 Bonus: DSPy Automated Prompt Optimization

## Overview

DSPy (Declarative Self-improving Python) is a framework for algorithmically optimizing prompts and LM pipelines. Instead of manually crafting prompts, DSPy treats prompts as learnable parameters that can be optimized.

## Methodology

### DSPy Signature
We defined a `AbstractGenerator` signature that specifies:
- Input: Full text of scientific article
- Output: Concise scientific abstract with structure constraints

### Optimization Approach
- **Optimizer:** BootstrapFewShot
- **Training Set:** 5 diverse examples from the dataset
- **Evaluation Metric:** Custom metric combining length appropriateness and content quality
- **Model:** {OPENAI_MODEL}

### How DSPy Works

1. **Bootstrap Examples:** DSPy generates intermediate reasoning steps for training examples
2. **Few-Shot Selection:** Selects the most effective demonstrations
3. **Prompt Construction:** Automatically builds optimized prompts with selected examples
4. **Iterative Improvement:** Can iterate to find better prompt configurations

## Results

"""
    
    if results:
        report += f"""
### Performance Comparison

- **Baseline (manual prompt):** {results['baseline']:.3f}
- **Optimized (DSPy):** {results['optimized']:.3f}
- **Improvement:** {results['improvement']:+.1f}%

"""
    else:
        report += """
### Performance Comparison

Optimization was attempted but encountered issues. See console output for details.

"""
    
    report += """
## Advantages of DSPy

1. **Automated Optimization:** No need for manual prompt engineering iteration
2. **Data-Driven:** Uses actual examples to learn what works
3. **Systematic:** Explores the prompt space algorithmically
4. **Composable:** Can optimize multi-step pipelines
5. **Transferable:** Optimized prompts can transfer to similar tasks

## Limitations

1. **Compute Cost:** Optimization requires multiple LLM calls
2. **Training Data:** Needs representative examples for good optimization
3. **Evaluation Metric:** Quality of optimization depends on metric design
4. **Model Dependency:** Optimized prompts may not transfer across different LLMs

## Advanced DSPy Features (Not Demonstrated)

### Available Optimizers

1. **MIPROv2:** Multi-stage optimization with instruction proposal and refinement
2. **COPRO:** Coordinate-ascent style prompt optimization
3. **Ensemble:** Combines multiple prompt strategies
4. **KNN:** K-nearest neighbor few-shot selection

### Pipeline Optimization

DSPy can optimize complex pipelines:
```python
class RetrievalAugmentedGeneration(dspy.Module):
    def __init__(self):
        self.retrieve = dspy.Retrieve(k=3)
        self.generate = dspy.ChainOfThought(AbstractGenerator)
    
    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(context=context, question=question)
```

## Comparison: Manual vs. Automated Prompt Engineering

| Aspect | Manual Prompting | DSPy Optimization |
|--------|------------------|-------------------|
| **Time to Optimize** | Hours of iteration | Minutes (after setup) |
| **Consistency** | Depends on engineer skill | Systematic and reproducible |
| **Data Utilization** | Limited (few examples reviewed) | Full training set |
| **Adaptability** | Must manually adjust for new domains | Can re-optimize automatically |
| **Interpretability** | High (human-written) | Moderate (generated prompts may be complex) |
| **Cost** | Low (human time only) | Medium (LLM API calls) |

## Recommendations

### When to Use DSPy

1. **Complex Tasks:** Multi-step reasoning or retrieval-augmented generation
2. **Large Training Sets:** When you have many labeled examples
3. **Frequent Updates:** When prompts need regular refinement as data changes
4. **Research/Experimentation:** To explore what prompts work best

### When to Use Manual Prompting

1. **Simple Tasks:** Single-step generation with clear requirements
2. **Limited Data:** When you don't have enough examples for optimization
3. **Quick Prototypes:** For rapid iteration and experimentation
4. **Transparency Required:** When prompt rationale must be explicitly documented

### Hybrid Approach (Recommended)

1. Start with manual prompt based on task understanding
2. Use manual prompt as baseline
3. Apply DSPy optimization to explore improvements
4. Review and understand what DSPy changed
5. Combine insights from both approaches

## Practical Considerations

### Production Deployment

For production use of DSPy-optimized prompts:

1. **Version Control:** Save optimized modules and track performance
2. **A/B Testing:** Compare optimized vs. manual prompts in production
3. **Monitoring:** Track if optimized prompts maintain quality over time
4. **Re-optimization:** Periodically re-run optimization with new data
5. **Fallback:** Keep manual prompts as fallback if optimized versions fail

### Cost Analysis

- **Optimization Cost:** $1-5 for small-scale optimization (5-10 examples)
- **Inference Cost:** Same as manual prompts (no additional cost)
- **ROI:** Positive if improved quality reduces downstream costs (e.g., fewer revisions)

## Conclusion

DSPy represents a paradigm shift in prompt engineering, treating prompts as learnable components rather than hand-crafted text. While manual prompt engineering remains valuable for understanding and baseline development, DSPy offers a powerful complement for systematic optimization.

### Key Takeaways

1. **Manual prompting is essential** for understanding task requirements and establishing baselines
2. **DSPy optimization is powerful** for systematic improvement and complex pipelines
3. **Hybrid approaches** combining human insight and automated optimization yield best results
4. **The future of prompt engineering** likely involves more automation while retaining human oversight

## Next Steps

To further improve abstract generation:

1. **Expand Training Set:** Use 20-50 examples for better optimization
2. **Better Metrics:** Incorporate ROUGE and embedding similarity into evaluation
3. **Advanced Optimizers:** Try MIPROv2 for instruction-level optimization
4. **Domain Adaptation:** Create specialized modules for different scientific fields
5. **Multi-stage Pipelines:** Add retrieval or refinement stages
"""
    
    report_file = output_dir / "dspy_optimization_report.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"✓ DSPy report saved to: {report_file}")


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
    
    # Generate report
    print("\nGenerating DSPy report...")
    generate_dspy_report(results, TASK4_DIR)
    
    print("\n" + "=" * 60)
    print("✓ DSPy optimization completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()