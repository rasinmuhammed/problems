from bs4 import BeautifulSoup

def parse_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script and style tags
    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text(separator="\n")

    metadata = {
        "source_filename": file_path.name,
        "tag_summary": list(set(tag.name for tag in soup.find_all()))
    }

    return text.strip(), metadata
