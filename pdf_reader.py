from pypdf import PdfReader

# 1. PDF-la irundhu full text edukka
def read_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# 2. Text-ah chinna chunks-aa split (500 letters, 100 overlap)
def split_chunks(text, size=500, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks

if __name__ == "__main__":
    text = read_pdf("docs/Yasir_Resume_2026_Updated (1).pdf")
    chunks = split_chunks(text)
    print("Total letters:", len(text))
    print("Total chunks:", len(chunks))
    print("--- First chunk ---")
    print(chunks[0])
