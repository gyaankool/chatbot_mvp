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

PDF_PATHS = {
    "English": "pdfs/english.pdf",
    "Hindi": "pdfs/hindi.pdf",
    "Kannada": "pdfs/kannada.pdf",
    "Telugu": "pdfs/telugu.pdf",
    "Tamil": "pdfs/tamil.pdf",
    "Marathi": "pdfs/marathi.pdf",
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    language = data.get("language")
    question = data.get("question")

    pdf_path = PDF_PATHS.get(language)
    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({"answer": "❌ PDF not found for selected language."})

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    all_text = "\n".join([doc.page_content for doc in documents])

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(all_text)
    embeddings = OpenAIEmbeddings()
    vector_db = FAISS.from_texts(chunks, embeddings)

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
    app.run(debug=True)
