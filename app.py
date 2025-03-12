import streamlit as st
import os
import tempfile
import json
import uuid
import datetime
from pathlib import Path
from title_extractor import extract_slide_titles
from title_rewriter import rewrite_titles_with_key, rewrite_titles_with_context
from pptx_updater import update_pptx_titles
import traceback

# Admin API key (your key) - in production, store this in environment variables
ADMIN_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
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
    
    /* Accessibility-friendly section headers */
    h1, h2, h3 {
        color: #1A3E6C !important; /* Deep blue for accessibility */
    }
    
    .stRadio label {
        color: #2C3E50 !important; /* Dark slate for accessibility */
    }
    
    /* Make the customize section header more accessible */
    .customize-header {
        color: #1A3E6C !important;
        font-weight: 600;
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Make ALL free-floating text dark slate for better legibility */
    body, p, li, label, .stMarkdown, .stText, .stRadio label, .stCheckbox label, 
    .stSelectbox label, .stTextInput label, .stTextArea label, .stNumberInput label,
    .stExpander, .stRadio span, .stCheckbox span, .stSelectbox span {
        color: #2C3E50 !important;
    }
    
    /* Style for section headers - keep the deep blue */
    h1, h2, h3, h4, h5, h6 {
        color: #1A3E6C !important;
        font-weight: 600 !important;
    }
    
    /* Ensure inline text is also styled */
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: #2C3E50 !important;
    }
    
    /* Make sure upload instructions and other hints are legible */
    .stFileUploader label, .stFileUploader span,
    .uploadedFileName, .stAlert {
        color: #2C3E50 !important;
    }
    
    /* Ensure text inputs show dark text */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        color: #2C3E50 !important;
    }
    
    /* Style specifically for slide title instructions */
    .stMarkdown em {
        color: #2C3E50 !important;
    }
    
    /* Small text elements */
    small, .stMarkdown small {
        color: #2C3E50 !important;
    }
    
    /* Emphasize current selection in radio buttons */
    .stRadio [data-baseweb="radio"] input:checked + div::before {
        background-color: #1A3E6C !important;
    }
    
    /* Only target specific text elements */
    .stMarkdown p, 
    .stMarkdown li,
    label:not([class*="Upload"]),
    .stSubheader,
    .stRadio label,
    h4:not([class]) {
        color: #2C3E50 !important;
    }
    
    /* Section headers */
    h1, h2, h3 {
        color: #1A3E6C !important;
    }
    
    /* Target ONLY the file uploader background - nothing else */
    [data-testid="stFileUploader"] > div:first-child > div:first-child {
        background-color: white !important;
    }

    /* The most minimal, surgical approach - just one line of actual CSS */
    div[data-testid="stFileUploader"] > section > div {
        background-color: white;
    }

    /* Just target the inner box with minimal CSS */
    div[data-testid="stFileUploader"] section div div {
        background-color: white;
    }

    /* Target ONLY the file uploader inner box background */
    [data-testid="stFileUploadDropzoneContent"] {
        background-color: #262730 !important;
        color: white !important;
    }

    /* Ensure text and icon are visible on dark background */
    [data-testid="stFileUploadDropzoneContent"] p {
        color: white !important;
    }

    [data-testid="stFileUploadDropzoneContent"] svg {
        color: white !important;
        fill: white !important;
    }

    /* Target the inner white box with extreme specificity */
    div[data-testid="stFileUploadDropzoneContent"] {
        background-color: #262730 !important;
    }

    /* Make the text white */
    div[data-testid="stFileUploadDropzoneContent"] > div {
        color: white !important;
    }

    /* Make the icon white */
    div[data-testid="stFileUploadDropzoneContent"] svg path {
        fill: white !important;
        stroke: white !important;
    }

    /* Also target possible variations */
    [data-testid="stFileUploader"] div[role="button"] {
        background-color: #262730 !important;
    }

    [data-testid="stFileUploader"] div[role="button"] * {
        color: white !important;
    }

    /* Fix that white box once and for all by styling properly */
    div[data-testid="stFileUploadDropzoneContent"] {
        background-color: transparent !important;
    }

    /* Make upload box prettier and consistent */
    [data-testid="stFileUploader"] section div {
        border: 2px dashed #aaa !important;
        border-radius: 5px !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
    }

    /* Fix text colors for visibility */
    [data-testid="stFileUploadDropzoneContent"] div {
        color: #333 !important;
    }

    /* Make icon visible */
    [data-testid="stFileUploadDropzoneContent"] svg path {
        fill: #4682B4 !important;
    }

    /* Style browse button */
    [data-testid="stFileUploader"] button {
        background-color: #4682B4 !important;
        color: white !important;
    }

    /* Make the outer container transparent with black outline */
    [data-testid="stFileUploader"] {
        border: 1px solid black !important;
    }

    [data-testid="stFileUploader"] > section {
        background-color: transparent !important;
    }

    /* Fix the inner container with solid light grey border */
    [data-testid="stFileUploadDropzoneContent"] {
        background-color: rgba(255, 255, 255, 0.7) !important;
        border: 1px solid black !important;
    }

    /* Remove dotted lines specifically */
    [data-testid="stFileUploadDropzoneContent"] svg {
        stroke: black !important;
    }

    /* Minimal change to fix dotted lines */
    [data-testid="stFileUploadDropzoneContent"] {
        border: 1px solid black !important;
    }

    /* Target ONLY the dropzone content with a dashed border - this is the exact selector that worked before */
    div[data-testid="stFileUploadDropzoneContent"] {
        border: 2px dashed #aaa !important;
        border-radius: 5px !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-style: dashed !important; /* Explicitly set dashed style */
    }

    /* Nuclear approach to eliminate dotted lines */
    [data-testid="stFileUploadDropzoneContent"],
    [data-testid="stFileUploadDropzoneContent"] *,
    [data-testid="stFileUploadDropzoneContent"] *::before,
    [data-testid="stFileUploadDropzoneContent"] *::after {
        border-style: solid !important;
        stroke-dasharray: 0 !important;
    }

    /* Direct replacement with solid border */
    [data-testid="stFileUploadDropzoneContent"] {
        border: 2px solid #aaa !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
    }

    /* Target SVG elements that might be creating the dotted effect */
    [data-testid="stFileUploadDropzoneContent"] svg,
    [data-testid="stFileUploadDropzoneContent"] svg * {
        stroke-dasharray: 0 !important;
        stroke-dashoffset: 0 !important;
        stroke-linecap: butt !important;
        stroke-linejoin: miter !important;
    }

    /* Absolutely ensure no element is using a rect with stroke-dasharray */
    rect {
        stroke-dasharray: 0 !important;
    }

    /* Reset ONLY the file uploader components to defaults */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploadDropzoneContent"] {
        all: revert !important;
    }

    /* Ensure we're only targeting the specific uploader elements */
    [data-testid="stFileUploadDropzoneContent"] * {
        all: revert !important;
    }

    /* Hide the original border completely by setting its width to 0 */
    [data-testid="stFileUploadDropzoneContent"] {
        border-width: 0 !important;
        outline-width: 0 !important;
        box-shadow: none !important;
    }

    /* Create a completely new border using an absolutely positioned pseudo-element */
    [data-testid="stFileUploadDropzoneContent"]::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border: 2px solid #aaa;
        border-radius: 5px;
        pointer-events: none;
        z-index: 100;
    }

    /* Change that red outer border to black */
    [data-testid="stFileUploader"] {
        border-color: black !important;
    }

    /* Make the dotted lines very light, almost invisible */
    [data-testid="stFileUploadDropzoneContent"],
    [data-testid="stFileUploadDropzoneContent"] * {
        border-color: rgba(200, 200, 200, 0.3) !important;
    }

    /* Slightly lighten the outer border */
    [data-testid="stFileUploader"] {
        border-color: rgba(0, 0, 0, 0.5) !important;
    }

    /* Ensure text is readable */
    [data-testid="stFileUploadDropzoneContent"] div {
        color: #333 !important;
    }

    /* Reposition the "Browse files" button */
    [data-testid="stFileUploader"] > section {
        display: flex !important;
        flex-direction: row !important;
        align-items: stretch !important;
        gap: 10px !important;
    }

    /* Move the button to the left side */
    [data-testid="stFileUploader"] button {
        order: -1 !important;
        margin-left: 10px !important;
    }

    /* Keep the dropzone content to the right */
    [data-testid="stFileUploadDropzoneContent"] {
        flex-grow: 1 !important;
    }

    /* Force the button to match the exact height of the dropzone */
    [data-testid="stFileUploader"] button {
        height: 80px !important;  /* Match exact height of dropzone */
        box-sizing: border-box !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Set the dropzone to the same fixed height */
    [data-testid="stFileUploadDropzoneContent"] {
        height: 80px !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }

    /* Make dotted lines invisible */
    [data-testid="stFileUploadDropzoneContent"] {
        border-color: transparent !important;
    }

    /* Target SVG dashed strokes that might be creating the dotted appearance */
    [data-testid="stFileUploadDropzoneContent"] svg path,
    [data-testid="stFileUploadDropzoneContent"] svg rect,
    [data-testid="stFileUploadDropzoneContent"] svg line {
        stroke: transparent !important;
        stroke-opacity: 0 !important;
        opacity: 0 !important;
    }

    /* Ensure text and icon remain visible */
    [data-testid="stFileUploadDropzoneContent"] div {
        color: #333 !important;
    }

    [data-testid="stFileUploadDropzoneContent"] svg.css-1gpdmzr {
        opacity: 1 !important;
        stroke: initial !important;
        fill: #455a7f !important;
    }

    /* Ensure our height settings only apply to the browse button, not the X button */
    [data-testid="stFileUploader"] > section > button {
        height: 80px !important;
        box-sizing: border-box !important;
    }

    /* Reset any height settings for progress indicators and close buttons */
    [role="progressbar"],
    button[aria-label="Close"] {
        height: auto !important;
        min-height: auto !important;
        max-height: none !important;
    }

    /* Make "Confirm Titles" button text white */
    button:contains("Confirm Titles"),
    .stButton button {
        color: white !important;
    }

    /* Make text in the dark slide title boxes white instead of blue */
    [data-testid="stText"] > div > p {
        color: white !important;
    }

    /* Target specifically the slide title containers */
    .element-container div[data-testid="stText"] > div {
        color: white !important;
    }

    /* More specific targeting for the slide boxes */
    div[data-baseweb="card"] > div > div > p,
    div[data-baseweb="card"] span {
        color: white !important;
    }

    /* Specifically target the X button and reset its dimensions */
    button[aria-label="Close"],
    button.css-jlzg70,
    [data-testid="stFileUploader"] [aria-label="Close"],
    [role="dialog"] button {
        height: 32px !important;
        width: 32px !important;
        min-height: unset !important;
        max-height: 32px !important;
        padding: 6px !important;
        align-self: center !important;
        border-radius: 4px !important;
    }

    /* Fix container that might be stretching the button */
    [role="dialog"],
    [role="dialog"] > div {
        height: auto !important;
        min-height: unset !important;
        align-items: center !important;
    }

    /* Make the X icon itself appropriately sized */
    button[aria-label="Close"] svg {
        width: 12px !important;
        height: 12px !important;
    }

    /* Target text in dark containers - more specific selectors */
    div[data-testid="stText"] p,
    div[data-testid="stMarkdown"] p,
    [style*="rgb(30, 30, 46)"] p,
    [style*="rgb(30, 30, 46)"] span,
    [style*="rgb(30, 30, 46)"] div,
    [style*="rgb(25, 26, 30)"] p,
    [style*="rgb(25, 26, 30)"] span,
    [style*="rgb(25, 26, 30)"] div,
    .element-container div[data-testid="stText"] p {
        color: white !important;
    }

    /* Target specifically the slide title display */
    [data-baseweb="card"],
    [data-baseweb="card"] div, 
    [data-baseweb="card"] p, 
    [data-baseweb="card"] span {
        color: white !important;
    }

    /* Force all text in dark containers to be white */
    div.stMarkdown div[style*="background-color: rgb(30, 30, 46)"] *,
    div.stMarkdown div[style*="background-color: rgb(25, 26, 30)"] *,
    div.stContainer div[style*="background-color: rgb(30, 30, 46)"] *,
    div.stContainer div[style*="background-color: rgb(25, 26, 30)"] * {
        color: white !important;
    }

    /* NUCLEAR OPTION for text color - guaranteed to work */
    [style*="background-color: rgb(30, 30, 46)"],
    [style*="background-color: rgb(25, 26, 30)"],
    [style*="background-color: #1e1e2e"],
    [style*="background-color: #19191e"],
    [style*="background: rgb(30, 30, 46)"],
    [style*="background: rgb(25, 26, 30)"],
    [style*="background: #1e1e2e"],
    [style*="background: #19191e"],
    div.stMarkdown div p,
    div[data-testid="stText"] p,
    div[data-baseweb="card"] p,
    div[data-baseweb="card"] span {
        color: white !important;
        fill: white !important;
        stroke: white !important;
    }

    /* Extra specific - target p tags inside dark containers */
    div[data-testid="stText"] > div > p,
    .element-container div[data-testid="stText"] p,
    [data-baseweb="card"] p,
    [class*="stBox"] p,
    [class*="stCard"] p,
    div.stMarkdown p {
        color: white !important;
    }

    /* Force override by targeting the exact text elements */
    div.css-1fcdlhc,
    div.css-1fcdlhc p,
    div.css-1fcdlhc span,
    .css-1fcdlhc *,
    div[class*="stText"] p {
        color: white !important;
    }

    /* Absolutely guaranteed to work by using inline styles */
    body div.stApp div.stMarkdown p {
        color: white !important;
    }

    /* Override any styling on the text elements themselves */
    p, span, div {
        color: inherit !important;
    }

    div[style*="background-color: rgb(30, 30, 46)"] p,
    div[style*="background-color: rgb(25, 26, 30)"] p,
    div[style*="background-color: #1e1e2e"] p,
    div[style*="background-color: #19191e"] p {
        color: white !important;
    }

    /* Target only the specific slide title containers */
    div[style*="background-color: #1e1e2e"],
    div[style*="background-color: rgb(30, 30, 46)"],
    div[style*="background-color: rgb(25, 26, 30)"] {
        color: white !important;
    }

    /* Target direct children of those containers */
    div[style*="background-color: #1e1e2e"] > *,
    div[style*="background-color: rgb(30, 30, 46)"] > *,
    div[style*="background-color: rgb(25, 26, 30)"] > * {
        color: white !important;
    }

    /* Also target the specific slide title elements based on what I can see in screenshots */
    .stMarkdown div[style*="background-color"] {
        color: white !important;
    }

    /* RESET - remove any global text color changes that might affect light backgrounds */
    p, div, span {
        color: initial;
    }

    /* TARGET ONLY the dark boxes with slide titles */
    div[style*="background-color: #1e1e2e"] p,
    div[style*="background-color: rgb(30, 30, 46)"] p,
    div[style*="background-color: rgb(25, 26, 30)"] p,
    [data-testid="stMarkdown"] div[style*="background-color: #1e1e2e"],
    [data-testid="stMarkdown"] div[style*="background-color: rgb(30, 30, 46)"],
    [data-testid="stMarkdown"] div[style*="background-color: rgb(25, 26, 30)"] {
        color: white !important;
    }

    /* More specific selectors for the slide boxes */
    .stMarkdown div[style*="background-color: rgb(30, 30, 46)"],
    .stMarkdown div[style*="background-color: #1e1e2e"],
    .stMarkdown div[style*="background-color: rgb(25, 26, 30)"] {
        color: white !important;
    }

    /* ONLY target text on light backgrounds */
    .main .block-container p, 
    .main .block-container li, 
    .main .block-container label:not(.stRadio label[data-baseweb="radio"] span),
    .main .block-container .stMarkdown,
    .stSubheader,
    .main .block-container h4:not([class]),
    .main .block-container div:not([class*="st"]) {
        color: #2C3E50 !important;
    }
    
    /* Keep section headers deep blue */
    .main .block-container h1, 
    .main .block-container h2, 
    .main .block-container h3 {
        color: #1A3E6C !important;
    }
    
    /* EXPLICITLY PRESERVE white text in dark areas */
    .stFileUploader label, 
    .stFileUploader span,
    .stFileUploader p,
    [data-testid="stFileUploader"] span,
    button,
    .stButton button,
    [data-baseweb="base-button"] {
        color: inherit !important;
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
if 'style_option' not in st.session_state:
    st.session_state.style_option = "concise"  # Default value
if 'custom_guidance' not in st.session_state:
    st.session_state.custom_guidance = ""  # Default empty string

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
        key = ADMIN_API_KEY
        # Debug
        with st.expander("Debug - Admin Key"):
            st.write(f"Using admin key, length: {len(key) if key else 0}")
            st.write(f"Prefix: {key[:4] + '...' if key and len(key) > 4 else 'None'}")
        return key
    else:
        key = st.session_state.api_key
        # Debug
        with st.expander("Debug - User Key"):
            st.write(f"Using user key, length: {len(key) if key else 0}")
        return key

# Debug section
try:
    api_key_exists = "OPENAI_API_KEY" in st.secrets
    api_key_value = st.secrets.get("OPENAI_API_KEY", "")
    api_key_length = len(api_key_value) if api_key_value else 0
    api_key_prefix = api_key_value[:4] + "..." if api_key_value else "None"
    
    # Show debug info in an expander
    with st.expander("Debug Info (Only visible during testing)"):
        st.write(f"API Key in secrets: {api_key_exists}")
        st.write(f"API Key length: {api_key_length}")
        st.write(f"API Key prefix: {api_key_prefix}")
except Exception as e:
    st.error(f"Debug Error: {str(e)}")
    st.code(traceback.format_exc())

# Custom title with wave emoji
st.markdown('<div class="custom-title">🌊TitleWave</div>', unsafe_allow_html=True)
st.markdown('<div class="custom-subtitle">Upload your PowerPoint presentation to receive AI-enhanced slide titles 🪄 </div>', unsafe_allow_html=True)

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
        st.markdown("### Check Slide Titles Below", unsafe_allow_html=True)
        st.markdown("""
        Please double-check the extracted slide titles below, and edit them if needed before clicking 'Confirm Titles' to generate AI-enhanced versions.
        """, unsafe_allow_html=True)
        
        edited_titles = []
        # Create text inputs for each title
        for i, title in enumerate(titles, 1):
            # Use the session state value if it exists, otherwise use the extracted title
            current_value = st.session_state.edited_titles[i-1] if i <= len(st.session_state.edited_titles) else title
            edited_title = st.text_input(f"Slide {i}", value=current_value, key=f"edit_title_{i-1}")
            edited_titles.append(edited_title)
        
        # Confirm button
        if st.button("Confirm Titles"):
            st.session_state.edited_titles = edited_titles
            st.session_state.titles_confirmed = True
            st.success("Titles confirmed! You can now generate AI-enhanced versions.")
            st.rerun()  # Rerun to update the UI
        
        # Only show the Generate AI-Enhanced Titles button if titles are confirmed
        if st.session_state.titles_confirmed:
            # Use the edited titles instead of the original extracted ones
            titles_to_use = st.session_state.edited_titles
            
            st.subheader("Generate Enhanced Titles")
            
            # ADD CUSTOMIZATION UI HERE
            st.markdown('<h2 class="customize-header">Customize Your Title Suggestions</h2>', unsafe_allow_html=True)
            
            # Style selection
            style_option = st.radio(
                "Choose a base style for your enhanced titles:",
                ["concise", "descriptive", "engaging", "formal", "creative"],
                format_func=lambda x: {
                    "concise": "Short & Sweet (3-5 words, action-oriented)",
                    "descriptive": "Highly Descriptive (clear, explanatory)",
                    "engaging": "Engaging (questions, provocative statements)",
                    "formal": "Formal (professional, executive-friendly)",
                    "creative": "Creative (metaphors, imagery)"
                }[x]
            )
            
            # Custom guidance text area
            custom_guidance = st.text_area(
                "Anything else to keep in mind? (optional)",
                placeholder="Examples:\n• \"The audience are executives with short attention spans\"\n• \"Focus on emphasizing our competitive advantages\"\n• \"Write titles as if you were a drunken pirate\"\n• \"This is for a technical audience that values precision\"",
                height=100
            )
            
            # Store in session state
            st.session_state.style_option = style_option
            st.session_state.custom_guidance = custom_guidance
            
            # Generate AI-Enhanced Titles button
            if st.button("Generate AI-Enhanced Titles"):
                # If using free tier, increment usage counter
                if st.session_state.using_free_tier:
                    increment_usage()
                
                with st.spinner("Generating AI-enhanced titles..."):
                    # Get rewritten titles using the appropriate API key
                    active_api_key = get_active_api_key()
                    # Convert titles to the format expected by rewrite_titles_with_context
                    slides_data = [{"title": title, "content": ""} for title in titles_to_use]
                    suggested_titles = rewrite_titles_with_context(
                        slides_data, 
                        st.session_state.style_option, 
                        st.session_state.custom_guidance,
                        active_api_key
                    )
                    
                    # Store in session state to persist across reruns
                    st.session_state.all_rewritten_options = suggested_titles
                    st.session_state.show_selection = True
                    st.rerun()  # Rerun to update the UI with selection interface
            
            # Display title selection interface if available
            if 'show_selection' in st.session_state and st.session_state.show_selection and 'all_rewritten_options' in st.session_state:
                st.markdown("""
                <style>
                .section-header {
                    color: #1A3E6C !important; /* Deep blue for accessibility */
                    font-weight: 600;
                }
                .slide-header {
                    color: #2C3E50 !important; /* Dark slate for accessibility */
                    font-weight: 600; 
                }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown('<h2 class="section-header">Select New Titles</h2>', unsafe_allow_html=True)
                selected_titles = []
                
                for i, options in enumerate(st.session_state.all_rewritten_options):
                    if i < len(titles_to_use):  # Safety check
                        st.markdown(f'<div class="slide-header">Slide {i+1}</div>', unsafe_allow_html=True)
                        st.markdown(f"""<div style="background-color: #1e1e2e; padding: 10px; border-radius: 5px; color: white !important;"><span style="color: white !important;">{titles_to_use[i]}</span></div>""", unsafe_allow_html=True)
                        
                        # Create radio buttons for selection with original + 2 options
                        radio_options = ["[Keep Original]"] + options
                        selection = st.radio(
                            f"Choose title for slide {i+1}:",
                            radio_options,
                            key=f"slide_{i}"
                        )
                        
                        # Store the selection
                        if selection == "[Keep Original]":
                            selected_titles.append(titles_to_use[i])
                        else:
                            selected_titles.append(selection)
                        
                        st.markdown("<hr style='margin: 30px 0; opacity: 0.3;'>", unsafe_allow_html=True)
                
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

# Add this near the bottom of your app, after all the main UI components
# Small, subtle test button for API debugging
st.markdown("<hr style='margin-top: 50px; opacity: 0.3;'>", unsafe_allow_html=True)
with st.expander("🔧 Developer Tools", expanded=False):
    col1, col2 = st.columns([1, 3])
    with col1:
        test_api = st.button("Test API", help="Test OpenAI API connection", key="test_api_btn")
    
    if test_api:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say hello"}],
                max_tokens=10
            )
            with col2:
                st.success(f"✓ API works! Response: {response.choices[0].message.content}")
        except Exception as e:
            with col2:
                st.error(f"API Error: {type(e).__name__}")
                st.code(str(e))  # No nested expander, just show the error directly 