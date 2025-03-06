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

3. Set up your OpenAI API key (see [API Key Security](#api-key-security) below)

## Usage

1. Place your PowerPoint file in the project directory or update the file path in `main.py`
2. Run the application:

```
python main.py
```

3. Review the original and rewritten titles
4. Choose whether to apply the changes

## API Key Security

You'll need an OpenAI API key to use TitleWave. There are several secure ways to provide it:

### Option 1: Environment variable (recommended)

```bash
export OPENAI_API_KEY=your_api_key_here
```

### Option 2: Using a .env file (for development)

1. Copy the example environment file:
   ```
   cp .env.example .env
   ```
2. Edit the `.env` file and add your API key
3. Note: The `.env` file is in `.gitignore` and should never be committed to version control

### Security Best Practices

- Never hardcode your API key directly in the source code
- Never commit your actual API key to version control
- Consider using a secrets management tool for production use
- Regularly rotate your API keys
- Use environment-specific API keys (development, staging, production)

## Files Structure

- `main.py` - The main entry point for the application
- `title_extractor.py` - Module for extracting titles from PowerPoint files
- `title_rewriter.py` - Module for rewriting titles using OpenAI
- `pptx_updater.py` - Module for updating PowerPoint files with new titles
- `requirements.txt` - List of required dependencies 