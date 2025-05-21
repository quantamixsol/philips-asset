# Philips Asset Template Generator

This repository contains a Streamlit application for generating marketing copy based on Philips asset templates. The app can load existing templates, apply approved claims, and use OpenAI to fill in template fields.

## Configuration

The app reads your OpenAI API key from the `OPENAI_API_KEY` environment variable. If you want to use a fine-tuned model, set `OPENAI_FINETUNED_MODEL` to the model ID. By default the app uses a Philips fine-tuned GPT-4o model.

