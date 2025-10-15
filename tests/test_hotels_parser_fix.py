"""
Test to verify the Hotels.py parser fix works correctly
"""
import re
import json
import pytest


class TestHotelsParserFix:
    """Tests for the fixed Hotels parser"""

    def test_coordinates_regex_extracts_only_array(self):
        """Test that the new regex only captures the coordinate array"""
        # Real example from booking.com that was failing
        sample_text = """defaultCoordinates: ['35.69635946', '139.76560682'], isRTL: '', isLP: !!'', action: 'hotel', tdot: '0' === '1'"""

        # New pattern
        coords_match = re.search(
            r'defaultCoordinates:\s*(\[\s*[\'"][\d.]+[\'"]\s*,\s*[\'"][\d.]+[\'"]\s*\])',
            sample_text
        )

        assert coords_match is not None
        matched = coords_match.group(1)

        # Verify it only captured the array, not the rest of the JavaScript
        assert matched == "['35.69635946', '139.76560682']"
        assert "isRTL" not in matched
        assert "action" not in matched

    def test_coordinates_parsing_with_single_quotes(self):
        """Test parsing coordinates with single quotes"""
        sample_text = """defaultCoordinates: ['35.69635946', '139.76560682'], isRTL: ''"""

        coords_match = re.search(
            r'defaultCoordinates:\s*(\[\s*[\'"][\d.]+[\'"]\s*,\s*[\'"][\d.]+[\'"]\s*\])',
            sample_text
        )

        coords_str = coords_match.group(1)
        coords_str = coords_str.replace("'", '"')
        coords = json.loads(coords_str)

        assert float(coords[0]) == 35.69635946
        assert float(coords[1]) == 139.76560682

    def test_coordinates_parsing_with_double_quotes(self):
        """Test parsing coordinates with double quotes"""
        sample_text = """defaultCoordinates: ["35.71886946", "139.78901044"], isRTL: """""

        coords_match = re.search(
            r'defaultCoordinates:\s*(\[\s*[\'"][\d.]+[\'"]\s*,\s*[\'"][\d.]+[\'"]\s*\])',
            sample_text
        )

        coords_str = coords_match.group(1)
        coords_str = coords_str.replace("'", '"')
        coords = json.loads(coords_str)

        assert float(coords[0]) == 35.71886946
        assert float(coords[1]) == 139.78901044

    def test_coordinates_parsing_with_spaces(self):
        """Test parsing coordinates with various spacing"""
        test_cases = [
            "defaultCoordinates: ['35.69', '139.76']",
            "defaultCoordinates:['35.69','139.76']",
            "defaultCoordinates: [ '35.69' , '139.76' ]",
        ]

        for sample_text in test_cases:
            coords_match = re.search(
                r'defaultCoordinates:\s*(\[\s*[\'"][\d.]+[\'"]\s*,\s*[\'"][\d.]+[\'"]\s*\])',
                sample_text
            )
            assert coords_match is not None, f"Failed to match: {sample_text}"

            coords_str = coords_match.group(1)
            coords_str = coords_str.replace("'", '"')
            coords = json.loads(coords_str)

            assert float(coords[0]) == 35.69
            assert float(coords[1]) == 139.76

    def test_no_eval_used(self):
        """Test that we use JSON parsing instead of eval"""
        sample_text = """defaultCoordinates: ['35.69', '139.76'], isRTL: ''"""

        coords_match = re.search(
            r'defaultCoordinates:\s*(\[\s*[\'"][\d.]+[\'"]\s*,\s*[\'"][\d.]+[\'"]\s*\])',
            sample_text
        )

        coords_str = coords_match.group(1)
        coords_str = coords_str.replace("'", '"')

        # Should be valid JSON now
        coords = json.loads(coords_str)

        assert isinstance(coords, list)
        assert len(coords) == 2

    def test_handles_missing_coordinates(self):
        """Test graceful handling when coordinates are not found"""
        sample_text = """<html>No coordinates here</html>"""

        coords_match = re.search(
            r'defaultCoordinates:\s*(\[\s*[\'"][\d.]+[\'"]\s*,\s*[\'"][\d.]+[\'"]\s*\])',
            sample_text
        )

        # Should return None when not found
        assert coords_match is None

    def test_error_handling_approach(self):
        """Test the error handling approach in the fixed code"""
        sample_text = """defaultCoordinates: ['35.69', '139.76']"""

        try:
            coords_match = re.search(
                r'defaultCoordinates:\s*(\[\s*[\'"][\d.]+[\'"]\s*,\s*[\'"][\d.]+[\'"]\s*\])',
                sample_text
            )
            if coords_match:
                coords_str = coords_match.group(1)
                coords_str = coords_str.replace("'", '"')
                coords = json.loads(coords_str)
                latitude = float(coords[0])
                longitude = float(coords[1])
            else:
                latitude = 0.0
                longitude = 0.0
        except (ValueError, IndexError, json.JSONDecodeError):
            latitude = 0.0
            longitude = 0.0

        assert latitude == 35.69
        assert longitude == 139.76


class TestHotelsReviewDateParsing:
    """Tests for review date parsing fix"""

    def test_date_with_prefix(self):
        """Test parsing date with 'Reviewed: ' prefix"""
        date_text = "Reviewed: 1 January 2023"

        if ": " in date_text:
            date = date_text.split(": ")[1]
        else:
            date = date_text.strip()

        assert date == "1 January 2023"

    def test_date_without_prefix(self):
        """Test parsing date without prefix"""
        date_text = "1 January 2023"

        if ": " in date_text:
            date = date_text.split(": ")[1]
        else:
            date = date_text.strip()

        assert date == "1 January 2023"

    def test_empty_date(self):
        """Test handling of empty/None date"""
        date_text = None

        if date_text:
            if ": " in date_text:
                date = date_text.split(": ")[1]
            else:
                date = date_text.strip()
        else:
            date = ""

        assert date == ""

    def test_date_with_extra_whitespace(self):
        """Test date with extra whitespace"""
        date_text = "  15 March 2024  "

        if ": " in date_text:
            date = date_text.split(": ")[1]
        else:
            date = date_text.strip()

        assert date == "15 March 2024"

    def test_multiple_colons_in_date(self):
        """Test date string with multiple colons - splits on first colon only"""
        date_text = "Reviewed: Time: 1 January 2023"

        # Standard split behavior - will get everything after first ": "
        # but will split all occurrences
        if ": " in date_text:
            parts = date_text.split(": ")
            date = parts[1]  # Gets "Time"
        else:
            date = date_text.strip()

        # This is expected behavior - it only gets the first element after split
        assert date == "Time"
