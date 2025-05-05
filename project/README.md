# ChunkSmash Hackathon Submission

## Participant Details

- **Full Name:** Muhammed Rasin O M
- **GitHub Username:** [rasinmuhammed](https://github.com/rasinmuhammed)
- **Contact Email:** rasinbinabdulla@gmail.com

---

## 🧠 Chunking Strategy

We use **semantic chunking** based on sentence segmentation and contextual coherence. The pipeline:
- Preprocesses and normalizes text
- Segments into sentences
- Groups sentences into context-preserving chunks using subject continuity and topic shift detection
- Each chunk is enriched with summary, main subject, resolved references, and entities

---

## 📝 Logic Brief

1. **File Parsing:**
   - Supports PDF, DOCX, TXT, CSV, HTML, and MD via modular parsers.
2. **Preprocessing:**
   - Cleans and normalizes text, preserving casing for NER.
3. **Semantic Chunking:**
   - Groups sentences into coherent chunks using subject and topic continuity.
4. **Subject Detection:**
   - Uses spaCy and TF-IDF to extract the main subject and supporting entities for each chunk.
5. **Pronoun/Reference Resolution:**
   - Resolves ambiguous pronouns using context, entity type, and syntactic role.
6. **Topic Shift Detection:**
   - Flags topic shifts using semantic similarity and subject change.
7. **Output:**
   - Each chunk is output as a JSON object with all relevant metadata for RAG.

---

## 🔍 Pronoun/Reference Resolution

- **Approach:**
  - Only resolves actual pronouns (not determiners or relatives).
  - For personal pronouns ("he", "she", etc.), only resolves to PERSON entities using spaCy NER.
  - For other ambiguous pronouns ("it", "this", etc.), resolves to the nearest previous named entity or proper noun, but only if contextually appropriate.
  - No resolution is performed if no valid antecedent is found.
  - This prevents spurious mappings and ensures only high-confidence, contextually clear resolutions are included.

---

_This project is part of the ChunkSmash Hackathon 2025._ 