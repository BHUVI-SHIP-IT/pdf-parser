import streamlit as st
import fitz  # PyMuPDF
import re
import requests

# === Function to extract headings ===
def extract_headings_from_text(text):
    lines = text.split('\n')
    headings = []

    for line in lines:
        if re.match(r'^[A-Z][A-Z\s\d\.\-:]{3,}$', line.strip()) or (len(line.strip()) < 30 and len(line.strip()) > 4):
            headings.append(line.strip())

    return list(set(headings))

# === Function to extract text from PDF ===
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# === Function to summarize using OpenRouter ===
def summarize_with_openrouter(api_key, input_text):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mistral-7b-instruct",  # You can replace this
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes documents."},
            {"role": "user", "content": f"Summarize the following PDF content:\n\n{input_text[:4000]}"}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error from OpenRouter: {response.text}"

# === Streamlit UI ===
st.set_page_config(page_title="PDF Heading Extractor + Summarizer", layout="centered")
st.title("📄 PDF Heading Extractor + AI Summarizer")

uploaded_pdf = st.file_uploader("Upload your PDF", type="pdf")
display_option = st.radio("Select what to display:", ["📌 Headings Only", "📌 Headings + 🧠 Summary"])

openrouter_api_key = st.text_input("Enter your OpenRouter API key", type="password")

if uploaded_pdf is not None:
    with st.spinner("Extracting text from PDF..."):
        pdf_text = extract_text_from_pdf(uploaded_pdf)

    headings = extract_headings_from_text(pdf_text)

    if display_option == "📌 Headings Only":
        st.subheader("📌 Extracted Headings")
        if headings:
            for head in headings:
                st.markdown(f"- **{head}**")
        else:
            st.warning("No clear headings found.")

    elif display_option == "📌 Headings + 🧠 Summary":
        st.subheader("📌 Extracted Headings")
        if headings:
            for head in headings:
                st.markdown(f"- **{head}**")
        else:
            st.warning("No clear headings found.")

        if openrouter_api_key:
            if st.button("🔍 Summarize PDF with OpenRouter"):
                with st.spinner("Summarizing PDF using OpenRouter..."):
                    summary = summarize_with_openrouter(openrouter_api_key, pdf_text)
                st.subheader("🧠 PDF Summary")
                st.write(summary)
        else:
            st.info("Enter your OpenRouter API key to enable summarization.")
