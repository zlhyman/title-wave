import os
from title_extractor import extract_slide_titles
from title_rewriter import rewrite_titles
from pptx_updater import update_pptx_titles

def main():
    print("Welcome to TitleWave - Your AI-Powered Slide Title Enhancer!\n")
    pptx_path = "example.pptx"  # Replace with actual path
    output_pptx_path = "updated_presentation.pptx"
    
    titles = extract_slide_titles(pptx_path)
    rewritten_titles = rewrite_titles(titles)
    
    print("\nOriginal Titles:")
    for title in titles:
        print(f"- {title}")
    
    print("\nRewritten Titles:")
    for title in rewritten_titles:
        print(f"- {title}")
    
    # Allow manual selection before updating the PowerPoint file
    print("\nWould you like to apply these titles? (yes/no)")
    choice = input().strip().lower()
    if choice == "yes":
        update_pptx_titles(pptx_path, rewritten_titles, output_pptx_path)
        print(f"Updated presentation saved as {output_pptx_path}")
    else:
        print("No changes were applied.")

if __name__ == "__main__":
    main() 