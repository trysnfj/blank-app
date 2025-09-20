import streamlit as st
import re
import PyPDF2

try:
    from docx import Document
except ModuleNotFoundError:
    Document = None

# ---------------------------
# Reading-Aid configuration
# ---------------------------
st.set_page_config(page_title="Reading-Aid", layout="wide")
st.title("Reading-Aid")
st.caption("Emphasise the start of words to aid focus and readability. Upload a file or paste text below.")

# ---------------------------
# Helpers
# ---------------------------
WORD_SPLIT_REGEX = re.compile(r"(\W+)")  # keep punctuation & whitespace as separate tokens

def emphasise_text(
    text: str,
    bold_ratio: float = 0.5,
    min_word_len: int = 2,
    alpha_only: bool = True,
    include_numbers: bool = False,
) -> str:
    """
    Emphasise the first portion of words using Markdown bold.
    - Keeps punctuation/spacing intact.
    - Only transforms tokens that match the chosen criteria.
    """
    tokens = WORD_SPLIT_REGEX.split(text)
    out = []

    for tok in tokens:
        # Decide if we transform this token
        if alpha_only:
            is_target = tok.isalpha()
        else:
            if include_numbers:
                is_target = tok.isalnum()
            else:
                # letters-only OR mixed with punctuation that we've already split away
                is_target = tok.isalpha()

        if is_target and len(tok) >= min_word_len:
            cut = max(1, int(len(tok) * bold_ratio))
            out.append(f"**{tok[:cut]}**{tok[cut:]}")
        else:
            out.append(tok)

    return "".join(out)

def read_uploaded_file(uploaded_file) -> str:
    """
    Reads text/plain, .docx, or .pdf into a single text string.
    """
    file_type = uploaded_file.type
    uploaded_file.seek(0)

    if file_type == "text/plain":
        return uploaded_file.read().decode("utf-8", errors="ignore")

    if file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        if Document is None:
            raise ImportError("The 'python-docx' package is not installed. Add 'python-docx' to requirements.txt.")
        doc = Document(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs)

    if file_type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        text_parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
        return "\n".join(text_parts)

    raise ValueError("Unsupported file format. Please upload a .txt, .docx, or .pdf file.")

# ---------------------------
# UI: Inputs
# ---------------------------
with st.sidebar:
    st.subheader("Emphasis Settings")
    bold_ratio = st.slider("Portion of each word to emphasise", 0.1, 0.9, 0.5, step=0.05)
    min_word_len = st.number_input("Minimum word length to emphasise", min_value=1, max_value=20, value=2, step=1)
    alpha_only = st.checkbox("Letters only (ignore numbers/symbols)", value=True)
    include_numbers = st.checkbox("Include numbers (if letters-only is off)", value=False, disabled=alpha_only)
    st.markdown("---")
    st.caption("Tip: Increase the portion or minimum length for stronger emphasis.")

uploaded_file = st.file_uploader(
    "Upload a .txt, .docx or .pdf file (or paste text below):",
    type=["txt", "docx", "pdf"]
)

file_text = ""
if uploaded_file is not None:
    try:
        file_text = read_uploaded_file(uploaded_file)
    except Exception as e:
        st.error(f"File error: {e}")

user_input = st.text_area(
    "Input text",
    value=file_text or "",
    height=220,
    placeholder="Paste your text here…"
)

# ---------------------------
# Action
# ---------------------------
col1, col2 = st.columns([1, 1])
with col1:
    run = st.button("Emphasise Text")
with col2:
    clear = st.button("Clear")

if clear:
    st.experimental_rerun()

if run:
    if not user_input.strip():
        st.warning("Please paste text or upload a file.")
    else:
        output = emphasise_text(
            user_input,
            bold_ratio=bold_ratio,
            min_word_len=min_word_len,
            alpha_only=alpha_only,
            include_numbers=include_numbers,
        )

        st.subheader("Result")
        st.markdown(output, unsafe_allow_html=True)

        st.download_button(
            "Download as Markdown",
            data=output.encode("utf-8"),
            file_name="reading_aid_output.md",
            mime="text/markdown"
        )
