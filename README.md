# API Small Project

## Download and Setup

You can download the code from GitHub:

```bash
git clone https://github.com/rdrio02/API-Small-Project.git
cd API-Small-Project
```

Project structure:

```text
rdrio@Desktop-RDRIO:~/API-Small-Project$ tree
.
├── README.md
├── api
│   ├── Dockerfile
│   ├── app
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas
│   │   │   ├── book.schema.json
│   │   │   ├── book.update.schema.json
│   │   │   ├── rental.schema.json
│   │   │   ├── rental.start.schema.json
│   │   │   └── rental.stop.schema.json
│   │   ├── schemas.py
│   │   ├── search.py
│   │   └── serialization.py
│   └── requirements.txt
├── docker-compose.yml
├── nginx
│   └── nginx.conf
└── prometheus
    └── prometheus.yml
```
 
### Setup Instructions (5 Steps)

1. Install Docker and Docker Compose if not already installed.
2. Build and start the containers:

```bash
docker-compose up --build -d
```

3. Access the API at: `http://localhost:8000`
4. Access Grafana at: `http://localhost:3000` (Default credentials: `admin` / `admin`)
5. Access Kibana  at: `http://localhost:5601`

---

## API Collection

### Books

**Get all books**

* JSON:

```bash
curl -H "Accept: application/json" http://localhost:8000/books
```

* XML:

```bash
curl -H "Accept: application/xml" http://localhost:8000/books
```

* YAML:

```bash
curl -H "Accept: application/x-yaml" http://localhost:8000/books
```

* Default (JSON):

```bash
curl http://localhost:8000/books
```

**Add a book**

* JSON:

```bash
curl -X POST http://localhost:8000/books \
-H "Content-Type: application/json" \
-d '{"title":"Dune","author":"Frank Herbert","stock":12}'
```

* XML:

```bash
curl -X POST http://localhost:8000/books \
-H "Content-Type: application/xml" \
-H "Accept: application/xml" \
-d '<?xml version="1.0"?><book><title>Dune</title><author>Frank Herbert</author><stock>12</stock></book>'
```

* YAML:

```bash
curl -X POST http://localhost:8000/books \
-H "Content-Type: application/x-yaml" \
-H "Accept: application/x-yaml" \
-d 'title: Dune
author: Frank Herbert
stock: 12'
```

**Update a book**

* JSON:

```bash
curl -X PUT http://localhost:8000/books/35 \
-H "Content-Type: application/json" \
-d '{"stock": 20}'
```

* XML:

```bash
curl -X PUT http://localhost:8000/books/35 \
-H "Content-Type: application/xml" \
-H "Accept: application/xml" \
-d '<?xml version="1.0"?><book><stock>20</stock></book>'
```

* YAML:

```bash
curl -X PUT http://localhost:8000/books/35 \
-H "Content-Type: application/x-yaml" \
-H "Accept: application/x-yaml" \
-d 'stock: 20'
```

**Delete a book**

* Single book (JSON):

```bash
curl -X DELETE http://localhost:8000/books/39 -H "Accept: application/json"
```

* All books (requires API key):

```bash
curl -X DELETE http://localhost:8000/books \
-H "X-API-Key: admin-key-456" \
-H "Accept: application/json"
```

### Rentals

**Start rental**

* JSON:

```bash
curl -X POST http://localhost:8000/rentals/start \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-H "X-API-Key: dev-key-123" \
-d '{"bike_id": "BIKE-101","user_id": 1}'
```

* XML:

```bash
curl -X POST http://localhost:8000/rentals/start \
-H "Content-Type: application/xml" \
-H "Accept: application/xml" \
-H "X-API-Key: dev-key-123" \
-d '<?xml version="1.0"?><rental><bike_id>BIKE-101</bike_id><user_id>1</user_id></rental>'
```

* YAML:

```bash
curl -X POST http://localhost:8000/rentals/start \
-H "Content-Type: application/x-yaml" \
-H "Accept: application/x-yaml" \
-H "X-API-Key: dev-key-123" \
-d 'bike_id: BIKE-101
user_id: 1'
```

**Stop rental**

* JSON:

```bash
curl -X POST http://localhost:8000/rentals/stop \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-H "X-API-Key: dev-key-123" \
-d '{"rental_id": 15}'
```

* XML:

```bash
curl -X POST http://localhost:8000/rentals/stop \
-H "Content-Type: application/xml" \
-H "Accept: application/xml" \
-H "X-API-Key: dev-key-123" \
-d '<?xml version="1.0"?><rental><rental_id>16</rental_id></rental>'
```

* YAML:

```bash
curl -X POST http://localhost:8000/rentals/stop \
-H "Content-Type: application/x-yaml" \
-H "Accept: application/x-yaml" \
-H "X-API-Key: dev-key-123" \
-d 'rental_id: 15'
```

---

## Demo Script (~2 Minutes)

**1. List all books (JSON):**

```bash
curl -H "Accept: application/json" http://localhost:8000/books
```

**2. Add a new book:**

```bash
curl -X POST http://localhost:8000/books \
-H "Content-Type: application/json" \
-d '{"title":"Dune","author":"Frank Herbert","stock":12}'
```

**3. Update a book's stock:**

```bash
curl -X PUT http://localhost:8000/books/1 \
-H "Content-Type: application/json" \
-d '{"stock": 20}'
```

**4. Start a bike rental:**

```bash
curl -X POST http://localhost:8000/rentals/start \
-H "Content-Type: application/json" \
-H "X-API-Key: dev-key-123" \
-d '{"bike_id": "BIKE-101","user_id": 1}'
```

**5. Stop the bike rental:**

```bash
curl -X POST http://localhost:8000/rentals/stop \
-H "Content-Type: application/json" \
-H "X-API-Key: dev-key-123" \
-d '{"rental_id": 1}'
```
