# 🧠 Chunk Smash Hackathon: Semantic Chunking for Intelligent RAG Pipelines

Welcome to **Chunk Smash**, an NLP hackathon hosted by ZySec AI. Your mission is to build a powerful pipeline that ingests real-world documents, breaks them into semantically meaningful chunks, detects main topics, and resolves ambiguous references — all without using LLMs.

## 📘 Background

In Retrieval-Augmented Generation (RAG) systems, the quality of document chunks directly determines the accuracy of retrieval and the reliability of final outputs. But in practice, documents are messy — from PDFs with irregular formatting to DOCX files filled with nested tables and pronoun-heavy language.

**Chunking is not trivial.** It’s a core NLP task that requires:
- Understanding document structure,
- Preserving context across splits,
- Identifying main subjects,
- Resolving references like "this", "he", "it".

## 🚩 Problem Statement

Design a chunking pipeline that:
- Ingests multi-format documents
- Segments them into context-preserving chunks
- Identifies the **main subject** of each chunk
- Resolves **ambiguous references** (e.g., "this", "it", "he")
- Flags **topic shifts** between chunks

Your output will be used in downstream RAG systems — but in this hackathon, your focus is **only up to chunk generation and context enrichment**.

## 📋 Requirements

### ✅ 1. File Parsing
- Accept at least 3 formats: `.pdf`, `.docx`, `.txt`, `.csv`, `.html`, or `.md`
- Extract core textual content (cleaned of layout noise)
- (Optional) Extract structural metadata (e.g., section headers)

### ✅ 2. Chunking Logic
- Implement **at least one intelligent chunking strategy**, such as:
  - Paragraph or section-based splitting
  - Sentence grouping with overlap
  - Semantic-based segmentation using sentence embeddings

### ✅ 3. Subject & Context Detection
Each chunk must contain:
- A **main subject** (topic/theme)
- Flag for **topic shift** from the previous chunk
- A dictionary of **resolved pronoun references**
- The **ending sentence of the previous chunk**

### ✅ 4. Output Fields (per chunk)

<pre>
{
  "chunk_index": 2,
  "content": "The GDPR framework was enforced across the European Union in 2018. It was introduced to strengthen and unify data protection for individuals. This regulation applies to all companies handling EU citizen data, regardless of location.",
  "summary": "The GDPR, introduced in 2018, standardizes data protection laws across the EU and applies globally to companies handling EU citizen data.",
  "previous_ending_context": "Data breaches were rising in frequency across industries by the mid-2010s.",
  "main_subject": "GDPR Data Protection Framework",
  "resolved_references": {
    "It": "The GDPR framework",
    "This regulation": "The GDPR framework"
  },
  "topic_shift_flag": true,
  "entities": ["GDPR", "European Union", "2018", "data protection", "companies", "EU citizen data"],
  "metadata": {
    "section_title": "Legal Frameworks",
    "page": 4,
    "source_filename": "GDPR_Compliance_Whitepaper.pdf"
  }
}
</pre>

## 🗃️ Output Storage Format

### 📁 Directory

All output files should be placed in the following folder:

output/

### 📄 Filename Format

Each output file should be named using the format:

<original_filename>_chunks.json

**Example:**  
For an input file named `Policy_Guide.pdf`, the output file must be named:

output/Policy_Guide_chunks.json

## 🛠️ Deliverables

Participants must follow this submission process:

1. **Fork this repository** to your GitHub account.
2. Create a new branch using the naming convention:  chunksmash_**gitusername**
3. Inside your forked repo, add your work to a new folder:
      ### Your submission must include:
      
      - `code/` — Your complete, documented codebase (chunker, context handler, parser)
      - `output/` — JSON output files for at least 3 different input documents
      - `README.md` — Must include:
      - Your full name
      - GitHub username
      - Contact email
      - Your chunking strategy
      - Brief of your logic.
      - How pronoun/reference resolution is handled
      - *(Optional)* Short demo video (3–5 minutes) as a link or file

4. Once you're done, **open a Pull Request (PR)** from your branch to the main repo. Make sure your code is modular, your JSON output is valid, and everything is clearly documented. Submissions that don't follow this structure may not be evaluated.

## 🔒 Rules & Constraints

> ⚠️ **LLM Usage Policy**  
> Participants **may not use LLMs** (e.g., GPT, Claude, Mistral, LLaMA) for:
> - Summarization  
> - Subject detection  
> - Pronoun resolution

Only classical NLP methods (e.g., SpaCy, NLTK, sentence-transformers) or rule-based logic may be used. Violations will disqualify the submission.

## 🏆 Prizes & Rewards

- 🥇 **Top 1 Participant**: Offered a **full-time job opportunity**
- 🏅 **Next Top 4 (Ranks 2–5)**: Each awarded **$100 USD**

## 🧪 Scoring Rubric (100 Points)

| Category                     | Points | Description |
|-----------------------------|--------|-------------|
| File Parsing & Cleanup      | 15     | Handles formatting noise, layout issues |
| Chunking Logic              | 30     | Intelligent boundaries, overlap, and structure |
| Subject & Context Detection | 30     | Accurate topic detection, pronoun resolution |
| Code Quality & Structure    | 15     | Modularity, clarity, reusability |
| Reporting & Output Format   | 10     | Clean JSON structure and clear metadata |

## 🤝 Contact

**Organizer**: [ZySec HR](mailto:hr@zysec.ai)  
**Company**: ZySec AI

> “Smash documents into chunks — not into pieces.” 🔥
