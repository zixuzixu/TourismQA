"""
Tests for utils/crawlers/Processor.py
"""
import pytest
from collections import OrderedDict
from utils.crawlers.Processor import Processor


class TestProcessorStringProcessing:
    """Tests for Processor string processing"""

    @pytest.fixture
    def processor(self):
        """Create a Processor instance"""
        return Processor()

    def test_removes_extra_whitespace(self, processor):
        """Test that processString removes extra whitespace"""
        result = processor.processString("Hello    world   with   spaces")
        assert result == "Hello world with spaces"

    def test_removes_multiple_dots(self, processor):
        """Test that processString reduces multiple dots to one"""
        result = processor.processString("Hello... world....")
        # Trailing punctuation is stripped, so final dot is removed
        assert result == "Hello. world"

    def test_removes_multiple_question_marks(self, processor):
        """Test that processString reduces multiple question marks to one"""
        result = processor.processString("Really??? Are you sure???")
        # Trailing punctuation is stripped, so final question mark is removed
        assert result == "Really? Are you sure"

    def test_strips_punctuation_and_spaces(self, processor):
        """Test that processString strips leading/trailing punctuation"""
        result = processor.processString("  ...Hello world!!!  ")
        assert result == "Hello world"

    def test_handles_empty_string(self, processor):
        """Test that processString handles empty strings"""
        result = processor.processString("")
        assert result == ""

    def test_handles_only_whitespace(self, processor):
        """Test that processString handles strings with only whitespace"""
        result = processor.processString("    ")
        assert result == ""


class TestProcessReviewItem:
    """Tests for processReviewItem method"""

    @pytest.fixture
    def processor(self):
        """Create a Processor instance"""
        return Processor()

    def test_processes_all_fields(self, processor):
        """Test that processReviewItem processes all fields"""
        item = {
            "title": "  Great   stay!!!  ",
            "description": "We   had   a   wonderful   time...  ",
            "rating": "5.0",
            "date": "01 January 2023",
            "url": "  https://example.com  "
        }

        result = processor.processReviewItem(item)

        assert isinstance(result, OrderedDict)
        assert result["title"] == "Great stay"
        # Trailing punctuation is stripped
        assert result["description"] == "We had a wonderful time"
        assert result["rating"] == 5.0
        assert result["date"] == "01 January 2023"
        assert result["url"] == "https://example.com"

    def test_converts_rating_to_float(self, processor):
        """Test that rating is converted to float"""
        item = {
            "title": "Good",
            "description": "Nice",
            "rating": "4.5",
            "date": "01 January 2023",
            "url": "https://example.com"
        }

        result = processor.processReviewItem(item)

        assert isinstance(result["rating"], float)
        assert result["rating"] == 4.5

    def test_formats_date_from_different_formats(self, processor):
        """Test that date is properly formatted from various formats"""
        formats = [
            ("01 January 2023", "01 January 2023"),
            ("January 01, 2023", "01 January 2023"),
            ("2023-01-01", "01 January 2023"),
        ]

        for input_date, expected_date in formats:
            item = {
                "title": "Test",
                "description": "Test",
                "rating": "5.0",
                "date": input_date,
                "url": "https://example.com"
            }
            result = processor.processReviewItem(item)
            assert result["date"] == expected_date


class TestProcessEntityItem:
    """Tests for processEntityItem method"""

    @pytest.fixture
    def processor(self):
        """Create a Processor instance"""
        return Processor()

    def test_processes_entity_with_all_fields(self, processor, sample_entity):
        """Test that processEntityItem processes all entity fields"""
        result = processor.processEntityItem(sample_entity)

        assert isinstance(result, OrderedDict)
        assert result["id"] == "123_H_456"
        assert result["name"] == "The Grand Hotel"
        # Trailing punctuation is stripped
        assert result["description"] == "A beautiful hotel. with great views"
        assert result["address"] == "123 Main Street"
        assert result["latitude"] == 28.6139
        assert result["longitude"] == 77.2090
        assert result["rating"] == 4.5
        assert result["url"] == "https://www.tripadvisor.com/hotel"

    def test_filters_empty_properties(self, processor, sample_entity):
        """Test that empty properties are filtered out"""
        result = processor.processEntityItem(sample_entity)

        assert "" not in result["properties"]
        assert len(result["properties"]) == 3
        assert "WiFi" in result["properties"]
        assert "Pool" in result["properties"]
        assert "Restaurant" in result["properties"]

    def test_processes_reviews(self, processor, sample_entity):
        """Test that reviews are processed"""
        result = processor.processEntityItem(sample_entity)

        assert len(result["reviews"]) == 1
        review = result["reviews"][0]
        assert review["title"] == "Great stay"
        # Trailing punctuation is stripped
        assert review["description"] == "We had a wonderful time"
        assert review["rating"] == 5.0

    def test_converts_coordinates_to_float(self, processor, sample_entity):
        """Test that coordinates are converted to float"""
        result = processor.processEntityItem(sample_entity)

        assert isinstance(result["latitude"], float)
        assert isinstance(result["longitude"], float)

    def test_handles_entity_with_no_reviews(self, processor):
        """Test that entity with no reviews is processed correctly"""
        entity = {
            "id": "1_R_1",
            "name": "Test Restaurant",
            "properties": ["WiFi"],
            "description": "A test restaurant",
            "address": "123 Test St",
            "latitude": "0.0",
            "longitude": "0.0",
            "rating": "4.0",
            "url": "https://example.com",
            "reviews": []
        }

        result = processor.processEntityItem(entity)

        assert result["reviews"] == []
        assert result["name"] == "Test Restaurant"

    def test_maintains_field_order(self, processor, sample_entity):
        """Test that fields are in correct order"""
        result = processor.processEntityItem(sample_entity)

        keys = list(result.keys())
        expected_order = [
            "id", "name", "properties", "description", "address",
            "latitude", "longitude", "rating", "url", "reviews"
        ]
        assert keys == expected_order
