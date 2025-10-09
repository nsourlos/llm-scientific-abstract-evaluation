"""
Task 4 Bonus: LLM-based evaluation using DeepEval

This script uses DeepEval to evaluate abstracts with:
- G-Eval for quality assessment
- Faithfulness metric
- Answer relevancy
- Hallucination detection
- Summarization quality
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from deepeval import evaluate
from deepeval.metrics import (
    GEval, 
    FaithfulnessMetric, 
    AnswerRelevancyMetric,
    HallucinationMetric,
    SummarizationMetric
)
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from tqdm import tqdm
from src.config import IMPROVED_DATA, TASK4_DIR, OPENAI_API_KEY, OPENAI_MODEL
from src.utils import load_data
from src.cost_estimator import estimate_evaluation_cost, print_cost_summary


def create_test_cases(df: pd.DataFrame, use_improved: bool = True) -> list:
    """
    Create DeepEval test cases from dataframe
    
    Args:
        df: Dataframe with abstracts
        use_improved: Whether to use improved or original generated abstracts
    
    Returns:
        List of LLMTestCase objects
    """
    test_cases = []
    
    abstract_col = 'improved_abstract' if use_improved else 'generated_abstract'
    
    for idx, row in df.iterrows():
        # Prepare context - use full text for faithfulness and accuracy checks
        full_text = row['full_text']
        
        test_case = LLMTestCase(
            input=row['title'],  # Input is the paper title (the task is to generate an abstract for this title)
            actual_output=row[abstract_col],  # Generated abstract
            expected_output=row['abstract'],  # Reference abstract
            context=[full_text],  # For G-Eval accuracy metric - see the full context of the paper
            retrieval_context=[full_text]  # For Faithfulness metric
        )
        test_cases.append(test_case)
    
    return test_cases


def evaluate_with_geval(test_cases: list) -> list:
    """
    Evaluate using G-Eval metric
    
    G-Eval uses LLM to evaluate quality on custom criteria
    """
    print("\nEvaluating with G-Eval...")
    
    try:
        # Define evaluation criteria for scientific abstracts
        coherence_metric = GEval(
            name="Coherence",
            criteria="Coherence - the logical flow and organization of the abstract",
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT
            ],
            model=OPENAI_MODEL
        )
    
        accuracy_metric = GEval(
            name="Scientific Accuracy",
            criteria="Scientific accuracy - whether the abstract accurately represents the research without hallucinations or over-claiming",
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.CONTEXT
            ],
            model=OPENAI_MODEL
        )
        
        results = []
        for test_case in tqdm(test_cases[:5]):  # Limit to 5 for cost
            coherence_metric.measure(test_case)
            accuracy_metric.measure(test_case)
            
            results.append({
                'coherence': coherence_metric.score,
                'accuracy': accuracy_metric.score,
                'coherence_reason': coherence_metric.reason,
                'accuracy_reason': accuracy_metric.reason
            })
        
        return results
    
    except Exception as e:
        print(f"\n⚠ Warning: G-Eval evaluation failed: {e}")
        print("This may be due to API changes in newer DeepEval versions.")
        return []


def evaluate_with_faithfulness(test_cases: list) -> list:
    """
    Evaluate faithfulness - whether output is factually consistent with context
    """
    print("\nEvaluating faithfulness...")
    
    try:
        faithfulness_metric = FaithfulnessMetric(
            threshold=0.7, #Threshold for output to be considered faithful
            model=OPENAI_MODEL,
            include_reason=True
        )
        
        results = []
        for test_case in tqdm(test_cases[:5]):  # Limit to 5 for cost
            faithfulness_metric.measure(test_case)
            results.append({
                'faithfulness_score': faithfulness_metric.score,
                'faithfulness_reason': faithfulness_metric.reason
            })
        
        return results
    
    except Exception as e:
        print(f"\n⚠ Warning: Faithfulness evaluation failed: {e}")
        print("This may be due to API changes in newer DeepEval versions.")
        return []


def evaluate_with_relevancy(test_cases: list) -> list:
    """
    Evaluate answer relevancy - whether output addresses the input
    """
    print("\nEvaluating relevancy...")
    
    try:
        relevancy_metric = AnswerRelevancyMetric(
            threshold=0.7, #Threshold for output to be considered relevant
            model=OPENAI_MODEL,
            include_reason=True
        )
        
        results = []
        for test_case in tqdm(test_cases[:5]):  # Limit to 5 for cost
            relevancy_metric.measure(test_case)
            results.append({
                'relevancy_score': relevancy_metric.score,
                'relevancy_reason': relevancy_metric.reason
            })
        
        return results
    
    except Exception as e:
        print(f"\n⚠ Warning: Relevancy evaluation failed: {e}")
        print("This may be due to API changes in newer DeepEval versions.")
        return []


def evaluate_with_hallucination(test_cases: list) -> list:
    """
    Evaluate hallucination - whether output contains information not in source
    """
    print("\nEvaluating hallucination...")
    
    try:
        hallucination_metric = HallucinationMetric(
            threshold=0.8, #Threshold for output to be considered hallucinated
            model=OPENAI_MODEL,
            include_reason=True
        )
        
        results = []
        for test_case in tqdm(test_cases[:5]):  # Limit to 5 for cost
            hallucination_metric.measure(test_case)
            results.append({
                'hallucination_score': hallucination_metric.score,
                'hallucination_reason': hallucination_metric.reason
            })
        
        return results
    
    except Exception as e:
        print(f"\n⚠ Warning: Hallucination evaluation failed: {e}")
        print("This may be due to API changes in newer DeepEval versions.")
        return []


def evaluate_with_summarization(test_cases: list) -> list:
    """
    Evaluate summarization quality - how well the abstract summarizes the full text
    """
    print("\nEvaluating summarization quality...")
    
    try:
        summarization_metric = SummarizationMetric(
            threshold=0.7,
            model=OPENAI_MODEL,
            include_reason=True,
            assessment_questions=[
                "Does the summary capture the main research question?",
                "Are the key methods mentioned?",
                "Are the main results included?",
                "Is the conclusion present?"
            ]
        )
        
        results = []
        for test_case in tqdm(test_cases[:5]):  # Limit to 5 for cost
            summarization_metric.measure(test_case)
            results.append({
                'summarization_score': summarization_metric.score,
                'summarization_reason': summarization_metric.reason
            })
        
        return results
    
    except Exception as e:
        print(f"\n⚠ Warning: Summarization evaluation failed: {e}")
        print("This may be due to API changes in newer DeepEval versions.")
        return []


def save_results_to_csv(results: dict, df: pd.DataFrame, output_dir: Path):
    """
    Save evaluation results to CSV file
    
    Args:
        results: Dictionary with evaluation results
        df: Original dataframe with documents
        output_dir: Directory to save CSV
    """
    # Prepare data for CSV
    csv_data = []
    
    # Get first 5 samples (matching evaluation limit)
    for i in range(min(5, len(df))):
        row_data = {
            'sample_id': i + 1,
            'doi': df.iloc[i]['doi'] if 'doi' in df.columns else f'sample_{i+1}',
            'title': df.iloc[i]['title'][:100] + '...' if len(df.iloc[i]['title']) > 100 else df.iloc[i]['title']
        }
        
        # Add G-Eval results
        if results.get('geval') and i < len(results['geval']):
            geval_result = results['geval'][i]
            row_data['coherence_score'] = geval_result.get('coherence', None)
            row_data['coherence_reason'] = geval_result.get('coherence_reason', 'N/A')
            row_data['accuracy_score'] = geval_result.get('accuracy', None)
            row_data['accuracy_reason'] = geval_result.get('accuracy_reason', 'N/A')
        else:
            row_data['coherence_score'] = None
            row_data['coherence_reason'] = 'Evaluation failed'
            row_data['accuracy_score'] = None
            row_data['accuracy_reason'] = 'Evaluation failed'
        
        # Add Faithfulness results
        if results.get('faithfulness') and i < len(results['faithfulness']):
            faith_result = results['faithfulness'][i]
            row_data['faithfulness_score'] = faith_result.get('faithfulness_score', None)
            row_data['faithfulness_reason'] = faith_result.get('faithfulness_reason', 'N/A')
        else:
            row_data['faithfulness_score'] = None
            row_data['faithfulness_reason'] = 'Evaluation failed'
        
        # Add Relevancy results
        if results.get('relevancy') and i < len(results['relevancy']):
            rel_result = results['relevancy'][i]
            row_data['relevancy_score'] = rel_result.get('relevancy_score', None)
            row_data['relevancy_reason'] = rel_result.get('relevancy_reason', 'N/A')
        else:
            row_data['relevancy_score'] = None
            row_data['relevancy_reason'] = 'Evaluation failed'
        
        # Add Hallucination results
        if results.get('hallucination') and i < len(results['hallucination']):
            hall_result = results['hallucination'][i]
            row_data['hallucination_score'] = hall_result.get('hallucination_score', None)
            row_data['hallucination_reason'] = hall_result.get('hallucination_reason', 'N/A')
        else:
            row_data['hallucination_score'] = None
            row_data['hallucination_reason'] = 'Evaluation failed'
        
        # Add Summarization results
        if results.get('summarization') and i < len(results['summarization']):
            summ_result = results['summarization'][i]
            row_data['summarization_score'] = summ_result.get('summarization_score', None)
            row_data['summarization_reason'] = summ_result.get('summarization_reason', 'N/A')
        else:
            row_data['summarization_score'] = None
            row_data['summarization_reason'] = 'Evaluation failed'
        
        csv_data.append(row_data)
    
    # Create DataFrame and save to CSV
    results_df = pd.DataFrame(csv_data)
    csv_file = output_dir / "llm_evaluation_results.csv"
    results_df.to_csv(csv_file, index=False)
    print(f"✓ Results saved to CSV: {csv_file}")
    
    # Also save a summary CSV with just the scores
    summary_data = []
    metrics = ['coherence', 'accuracy', 'faithfulness', 'relevancy', 'hallucination', 'summarization']
    
    for metric in metrics:
        if metric in ['coherence', 'accuracy']:
            scores = [r.get(metric) for r in results.get('geval', []) if r.get(metric) is not None]
        else:
            scores = [r.get(f'{metric}_score') for r in results.get(metric, []) if r.get(f'{metric}_score') is not None]
        
        if scores:
            summary_data.append({
                'metric': metric,
                'mean_score': sum(scores) / len(scores),
                'min_score': min(scores),
                'max_score': max(scores),
                'n_samples': len(scores)
            })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        summary_file = output_dir / "llm_evaluation_summary.csv"
        summary_df.to_csv(summary_file, index=False)
        print(f"✓ Summary saved to CSV: {summary_file}")
    
    # Also save as Excel for easy viewing
    try:
        excel_file = output_dir / "llm_evaluation_results.xlsx"
        results_df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"✓ Results saved to Excel: {excel_file}")
    except Exception as e:
        print(f"⚠ Could not save Excel file: {e}")
    
    return results_df


def generate_llm_eval_report(results: dict, output_dir: Path):
    """Generate report from LLM evaluation results"""
    
    report = """# Task 4 Bonus: LLM-Based Evaluation Results

## Overview

This evaluation uses DeepEval with a model from OpenAI as the judge to assess abstract quality on multiple dimensions beyond simple string overlap.

## Evaluation Metrics

### 1. G-Eval: Coherence
Assesses the logical flow and organization of the abstract.

### 2. G-Eval: Scientific Accuracy  
Evaluates whether the abstract accurately represents the research without hallucinations or over-claiming.

### 3. Faithfulness
Measures whether the generated abstract is factually consistent with the source document.

### 4. Answer Relevancy
Assesses whether the abstract appropriately addresses the task of summarizing the document.

### 5. Hallucination Detection
Identifies whether the abstract contains information not present in the source document.

### 6. Summarization Quality
Evaluates how well the abstract captures key elements: research question, methods, results, and conclusions.

## Results

### Summary Statistics

"""
    
    # Add results
    for metric_name, metric_results in results.items():
        if metric_results:
            report += f"\n#### {metric_name}\n\n"
            scores = []
            if metric_name == 'geval':
                # Handle geval scores separately since they have coherence and accuracy
                for r in metric_results:
                    if 'coherence' in r:
                        scores.append(r['coherence'])
                    if 'accuracy' in r:
                        scores.append(r['accuracy'])
            else:
                # Handle other metrics normally
                scores = [r.get(f'{metric_name.lower()}_score', 0) for r in metric_results]
            
            if scores:
                avg_score = sum(scores) / len(scores)
                report += f"- Average Score: {avg_score:.3f}\n"
                report += f"- Number of Samples: {len(scores)} (coherence and accuracy)\n"
    

        report += "---\n"
    
    report += """

## Analysis

### Advantages of LLM-as-Judge Evaluation

1. **Nuanced Assessment:** Unlike ROUGE scores, LLM evaluation can assess semantic quality, logical flow, and scientific rigor.

2. **Explainable Results:** Each score comes with reasoning, providing actionable feedback for improvement.

### Limitations

1. **Cost:** LLM evaluation is more expensive than traditional metrics.

2. **Latency:** Slower than automated metrics (1-2 seconds per sample).

3. **Variability:** LLM judges may have some inconsistency across evaluations.

4. **Dependency:** Evaluation depends on the judge model's quality.

## Recommendations

### When to Use LLM Evaluation

- **Development Phase:** For deep analysis of a small sample to understand quality issues
- **Prompt Optimization:** To compare different prompt designs on nuanced quality dimensions

### When to Use Traditional Metrics

- **Large-Scale Evaluation:** For quick assessment of thousands of abstracts
- **Regression Testing:** To catch sudden drops in quality
- **Real-Time Monitoring:** For production systems requiring fast feedback

### Hybrid Approach (Recommended)

1. Use ROUGE/embedding metrics for continuous monitoring
2. Use LLM evaluation for:
   - Monthly quality audits
   - Prompt redesign validation
   - Investigation of edge cases

## Conclusion

LLM-based evaluation provides valuable insights into abstract quality that complement traditional metrics. While more expensive and slower, the explainable, nuanced assessments are invaluable for understanding and improving generation quality.
For a similar evaluation framework, see https://github.com/nsourlos/LLM_evaluation_framework
"""
    
    report_file = output_dir / "llm_evaluation_report.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"✓ LLM evaluation report saved to: {report_file}")


def main():
    """Main function"""
    print("=" * 60)
    print("TASK 4 BONUS: LLM-BASED EVALUATION")
    print("=" * 60)
    
    if not OPENAI_API_KEY:
        print("\n❌ Error: OPENAI_API_KEY not found")
        return
    
    # Estimate cost
    print("\nEstimating cost...")
    cost_estimate = estimate_evaluation_cost(
        n_samples=5,  # We limit to 5 samples for cost efficiency
        model=OPENAI_MODEL,
        n_metrics=5,  # G-Eval (2 metrics), Faithfulness, Relevancy, Hallucination, Summarization
        avg_input_tokens=2000,
        avg_output_tokens=200
    )
    
    # Display cost estimate and confirm
    if not print_cost_summary(
        task_name="LLM-Based Evaluation (DeepEval)",
        cost_dict=cost_estimate,
        proceed_prompt=True
    ):
        print("Evaluation cancelled.")
        return
    
    # Load data
    print("\nLoading data...")
    df = load_data(IMPROVED_DATA)
    print(f"✓ Loaded {len(df)} documents")
    
    # Create test cases
    print("\nCreating test cases...")
    test_cases = create_test_cases(df, use_improved=True)
    print(f"✓ Created {len(test_cases)} test cases")
    print("  (Evaluating first 5 for cost efficiency)")
    
    # Run evaluations
    results = {}
    
    try:
        results['geval'] = evaluate_with_geval(test_cases)
        results['faithfulness'] = evaluate_with_faithfulness(test_cases)
        results['relevancy'] = evaluate_with_relevancy(test_cases)
        results['hallucination'] = evaluate_with_hallucination(test_cases)
        results['summarization'] = evaluate_with_summarization(test_cases)
    except Exception as e:
        print(f"\n⚠ Warning: Some evaluations failed: {e}")
        print("This may be due to API limits or model availability.")
    
    # Save results to CSV
    print("\nSaving results to CSV...")
    save_results_to_csv(results, df, TASK4_DIR)
    
    # Generate report
    print("\nGenerating report...")
    generate_llm_eval_report(results, TASK4_DIR)
    
    print("\n" + "=" * 60)
    print("✓ LLM evaluation completed!")
    print("=" * 60)
    print("\nOutput files:")
    print(f"  - {TASK4_DIR / 'llm_evaluation_results.csv'}")
    print(f"  - {TASK4_DIR / 'llm_evaluation_results.xlsx'}")
    print(f"  - {TASK4_DIR / 'llm_evaluation_summary.csv'}")
    print(f"  - {TASK4_DIR / 'llm_evaluation_report.md'}")


if __name__ == "__main__":
    main()