from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader  # ✅ Updated import
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
app = Flask(__name__)

# Updated for multiple PDFs for different languages
PDF_PATHS = {
    "English": ["pdfs/english1.pdf", "pdfs/english2.pdf", "pdfs/english3.pdf", "pdfs/english4.pdf", "pdfs/english5.pdf"],
    "Hindi": ["pdfs/hindi1.pdf", "pdfs/hindi2.pdf", "pdfs/hindi3.pdf", "pdfs/hindi4.pdf", "pdfs/hindi5.pdf"],
    "Kannada": ["pdfs/kannada1.pdf", "pdfs/kannada2.pdf", "pdfs/kannada3.pdf", "pdfs/kannada4.pdf", "pdfs/kannada5.pdf"],
    "Telugu": ["pdfs/telugu1.pdf", "pdfs/telugu2.pdf", "pdfs/telugu3.pdf", "pdfs/telugu4.pdf", "pdfs/telugu5.pdf"],
    "Tamil": ["pdfs/tamil1.pdf", "pdfs/tamil2.pdf", "pdfs/tamil3.pdf", "pdfs/tamil4.pdf", "pdfs/tamil5.pdf"],
    "Marathi": ["pdfs/marathi1.pdf", "pdfs/marathi2.pdf", "pdfs/marathi3.pdf", "pdfs/marathi4.pdf", "pdfs/marathi5.pdf"],
}

def get_vector_db_path(language):
    return f"vector_db_{language.lower()}"

def create_vector_db(language):
    pdf_paths = PDF_PATHS.get(language)
    if not pdf_paths:
        return None

    all_text = ""
    for pdf_path in pdf_paths:
        if os.path.exists(pdf_path):
            print(f"Loading: {pdf_path}")
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            all_text += "\n".join([doc.page_content for doc in documents])
        else:
            print(f"❌ PDF not found: {pdf_path}")
            return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(all_text)
    embeddings = OpenAIEmbeddings()
    vector_db = FAISS.from_texts(chunks, embeddings)

    # Save the vector database to disk
    vector_db_path = get_vector_db_path(language)
    vector_db.save_local(vector_db_path)
    return vector_db

def load_or_create_vector_db(language):
    vector_db_path = get_vector_db_path(language)
    if os.path.exists(vector_db_path):
        print(f"Loading existing vector DB: {vector_db_path}")
        return FAISS.load_local(vector_db_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    else:
        print(f"Creating new vector DB for language: {language}")
        return create_vector_db(language)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    print("⚡ Chat request received")
    data = request.get_json()
    language = data.get("language")
    question = data.get("question")

    vector_db = load_or_create_vector_db(language)
    if not vector_db:
        return jsonify({"answer": "❌ PDF not found for selected language."})

    # 🎯 Prompt engineering: Detect user's intent for answer length
    if any(keyword in question.lower() for keyword in ["brief", "short", "summary", "in short"]):
        instruction = "Answer briefly and concisely in less than 40 words. \n"
    elif any(keyword in question.lower() for keyword in ["explain", "describe", "in detail", "elaborate"]):
        instruction = "Explain the answer in detail, with clarity in 100 words.\n"
    else:
        instruction = "Give a clear and appropriate answer based on the question, but keep short and precise.\n"

    prompt = instruction + "Question: " + question

    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-4o-mini"),
        chain_type="stuff",
        retriever=vector_db.as_retriever()
    )

    response = qa_chain.run(prompt)
    return jsonify({"answer": response})

if __name__ == "__main__":
    # ✅ Required for Render
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
