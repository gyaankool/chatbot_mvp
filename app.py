from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
app = Flask(__name__)

# Path to store the FAISS vector database
VECTOR_DB_PATH = "vector_db"

# Multiple PDFs by language
PDF_PATHS = {
    "English": ["pdfs/english1.pdf", "pdfs/english2.pdf", "pdfs/english3.pdf", "pdfs/english4.pdf", "pdfs/english5.pdf"],
    "Hindi": ["pdfs/hindi1.pdf", "pdfs/hindi2.pdf", "pdfs/hindi3.pdf", "pdfs/hindi4.pdf", "pdfs/hindi5.pdf"],
    "Kannada": ["pdfs/kannada1.pdf", "pdfs/kannada2.pdf", "pdfs/kannada3.pdf", "pdfs/kannada4.pdf", "pdfs/kannada5.pdf"],
    "Telugu": ["pdfs/telugu1.pdf", "pdfs/telugu2.pdf", "pdfs/telugu3.pdf", "pdfs/telugu4.pdf", "pdfs/telugu5.pdf"],
    "Tamil": ["pdfs/tamil1.pdf", "pdfs/tamil2.pdf", "pdfs/tamil3.pdf", "pdfs/tamil4.pdf", "pdfs/tamil5.pdf"],
    "Marathi": ["pdfs/marathi1.pdf", "pdfs/marathi2.pdf", "pdfs/marathi3.pdf", "pdfs/marathi4.pdf", "pdfs/marathi5.pdf"],
}

def create_vector_db(language):
    pdf_paths = PDF_PATHS.get(language)
    if not pdf_paths:
        print("❌ Language not found in PDF_PATHS")
        return None

    documents = []
    for pdf_path in pdf_paths:
        abs_path = os.path.join(os.getcwd(), pdf_path)
        if os.path.exists(abs_path):
            print(f"✅ Loading PDF: {abs_path}")
            loader = PyPDFLoader(abs_path)
            documents.extend(loader.load())
        else:
            print(f"❌ Missing PDF: {abs_path}")

    if not documents:
        print("❌ No valid PDFs found, cannot create vector DB.")
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    vector_db = FAISS.from_documents(chunks, embeddings)

    vector_db.save_local(VECTOR_DB_PATH)
    print("✅ Vector DB saved.")
    return vector_db

def load_or_create_vector_db(language):
    if os.path.exists(VECTOR_DB_PATH):
        print("📁 Loading existing vector DB...")
        return FAISS.load_local(VECTOR_DB_PATH, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    else:
        print("📦 Creating new vector DB...")
        return create_vector_db(language)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    print("💬 Received POST")
    data = request.get_json()
    language = data.get("language")
    question = data.get("question")
    print(f"🌐 Language: {language}, 🧠 Question: {question}")

    vector_db = load_or_create_vector_db(language)
    if not vector_db:
        return jsonify({"answer": "❌ PDF not found for selected language."})

    # Prompt instruction
    if any(keyword in question.lower() for keyword in ["brief", "short", "summary", "in short"]):
        instruction = "Answer briefly and concisely in less than 40 words.\n"
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
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
