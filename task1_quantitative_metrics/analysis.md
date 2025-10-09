# Task 1: Quantitative Metrics Analysis

## Summary Statistics

| Metric | Mean | Median | Std | Min | Max |
|--------|------|--------|-----|-----|-----|
| rouge1 | 0.4464 | 0.4346 | 0.0576 | 0.3260 | 0.5683 |
| rouge2 | 0.1282 | 0.1197 | 0.0480 | 0.0573 | 0.2541 |
| rougeL | 0.2198 | 0.2055 | 0.0436 | 0.1436 | 0.3127 |
| embedding_similarity | 0.8504 | 0.8655 | 0.0590 | 0.7031 | 0.9227 |

## Interpretation

### String-Overlap Metrics (ROUGE Scores)

**ROUGE-1 (Unigram Overlap):**
- Mean: 0.4464
- The ROUGE-1 score measures the overlap of individual words between the reference and generated abstracts.
- This score indicates that the generated abstracts share 44.6% word-level overlap with the original abstracts.

**ROUGE-2 (Bigram Overlap):**
- Mean: 0.1282
- ROUGE-2 measures the overlap of two-word sequences, which better captures phrase-level similarity (local coherence).
- The ROUGE-2 score being lower than ROUGE-1 shows that matching exact phrases is more challenging than matching individual words.

**ROUGE-L (Longest Common Subsequence):**
- Mean: 0.2198
- ROUGE-L measures the longest common subsequence, which captures sentence-level structure.
- This score reflects the degree to which the generated abstracts preserve the sequential structure of the originals.

**Note:** Additional metrics like BLEU score and Jaccard similarity index could provide complementary perspectives but were not included in this analysis.


### Embedding-Based Metric (Semantic Similarity)

**Cosine Similarity:**
- Mean: 0.8504
- This metric uses embeddings from `Qwen/Qwen3-Embedding-0.6B` to measure semantic similarity. We used the implementation from `sentence transformers` library and not from `sklearn` to make the code faster in case GPU is available.
- The cosine similarity score ranges from 0 to 1, where 1 indicates perfect semantic alignment.
- This metric is crucial for scientific abstracts as it measures meaning preservation rather than exact wording.
- The model is one of the best performing models under 1B parameters according to the MTEB leaderboard, balancing quality and efficiency.
- Other strong alternatives include BAAI/bge-small-en-v1.5 (best under 100M parameters) and OpenAI's text-embedding-3-small but it does not disclose parameter count.


## Key Findings

1. **Low ROUGE-1, 2 and L values:**
For Rouge-1 the value is moderate (some key terms are captured but others missed), Rouge-2 value is weak (less coherence of generated abstract compared to reference), and Rouge-L is low/moderate (structure/order differs significantly). Overall, topic is correctly captured by the generated abstract, but not the exact focus of it. 

2. **Embedding similarity vs. ROUGE:**
The embedding similarity is high which means that the AI-generated abstract preserve core ideas, terminology, and are quite faithful to the actual abstracts. By comparing the similarity to ROUGE scores, we can conclude that the generated abstracts are conceptually preserving the meaning and idead of the original abstracts but are stylistically independent. 


![Summary Statistics Across Metrics](summary_statistics.png)  
*Figure 1: Summary statistics comparing ROUGE-1, ROUGE-2, ROUGE-L, and embedding similarity scores. The embedding metric shows a notably higher mean and median, indicating strong semantic alignment despite low lexical overlap.*


![Distribution of ROUGE and Embedding Metrics](all_metrics_distribution.png)  
*Figure 2: Histograms showing distributions for ROUGE-1, ROUGE-2, ROUGE-L, and embedding similarity scores.*

![ROUGE-L vs. Embedding Similarity](metrics_visualization.png)  
*Figure 3: Relationship between ROUGE-L and embedding similarity. The moderate correlation (r ≈ 0.51) suggests that while structural overlap and semantic similarity are related, they capture distinct aspects of abstract quality.*
