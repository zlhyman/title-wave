from pptx import Presentation

def update_pptx_titles(original_pptx_path, new_titles, output_pptx_path):
    """Updates PowerPoint file with new titles."""
    prs = Presentation(original_pptx_path)
    title_index = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text:
                text = shape.text_frame.text.strip()
                if len(text) < 100 and title_index < len(new_titles):
                    shape.text_frame.text = new_titles[title_index]
                    title_index += 1
    prs.save(output_pptx_path) 