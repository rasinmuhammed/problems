import spacy
from typing import Dict, Optional

class ReferenceResolver:
    """
    Resolves ambiguous pronouns and references in text using spaCy and rule-based logic.
    Only resolves actual pronouns, not determiners or relative pronouns.
    For personal pronouns (he, she, etc.), only resolves to PERSON entities.
    """
    AMBIGUOUS_PRONOUNS = {"it", "this", "that", "he", "she", "they", "these", "those", "him", "her", "them"}
    GENERIC_WORDS = AMBIGUOUS_PRONOUNS | {"unknown", "work", "part", "format", "future", "occasion", "addition", "provisions", "forms", "calls", "service", "agreement", "order", "payments", "press"}
    ALLOWED_ENTITY_LABELS = {"PERSON", "ORG", "GPE", "PRODUCT", "EVENT", "LAW", "WORK_OF_ART", "LOC", "FAC", "NORP", "DATE", "TIME"}
    PERSONAL_PRONOUNS = {"he", "him", "his", "she", "her", "hers"}

    def __init__(self, spacy_model: str = "en_core_web_trf"):
        self.nlp = spacy.load(spacy_model)

    def is_good_antecedent(self, antecedent: str) -> bool:
        if not antecedent or len(antecedent) < 2:
            return False
        if antecedent.lower() in self.GENERIC_WORDS:
            return False
        return True

    def resolve_references(self, text: str, previous_context: Optional[str] = None) -> Dict[str, str]:
        """
        Resolves ambiguous pronouns in the given text using context and returns a mapping.
        Only high-confidence, contextually clear resolutions are included.
        Only resolves actual pronouns, not determiners or relative pronouns.
        For personal pronouns (he, she, etc.), only resolves to PERSON entities.
        """
        if previous_context:
            text = previous_context + " " + text
        doc = self.nlp(text)
        resolved = {}

        for token in doc:
            if (
                token.text.lower() in self.AMBIGUOUS_PRONOUNS
                and token.pos_ == "PRON"
                and token.dep_ not in {"relcl", "poss"}
            ):
                pronoun = token.text.lower()
                sents = list(doc.sents)
                sent_idx = None
                for i, sent in enumerate(sents):
                    if token.i >= sent.start and token.i < sent.end:
                        sent_idx = i
                        break
                candidates = []
                if sent_idx is not None:
                    sent = sents[sent_idx]
                    for ent in sent.ents:
                        if ent.label_ in self.ALLOWED_ENTITY_LABELS and self.is_good_antecedent(ent.text):
                            candidates.append(ent.text)
                    for t in sent:
                        if t.pos_ == "PROPN" and self.is_good_antecedent(t.text):
                            candidates.append(t.text)
                    if sent_idx > 0:
                        prev_sent = sents[sent_idx-1]
                        for ent in prev_sent.ents:
                            if ent.label_ in self.ALLOWED_ENTITY_LABELS and self.is_good_antecedent(ent.text):
                                candidates.append(ent.text)
                        for t in prev_sent:
                            if t.pos_ == "PROPN" and self.is_good_antecedent(t.text):
                                candidates.append(t.text)
                # For personal pronouns, only resolve to PERSON entities
                if pronoun in self.PERSONAL_PRONOUNS:
                    person_candidates = [ent.text for ent in doc.ents if ent.label_ == "PERSON" and self.is_good_antecedent(ent.text)]
                    # Only consider PERSONs that appear before the pronoun
                    person_candidates = [c for c in person_candidates if any(doc[i].text == c for i in range(token.i))]
                    if person_candidates:
                        antecedent = person_candidates[-1]
                        resolved[token.text] = antecedent
                    continue  # skip if no valid PERSON candidate
                # For other pronouns, fallback to previous logic
                antecedent = None
                for prev in reversed(candidates):
                    if prev.lower() != token.text.lower() and self.is_good_antecedent(prev):
                        antecedent = prev
                        break
                if antecedent:
                    resolved[token.text] = antecedent

        # For demonstrative noun phrases, only resolve if the chunk is a single word and is a pronoun
        for chunk in doc.noun_chunks:
            if (
                len(chunk) == 1
                and chunk[0].text.lower() in self.AMBIGUOUS_PRONOUNS
                and chunk[0].pos_ == "PRON"
            ):
                continue
        return resolved
