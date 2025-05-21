import streamlit as st
import pandas as pd
import io
from PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv
import re, json
import os
load_dotenv()

OPENAI_CLIENT = OpenAI()
FINETUNED_MODEL = os.getenv(
    "OPENAI_FINETUNED_MODEL",
    "ft:gpt-4o-mini-2024-07-18:quantamix-solutions:philipsfinetunedoptimised:AqQmabHZ",
)
# --- Page Configuration & Branding CSS ---
st.set_page_config(page_title="Philips Asset Template Generator", layout="wide")
st.markdown(
    """
    <style>
    /* Sidebar branding */
    .stSidebar .sidebar-content { background-color: #0057A4; color: white; }
    .stSidebar .sidebar-content a { color: white; }
    /* Buttons */
    .stButton>button, .stDownloadButton>button { background-color: #0057A4; color: white; border: none; }
    /* Font */
    .stApp { font-family: Arial, sans-serif; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Logo & Title ---
st.image("Phillips-Logo.png", width=120)
st.title("Philips Asset Template Generator")
st.caption("© Koninklijke Philips N.V. All rights reserved.")

# Fields that will be replaced by the AI output
AI_FIELDS = {
    "Functional Description 1",
    "Functional Description 2",
    "Wow",
    "Subwow",
    "Marketing Text",
    "Feature 1 Name",
    "Feature 1 Description",
    "Feature 1 Glossary",
    "Feature 2 Name",
    "Feature 2 Description",
}

def parse_char_limit(val):
    """Extract integer character limit from the Char Count column."""
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str):
        m = re.search(r"(\d+)", val)
        if m:
            return int(m.group(1))
    return None


# --- Helper: Extract text from PDF ---
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

# --- Sidebar: Uploads & Settings ---
st.sidebar.header("1. Upload Files & Settings")
use_finetuned_model = st.sidebar.radio(
    "Select Model Type",
    ["GPT-4o (Standard)", "Fine-tuned Model"],
    index=0,
    help="Choose between using OpenAI's GPT-4o or a fine-tuned version."
)

uploaded_template = st.sidebar.file_uploader(
    "Upload Existing Asset Template (XLSX/XLSM)", type=["xlsx", "xlsm"],
    help="Import an existing asset template to prefill structure.", key="upl_temp"
)
branding_pdf = st.sidebar.file_uploader(
    "Upload Branding Guidelines (PDF)", type=["pdf"], help="Brand guidelines PDF.", key="brand_pdf"
)
product_pdf = st.sidebar.file_uploader(
    "Upload Product Details (PDF)", type=["pdf"], help="Product details PDF.", key="prod_pdf"
)
acl_file = st.sidebar.file_uploader(
    "Upload Approved Claims List (CSV)", type=["csv"], help="ACL CSV.", key="acl_csv"
)

# --- Load ACL & Guidelines ---
acl_df = pd.DataFrame()
if acl_file:
    try:
        acl_df = pd.read_csv(acl_file)
    except Exception as e:
        st.sidebar.error(f"Failed to read ACL CSV: {e}")

branding_text = extract_text_from_pdf(branding_pdf) if branding_pdf else ""
product_text = extract_text_from_pdf(product_pdf) if product_pdf else ""

# --- Initialize or Load Template Structure ---
if uploaded_template:
    try:
        with io.BytesIO(uploaded_template.read()) as buf:
            raw = pd.read_excel(buf, sheet_name=0, engine='openpyxl')
        df = raw.dropna(how='all', axis=0).dropna(how='all', axis=1)
        headers = df.iloc[0].astype(str).str.strip().tolist()
        if 'Field Name' in headers and 'Content Type' in headers:
            df.columns = headers
            df = df[1:]
        df.columns = [str(c).strip() for c in df.columns]
        template_df = df.fillna('').reset_index(drop=True)
    except Exception as e:
        st.error(f"Error loading template: {e}")
        st.stop()
else:
    rows = []
    for i in range(1, 3):
        rows.append({"Field Name": f"Functional Description {i}", "Content Type": "Functional Description", "Char Count": "—"})
    rows += [
        {"Field Name": "Wow", "Content Type": "Headline", "Char Count": "<50"},
        {"Field Name": "Subwow", "Content Type": "Headline", "Char Count": "<100"},
        {"Field Name": "Marketing Text", "Content Type": "Marketing Text", "Char Count": "<200"},
    ]
    for idx in range(1, 4):
        rows += [
            {"Field Name": f"Feature {idx} Name", "Content Type": "Feature Name", "Char Count": "—"},
            {"Field Name": f"Feature {idx} Description", "Content Type": "Feature Description", "Char Count": "<100"},
            {"Field Name": f"Feature {idx} Glossary", "Content Type": "Feature Glossary", "Char Count": "<300"},
        ]
    rows += [
        {"Field Name": "Pack Contents", "Content Type": "Pack Contents", "Char Count": "—"},
        {"Field Name": "Disclaimer", "Content Type": "Disclaimer", "Char Count": "—"},
    ]
    template_df = pd.DataFrame(rows).fillna('')

# Map columns
col_map = {c.lower(): c for c in template_df.columns}
if not all(k in col_map for k in ['field name','content type','char count']):
    st.error("Missing required columns: Field Name, Content Type, Char Count.")
    st.stop()
field_c, type_c, char_c = col_map['field name'], col_map['content type'], col_map['char count']

# --- CTN Input & Column Setup ---
ctn = st.text_input("Enter new CTN number", help="E.g. 1234567890", key="ctn_input")
col_name = ctn.strip() or "CTN"
if col_name not in template_df.columns:
    template_df[col_name] = ""

# --- Display Template ---
st.header("Template Structure & Definitions")
st.dataframe(template_df, use_container_width=True)

# --- Fill Fixed Fields ---
st.header("Fill Functional Descriptions & ACL Content")
filled = template_df.copy()
for i, row in filled.iterrows():
    content_type = row[type_c]
    field = row[field_c]
    if content_type == "Functional Description":
        filled.at[i, col_name] = st.text_area(field, key=f"func_{i}", height=80)
    elif content_type == "Pack Contents":
        if 'Pack Contents' in acl_df.columns:
            filled.at[i, col_name] = ", ".join(acl_df['Pack Contents'].dropna().unique())
        else:
            filled.at[i, col_name] = ""
    elif content_type == "Disclaimer":
        if 'Disclaimer' in acl_df.columns:
            filled.at[i, col_name] = "\n".join(acl_df['Disclaimer'].dropna())
        else:
            filled.at[i, col_name] = ""

# --- AI Generation ---
st.header("AI-Generated Copy")
if st.button("Generate AI Content", key="gen_ai"):
    system_prompt = (
        f"You are a Philips copywriter. Brand guidelines: {branding_text[:500]}. "
        f"Product details: {product_text[:500]}. CTN: {ctn}. "
        "Generate copy for each field in the following template. Only reference the provided product information; "
        "do not mention unrelated Philips products or categories. "
        "Output MUST be a single valid JSON object whose keys exactly match the template’s “Field Name” values "
        "and whose values are the generated strings. "
        "Do not include any markdown or explanatory text—only the JSON. "
        "Example format:\n"
        "{\n"
        '  "Wow": "…",\n'
        '  "Subwow": "…",\n'
        '  "Marketing Text": "…",\n'
        '  "Feature 1 Name": "…",\n'
        '  ...\n'
        "}\n"
    )
    user_prompt = "Fields with limits:\n"
    for i, row in filled.iterrows():
        if row[type_c] in ["Headline", "Marketing Text", "Feature Name", "Feature Description", "Feature Glossary", "Pack Contents", "Disclaimer"]:
            char_count = row.get(char_c, 300)
            if isinstance(char_count, str) and char_count.strip().startswith("<"):
                limit = char_count
            else:
                limit = f"<{char_count}>"
            user_prompt += f"- {row[field_c]} ({limit}) chars\n"
    selected_model = (
        FINETUNED_MODEL if use_finetuned_model == "Fine-tuned Model" else "gpt-4o"
    )
    try:
        resp = OPENAI_CLIENT.chat.completions.create(
            model=selected_model,
            messages=[
                {"role":"system","content":system_prompt},
                {"role":"user","content":user_prompt},
            ],
            temperature=0.2,
        )
        # we want to fill this into the table
        ai_output = resp.choices[0].message.content
        st.text_area("AI Output", ai_output, height=300, key="ai_out")
                
        parsed_content = {}

        try:
            parsed_content = json.loads(ai_output)
        except json.JSONDecodeError:
            # Fallback to regex parsing if not valid JSON
            matches = re.findall(r"\*\*(.+?):\*\*\s*(.+?)(?=\n\*\*|\Z)", ai_output, re.DOTALL)
            parsed_content = {k.strip(): v.strip() for k, v in matches}

        # --- Fill into Template with character limit checks ---
        warnings = []
        for i, row in filled.iterrows():
            field = row[field_c].strip()
            new_val = parsed_content.get(field, "")
            if new_val:
                limit = parse_char_limit(row.get(char_c))
                if limit and len(new_val) > limit:
                    warnings.append(f"{field} exceeds {limit} characters; truncated.")
                    new_val = new_val[:limit]
                filled.at[i, col_name] = new_val

        if warnings:
            for w in warnings:
                st.warning(w)

        st.subheader("Review & Edit AI Content")
        for i, row in filled.iterrows():
            field = row[field_c].strip()
            if field in AI_FIELDS:
                current = filled.at[i, col_name]
                updated = st.text_area(field, value=current, key=f"edit_{i}")
                filled.at[i, col_name] = updated

        st.header("Filled Template Structure")
        st.dataframe(filled, use_container_width=True)

    except Exception as e:
        st.error(f"AI generation failed: {e}")

# --- Export ---
st.header("Export Completed Template")
csv = filled.to_csv(index=False).encode()
st.download_button("Download CSV", csv, file_name=f"{col_name}_asset_template.csv", key="dl_csv")

# # --- Footer Instructions ---
# st.markdown(
#     "---\n"
#     "**To run locally:**\n"
#     "1. PowerShell: `$Env:OPENAI_API_KEY='sk-...'`\n"
#     "2. CMD: `set OPENAI_API_KEY=sk-...`\n"
#     "3. `streamlit run asset_app.py`"
# )