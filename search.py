import os
import psycopg
from dotenv import load_dotenv
from fastembed import TextEmbedding
from groq import Groq
from pgvector.psycopg import register_vector

load_dotenv()

# Models oru dhadavai load
embed_model = TextEmbedding("BAAI/bge-small-en-v1.5")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = "openai/gpt-oss-20b"

# 1. Question -> 384 numbers -> DB-la top 3 close chunks
def search(question, top_k=3):
    q_vector = next(embed_model.query_embed(question))
    with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
        register_vector(conn)
        rows = conn.execute(
            """SELECT content, 1 - (embedding <=> %s) AS score
               FROM chunks ORDER BY embedding <=> %s LIMIT %s""",
            (q_vector, q_vector, top_k),
        ).fetchall()
    return rows

# 2. Top chunks text + question -> Groq -> answer
def ask(question):
    rows = search(question)
    context = "\n\n".join(content for content, score in rows)

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Answer ONLY using the given context. "
                "If the answer is not in the context, say: I don't know from the document.",
            },
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return response.choices[0].message.content, rows

if __name__ == "__main__":
    while True:
        question = input("\nQuestion (exit to stop): ")
        if question.lower() == "exit":
            break
        answer, rows = ask(question)
        print("\n--- Top chunks score ---")
        for content, score in rows:
            print(f"{score:.2f} | {content[:60]!r}")
        print("\n--- Answer ---")
        print(answer)
