import json
import logging
from pathlib import Path
from typing import List, Dict
from transformers import pipeline
import re
import spacy

from .parsers.pdf_parser import parse_pdf
from .parsers.docx_parser import parse_docx
from .parsers.txt_parser import parse_txt
from .parsers.csv_parser import parse_csv
from .parsers.html_parser import parse_html
from .parsers.md_parser import parse_md
from .chunker.semantic_chunker import semantic_chunk_text
from .resolver.pronoun_resolver import ReferenceResolver
from .utils.subject_detector import SubjectDetector
from .utils.topic_shift import detect_topic_shift
from .utils.preprocessor import preprocess_text, extract_entities

# Setup Logging
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(logs_dir / "pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Load spaCy model once for fallback subject detection
_fallback_nlp = spacy.load("en_core_web_trf")

def fallback_main_subject(chunk_text, generic_subjects):
    doc = _fallback_nlp(chunk_text)
    candidates = [ent.text for ent in doc.ents if ent.label_ in {
        "PERSON", "ORG", "GPE", "PRODUCT", "EVENT", "LAW", 
        "WORK_OF_ART", "LOC", "FAC", "NORP"} and ent.text.lower() not in generic_subjects]
    if not candidates:
        candidates = [np.text for np in doc.noun_chunks if len(np.text) > 2 and np.text.lower() not in generic_subjects]
    if not candidates:
        lines = chunk_text.split(". ")
        possible_title = lines[0].strip() if lines else "Content"
        return possible_title if 3 < len(possible_title) < 80 else "Content"
    else:
        return candidates[0]

class ChunkProcessor:
    def __init__(self):
        self.previous_chunk = None
        self.previous_subject = None
        self.ref_resolver = ReferenceResolver()
        self.subject_detector = SubjectDetector()
    
    def process_chunk(self, chunk: Dict, metadata: Dict) -> Dict:
        chunk_text = chunk["text"]
        summary = self._generate_summary(chunk_text)
        subject_info = self.subject_detector.detect_main_subject(chunk_text, self.previous_chunk["text"] if self.previous_chunk else None)
        main_subject = subject_info["main_subject"]
        generic_subjects = {"unknown", "it", "this", "that", "he", "she", "they", "these", "those", "his", "her", "their", "them", "its", "him"}
        if not main_subject or main_subject.lower() in generic_subjects or len(main_subject) < 3:
            main_subject = fallback_main_subject(chunk_text, generic_subjects)
        ambiguous_pronouns = {"it", "this", "that", "he", "she", "they", "these", "those", "him", "her", "them"}
        resolved_dict = self.ref_resolver.resolve_references(
            chunk_text,
            previous_context=self.previous_chunk["text"] if self.previous_chunk else ""
        )
        resolved_refs = {}
        for pronoun, antecedent in resolved_dict.items():
            if pronoun.lower() in ambiguous_pronouns and antecedent and antecedent.lower() not in ambiguous_pronouns and len(antecedent) > 2:
                resolved_refs[pronoun] = antecedent
        topic_shift_info = detect_topic_shift(
            self.previous_chunk["text"] if self.previous_chunk else None,
            chunk_text,
            self.previous_subject,
            main_subject
        )
        topic_shift_flag = False
        if isinstance(topic_shift_info, dict):
            if topic_shift_info.get("has_shift"): topic_shift_flag = True
            if topic_shift_info.get("transition") and topic_shift_info["transition"].get("prev_topic") != topic_shift_info["transition"].get("curr_topic"): topic_shift_flag = True
            if topic_shift_info.get("analysis", {}).get("discourse_markers"): topic_shift_flag = True
        all_entities = extract_entities(chunk_text)
        allowed_labels = {"PERSON", "ORG", "GPE", "PRODUCT", "EVENT", "LAW", "WORK_OF_ART", "LOC", "FAC", "NORP", "DATE", "TIME"}
        section_headers = set()
        if "section_title" in metadata:
            section_headers.add(metadata["section_title"].lower())
        entities = [ent for ent, label in all_entities.items()
                    if label in allowed_labels and len(ent) > 1 and not ent.isdigit() and ent.lower() not in section_headers and ent.lower() not in generic_subjects]
        filtered_metadata = {k: v for k, v in metadata.items() if k in ["section_title", "page", "source_filename"]}
        if "page" not in filtered_metadata:
            match = re.search(r"page\s*(\d+)", chunk_text, re.IGNORECASE)
            if match:
                filtered_metadata["page"] = int(match.group(1))
        if "section_title" not in filtered_metadata:
            lines = chunk_text.split(". ")
            if lines:
                possible_title = lines[0].strip()
                if 3 < len(possible_title) < 80:
                    filtered_metadata["section_title"] = possible_title
        # Add previous ending context as last sentence of previous chunk
        previous_ending_context = ""
        if self.previous_chunk:
            prev_text = self.previous_chunk["text"]
            sentences = re.split(r'(?<=[.!?]) +', prev_text)
            previous_ending_context = sentences[-1].strip() if sentences else prev_text.strip()
        processed_chunk = {
            "chunk_index": chunk["start_index"],
            "content": chunk_text,
            "summary": summary,
            "previous_ending_context": previous_ending_context,
            "main_subject": main_subject,
            "resolved_references": resolved_refs,
            "topic_shift_flag": topic_shift_flag,
            "entities": entities,
            "metadata": filtered_metadata
        }
        self.previous_chunk = chunk
        self.previous_subject = main_subject
        return processed_chunk

    def _generate_summary(self, text: str) -> str:
        try:
            summary = summarizer(text, max_length=60, min_length=30, do_sample=False)[0]["summary_text"]
            return summary
        except Exception as e:
            logger.warning(f"Failed to generate summary: {e}")
            return text[:200] + "..."

def process_file(file_path: Path) -> List[Dict]:
    logger.info(f"Started processing file: {file_path}")
    ext = file_path.suffix.lower()
    try:
        if ext == ".pdf":
            text, metadata = parse_pdf(file_path)
        elif ext == ".docx":
            text, metadata = parse_docx(file_path)
        elif ext == ".txt":
            text, metadata = parse_txt(file_path)
        elif ext == ".csv":
            text, metadata = parse_csv(file_path)
        elif ext == ".html":
            text, metadata = parse_html(file_path)
        elif ext == ".md":
            text, metadata = parse_md(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    except Exception as e:
        logger.error(f"Failed to parse file {file_path.name}: {e}")
        raise
    clean_text = preprocess_text(text)
    chunks = semantic_chunk_text(clean_text)
    processor = ChunkProcessor()
    processed_chunks = []
    for chunk in chunks:
        try:
            processed_chunk = processor.process_chunk(chunk, metadata)
            processed_chunks.append(processed_chunk)
            logger.debug(f"Processed chunk {chunk['start_index']} successfully")
        except Exception as e:
            logger.error(f"Error processing chunk {chunk['start_index']}: {e}")
            continue
    logger.info(f"Finished processing file: {file_path}")
    return processed_chunks

def main():
    input_folder = Path("input")
    output_folder = Path("output")
    output_folder.mkdir(exist_ok=True)

    for file in input_folder.iterdir():
        try:
            logger.info(f"Processing {file.name}")
            result = process_file(file)
            out_path = output_folder / f"{file.stem}_chunks.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved output to {out_path}")
        except Exception as e:
            logger.exception(f"Error processing {file.name}")


if __name__ == "__main__":
    main()
