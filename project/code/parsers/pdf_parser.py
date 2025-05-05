import pdfplumber

def parse_pdf(file_path):
    text = ""
    metadata = {
        "source_filename": file_path.name,
        "pages": 0
    }

    with pdfplumber.open(file_path) as pdf:
        metadata["pages"] = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {i + 1} ---\n{page_text}\n"
    
    print(text)

    return text.strip(), metadata

