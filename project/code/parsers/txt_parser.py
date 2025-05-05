def parse_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    metadata = {
        "source_filename": file_path.name,
        "lines": text.count("\n")
    }
    return text.strip(), metadata
