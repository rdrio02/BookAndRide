from unittest.mock import patch
from fastapi.testclient import TestClient
from bookandride_api.main import app

client = TestClient(app)

def test_start_rental_logging(caplog):
    caplog.set_level("INFO")
    
    with patch("bookandride_api.main.index_rental") as mock_index:
        mock_index.return_value = None
        
        response = client.post(
            "/rentals/start",
            headers={
                "X-User-Id": "1",
                "X-Api-Key": "dev-key-123",
                "Content-Type": "application/json",
            },
            json={"bike_id": "B10", "user_id": 1},
        )
        
        # Basic assertions
        assert response.status_code == 200
        json_data = response.json()
        assert "rental_id" in json_data
        assert "started_at" in json_data
        mock_index.assert_called_once()
