from bs4 import BeautifulSoup
import markdown

def parse_md(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html_content = markdown.markdown(md_content)
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator="\n")

    metadata = {
        "source_filename": file_path.name,
        "original_length": len(md_content),
        "html_length": len(html_content)
    }

    return text.strip(), metadata
