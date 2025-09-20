import streamlit as st

# ...existing code...
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

# File uploader (use keys so we can clear state safely on reset)
uploaded_file = st.file_uploader("Upload a text, Word (.docx), or PDF file:", key="uploaded_file")

# Prepare the initial text value (from uploaded file if present)
file_text = ""
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

# Use session state-backed text area so we can reset it without calling experimental_rerun
initial_text = file_text if file_text else ""
label = "File content" if file_text else "Paste or type text to emphasize:"
user_input = st.text_area(label, value=initial_text, height=200, key="user_input")

# Controls
mode = st.radio("Emphasis mode:", ["bold-first", "micro-space"], horizontal=True, key="mode")
bold_ratio = st.slider("Portion of each word to emphasize:", 0.1, 0.9, 0.5, key="bold_ratio")
min_word_len = st.slider("Minimum word length to modify:", 1, 10, 3, key="min_word_len")

# Action buttons
col1, col2 = st.columns(2)
with col1:
    apply = st.button("Apply Emphasis", key="apply")
with col2:
    reset = st.button("Reset", key="reset")

if apply:
    text_val = st.session_state.get("user_input", "")
    if text_val and text_val.strip():
        result = emphasize_text(text_val, bold_ratio=st.session_state.get("bold_ratio", bold_ratio), min_word_len=st.session_state.get("min_word_len", min_word_len), mode=st.session_state.get("mode", mode))
        # markdown is fine for bold; micro-space renders as text
        st.markdown(result, unsafe_allow_html=True)
    else:
        st.warning("Please enter or upload some text first.")

if reset:
    # Selectively reset only the keys used by the app to avoid clearing other session data.
    for k in ["uploaded_file", "user_input", "mode", "bold_ratio", "min_word_len"]:
        if k in st.session_state:
            # restore sensible defaults
            if k == "uploaded_file":
                st.session_state[k] = None
            elif k == "user_input":
                st.session_state[k] = ""
            elif k == "mode":
                st.session_state[k] = "bold-first"
            elif k == "bold_ratio":
                st.session_state[k] = 0.5
            elif k == "min_word_len":
                st.session_state[k] = 3

