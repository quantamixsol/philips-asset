# Philips Asset Template Generator

This repository contains a Streamlit application for generating marketing copy based on Philips asset templates. The app can load existing templates, apply approved claims, and use OpenAI to fill in template fields.


## How to run locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your OpenAI API key as an environment variable:
   - PowerShell
     ```powershell
     $Env:OPENAI_API_KEY="sk-..."
     ```
   - CMD
     ```cmd
     set OPENAI_API_KEY=sk-...
     ```
3. Start the Streamlit app:
   ```bash
   streamlit run asset_app.py
   ```
