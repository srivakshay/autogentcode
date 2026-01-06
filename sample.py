import os
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.readers.file import FlatReader
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.vector_stores.opensearch import OpensearchVectorStore, OpensearchVectorClient
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from pathlib import Path

# 1. Setup Embedding Model
Settings.embed_model = AzureOpenAIEmbedding(
    model="text-embedding-3-small",
    deployment_name="text-embedding-3-small",
    api_key=os.environ["AZURE_OPENAI_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
)

# 2. Parse Markdown
# FlatReader reads the file as a single document; MarkdownNodeParser breaks it by logic
reader = FlatReader()
md_docs = reader.load_data(Path("./data/document.md"))

# Use MarkdownNodeParser to respect headers (# ## ###)
# This ensures that a chunk doesn't cut off in the middle of a sub-section
parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(md_docs)

# 3. OpenSearch Connection
client = OpensearchVectorClient(
    endpoint="https://your-opensearch-endpoint:9200",
    index_name="markdown_index",
    dim=1536,
    http_auth=("admin", "admin")
)

vector_store = OpensearchVectorStore(client)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 4. Vectorize and Store
index = VectorStoreIndex(
    nodes, 
    storage_context=storage_context
)

print(f"Successfully indexed {len(nodes)} markdown nodes to OpenSearch.")
