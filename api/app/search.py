# app/search.py
import os
from elasticsearch import Elasticsearch

ELASTIC_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

# Create the Elasticsearch client
es = Elasticsearch(ELASTIC_URL)

def ensure_index(index_name: str):
    """Ensure that an index exists with basic mapping."""
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body={
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "author": {"type": "text"},
                    "stock": {"type": "integer"}
                }
            }
        })

def index_book(book):
    """Index a single book document."""
    ensure_index("books")
    es.index(index="books", id=book.id, document={
        "title": book.title,
        "author": book.author,
        "stock": book.stock,
    })

def search_books(query: str):
    """Search books by title or author."""
    ensure_index("books")
    res = es.search(
        index="books",
        query={
            "multi_match": {
                "query": query,
                "fields": ["title", "author"],
                "fuzziness": "AUTO"  # allows partial or misspelled matches
            }
        }
    )
    return [hit["_source"] for hit in res["hits"]["hits"]]
