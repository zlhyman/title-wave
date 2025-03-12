import openai
from openai import OpenAI
import os
import sys
import time
import random

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
    
    # Prepare prompt
    prompt = f"""
    You are a professional presentation consultant specializing in creating impactful slide titles.
    
    I'll provide you with the content of a presentation. For each slide, suggest TWO DIFFERENT title options that:
    1. Capture the essence of the slide content
    2. Fit with the flow of the overall presentation
    3. Follow the selected style: {style_option}
    
    Here's the presentation structure:
    """
    
    # Add slides to context
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
    
    prompt += """
    For each slide, provide EXACTLY TWO different title suggestions that offer distinct approaches.
    Format your response precisely as:
    
    Slide 1:
    Option A: [Your first suggested title]
    Option B: [Your second suggested title]
    
    Slide 2:
    Option A: [Your first suggested title]
    Option B: [Your second suggested title]
    
    And so on for each slide.
    """
    
    # Call OpenAI API with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.8
            )
            break
        except Exception as e:
            if "RateLimitError" in str(type(e)) and attempt < max_retries - 1:
                # Exponential backoff with jitter
                sleep_time = (2 ** attempt) + random.random()
                time.sleep(sleep_time)
            else:
                raise
    
    # Parse the response to extract the suggested titles
    result = response.choices[0].message.content
    
    # Process format with two options per slide
    slides_suggestions = []
    current_slide = None
    options = []
    
    for line in result.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('Slide '):
            # If we were processing a slide, save its options
            if current_slide is not None and options:
                slides_suggestions.append(options)
                options = []
            
            # Start a new slide
            current_slide = line
        elif line.startswith('Option A:'):
            options.append(line[line.find(':')+1:].strip())
        elif line.startswith('Option B:'):
            options.append(line[line.find(':')+1:].strip())
    
    # Add the last slide's options
    if options:
        slides_suggestions.append(options)
    
    return slides_suggestions 