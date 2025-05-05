# 📚 ChunkSmash: Modular Semantic Chunking Pipeline for RAG

## 🚀 Project Overview

**ChunkSmash** is a high-quality, modular document chunking pipeline designed for Retrieval-Augmented Generation (RAG) and advanced document understanding. It parses multi-format documents, segments them into context-preserving chunks, detects main subjects, resolves ambiguous references, flags topic shifts, and outputs rich, RAG-ready JSON metadata.

---

## 🏗️ Architecture

```
[ Parsers ]  →  [ Preprocessor ]  →  [ Semantic Chunker ]  →  [ Chunk Processor ]
   |                |                      |                        |
 .pdf/.docx/...   Clean text         Contextual Chunks         [SubjectDetector]
                                                           [ReferenceResolver]
                                                           [TopicShiftDetector]
                                                           [EntityExtractor]
```

- **Parsers**: Modular support for PDF, DOCX, TXT, CSV, HTML, MD, etc.
- **Preprocessor**: Cleans and normalizes text, preserves casing for NER.
- **Semantic Chunker**: Groups sentences into coherent, context-rich chunks.
- **Chunk Processor**: For each chunk:
  - Summarizes content
  - Detects main subject (class: `SubjectDetector`)
  - Resolves references (class: `ReferenceResolver`)
  - Flags topic shifts (class: `TopicShiftDetector`)
  - Extracts entities
  - Outputs RAG-ready JSON

---

## 🧩 Key Modules

- `SubjectDetector`: Class-based, extensible main subject and entity detector using spaCy and TF-IDF.
- `ReferenceResolver`: Class-based, high-confidence pronoun and reference resolver with context support.
- `TopicShiftDetector`: Detects topic shifts using semantic similarity, discourse markers, and subject change.
- `EntityExtractor`: Strict, RAG-friendly entity extraction.
- `ChunkProcessor`: Orchestrates all chunk-level processing.

---

## 🛠️ Usage

### 1. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_trf
```

### 2. Run the pipeline on a file
```bash
python run_pipeline.py input/yourfile.pdf
```
- Output is saved as `output/yourfile_chunks.json`.

### 3. Output Format
Each chunk is a JSON object with:
```json
{
  "chunk_index": 0,
  "content": "...",
  "summary": "...",
  "previous_ending_context": "...",
  "main_subject": "...",
  "resolved_references": { "this": "Notion Press" },
  "topic_shift_flag": true,
  "entities": ["Notion Press", "India"],
  "metadata": { "source_filename": "...", "page": 1, "section_title": "..." }
}
```

---

## 🧑‍💻 API (Extend or Use in Your Code)

```python
from code.resolver.pronoun_resolver import ReferenceResolver
from code.utils.subject_detector import SubjectDetector

ref_resolver = ReferenceResolver()
subject_detector = SubjectDetector()

resolved = ref_resolver.resolve_references(chunk, previous_chunk)
subject_info = subject_detector.detect_main_subject(chunk, previous_chunk)
```

---

## 🧑‍🔬 Extensibility & Cool Features
- **Plug-and-play**: Swap out or extend any module (parsers, chunker, detectors).
- **Class-based**: Easy to test, extend, or use in other projects.
- **Transformer-powered**: Uses spaCy transformer models and sentence transformers for best-in-class NLP.
- **RAG-Ready**: Output is designed for direct use in retrieval-augmented generation and LLM pipelines.
- **Hackathon-Optimized**: Fast, robust, and easy to demo.

---

## 🏆 For Hackathon Judges
- **Super modular**: Each NLP task is a class, easy to swap or improve.
- **High-quality output**: Only high-confidence, contextually clear resolutions and entities.
- **Rich metadata**: Every chunk is packed with context for downstream AI.
- **Easy to run**: One command, any document.

---

## 📬 Contact
- **Author**: Muhammed Rasin O M ([rasinmuhammed](https://github.com/rasinmuhammed))
- **Email**: rasinbinabdulla@gmail.com

---

_This project is part of the ChunkSmash Hackathon 2025. Good luck to all teams!_