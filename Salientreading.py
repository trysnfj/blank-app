import streamlit as st
import re
import PyPDF2

try:
    from docx import Document
except ModuleNotFoundError:
    Document = None

# -------- Emphasis engine (brand-neutral) --------
def emphasize_text(text, bold_ratio=0.5, min_word_len=3, mode="bold-first"):
    """
    Emphasize part of each alphabetic word.
    modes:
      - "bold-first": bolds the first bold_ratio of characters
      - "micro-space": inserts thin spaces (U+2009) after the emphasized chunk
    """
    words = re.split(r'(\W+)', text)  # keep punctuation & whitespace
    out = []

    for w in words:
        if w.isalpha() and len(w) >= min_word_len:
            n = max(1, int(len(w) * bold_ratio))
            head, tail = w[:n], w[n:]
            if mode == "bold-first":
                out.append(f"**{head}**{tail}")
            elif mode == "micro-space":
                out.append(f"{head}\u2009{tail}")
            else:
                out.append(w)
        else:
            out.append(w)

    return ''.join(out)

# -------- Streamlit UI --------
st.title("Salient Reader")
st.caption(
    "An independent accessibility experiment that emphasizes portions of words to aid focus. "
    "Not affiliated with or endorsed by any third-party brand or method."
)

# File uploader
uploaded_file = st.file_uploader("Upload a text, Word (.docx), or PDF file:")

user_input, file_text = "", ""
if uploaded_file is not None:
    file_type = uploaded_file.type
    try:
        if file_type == "text/plain":
            file_text = uploaded_file.read().decode("utf-8", errors="ignore")
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            if Document is None:
                raise ImportError("The 'python-docx' library is not installed.")
            doc = Document(uploaded_file)
            file_text = "\n".join(p.text for p in doc.paragraphs)
        elif file_type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    file_text += text
        else:
            st.error("Unsupported file format. Please upload .txt, .docx, or .pdf.")
    except ImportError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
    if file_text:
        user_input = st.text_area("File content", file_text, height=200)
else:
    user_input = st.text_area("Paste or type text to emphasize:", height=200)

# Controls
mode = st.radio("Emphasis mode:", ["bold-first", "micro-space"], horizontal=True)
bold_ratio = st.slider("Portion of each word to emphasize:", 0.1, 0.9, 0.5)
min_word_len = st.slider("Minimum word length to modify:", 1, 10, 3)

# Action buttons
col1, col2 = st.columns(2)
with col1:
    apply = st.button("Apply Emphasis")
with col2:
    reset = st.button("Reset")

if apply:
    if user_input.strip():
        result = emphasize_text(user_input, bold_ratio=bold_ratio, min_word_len=min_word_len, mode=mode)
        # markdown is fine for bold; micro-space renders as text
        st.markdown(result, unsafe_allow_html=True)
    else:
        st.warning("Please enter or upload some text first.")

if reset:
    st.experimental_rerun()

