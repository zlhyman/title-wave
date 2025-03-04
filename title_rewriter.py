import openai

def rewrite_titles(titles):
    """Uses OpenAI to generate rewritten slide titles."""
    rewritten_titles = []
    for title in titles:
        prompt = f"""
        Rewrite the following slide title into three improved versions:
        1. Concise & Clear
        2. Executive-Friendly
        3. Storytelling-Driven

        Title: "{title}"
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an expert at improving presentation slide titles."},
                      {"role": "user", "content": prompt}]
        )
        rewritten_titles.append(response['choices'][0]['message']['content'].strip())
    return rewritten_titles 