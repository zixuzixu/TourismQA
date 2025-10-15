"""
Pytest configuration and fixtures for TourismQA tests
"""
import json
import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_entity():
    """Sample entity data for testing"""
    return {
        "id": "123_H_456",
        "name": "  The Grand Hotel  ",
        "properties": ["  WiFi  ", "Pool", "", "   Restaurant   "],
        "description": "A    beautiful   hotel...   with   great   views....    ",
        "address": "  123 Main Street  ",
        "latitude": "28.6139",
        "longitude": "77.2090",
        "rating": "4.5",
        "url": "  https://www.tripadvisor.com/hotel  ",
        "reviews": [
            {
                "title": "  Great   stay!!!  ",
                "description": "We   had   a   wonderful   time...  ",
                "rating": "5.0",
                "date": "01 January 2023",
                "url": "  https://www.tripadvisor.com/review1  "
            }
        ]
    }


@pytest.fixture
def sample_post():
    """Sample post data for testing"""
    return {
        "url": "https://www.tripadvisor.com/post123",
        "title": "Best hotel in Manhattan",
        "question": "I'm looking for a good hotel in Manhattan. Any recommendations?",
        "city": "New York",
        "answers": [
            {
                "date": "17 Oct 2019, 11:09 PM",
                "body": "I recommend the Washington Square Hotel."
            }
        ]
    }


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file for testing"""
    data = {"test": "data", "items": [1, 2, 3]}
    file_path = temp_dir / "test.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return file_path


@pytest.fixture
def sample_cities_data():
    """Sample cities data"""
    return {
        "0": "New York",
        "1": "London",
        "2": "Paris",
        "123": "New Delhi"
    }


@pytest.fixture
def average_post_length():
    """Average post length for Processor1 tests"""
    return 200
