from bookandride_api.logging_config import logger
from bookandride_api.main import calculate_price

def test_logging_price(caplog):
    caplog.set_level("INFO")
    calculate_price(40)
    assert "calculated price" in caplog.text.lower()
