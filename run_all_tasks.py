"""
Main runner script to execute all tasks in sequence

This script provides a convenient way to run all tasks or individual tasks.
"""

import sys
import argparse
from pathlib import Path


def run_task1():
    """Run Task 1: Quantitative Metrics"""
    print("\n" + "="*80)
    print("RUNNING TASK 1: QUANTITATIVE METRICS")
    print("="*80)
    
    from task1_quantitative_metrics.compute_metrics import main
    main()
    
    # Ask if user wants to generate visualizations
    try:
        visualize = input("\nGenerate visualizations for Task 1? (y/n): ")
        if visualize.lower() == 'y':
            from task1_quantitative_metrics.visualize_results import main as viz_main
            viz_main()
    except KeyboardInterrupt:
        print("\nSkipping visualizations...")


def run_task2():
    """Run Task 2: Qualitative Review"""
    print("\n" + "="*80)
    print("RUNNING TASK 2: QUALITATIVE REVIEW")
    print("="*80)
    
    from task2_qualitative_review.select_samples import main
    main()


def run_task3_generate():
    """Run Task 3: Generate Improved Abstracts"""
    print("\n" + "="*80)
    print("RUNNING TASK 3: GENERATE IMPROVED ABSTRACTS")
    print("="*80)
    
    from task3_improvements.generate_abstracts import main
    main()


def run_task3_compare():
    """Run Task 3: Compare Results"""
    print("\n" + "="*80)
    print("RUNNING TASK 3: COMPARE RESULTS")
    print("="*80)
    
    from task3_improvements.compare_results import main
    main()
    
    # Ask if user wants to generate visualizations
    try:
        visualize = input("\nGenerate comparison visualizations? (y/n): ")
        if visualize.lower() == 'y':
            from task3_improvements.visualize_comparison import main as viz_main
            viz_main()
    except KeyboardInterrupt:
        print("\nSkipping visualizations...")


def run_task4_llm_eval():
    """Run Task 4: LLM Evaluation"""
    print("\n" + "="*80)
    print("RUNNING TASK 4: LLM EVALUATION")
    print("="*80)
    
    from task4_bonus.llm_evaluation import main
    main()


def run_task4_dspy():
    """Run Task 4: DSPy Optimization"""
    print("\n" + "="*80)
    print("RUNNING TASK 4: DSPy OPTIMIZATION")
    print("="*80)
    
    from task4_bonus.prompt_optimization import main
    main()


def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(
        description="Run LLM evaluation tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_tasks.py --all              # Run all tasks (requires API key)
  python run_all_tasks.py --task 1           # Run only Task 1
  python run_all_tasks.py --task 1 2         # Run Tasks 1 and 2
  python run_all_tasks.py --no-api           # Run tasks that don't require API
        """
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all tasks in sequence'
    )
    
    parser.add_argument(
        '--task',
        type=int,
        nargs='+',
        choices=[1, 2, 3, 4],
        help='Run specific task(s) (1-4)'
    )
    
    parser.add_argument(
        '--no-api',
        action='store_true',
        help='Run only tasks that don\'t require OpenAI API (Task 1 and Task 2 selection)'
    )
    
    parser.add_argument(
        '--skip-generation',
        action='store_true',
        help='Skip abstract generation (assumes already generated)'
    )
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if not (args.all or args.task or args.no_api):
        parser.print_help()
        return
    
    print("\n" + "="*80)
    print("SPRINGER NATURE - LLM EVALUATION ASSIGNMENT")
    print("="*80)
    
    try:
        if args.no_api:
            print("\nRunning tasks that don't require API...")
            run_task1()
            run_task2()
            print("\n✓ Non-API tasks completed!")
            print("\nNext steps:")
            print("  1. Review qualitative_report_template.md and fill in analyses")
            print("  2. Run Task 3 to generate improved abstracts (requires API)")
            
        elif args.all:
            print("\nRunning all tasks...")
            run_task1()
            run_task2()
            
            print("\n⚠ Task 2 requires manual qualitative analysis.")
            print("  Please review and complete the qualitative report before proceeding.")
            print("  File: task2_qualitative_review/qualitative_report_template.md")
            
            cont = input("\nContinue with Task 3 (generation)? (y/n): ")
            if cont.lower() == 'y':
                run_task3_generate()
                run_task3_compare()
                
                cont = input("\nContinue with Task 4 (bonus)? (y/n): ")
                if cont.lower() == 'y':
                    run_task4_llm_eval()
                    run_task4_dspy()
            
        elif args.task:
            for task_num in sorted(args.task):
                if task_num == 1:
                    run_task1()
                elif task_num == 2:
                    run_task2()
                elif task_num == 3:
                    if not args.skip_generation:
                        run_task3_generate()
                    run_task3_compare()
                elif task_num == 4:
                    choice = input("\nTask 4 options:\n  1. LLM Evaluation\n  2. DSPy Optimization\n  3. Both\nChoice (1/2/3): ")
                    if choice in ['1', '3']:
                        run_task4_llm_eval()
                    if choice in ['2', '3']:
                        run_task4_dspy()
        
        print("\n" + "="*80)
        print("✓ ALL REQUESTED TASKS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\nGenerated files can be found in their respective task directories.")
        print("See README.md for detailed documentation.")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()