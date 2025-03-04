from pptx import Presentation

def extract_slide_titles(pptx_path):
    """Extracts slide titles from a PowerPoint file."""
    prs = Presentation(pptx_path)
    titles = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text:
                text = shape.text_frame.text.strip()
                if len(text) < 100:  # Filter for titles (assuming shorter text blocks)
                    titles.append(text)
    return titles 