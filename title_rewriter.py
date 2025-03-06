import openai
from openai import OpenAI
import os
import sys

def rewrite_titles(titles):
    """Uses OpenAI to generate rewritten slide titles."""
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # Check if API key exists
    if not api_key:
        print("\nError: OpenAI API key not found!")
        print("Please set your OPENAI_API_KEY as an environment variable:")
        print("  - Create a .env file with your API key (see .env.example)")
        print("  - Or set it directly in your terminal with:")
        print("    export OPENAI_API_KEY=your_api_key_here")
        print("\nNote: Never commit your actual API key to version control!")
        sys.exit(1)
    
    # Initialize the OpenAI client
    client = OpenAI()
    
    rewritten_titles = []
    for title in titles:
        prompt = f"""
        Rewrite the following slide title into three improved versions:
        1. Concise & Clear
        2. Executive-Friendly
        3. Storytelling-Driven

        Title: "{title}"
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an expert at improving presentation slide titles."},
                      {"role": "user", "content": prompt}]
        )
        rewritten_titles.append(response.choices[0].message.content.strip())
    return rewritten_titles 