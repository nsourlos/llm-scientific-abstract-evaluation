"""
Task 3: Generate improved abstracts using OpenAI API with better prompt

This script:
1. Loads the improved prompt
2. Calls OpenAI API to generate new abstracts
3. Saves the results
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from openai import OpenAI
from tqdm import tqdm
import time
from src.config import (
    ORIGINAL_DATA, IMPROVED_PROMPT, IMPROVED_DATA, 
    OPENAI_API_KEY, OPENAI_MODEL
)
from src.utils import load_data, save_data, load_prompt
from src.cost_estimator import estimate_generation_cost, print_cost_summary


def generate_abstract(client: OpenAI, full_text: str, prompt_template: str, model: str) -> str:
    """
    Generate an abstract using OpenAI API
    
    Args:
        client: OpenAI client
        full_text: Full text of the scientific document
        prompt_template: Prompt template with {full_text} placeholder
        model: OpenAI model to use
    
    Returns:
        Generated abstract
    """
    # Format the prompt
    prompt = prompt_template.format(full_text=full_text)

    try:
        # Use max_completion_tokens for newer OpenAI API versions (v1.0+)
        completion_args = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an expert scientific writer specializing in writing concise, accurate abstracts for scientific papers."},
                {"role": "user", "content": prompt}
            ],
        }
        
        if model != "gpt-5-nano":
            completion_args["temperature"] = 0.01  # Lower temperature for more consistent, factual outputs
            completion_args["max_completion_tokens"] = 500 # Typical abstract length (updated parameter name)

        response = client.chat.completions.create(**completion_args)

        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Error generating abstract: {e}")
        return ""


def generate_all_abstracts(df: pd.DataFrame, prompt_template: str, model: str) -> pd.DataFrame:
    """
    Generate abstracts for all documents in the dataframe
    
    Args:
        df: Dataframe with 'full_text' column
        prompt_template: Prompt template
        model: OpenAI model name
    
    Returns:
        Dataframe with 'improved_abstract' column
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    improved_abstracts = []
    
    print(f"Generating abstracts using {model}...")
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        abstract = generate_abstract(client, row['full_text'], prompt_template, model)
        improved_abstracts.append(abstract)
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    df['improved_abstract'] = improved_abstracts
    
    return df


def create_improved_prompt() -> str:
    """
    Create an improved prompt based on qualitative analysis
    
    This prompt addresses the key issues found in Task 2:
    1. Lack of structure and scientific format
    2. Missing key components (methods, results, conclusions)
    3. Inconsistent length and detail
    4. Potential hallucinations
    """
    
    improved_prompt = """Write a scientific abstract for the following research article. 

REQUIREMENTS:
1. Structure: Follow the standard scientific abstract format with these components:
   - Background/Context (1-2 sentences): Why is this research important?
   - Objective/Purpose (1 sentence): What is the main goal?
   - Methods (1-2 sentences): How was the study conducted?
   - Results (2-3 sentences): What were the key findings?
   - Conclusion (1-2 sentences): What do the findings mean?

2. Style:
   - Use formal, scientific language
   - Be concise and precise
   - Use past tense for methods and results
   - Use present tense for conclusions and implications
   - Avoid promotional or exaggerated language

3. Content:
   - Only include information explicitly stated in the article
   - Focus on the most significant findings and contributions
   - Include specific data points and metrics when available
   - Do not add interpretations beyond what the article states

4. Length: Aim for 150-250 words (typical abstract length)

5. Accuracy:
   - Do NOT hallucinate or invent information
   - Do NOT include speculative statements
   - Do NOT over-claim the significance of findings

Article text:
{full_text}

Write the abstract below:"""

    return improved_prompt


def main():
    """Main function to generate improved abstracts"""
    print("=" * 60)
    print("TASK 3: GENERATE IMPROVED ABSTRACTS")
    print("=" * 60)
    
    # Check API key
    if not OPENAI_API_KEY:
        print("\n❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please ensure .env file contains OPENAI_API_KEY")
        return
    
    # Create improved prompt
    print("\n1. Creating improved prompt...")
    improved_prompt = create_improved_prompt()
    
    # Save improved prompt
    improved_prompt_file = Path(__file__).parent.parent / "data" / "improved_prompt.txt"
    with open(improved_prompt_file, 'w') as f:
        f.write(improved_prompt)
    print(f"✓ Improved prompt saved to: {improved_prompt_file}")
    
    # Load data
    print("\n2. Loading original data...")
    df = load_data(ORIGINAL_DATA)
    print(f"✓ Loaded {len(df)} documents")
    
    # Estimate cost
    print(f"\n3. Estimating cost...")
    cost_estimate = estimate_generation_cost(
        df=df,
        prompt_template=improved_prompt,
        model=OPENAI_MODEL,
        max_output_tokens=500,
        n_samples=None
    )
    
    # Display cost estimate and confirm
    if not print_cost_summary(
        task_name="Abstract Generation",
        cost_dict=cost_estimate,
        proceed_prompt=True
    ):
        print("Generation cancelled.")
        return
    
    print(f"\n4. Generating abstracts using {OPENAI_MODEL}...")
    print(f"   Time estimate: ~2-3 minutes for {len(df)} documents")
    
    df_improved = generate_all_abstracts(df, improved_prompt, OPENAI_MODEL)
    
    # Save results
    print("\n5. Saving results...")
    save_data(df_improved, IMPROVED_DATA)
    print(f"✓ Improved abstracts saved to: {IMPROVED_DATA}")
    
    # Preview results
    print("\n6. Preview of improved abstracts:")
    print("-" * 60)
    for i in range(min(2, len(df_improved))):
        print(f"\nDocument {i+1}: {df_improved.iloc[i]['title'][:60]}...")
        print(f"\nImproved Abstract:\n{df_improved.iloc[i]['improved_abstract'][:200]}...\n")
        print("-" * 60)
    
    # Display actual cost summary
    print("\n7. Cost Summary:")
    print(f"   Estimated cost: ${cost_estimate['estimated_total_cost_usd']:.4f}")
    print(f"   (Actual cost may vary slightly based on exact token counts)")
    
    print("\n" + "=" * 60)
    print("✓ Task 3 generation completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()