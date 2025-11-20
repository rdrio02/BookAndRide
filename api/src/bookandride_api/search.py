# app/search.py
import os
from elasticsearch import Elasticsearch


# Create the Elasticsearch client
ELASTIC_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
es = Elasticsearch(ELASTIC_URL)


def ensure_index(index_name: str):
    """Ensure that an index exists with a basic mapping."""
    try:
        if not es.indices.exists(index=index_name):
            es.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "title": {"type": "text"},
                            "author": {"type": "text"},
                            "stock": {"type": "integer"},
                        }
                    }
                },
            )
    except Exception as e:
        # Log the exact error so you can see what Elasticsearch says
        print(f"[Elasticsearch] Failed to ensure index '{index_name}': {e}")


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


def index_rental(rental: dict):
    """
    Index a rental document in Elasticsearch.
    rental: dict with keys:
      - rental_id
      - user_id
      - bike_id
      - started_at (ISO string)
      - stopped_at (ISO string)
      - total_minutes
      - price_eur
    """
    es.index(
        index="rentals",               # index name
        id=rental["rental_id"],        # document ID
        document=rental                # the actual rental data
    )