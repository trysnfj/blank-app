import streamlit as st
import re
import PyPDF2

try:
    from docx import Document
except ModuleNotFoundError:
    Document = None

# ------- Brand-neutral emphasis function -------
def emphasize_text(text, bold_ratio=0.5):
    """
    Emphasizes the first portion of each alphabetic word by bolding it.
    This is an independent accessibility experiment; not affiliated with any third-party brand.
    """
    words = re.split(r'(\W+)', text)  # keep punctuation/whitespace
    transformed = []
    for word in words:
        if word.isalpha():
            n = max(1, int(len(word) * bold_ratio))
            head, tail = word[:n], word[n:]
            transformed.append(f"**{head}**{tail}")
        else:
            transformed.append(word)
    return ''.join(transformed)

# ------- Streamlit UI -------
st.title("Salient Reader")
st.caption("Experimental tool that emphasizes the first part of words to aid focus. "
           "Not affiliated with or endorsed by any third-party brand or method.")

uploaded_file = st.file_uploader("Upload a .txt, .docx, or .pdf file:")
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
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    file_text += text
        else:
            st.error("Unsupported file. Please upload .txt, .docx, or .pdf.")
    except ImportError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Error processing file: {e}")

    if file_text:
        user_input = s_
