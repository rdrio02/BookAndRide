# Assessment 1 - DatOps

# Description
This Project is about making or building a API capable of storing books and rentals of bikes using FastAPI. The Project is capable of doing serialization and deserialization and also provides with data visualization using Grafana and ElasticSearch.


# Get Books Data

### JSON format
```bash
curl -H "Accept: application/json" http://localhost:8000/books
```

### XML format
```bash
curl -H "Accept: application/xml" http://localhost:8000/books
```

### YAML format
```bash
curl -H "Accept: application/x-yaml" http://localhost:8000/books
```

### Get Books without accept headers (returns in JSON)
```bash
curl http://localhost:8000/books
```

---

## ADD a Book

### JSON input, default output JSON
```bash
curl -X POST http://localhost:8000/books   -H "Content-Type: application/json"   -d '{"title":"Dune","author":"Frank Herbert","stock":12}'
```

### JSON input, explicit JSON output
```bash
curl -X POST http://localhost:8000/books   -H "Content-Type: application/json"   -H "Accept: application/json"   -d '{"title":"Dune","author":"Frank Herbert","stock":12}'
```

### XML input, XML output
```bash
curl -X POST http://localhost:8000/books   -H "Content-Type: application/xml"   -H "Accept: application/xml"   -d '<?xml version="1.0" encoding="UTF-8"?>
<book>
<title>Dune</title>
<author>Frank Herbert</author>
<stock>12</stock>
</book>'
```

### YAML input, YAML output
```bash
curl -X POST http://localhost:8000/books   -H "Content-Type: application/x-yaml"   -H "Accept: application/x-yaml"   -d '
title: Dune
author: Frank Herbert
stock: 12
'
```

---

## Update a Book

### JSON input, default JSON output
```bash
curl -X PUT http://localhost:8000/books/35   -H "Content-Type: application/json"   -d '{"stock": 20}'
```

### XML input, XML output
```bash
curl -X PUT http://localhost:8000/books/35   -H "Content-Type: application/xml"   -H "Accept: application/xml"   -d '<?xml version="1.0"?>
<book>
<stock>20</stock>
</book>'
```

### YAML input, YAML output
```bash
curl -X PUT http://localhost:8000/books/35   -H "Content-Type: application/x-yaml"   -H "Accept: application/x-yaml"   -d '
stock: 20
'
```

---

## Delete a Book

```bash
curl -X DELETE http://localhost:8000/books/35
```

### JSON
```bash
curl -X DELETE http://localhost:8000/books/39 -H "Accept: application/json"
```

### XML
```bash
curl -X DELETE http://localhost:8000/books/39 -H "Accept: application/xml"
```

### YAML
```bash
curl -X DELETE http://localhost:8000/books/39 -H "Accept: application/x-yaml"
```

---

## Delete ALL (Requires API Key)

### JSON
```bash
curl -X DELETE http://localhost:8000/books   -H "X-API-Key: admin-key-456"   -H "Accept: application/json"
```

### XML
```bash
curl -X DELETE http://localhost:8000/books   -H "X-API-Key: admin-key-456"   -H "Accept: application/xml"
```

### YAML
```bash
curl -X DELETE http://localhost:8000/books   -H "X-API-Key: admin-key-456"   -H "Accept: application/x-yaml"
```

---

# Rentals

## Start Rentals

### JSON
```bash
curl -X POST http://localhost:8000/rentals/start   -H "Content-Type: application/json"   -H "Accept: application/json"   -H "X-API-Key: dev-key-123"   -d '{
        "bike_id": "BIKE-101",
        "user_id": 1
      }'
```

### XML
```bash
curl -X POST http://localhost:8000/rentals/start   -H "Content-Type: application/xml"   -H "Accept: application/xml"   -H "X-API-Key: dev-key-123"   -d '<?xml version="1.0"?>
<rental>
<bike_id>BIKE-101</bike_id>
<user_id>1</user_id>
</rental>'
```

### YAML
```bash
curl -X POST http://localhost:8000/rentals/start   -H "Content-Type: application/x-yaml"   -H "Accept: application/x-yaml"   -H "X-API-Key: dev-key-123"   -d '
bike_id: BIKE-101
user_id: 1
'
```

---

## Stop Rentals

### JSON
```bash
curl -X POST http://localhost:8000/rentals/stop   -H "Content-Type: application/json"   -H "Accept: application/json"   -H "X-API-Key: dev-key-123"   -d '{
        "rental_id": 15
      }'
```

### XML
```bash
curl -X POST http://localhost:8000/rentals/stop   -H "Content-Type: application/xml"   -H "Accept: application/xml"   -H "X-API-Key: dev-key-123"   -d '<?xml version="1.0"?>
<rental>
<rental_id>16</rental_id>
</rental>'
```

### YAML
```bash
curl -X POST http://localhost:8000/rentals/stop   -H "Content-Type: application/x-yaml"   -H "Accept: application/x-yaml"   -H "X-API-Key: dev-key-123"   -d '
rental_id: 15
'
```
