import spacy
import numpy as np
from sentence_transformers import SentenceTransformer, util
from typing import List, Tuple, Dict
from sklearn.cluster import AgglomerativeClustering

nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def get_optimal_chunks(sentences: List[str], embeddings: np.ndarray, min_chunk_size: int = 3, max_chunk_size: int = 8) -> List[List[int]]:
    """
    Use hierarchical clustering to find optimal chunk boundaries based on semantic similarity
    """
    if len(sentences) <= min_chunk_size:
        return [list(range(len(sentences)))]
    
    # Calculate similarity matrix
    similarities = util.cos_sim(embeddings, embeddings).cpu().numpy()
    
    # Perform hierarchical clustering
    n_clusters = max(1, len(sentences) // ((min_chunk_size + max_chunk_size) // 2))
    clustering = AgglomerativeClustering(
        n_clusters=n_clusters,
        metric='precomputed',
        linkage='complete'
    ).fit(1 - similarities)  # Convert similarities to distances
    
    # Get chunks based on cluster labels
    chunks = []
    current_chunk = []
    
    for i, label in enumerate(clustering.labels_):
        current_chunk.append(i)
        if i == len(clustering.labels_) - 1 or clustering.labels_[i] != clustering.labels_[i + 1]:
            if len(current_chunk) >= min_chunk_size:
                chunks.append(current_chunk)
            else:
                # Merge small chunks with the previous chunk or start a new one
                if chunks:
                    chunks[-1].extend(current_chunk)
                else:
                    chunks.append(current_chunk)
            current_chunk = []
    
    return chunks

def calculate_chunk_coherence(chunk_sentences: List[str], embeddings: np.ndarray) -> float:
    """
    Calculate the semantic coherence of a chunk using average cosine similarity
    """
    if len(chunk_sentences) <= 1:
        return 1.0
    
    chunk_embeddings = embeddings[chunk_sentences]
    similarities = util.cos_sim(chunk_embeddings, chunk_embeddings).cpu()
    
    # Calculate average similarity excluding self-similarity
    mask = ~np.eye(similarities.shape[0], dtype=bool)
    return float(similarities[mask].mean())

def semantic_chunk_text(text: str, min_chunk_size: int = 3, max_chunk_size: int = 8) -> List[Dict]:
    """
    Enhanced semantic chunking with improved context preservation and chunk analysis
    """
    # Process text into sentences
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    if not sentences:
        return []
    
    # Generate embeddings for all sentences
    embeddings = embedder.encode(sentences, convert_to_tensor=True)
    
    # Get optimal chunk boundaries
    chunk_indices = get_optimal_chunks(sentences, embeddings, min_chunk_size, max_chunk_size)
    
    chunks = []
    prev_chunk_end = ""
    
    for i, indices in enumerate(chunk_indices):
        chunk_sentences = [sentences[idx] for idx in indices]
        chunk_text = " ".join(chunk_sentences)
        
        # Calculate chunk metrics
        coherence = calculate_chunk_coherence(indices, embeddings)
        
        # Create chunk with metadata
        chunk = {
            "text": chunk_text,
            "sentences": chunk_sentences,
            "coherence_score": float(coherence),
            "previous_context": prev_chunk_end,
            "start_index": indices[0],
            "end_index": indices[-1],
            "sentence_count": len(chunk_sentences)
        }
        
        chunks.append(chunk)
        prev_chunk_end = chunk_sentences[-1]
    
    return chunks
