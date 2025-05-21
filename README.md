# Philips Asset Template Generator

This repository contains a Streamlit application for generating marketing copy based on Philips asset templates. The app can load existing templates, apply approved claims, and use OpenAI to fill in template fields.

## Configuration

The app reads your OpenAI API key from the `OPENAI_API_KEY` environment variable. If you want to use a fine-tuned model, set `OPENAI_FINETUNED_MODEL` to the model ID. By default the app uses a Philips fine-tuned GPT-4o model.

After you upload an asset template you can generate marketing copy for the predefined AI fields. The character limits in the template are enforced and the generated text can be reviewed and edited before export.

The interface allows entering multiple CTN numbers at once. For each CTN the app requests functional descriptions and then generates three variations of the marketing copy using OpenAI. The completed table can be downloaded as CSV or Excel for further editing.

