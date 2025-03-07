import streamlit as st
import os
import tempfile
import json
import uuid
import datetime
from pathlib import Path
from title_extractor import extract_slide_titles
from title_rewriter import rewrite_titles_with_key
from pptx_updater import update_pptx_titles

# Admin API key (your key) - in production, store this in environment variables
ADMIN_API_KEY = "sk-your-api-key-here" 
FREE_TIER_LIMIT = 5  # Number of free decks per month per user

# Set up page config - use centered layout for consistency
st.set_page_config(
    page_title="TitleWave",
    page_icon="🌊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide default elements and set styling
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {background-color: #E0D3AF;}
    
    /* Add space AFTER the expander */
    div[data-testid="stExpander"] {
        margin-bottom: 20px !important;  /* Adjust this value as needed */
    }
            
    /* Import Poppins font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    /* Apply Poppins to main title */
    .custom-title {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700 !important;
        font-size: 3.5rem !important;
        margin-bottom: 0.5rem !important;
        color: #333 !important;
        text-align: center !important;
    }
    
    /* Subtitle styling */
    .custom-subtitle {
        font-size: 1.2rem !important;
        margin-top: 0 !important;
        margin-bottom: 2rem !important;
        color: #555 !important;
        text-align: center !important;
    }
    
    /* Add space above the file uploader */
    section[data-testid="stFileUploader"] {
        margin-top: 40px !important;
    }

    /* Remove space between info/success messages */
    .element-container:has(.stProgress) {
        margin-bottom: -15px !important;
    }
    
    /* Adjust padding on info/success messages */
    .stAlert {
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'using_free_tier' not in st.session_state:
    st.session_state.using_free_tier = True
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# IMPORTANT: Define these functions BEFORE using them
def get_user_usage():
    """Get usage for current user in current month"""
    usage_file = Path("usage_data.json")
    user_id = st.session_state.user_id
    current_month = datetime.datetime.now().strftime("%Y-%m")
    
    if usage_file.exists():
        try:
            with open(usage_file, 'r') as f:
                usage_data = json.load(f)
        except:
            usage_data = {}
    else:
        usage_data = {}
    
    if user_id not in usage_data:
        usage_data[user_id] = {}
    
    if current_month not in usage_data[user_id]:
        usage_data[user_id][current_month] = 0
    
    return usage_data[user_id][current_month], usage_data, usage_file, current_month

def increment_usage():
    """Increment usage for current user"""
    usage, usage_data, usage_file, current_month = get_user_usage()
    user_id = st.session_state.user_id
    
    usage_data[user_id][current_month] += 1
    
    with open(usage_file, 'w') as f:
        json.dump(usage_data, f)
    
    return usage_data[user_id][current_month]

# Function to get the appropriate API key
def get_active_api_key():
    if st.session_state.using_free_tier and free_tier_available:
        return ADMIN_API_KEY
    else:
        return st.session_state.api_key

# Custom title with wave emoji
st.markdown('<div class="custom-title">🌊 TitleWave</div>', unsafe_allow_html=True)
st.markdown('<div class="custom-subtitle">Upload your PowerPoint presentation to get AI-enhanced slide titles!</div>', unsafe_allow_html=True)

# ----- MOVED FILE UPLOADER HERE -----
# Show the file uploader first
st.markdown('<div style="margin-bottom: 30px;"></div>', unsafe_allow_html=True)  # Space before file uploader
uploaded_file = st.file_uploader("Choose a PowerPoint file", type=["ppt", "pptx"])
st.markdown('<div style="margin-bottom: 30px;"></div>', unsafe_allow_html=True)  # Space after file uploader

# ----- THEN SHOW USAGE INFO -----
# Usage information
current_usage, _, _, _ = get_user_usage()
usage_percentage = min(100, (current_usage / FREE_TIER_LIMIT) * 100)
free_tier_available = current_usage < FREE_TIER_LIMIT

# Display usage meter
usage_html = f"""
<div style="background-color: rgba(0, 0, 0, 0.1); padding: 15px; border-radius: 5px; margin-bottom: 0;">
    <div style="color: #31708f; margin-bottom: 10px;">
        Free tier usage: {current_usage}/{FREE_TIER_LIMIT} presentations this month
    </div>
    <div style="height: 10px; background-color: #f5f5f5; border-radius: 5px; margin: 10px 0;">
        <div style="height: 100%; width: {usage_percentage}%; background-color: #4CAF50; border-radius: 5px;"></div>
    </div>
</div>
"""
st.markdown(usage_html, unsafe_allow_html=True)

# "No API key required" message
if free_tier_available:
    message_html = """
    <div style="background-color: rgba(76, 175, 80, 0.1); padding: 15px; border-radius: 5px; margin-top: 0; margin-bottom: 20px; color: #3c763d;">
        No API key required - just upload your presentation!
    </div>
    """
    st.markdown(message_html, unsafe_allow_html=True)
else:
    # Warning message for exceeded limit
    message_html = """
    <div style="background-color: rgba(217, 83, 79, 0.1); padding: 15px; border-radius: 5px; margin-top: 0; margin-bottom: 20px; color: #a94442;">
        ⚠️ You've reached your free tier limit for this month. Please enter your own OpenAI API key to continue.
    </div>
    """
    st.markdown(message_html, unsafe_allow_html=True)

# API key handling with expander
with st.expander("Already have an OpenAI API key? (optional)", expanded=False):
    st.markdown("""
    <small>If you already have your own OpenAI API key, you can use it instead of the free tier.</small>
    """, unsafe_allow_html=True)
    
    use_own_key = st.checkbox("Use my own API key", value=not st.session_state.using_free_tier)
    
    if use_own_key:
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.api_key,
            placeholder="sk-...",
            help="Get your API key from https://platform.openai.com/api-keys"
        )
        
        if api_key:
            st.session_state.api_key = api_key
            st.session_state.using_free_tier = False
            st.success("Your API key is set for this session.")
        else:
            st.session_state.using_free_tier = True
    else:
        st.session_state.using_free_tier = True

# File uploader - only show if free tier is available or user provided API key
show_uploader = (st.session_state.using_free_tier and free_tier_available) or st.session_state.api_key
if show_uploader:
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_pptx_path = tmp_file.name
        
        # Extract titles
        with st.spinner("Extracting slide titles..."):
            titles = extract_slide_titles(temp_pptx_path)
        
        # Initialize session state for title editing if not already present
        if 'edited_titles' not in st.session_state:
            st.session_state.edited_titles = titles.copy()
        if 'titles_confirmed' not in st.session_state:
            st.session_state.titles_confirmed = False
        
        # Title editing and confirmation section
        st.subheader("Review and Edit Slide Titles")
        st.write("Please review the extracted titles and edit them if needed before generating AI-enhanced versions.")
        
        edited_titles = []
        # Create text inputs for each title
        for i, title in enumerate(titles):
            # Use the session state value if it exists, otherwise use the extracted title
            current_value = st.session_state.edited_titles[i] if i < len(st.session_state.edited_titles) else title
            edited_title = st.text_input(f"Slide {i+1}", value=current_value, key=f"edit_title_{i}")
            edited_titles.append(edited_title)
        
        # Confirm button
        if st.button("Confirm Titles"):
            st.session_state.edited_titles = edited_titles
            st.session_state.titles_confirmed = True
            st.success("Titles confirmed! You can now generate AI-enhanced versions.")
            st.experimental_rerun()  # Rerun to update the UI
        
        # Only show the Generate AI-Enhanced Titles button if titles are confirmed
        if st.session_state.titles_confirmed:
            # Use the edited titles instead of the original extracted ones
            titles_to_use = st.session_state.edited_titles
            
            st.subheader("Generate Enhanced Titles")
            # Generate AI-Enhanced Titles button
            if st.button("Generate AI-Enhanced Titles"):
                # If using free tier, increment usage counter
                if st.session_state.using_free_tier:
                    increment_usage()
                
                with st.spinner("Generating AI-enhanced titles..."):
                    # Get rewritten titles using the appropriate API key
                    active_api_key = get_active_api_key()
                    rewritten_titles_raw = rewrite_titles_with_key(titles_to_use, active_api_key)
                    
                    # Parse the raw responses
                    all_rewritten_options = []
                    for slide_response in rewritten_titles_raw:
                        options = slide_response.split("\n")
                        # Clean up and extract just the title text
                        cleaned_options = []
                        for option in options:
                            if ":" in option and any(prefix in option for prefix in ["1. Concise", "2. Executive", "3. Storytelling"]):
                                cleaned_options.append(option.split(": ", 1)[1].strip())
                        if cleaned_options:
                            all_rewritten_options.append(cleaned_options)
                        else:
                            # Fallback if parsing failed
                            all_rewritten_options.append([f"Enhanced: {titles_to_use[len(all_rewritten_options)]}"])
                    
                    # Store in session state to persist across reruns
                    st.session_state.all_rewritten_options = all_rewritten_options
                    st.session_state.show_selection = True
                    st.experimental_rerun()  # Rerun to update the UI with selection interface
            
            # Display title selection interface if available
            if 'show_selection' in st.session_state and st.session_state.show_selection and 'all_rewritten_options' in st.session_state:
                st.subheader("Select New Titles")
                selected_titles = []
                
                for i, options in enumerate(st.session_state.all_rewritten_options):
                    if i < len(titles_to_use):  # Safety check
                        st.markdown(f"**Slide {i+1}**")
                        st.markdown(f"*Original: {titles_to_use[i]}*")
                        
                        # Add option to keep original
                        options = ["[Keep Original]"] + options
                        
                        # Create radio buttons for selection
                        selection = st.radio(
                            f"Choose title for slide {i+1}:",
                            options,
                            key=f"slide_{i}"
                        )
                        
                        # Store the selection
                        if selection == "[Keep Original]":
                            selected_titles.append(titles_to_use[i])
                        else:
                            selected_titles.append(selection)
                
                # Button to create the updated presentation
                if st.button("Create Updated Presentation"):
                    with st.spinner("Updating presentation..."):
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
                            os.unlink(output_pptx_path)
                        except:
                            pass
else:
    # This is the warning that shows at the bottom - only show if needed
    if not free_tier_available and not st.session_state.api_key:
        st.info("Please enter your OpenAI API key above to use the application.")

# Clean up temp files on session end
if 'temp_pptx_path' in locals():
    try:
        os.unlink(temp_pptx_path)
    except:
        pass 