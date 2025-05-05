import spacy
import re
import logging

# Load the English spaCy model
nlp = spacy.load("en_core_web_trf")
logger = logging.getLogger(__name__)
GENERIC_WORDS = {"unknown", "it", "this", "that", "he", "she", "they", "these", "those", "his", "her", "their", "them", "its", "him"}

def preprocess_text(text):
    # Remove page headers/footers (e.g., 'Page 1', 'Page 2', etc.)
    text = re.sub(r'\bPage\s*\d+\b', ' ', text)
    # Remove lines that are just numbers or section titles (e.g., '1', '2', 'I. INTRODUCTION')
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[IVXLC]+\.?\s+[A-Z][A-Z\s]+$', '', text, flags=re.MULTILINE)
    # Remove figure/table captions (e.g., 'Figure 1', 'Table 2', etc.)
    text = re.sub(r'(Figure|Table)\s*\d+.*\n', '', text)
    # Remove section headers (e.g., 'ABSTRACT', 'CONCLUSION', etc.)
    text = re.sub(r'^[A-Z][A-Z\s]{2,}$', '', text, flags=re.MULTILINE)
    # Fix concatenated words (lowercase followed by uppercase, e.g., 'deepLearning')
    text = re.sub(r'([a-z])([A-Z])', r'\1. \2', text)
    # Remove hyphenation at line breaks (e.g., 'multi-\nmodal' -> 'multimodal')
    text = re.sub(r'-\s*\n\s*', '', text)
    # Replace newlines with spaces
    text = text.replace('\n', ' ')
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove extra spaces
    text = text.strip()
    return text


def extract_entities(text):
    doc = nlp(text)
    allowed_labels = {"PERSON", "ORG", "GPE", "PRODUCT", "EVENT", "LAW", "WORK_OF_ART", "LOC", "FAC", "NORP", "DATE", "TIME"}
    entities = {}
    for ent in doc.ents:
        # Only include if:
        # - label is allowed
        # - not a number
        # - not generic
        # - not all lowercase
        # - not too short
        # - not a section header (heuristic: not all uppercase or not matching common section header patterns)
        if (
            ent.label_ in allowed_labels
            and len(ent.text) > 2
            and not ent.text.isdigit()
            and ent.text.lower() not in GENERIC_WORDS
            and not ent.text.islower()
            and not (ent.text.isupper() and len(ent.text.split()) <= 3)
            and not re.match(r"^page \d+$", ent.text.lower())
        ):
            entities[ent.text] = ent.label_
    logger.debug(f"Entities: {entities}")
    return entities


def extract_subjects(text):
    # Step 4: POS tagging and subject detection (using nsubj for main subject)
    doc = nlp(text)
    subjects = []
    for token in doc:
        if "subj" in token.dep_:  # Nominal subject
            subjects.append(token.text)
    return subjects
