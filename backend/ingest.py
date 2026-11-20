# ingest.py - reads your PDFs, cuts them into small pieces
# and saves the pieces in the "notes box" (ChromaDB)
import hashlib
import os

try:
    import chromadb  # type: ignore[import-not-found]
except ImportError as exc:
    raise ImportError("The 'chromadb' package is required. Install it with 'pip install chromadb'.") from exc

from pypdf import PdfReader

# The notes box, saved in a folder called notes_db
client = chromadb.PersistentClient(path="notes_db")
collection = client.get_or_create_collection("my_notes")

def cut_into_pieces(text, size=800, overlap=100):
    pieces = []
    start = 0
    while start < len(text):
        pieces.append(text[start:start + size])
        start = start + size - overlap
    return pieces

def add_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    chunks = cut_into_pieces(text)
    if not chunks:
        raise ValueError(f"No extractable text found in PDF: {pdf_path}")

    source = os.path.abspath(pdf_path)
    source_id = hashlib.sha256(source.encode("utf-8")).hexdigest()
    collection.upsert(
        documents=chunks,
        ids=[f"{source_id}-{index}" for index in range(len(chunks))],
        metadatas=[{"source": source} for _ in chunks],
    )

# This part runs only when you type: python ingest.py
if __name__ == "__main__":
    for file in os.listdir("docs"):
        if file.lower().endswith(".pdf"):
            add_pdf(os.path.join("docs", file))
    print("Total pieces in the notes box:", collection.count())
