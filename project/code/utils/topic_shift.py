from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Dict, List, Tuple, Optional
from sentence_transformers import SentenceTransformer
import spacy

# Load models
nlp = spacy.load("en_core_web_trf")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

class TopicTransition:
    def __init__(self, prev_topic: str, curr_topic: str, confidence: float, transition_type: str):
        self.prev_topic = prev_topic
        self.curr_topic = curr_topic
        self.confidence = confidence
        self.transition_type = transition_type
        self.supporting_evidence = []

    def add_evidence(self, evidence: str, evidence_type: str):
        self.supporting_evidence.append({
            "evidence": evidence,
            "type": evidence_type
        })

def get_semantic_similarity(text1: str, text2: str) -> float:
    """Calculate semantic similarity using sentence transformers"""
    emb1 = embedder.encode(text1, convert_to_tensor=True)
    emb2 = embedder.encode(text2, convert_to_tensor=True)
    # Ensure numpy arrays on CPU
    emb1_np = emb1.cpu().numpy() if hasattr(emb1, 'cpu') else emb1
    emb2_np = emb2.cpu().numpy() if hasattr(emb2, 'cpu') else emb2
    return float(cosine_similarity(emb1_np.reshape(1, -1), emb2_np.reshape(1, -1))[0, 0])

def extract_key_terms(doc: spacy.tokens.Doc) -> List[str]:
    """Extract important terms from text"""
    key_terms = []
    
    # Get named entities
    key_terms.extend([ent.text for ent in doc.ents])
    
    # Get important noun phrases
    key_terms.extend([chunk.text for chunk in doc.noun_chunks 
                     if not any(token.pos_ == "PRON" for token in chunk)])
    
    # Get important verbs
    key_terms.extend([token.lemma_ for token in doc 
                     if token.pos_ == "VERB" and not token.is_stop])
    
    return list(set(key_terms))

def analyze_discourse_markers(text: str) -> List[Dict]:
    """Analyze discourse markers indicating topic transitions"""
    markers = {
        "contrast": ["however", "but", "although", "conversely", "in contrast"],
        "addition": ["moreover", "furthermore", "additionally", "in addition"],
        "sequence": ["first", "second", "finally", "then", "next"],
        "summary": ["therefore", "thus", "in conclusion", "to summarize"],
        "topic_shift": ["regarding", "concerning", "as for", "turning to", "speaking of"]
    }
    
    found_markers = []
    doc = nlp(text.lower())
    
    for sent in doc.sents:
        sent_text = sent.text.lower()
        for marker_type, marker_list in markers.items():
            for marker in marker_list:
                if marker in sent_text:
                    found_markers.append({
                        "marker": marker,
                        "type": marker_type,
                        "sentence": sent.text
                    })
    
    return found_markers

def detect_topic_shift(prev_chunk: Optional[str], curr_chunk: str, 
                      prev_subject: Optional[str] = None, 
                      curr_subject: Optional[str] = None,
                      threshold: float = 0.5) -> Dict:
    """
    Enhanced topic shift detection with detailed analysis and confidence scoring
    """
    if not prev_chunk:
        return {
            "has_shift": True,
            "confidence": 1.0,
            "transition": None,
            "analysis": {
                "reason": "First chunk in sequence",
                "semantic_similarity": None,
                "discourse_markers": []
            }
        }
    
    # Calculate semantic similarity
    similarity = get_semantic_similarity(prev_chunk, curr_chunk)
    
    # Analyze discourse markers
    discourse_markers = analyze_discourse_markers(curr_chunk)
    
    # Process chunks with spaCy
    prev_doc = nlp(prev_chunk)
    curr_doc = nlp(curr_chunk)
    
    # Extract key terms
    prev_terms = extract_key_terms(prev_doc)
    curr_terms = extract_key_terms(curr_doc)
    
    # Calculate term overlap
    common_terms = set(prev_terms) & set(curr_terms)
    term_overlap = len(common_terms) / max(len(prev_terms), len(curr_terms)) if prev_terms else 0
    
    # Initialize confidence score
    confidence = 0.0
    has_shift = False
    shift_type = "continuous"
    
    # Analyze different factors
    if similarity < threshold:
        confidence += 0.4
        has_shift = True
        shift_type = "semantic_break"
    
    if term_overlap < 0.3:
        confidence += 0.3
        has_shift = True
        shift_type = "vocabulary_shift"
    
    if any(marker["type"] == "topic_shift" for marker in discourse_markers):
        confidence += 0.3
        has_shift = True
        shift_type = "explicit_transition"
    
    # Create transition object if shift detected
    transition = None
    if has_shift:
        transition = TopicTransition(
            prev_subject or "unknown",
            curr_subject or "unknown",
            confidence,
            shift_type
        )
        
        # Add supporting evidence
        if similarity < threshold:
            transition.add_evidence(
                f"Semantic similarity: {similarity:.2f} < threshold: {threshold}",
                "semantic"
            )
        if term_overlap < 0.3:
            transition.add_evidence(
                f"Term overlap: {term_overlap:.2f}",
                "lexical"
            )
        for marker in discourse_markers:
            transition.add_evidence(
                f"Discourse marker: {marker['marker']} ({marker['type']})",
                "discourse"
            )
    
    return {
        "has_shift": has_shift,
        "confidence": confidence,
        "transition": transition.__dict__ if transition else None,
        "analysis": {
            "semantic_similarity": similarity,
            "term_overlap": term_overlap,
            "common_terms": list(common_terms),
            "discourse_markers": discourse_markers,
            "prev_key_terms": prev_terms,
            "curr_key_terms": curr_terms
        }
    }


def cosine_similarity_tfidf(doc1_list, doc2_list):
    """
    Compute cosine similarity between two lists of strings using TF-IDF,
    with safe handling for empty or stopword-only documents.
    """
    # Remove empty or whitespace-only documents
    doc1_list = [doc.strip() for doc in doc1_list if doc.strip()]
    doc2_list = [doc.strip() for doc in doc2_list if doc.strip()]

    # If all inputs are empty after cleaning, return zero similarity
    if not doc1_list or not doc2_list:
        return [[0.0]]

    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(doc1_list + doc2_list)
        tfidf_matrix_1 = tfidf_matrix[:len(doc1_list)]
        tfidf_matrix_2 = tfidf_matrix[len(doc1_list):]
        return cosine_similarity(tfidf_matrix_1, tfidf_matrix_2)
    except ValueError:
        # This catches the empty vocabulary error
        return [[0.0]]

