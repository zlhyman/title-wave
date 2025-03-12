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
    
    return rewrite_titles_with_key(titles, api_key)

def rewrite_titles_with_key(titles, api_key):
    """Generate three AI-enhanced versions of each title using OpenAI API."""
    client = OpenAI(api_key=api_key)
    
    rewritten_titles = []
    
    for title in titles:
        # Craft a prompt for this specific title
        prompt = f"""
        I need you to enhance the following presentation slide title:
        
        "{title}"
        
        Please provide THREE different versions of this title:
        1. Concise: A short, impactful version (3-5 words)
        2. Executive: Professional and clear for business presentations
        3. Storytelling: Engaging and narrative-focused
        
        Format as:
        1. Concise: [your title]
        2. Executive: [your title]
        3. Storytelling: [your title]
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
        )
        
        rewritten_titles.append(response.choices[0].message.content)
    
    return rewritten_titles

def rewrite_titles_with_context(slides_data, style_option, custom_guidance, api_key):
    """Rewrite titles based on entire presentation context and chosen style"""
    
    # Create client with API key
    client = OpenAI(api_key=api_key)
    
    # Prepare a more sophisticated prompt that includes the entire presentation context
    prompt = f"""
    You are a professional presentation consultant specializing in creating impactful slide titles.
    
    I'll provide you with the content of an entire presentation. For each slide, suggest a new title that:
    1. Captures the essence of the slide content
    2. Fits with the flow of the overall presentation
    3. Follows the selected style: {style_option}
    
    Here's the presentation structure:
    """
    
    # Add all slides to the context
    for i, slide in enumerate(slides_data):
        prompt += f"\nSLIDE {i+1}:\n"
        prompt += f"Current title: {slide['title']}\n"
        prompt += f"Content: {slide['content']}\n"
    
    # Add style guidance
    style_guidance = {
        "concise": "Create extremely concise, punchy titles (3-5 words) that use strong action verbs.",
        "descriptive": "Create descriptive titles that clearly explain the slide content using full phrases.",
        "engaging": "Create engaging, conversation-starting titles that use questions or provocative statements.",
        "formal": "Create formal, professional titles appropriate for executive presentations.",
        "creative": "Create creative, metaphorical titles that use imagery and figurative language."
    }
    
    prompt += f"\nStyle guidance: {style_guidance.get(style_option, 'Create clear, concise titles.')}\n"
    
    # Add custom guidance if provided
    if custom_guidance:
        prompt += f"\nAdditional guidance: {custom_guidance}\n"
    
    prompt += "\nFor each slide, provide exactly ONE suggested title that is truly unique and imaginative. Format your response as:\n"
    prompt += "Slide 1: [Your suggested title]\nSlide 2: [Your suggested title]\n..."
    
    # Call the OpenAI API with new client format
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.8  # Slightly higher temperature for more creativity
    )
    
    # Parse the response to extract the suggested titles
    result = response.choices[0].message.content
    suggested_titles = []
    
    for line in result.split('\n'):
        if line.startswith('Slide ') and ':' in line:
            title = line.split(':', 1)[1].strip()
            suggested_titles.append(title)
    
    return suggested_titles 