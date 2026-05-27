import pandas as pd
import numpy as np
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

BASE_DIR = 'e:/pycharm_project2/tiktok_project'

def try_hdbscan(embeddings, min_cluster_size=20, min_samples=5):
    try:
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        labels = clusterer.fit_predict(embeddings)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        print(f"HDBSCAN: found {n_clusters} clusters (noise points: {list(labels).count(-1)})")
        if n_clusters >= 3:
            return labels
    except Exception as e:
        print(f"HDBSCAN failed: {e}")
    return None

def fallback_kmeans(embeddings, n_clusters=8):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    return kmeans.fit_predict(embeddings)

def merge_similar_clusters(embeddings, labels, threshold=0.85):
    unique_labels = sorted(set(labels))
    unique_labels = [l for l in unique_labels if l != -1]
    
    cluster_centers = {}
    for label in unique_labels:
        mask = labels == label
        cluster_centers[label] = np.mean(embeddings[mask], axis=0)
    
    label_to_merged = {}
    merged_labels_map = {}
    new_label_counter = 0
    
    for i, label_a in enumerate(unique_labels):
        if label_a in label_to_merged:
            continue
        merged_labels_map[label_a] = new_label_counter
        label_to_merged[label_a] = new_label_counter
        center_a = cluster_centers[label_a]
        
        for label_b in unique_labels[i+1:]:
            if label_b in label_to_merged:
                continue
            center_b = cluster_centers[label_b]
            sim = cosine_similarity([center_a], [center_b])[0][0]
            if sim > threshold:
                label_to_merged[label_b] = new_label_counter
                merged_labels_map[label_b] = new_label_counter
                print(f"  Merging cluster {label_b} into {new_label_counter} (similarity: {sim:.3f})")
        
        new_label_counter += 1
    
    merged_labels = np.zeros_like(labels)
    for i, label in enumerate(labels):
        if label == -1:
            merged_labels[i] = -1
        else:
            merged_labels[i] = merged_labels_map.get(label, label)
    
    n_merged = len(set(merged_labels)) - (1 if -1 in merged_labels else 0)
    print(f"After merging: {n_merged} clusters")
    return merged_labels

def calculate_intra_cluster_similarity(embeddings, labels):
    unique_labels = sorted(set(labels))
    unique_labels = [l for l in unique_labels if l != -1]
    
    scores = {}
    for label in unique_labels:
        mask = labels == label
        cluster_embeddings = embeddings[mask]
        if len(cluster_embeddings) < 2:
            scores[label] = 0.0
            continue
        sim_matrix = cosine_similarity(cluster_embeddings)
        n = len(sim_matrix)
        avg_sim = (np.sum(sim_matrix) - n) / (n * (n - 1))
        scores[label] = avg_sim
    
    return scores

def relabel_clusters(labels):
    unique_labels = sorted(set(labels))
    unique_labels = [l for l in unique_labels if l != -1]
    label_map = {old: new for new, old in enumerate(unique_labels)}
    
    new_labels = np.zeros_like(labels)
    for i, label in enumerate(labels):
        if label == -1:
            new_labels[i] = -1
        else:
            new_labels[i] = label_map[label]
    
    return new_labels, label_map

def main():
    input_embeddings = f'{BASE_DIR}/outputs/embeddings.npy'
    input_data = f'{BASE_DIR}/outputs/cleaned_data.csv'
    output_file = f'{BASE_DIR}/outputs/clustered.csv'
    
    embeddings = np.load(input_embeddings)
    df = pd.read_csv(input_data)
    
    print(f"Data after cleaning: {len(df)} comments")
    
    print("\n[Step 1] Running HDBSCAN clustering...")
    labels = try_hdbscan(embeddings, min_cluster_size=20, min_samples=5)
    
    if labels is None:
        print("[Step 1] HDBSCAN failed, falling back to KMeans...")
        labels = fallback_kmeans(embeddings, n_clusters=8)
    
    print(f"\n[Step 2] Merging similar clusters (threshold=0.85)...")
    merged_labels = merge_similar_clusters(embeddings, labels, threshold=0.85)
    
    final_labels, label_map = relabel_clusters(merged_labels)
    df['cluster_id'] = final_labels
    
    print(f"\n[Step 3] Calculating intra-cluster similarity scores...")
    similarity_scores = calculate_intra_cluster_similarity(embeddings, final_labels)
    df['intra_cluster_sim'] = df['cluster_id'].map(similarity_scores)
    
    df.to_csv(output_file, index=False)
    
    print(f"\nClustered data saved to {output_file}")
    print(f"\nCluster distribution:")
    print(df['cluster_id'].value_counts().sort_index())
    
    print("\nCluster details:")
    for cluster_id in sorted(df['cluster_id'].unique()):
        if cluster_id == -1:
            continue
        cluster_data = df[df['cluster_id'] == cluster_id]
        avg_score = cluster_data['score'].mean()
        intra_sim = similarity_scores[cluster_id]
        print(f"  Cluster {cluster_id}: {len(cluster_data)} comments, avg score: {avg_score:.2f}, intra-sim: {intra_sim:.3f}")

if __name__ == '__main__':
    main()
