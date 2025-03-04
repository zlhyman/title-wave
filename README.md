# TitleWave

TitleWave is an AI-powered slide title enhancer that helps you improve the titles in your PowerPoint presentations.

## Features

- Extracts slide titles from PowerPoint presentations
- Uses OpenAI GPT-4 to rewrite titles in three different styles:
  1. Concise & Clear
  2. Executive-Friendly
  3. Storytelling-Driven
- Allows you to review the rewritten titles before applying them
- Updates your PowerPoint file with the selected titles

## Installation

1. Clone this repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```
export OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Place your PowerPoint file in the project directory or update the file path in `main.py`
2. Run the application:

```
python main.py
```

3. Review the original and rewritten titles
4. Choose whether to apply the changes

## Files Structure

- `main.py` - The main entry point for the application
- `title_extractor.py` - Module for extracting titles from PowerPoint files
- `title_rewriter.py` - Module for rewriting titles using OpenAI
- `pptx_updater.py` - Module for updating PowerPoint files with new titles
- `requirements.txt` - List of required dependencies 