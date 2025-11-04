"""FAISS index management"""
import numpy as np
import faiss
from src.core.image_processor import process_single_image

def build_index(embeddings):
    """Build FAISS index"""
    if len(embeddings) == 0:
        print("❌ No embeddings to index")
        return None
    
    print(f"🔍 Building FAISS index for {len(embeddings)} embeddings...")
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype('float32'))
    
    print(f"✅ FAISS index built with {index.ntotal} embeddings")
    return index

def get_top_matches(index, labels, image_path, app, k=5):
    """Get top k matches for an image"""
    if index is None:
        print("❌ No index built yet")
        return []
    
    embedding = process_single_image(app, image_path, "query")
    
    if embedding is None:
        return []
    
    k = min(k, index.ntotal)
    D, I = index.search(np.array([embedding]).astype('float32'), k=k)
    
    results = []
    for i in range(k):
        score = float(D[0][i])
        label = labels[I[0][i]]
        results.append((label, score))
    
    return results