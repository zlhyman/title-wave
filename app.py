import streamlit as st
import os
import tempfile
from title_extractor import extract_slide_titles
from title_rewriter import rewrite_titles
from pptx_updater import update_pptx_titles

st.set_page_config(page_title="TitleWave", page_icon="📊")

st.title("TitleWave - AI-Powered Slide Title Enhancer")
st.markdown("Upload your PowerPoint presentation and get AI-enhanced slide titles!")

# File uploader
uploaded_file = st.file_uploader("Choose a PowerPoint file", type=["ppt", "pptx"])

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_pptx_path = tmp_file.name
    
    # Extract titles
    with st.spinner("Extracting slide titles..."):
        titles = extract_slide_titles(temp_pptx_path)
    
    st.subheader("Original Slide Titles")
    for i, title in enumerate(titles):
        st.write(f"Slide {i+1}: {title}")
    
    # Rewrite titles with AI
    if st.button("Generate AI-Enhanced Titles"):
        with st.spinner("Generating improved titles with AI..."):
            rewritten_titles_raw = rewrite_titles(titles)
            
            # Parse the raw responses into structured data
            all_rewritten_options = []
            for slide_response in rewritten_titles_raw:
                options = slide_response.split("\n")
                # Clean up and extract just the title text (remove numbering and category)
                cleaned_options = []
                for option in options:
                    if ":" in option and any(prefix in option for prefix in ["1. Concise", "2. Executive", "3. Storytelling"]):
                        cleaned_options.append(option.split(": ", 1)[1].strip())
                if cleaned_options:
                    all_rewritten_options.append(cleaned_options)
                else:
                    # Fallback if parsing failed
                    all_rewritten_options.append([f"Enhanced: {titles[len(all_rewritten_options)]}"])
        
        # Create a selection interface for each slide
        st.subheader("Select New Titles")
        selected_titles = []
        
        for i, options in enumerate(all_rewritten_options):
            st.markdown(f"**Slide {i+1}**")
            st.markdown(f"*Original: {titles[i]}*")
            
            # Add option to keep original
            options = ["[Keep Original]"] + options
            
            # Create radio buttons for selection
            selection = st.radio(
                f"Choose title for slide {i+1}:",
                options,
                key=f"slide_{i}"
            )
            
            # Store the selection (or keep original if that's what was selected)
            if selection == "[Keep Original]":
                selected_titles.append(titles[i])
            else:
                selected_titles.append(selection)
        
        # Create and provide the updated presentation for download
        if st.button("Create Updated Presentation"):
            with st.spinner("Updating presentation with new titles..."):
                # Create a new temp file for the output
                output_pptx_path = temp_pptx_path.replace('.pptx', '_updated.pptx')
                update_pptx_titles(temp_pptx_path, selected_titles, output_pptx_path)
                
                # Read the updated file for download
                with open(output_pptx_path, "rb") as file:
                    updated_pptx_bytes = file.read()
                
                st.success("Presentation updated successfully!")
                
                # Provide download button
                st.download_button(
                    label="Download Updated Presentation",
                    data=updated_pptx_bytes,
                    file_name=uploaded_file.name.replace('.pptx', '_enhanced.pptx').replace('.ppt', '_enhanced.pptx'),
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
                
                # Clean up temp files
                try:
                    os.unlink(temp_pptx_path)
                    os.unlink(output_pptx_path)
                except:
                    pass 