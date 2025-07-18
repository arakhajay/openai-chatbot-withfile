import streamlit as st
import openai
import pdfplumber
from docx import Document
from io import BytesIO

# Function to extract text from different file types
def extract_text(file):
    file_type = file.type
    file_bytes = file.read()

    if file_type == "text/plain":
        return file_bytes.decode("utf-8")

    elif file_type == "application/pdf":
        text = ""
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(BytesIO(file_bytes))
        return "\n".join([para.text for para in doc.paragraphs])

    else:
        return "Unsupported file format."

# Query OpenAI API
def query_openai(api_key, model, prompt, file=None):
    openai.api_key = api_key

    if file:
        file_text = extract_text(file)
        prompt = f"{prompt}\n\n{file_text}"

    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=params["temperature"],
        max_tokens=params["max_tokens"]
    )
    return response.choices[0].message.content.strip()

# Streamlit app layout
st.title("OpenAI Q&A Chatbot with File Upload ")

with st.sidebar:
    api_key = st.text_input("Enter your OpenAI API Key", type="password")
    model = st.selectbox("Select the Model", options=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"])

    # Other parameters
    params = {
        "temperature": st.slider("Temperature", 0.0, 1.0, 0.5, 0.01),
        "max_tokens": st.slider("Max tokens", 1, 1000, 150)
    }

# Main UI
user_prompt = st.text_area("Type your prompt/question here:")
uploaded_file = st.file_uploader("Or upload a file (txt, pdf, docx):", type=["txt", "pdf", "docx"])

if st.button("Ask GPT"):
    if not api_key:
        st.error("Please enter your OpenAI API Key.")
    elif not user_prompt and not uploaded_file:
        st.warning("Please provide a prompt or upload a file.")
    else:
        try:
            response = query_openai(api_key, model, user_prompt, uploaded_file)
            st.success("Response:")
            st.write(response)
        except Exception as e:
            st.error(f"Error: {e}")
