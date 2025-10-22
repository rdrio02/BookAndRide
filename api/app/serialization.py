import json
import xmltodict
from fastapi import HTTPException, Response
from fastapi.responses import JSONResponse
from jsonschema import validate, ValidationError
from pydantic import BaseModel
from typing import Any


def parse_body(raw: bytes, content_type: str, schema: dict, model: type[BaseModel]) -> dict:
    """Parse JSON or XML request bodies and validate against schema."""
    if content_type == "application/json":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise HTTPException(422, detail={"error": "invalid_json", "message": str(e)})
    elif content_type == "application/xml":
        try:
            data = xmltodict.parse(raw)
            
            # Unwrap the first root element (e.g., <rental> or <book>)
            if len(data) == 1:
                data = next(iter(data.values()))
            
            # Convert types to match your JSON Schema
            for key, prop in schema.get("properties", {}).items():
                if key not in data:
                    continue
                expected_type = prop.get("type")
                if expected_type == "integer":
                    data[key] = int(data[key])
                elif expected_type == "number":
                    data[key] = float(data[key])
                elif expected_type == "boolean":
                    val = str(data[key]).lower()
                    data[key] = val == "true"
        except Exception as e:
            raise HTTPException(422, detail={"error": "invalid_xml", "message": str(e)})
    else:
        raise HTTPException(415, detail="Unsupported Media Type")

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise HTTPException(
            422, detail={"error": "schema_validation", "message": e.message, "path": list(e.path)}
        )

    return model(**data).model_dump()


def negotiate(accept_header: str | None) -> str:
    """Return appropriate response media type based on Accept header."""
    if not accept_header:
        return "application/json"
    accepts = [a.strip() for a in accept_header.split(",")]
    if any(a.startswith("application/xml") for a in accepts):
        return "application/xml"
    if any(a.startswith("application/json") for a in accepts):
        return "application/json"
    raise HTTPException(406, detail="Not Acceptable")


def render(data: dict[str, Any], accept: str) -> Response:
    """Serialize response data to JSON or XML."""
    if accept == "application/xml":
        xml = xmltodict.unparse({"book": data}, pretty=True)
        return Response(content=xml, media_type="application/xml")
    return JSONResponse(content=data)

def render_rental(data: dict, accept: str | None = None):
    """
    Serialize rental data to JSON or XML based on Accept header.
    """
    if accept is None:
        accept = "application/json"

    if accept == "application/xml":
        # Wrap rental in root element
        xml = xmltodict.unparse({"rental": data}, pretty=True)
        return Response(content=xml, media_type="application/xml")
    return JSONResponse(content=data)
