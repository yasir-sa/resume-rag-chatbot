import os
import psycopg
from dotenv import load_dotenv
from fastembed import TextEmbedding
from pgvector.psycopg import register_vector
from pdf_reader import read_pdf, split_chunks

load_dotenv()

PDF_PATH = "docs/Yasir_Resume_2026_Updated (1).pdf"

# 1. PDF read + 12 chunks
text = read_pdf(PDF_PATH)
chunks = split_chunks(text)

# 2. Ovvoru chunk -> 384 numbers
model = TextEmbedding("BAAI/bge-small-en-v1.5")
vectors = list(model.embed(chunks))

# 3. Neon DB-la save
with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
    register_vector(conn)  # numbers list-ah vector type-aa anuppa

    # Same PDF marubadiyum run pannaa duplicate aagaama pazhaya rows delete
    conn.execute("DELETE FROM chunks WHERE source = %s", (PDF_PATH,))

    for chunk, vector in zip(chunks, vectors):
        conn.execute(
            "INSERT INTO chunks (source, content, embedding) VALUES (%s, %s, %s)",
            (PDF_PATH, chunk, vector),
        )

print(f"{len(chunks)} chunks DB-la save aagiduchu!")
