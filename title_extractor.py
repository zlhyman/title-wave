from pptx import Presentation

def extract_slide_titles(pptx_path):
    """Extract slide titles from a PowerPoint presentation."""
    prs = Presentation(pptx_path)
    
    titles = []
    for slide in prs.slides:
        # Try to get the title from the slide
        title = ""
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text:
                # For simplicity, we'll assume the first shape with text is the title
                # A more robust solution would check shape type or placeholder type
                title = shape.text
                break
        
        # If no title found, provide a placeholder
        if not title:
            title = f"Slide #{len(titles)+1} (No Title)"
        
        titles.append(title)
    
    return titles 

def extract_slide_content(pptx_file):
    """Extract both titles and content from all slides"""
    presentation = Presentation(pptx_file)
    slides_data = []
    
    for slide in presentation.slides:
        slide_dict = {"title": "", "content": ""}
        
        # Extract title
        if slide.shapes.title:
            slide_dict["title"] = slide.shapes.title.text
        
        # Extract all text content from the slide
        content_text = []
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text:
                # Skip the title text to avoid duplication
                if shape != slide.shapes.title:
                    content_text.append(shape.text)
                    
        slide_dict["content"] = "\n".join(content_text)
        slides_data.append(slide_dict)
        
    return slides_data 