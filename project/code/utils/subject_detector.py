from collections import Counter
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Tuple
import numpy as np
from spacy.tokens import Doc

class SubjectDetector:
    """
    Detects main subjects and entities in text chunks using linguistic and statistical heuristics.
    """
    def __init__(self, spacy_model: str = "en_core_web_trf"):
        self.nlp = spacy.load(spacy_model)
        self.tfidf = TfidfVectorizer(max_df=0.95, min_df=2, max_features=100, stop_words='english')

    def extract_noun_phrases(self, doc: Doc) -> List[str]:
        """Extract meaningful noun phrases from text"""
        noun_phrases = []
        for chunk in doc.noun_chunks:
            # Filter out pronouns and determiners
            if not any(token.pos_ == "PRON" for token in chunk):
                # Keep only the core noun phrase
                core = " ".join([token.text for token in chunk 
                               if token.pos_ in {"NOUN", "PROPN"} 
                               or token.dep_ in {"compound", "amod"}])
                if core:
                    noun_phrases.append(core)
        return noun_phrases

    def score_candidates(self, candidates: List[str], doc: Doc) -> List[Tuple[str, float]]:
        """Score candidate subjects based on multiple factors"""
        scores = Counter()
        
        # Score based on frequency and position
        for i, sent in enumerate(doc.sents):
            sent_candidates = [c for c in candidates if c in sent.text]
            for candidate in sent_candidates:
                # Position score (earlier sentences get higher weight)
                pos_weight = 1.0 / (i + 1)
                scores[candidate] += pos_weight
                
                # Syntactic role score
                for token in sent:
                    if token.text in candidate.split():
                        if token.dep_ in {"nsubj", "nsubjpass"}:
                            scores[candidate] += 2.0
                        elif token.dep_ in {"dobj", "pobj"}:
                            scores[candidate] += 1.0
        
        # Score based on named entity type
        for ent in doc.ents:
            if ent.text in candidates:
                if ent.label_ in {"PERSON", "ORG", "GPE"}:
                    scores[ent.text] += 1.5
                elif ent.label_ in {"PRODUCT", "WORK_OF_ART", "EVENT"}:
                    scores[ent.text] += 1.0
        
        # Normalize scores
        if scores:
            max_score = max(scores.values())
            return [(c, s/max_score) for c, s in scores.most_common()]
        return []

    def detect_main_subject(self, chunk: str, previous_chunk: str = None) -> Dict:
        """
        Enhanced subject detection with confidence scores and supporting evidence
        """
        doc = self.nlp(chunk)
        
        # Extract candidate subjects
        candidates = list(set(self.extract_noun_phrases(doc) + [ent.text for ent in doc.ents]))
        
        if not candidates:
            return {
                "main_subject": "Unknown",
                "confidence": 0.0,
                "supporting_subjects": [],
                "context": {}
            }
        
        # Score candidates
        scored_candidates = self.score_candidates(candidates, doc)
        
        if not scored_candidates:
            return {
                "main_subject": candidates[0],
                "confidence": 0.1,
                "supporting_subjects": candidates[1:],
                "context": {}
            }
        
        # Get main subject and supporting subjects
        main_subject, confidence = scored_candidates[0]
        supporting_subjects = [
            {"subject": subj, "confidence": score} 
            for subj, score in scored_candidates[1:]
        ]
        
        # Extract contextual information
        context_info = {
            "entities": [(ent.text, ent.label_) for ent in doc.ents],
            "key_phrases": self.extract_noun_phrases(doc),
            "sentence_count": len(list(doc.sents))
        }
        
        return {
            "main_subject": main_subject,
            "confidence": confidence,
            "supporting_subjects": supporting_subjects,
            "context": context_info
        }
