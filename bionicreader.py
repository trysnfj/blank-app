import streamlit as st
import re
import PyPDF2

try:
    from docx import Document
except ModuleNotFoundError:
    Document = None

# Define the function to apply bionic reading
def bionic_read(text, bold_ratio=0.5):
    words = re.split('(\W+)', text)  # Split text by words and keep punctuation
    transformed_words = []
    
    for word in words:
        if word.isalpha():  # Only apply to alphabetic words
            bold_part_len = max(1, int(len(word) * bold_ratio))  # Prevent 0 length
            bold_part = word[:bold_part_len]
            rest_part = word[bold_part_len:]
            transformed_word = f"**{bold_part}**{rest_part}"
        else:
            transformed_word = word
        transformed_words.append(transformed_word)
    
    return ''.join(transformed_words)

# Streamlit app
st.title("Bionic Reading App")
st.markdown("This app helps you read faster by emphasizing the first part of each word.")

# File uploader for text, Word, or PDF files
uploaded_file = st.file_uploader("Upload a text, Word, or PDF file:")

user_input = ""
file_text = ""
if uploaded_file is not None:
    file_type = uploaded_file.type
    try:
        if file_type == "text/plain":
            file_text = uploaded_file.read().decode("utf-8")
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            if Document is None:
                raise ImportError("The 'python-docx' library is not installed.")
            doc = Document(uploaded_file)
            file_text = "\n".join([para.text for para in doc.paragraphs])
        elif file_type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    file_text += text
        else:
            st.error("Unsupported file format. Please upload a text, Word, or PDF file.")
    except ImportError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
    if file_text:
        user_input = st.text_area("File Content", file_text, height=200)
else:
    user_input = st.text_area("Enter the text you want to read in Bionic style:", height=200)

# Slider to adjust bold ratio
bold_ratio = st.slider("Select the bold ratio (percentage of each word to bold):", 0.1, 0.9, 0.5)

# Convert text to bionic reading style if button is pressed
if st.button("Convert to Bionic Reading"):
    if user_input:
        bionic_text = bionic_read(user_input, bold_ratio)
        st.markdown(bionic_text, unsafe_allow_html=True)
    else:
        st.warning("Please enter or upload some text.")

# Reset button to clear inputs
if st.button("Reset"):
    st.experimental_rerun()
