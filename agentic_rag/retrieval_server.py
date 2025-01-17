import os
import pathway as pw
from pathway.xpacks.llm.servers import DocumentStoreServer
from pathway.xpacks.llm.document_store import DocumentStore
from pathway.stdlib.indexing import HybridIndexFactory
from pathway.xpacks.llm.embedders import GeminiEmbedder
from pathway.xpacks.llm.splitters import TokenCountSplitter
from pathway.io.fs import read
from constants import CLEANED_DATA_FOLDER, GEMINI_API_KEY, PATHWAY_LICENSE_KEY, HOST, PORT
pw.set_license_key(PATHWAY_LICENSE_KEY)
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
data = read(
    CLEANED_DATA_FOLDER,
    format="binary",
    with_metadata=True,
)

splitter = TokenCountSplitter(max_tokens=512)
embedder = GeminiEmbedder(model="models/embedding-001", api_key=GEMINI_API_KEY)

knn_factory = pw.indexing.BruteForceKnnFactory(embedder = embedder)
bm25_factory = pw.indexing.TantivyBM25Factory()
hybrid_factory = HybridIndexFactory(retriever_factories=[bm25_factory, knn_factory])

document_store = DocumentStore(docs=data,splitter=splitter, retriever_factory=knn_factory)
server = DocumentStoreServer(host=HOST, port=PORT, document_store=document_store)
server.run(with_cache=False)
