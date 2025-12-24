# services/embedder.py

from sentence_transformers import SentenceTransformer

# Definition of the function to call the embedding model (here local)

model = SentenceTransformer("intfloat/multilingual-e5-small")

class LocalEmbeddingWrapper:
    def __init__(self, model):
        self.model = model
        self.embedding_dim = 384  # to change with the model => print(model.get_sentence_embedding_dimension())

    async def __call__(self, texts):
        # Not really async, but simulated (OK for LightRAG)
        return self.model.encode(texts, convert_to_numpy=True).tolist()

embedder = LocalEmbeddingWrapper(model)