# TourismQA Tests

This directory contains the test suite for the TourismQA project.

## Test Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_common.py` - Tests for utility functions in `utils/common.py`
- `test_processor_entity.py` - Tests for entity data processing
- `test_processor1.py` - Tests for post filtering logic (Processor1)
- `test_integration.py` - Integration tests for complete workflows

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=src --cov=utils --cov-report=term-missing
```

### Run specific test file
```bash
pytest tests/test_common.py
```

### Run specific test class
```bash
pytest tests/test_common.py::TestLoadJSON
```

### Run specific test
```bash
pytest tests/test_common.py::TestLoadJSON::test_loads_json_file
```

### Run with verbose output
```bash
pytest -v
```

### Run with output capture disabled (see print statements)
```bash
pytest -s
```

## Test Coverage

The test suite covers:

1. **Utility Functions** (`test_common.py`)
   - File I/O operations (JSON, pickle)
   - Directory creation
   - Data structure updates
   - Path handling

2. **Entity Processing** (`test_processor_entity.py`)
   - String normalization
   - Entity data cleaning
   - Review processing
   - Data type conversions

3. **Post Filtering** (`test_processor1.py`)
   - Trip report detection
   - Inappropriate content filtering
   - Long post detection
   - Irrelevant post filtering

4. **Integration Tests** (`test_integration.py`)
   - End-to-end entity processing
   - Post filtering pipeline
   - Data persistence

## Writing New Tests

When adding new tests:

1. Use fixtures from `conftest.py` for common test data
2. Follow the existing naming convention: `test_<functionality>.py`
3. Group related tests in classes: `class TestFeatureName`
4. Use descriptive test names: `def test_specific_behavior(self)`
5. Add docstrings to explain what each test verifies

### Example:
```python
class TestNewFeature:
    """Tests for new feature functionality"""

    @pytest.fixture
    def setup_data(self):
        """Create test data"""
        return {"key": "value"}

    def test_feature_works(self, setup_data):
        """Test that feature works correctly"""
        result = some_function(setup_data)
        assert result == expected_value
```

## Fixtures

Common fixtures available in `conftest.py`:

- `temp_dir` - Temporary directory for test files
- `sample_entity` - Sample entity data structure
- `sample_post` - Sample post data structure
- `sample_json_file` - Pre-created JSON file
- `sample_cities_data` - Sample cities mapping
- `average_post_length` - Average post length for filtering tests

## Dependencies

Test dependencies are listed in `pyproject.toml` under `[project.optional-dependencies]`:
- pytest
- pytest-cov
