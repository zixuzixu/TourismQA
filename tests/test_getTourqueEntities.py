"""
Tests for src/tourque/entities/getTourqueEntities.py
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from src.tourque.entities.getTourqueEntities import TourqueEntitiesCrawler


class TestTourqueEntitiesCrawler:
    """Tests for TourqueEntitiesCrawler class"""

    def test_initialization(self):
        """Test that TourqueEntitiesCrawler initializes correctly"""
        with patch('src.tourque.entities.getTourqueEntities.CrawlerProcess'):
            crawler = TourqueEntitiesCrawler()
            assert hasattr(crawler, 'process')

    def test_crawler_process_settings(self):
        """Test that CrawlerProcess is initialized with correct settings"""
        with patch('src.tourque.entities.getTourqueEntities.CrawlerProcess') as mock_process:
            TourqueEntitiesCrawler()

            # Verify CrawlerProcess was called with correct settings
            mock_process.assert_called_once()
            call_args = mock_process.call_args
            assert 'settings' in call_args.kwargs
            assert 'FEEDS' in call_args.kwargs['settings']
            assert 'items.json' in call_args.kwargs['settings']['FEEDS']


class TestEntityTypeFiltering:
    """Tests for entity type filtering logic"""

    @pytest.fixture
    def sample_entities(self):
        """Sample entity data with different types"""
        return [
            {"id": "123_R_001", "url": "https://tripadvisor.com/restaurant1"},
            {"id": "123_R_002", "url": "https://tripadvisor.com/restaurant2"},
            {"id": "123_H_001", "url": "https://booking.com/hotel1"},
            {"id": "123_H_002", "url": "https://booking.com/hotel2"},
            {"id": "123_A_001", "url": "https://tripadvisor.com/attraction1"},
            {"id": "123_A_002", "url": "https://tripadvisor.com/attraction2"},
        ]

    def test_restaurant_filtering(self, sample_entities):
        """Test that restaurant entities are correctly filtered"""
        restaurants = list(filter(lambda item: item["id"].split("_")[1] == "R", sample_entities))
        assert len(restaurants) == 2
        assert all(item["id"].split("_")[1] == "R" for item in restaurants)

    def test_hotel_filtering(self, sample_entities):
        """Test that hotel entities are correctly filtered"""
        hotels = list(filter(lambda item: item["id"].split("_")[1] == "H", sample_entities))
        assert len(hotels) == 2
        assert all(item["id"].split("_")[1] == "H" for item in hotels)

    def test_attraction_filtering(self, sample_entities):
        """Test that attraction entities are correctly filtered"""
        attractions = list(filter(lambda item: item["id"].split("_")[1] == "A", sample_entities))
        assert len(attractions) == 2
        assert all(item["id"].split("_")[1] == "A" for item in attractions)

    def test_no_entities_lost_in_filtering(self, sample_entities):
        """Test that all entities are categorized correctly"""
        restaurants = list(filter(lambda item: item["id"].split("_")[1] == "R", sample_entities))
        hotels = list(filter(lambda item: item["id"].split("_")[1] == "H", sample_entities))
        attractions = list(filter(lambda item: item["id"].split("_")[1] == "A", sample_entities))

        total_filtered = len(restaurants) + len(hotels) + len(attractions)
        assert total_filtered == len(sample_entities)


class TestEntityIDParsing:
    """Tests for entity ID parsing logic"""

    def test_parse_city_id_from_entity_id(self):
        """Test parsing city ID from entity ID"""
        entity_id = "123_R_456"
        city_id = entity_id.split("_")[0]
        assert city_id == "123"

    def test_parse_type_from_entity_id(self):
        """Test parsing entity type from entity ID"""
        entity_id = "123_R_456"
        entity_type = entity_id.split("_")[1]
        assert entity_type == "R"

    def test_parse_entity_number_from_id(self):
        """Test parsing entity number from entity ID"""
        entity_id = "123_R_456"
        entity_number = entity_id.split("_")[2]
        assert entity_number == "456"

    def test_path_construction_from_entity_id(self, temp_dir):
        """Test that file paths are correctly constructed from entity ID"""
        entity_id = "123_R_456"
        output_dir = temp_dir

        expected_path = output_dir / "123" / "123_R_456.json"
        actual_path = (output_dir / entity_id.split("_")[0] / entity_id).with_suffix(".json")

        assert actual_path == expected_path


class TestExistingEntitySkipping:
    """Tests for skipping already existing entities"""

    def test_skips_existing_entities(self, temp_dir):
        """Test that existing entities are not added to fetch list"""
        # Create sample input data
        input_data = [
            {"id": "123_R_001", "url": "https://example.com/1"},
            {"id": "123_R_002", "url": "https://example.com/2"},
            {"id": "123_R_003", "url": "https://example.com/3"},
        ]

        # Create an existing entity file
        existing_entity_path = temp_dir / "123" / "123_R_001.json"
        existing_entity_path.parent.mkdir(parents=True, exist_ok=True)
        with open(existing_entity_path, "w") as f:
            json.dump({"id": "123_R_001", "name": "Existing Restaurant"}, f)

        # Simulate the filtering logic
        data = []
        for item in input_data:
            entity_path = (temp_dir / item["id"].split("_")[0] / item["id"]).with_suffix(".json")
            if not entity_path.exists():
                data.append(item)

        # Should have 2 items (skipping the existing one)
        assert len(data) == 2
        assert data[0]["id"] == "123_R_002"
        assert data[1]["id"] == "123_R_003"

    def test_includes_non_existing_entities(self, temp_dir):
        """Test that non-existing entities are included in fetch list"""
        input_data = [
            {"id": "123_R_001", "url": "https://example.com/1"},
            {"id": "123_R_002", "url": "https://example.com/2"},
        ]

        # Don't create any existing files
        data = []
        for item in input_data:
            entity_path = (temp_dir / item["id"].split("_")[0] / item["id"]).with_suffix(".json")
            if not entity_path.exists():
                data.append(item)

        # All items should be included
        assert len(data) == 2


class TestEntitySaving:
    """Tests for saving entity data"""

    def test_entity_saved_to_correct_path(self, temp_dir):
        """Test that entities are saved to correct directory structure"""
        entity = {
            "id": "123_R_456",
            "name": "Test Restaurant",
            "rating": 4.5
        }

        output_path = (temp_dir / entity["id"].split("_")[0] / entity["id"]).with_suffix(".json")

        # Create parent directory
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save entity
        with open(output_path, "w") as f:
            json.dump(entity, f)

        # Verify
        assert output_path.exists()
        assert output_path.parent.name == "123"

        # Load and verify content
        with open(output_path, "r") as f:
            loaded = json.load(f)
        assert loaded["id"] == entity["id"]
        assert loaded["name"] == entity["name"]

    def test_multiple_cities_directory_structure(self, temp_dir):
        """Test that entities from different cities are saved in separate directories"""
        entities = [
            {"id": "123_R_001", "name": "Restaurant in City 123"},
            {"id": "456_H_001", "name": "Hotel in City 456"},
            {"id": "789_A_001", "name": "Attraction in City 789"},
        ]

        for entity in entities:
            output_path = (temp_dir / entity["id"].split("_")[0] / entity["id"]).with_suffix(".json")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(entity, f)

        # Verify directory structure
        assert (temp_dir / "123").exists()
        assert (temp_dir / "456").exists()
        assert (temp_dir / "789").exists()

        assert (temp_dir / "123" / "123_R_001.json").exists()
        assert (temp_dir / "456" / "456_H_001.json").exists()
        assert (temp_dir / "789" / "789_A_001.json").exists()


class TestTourqueEntitiesCrawlerCall:
    """Tests for TourqueEntitiesCrawler __call__ method"""

    @pytest.fixture
    def mock_crawler(self):
        """Create a mock crawler with patched dependencies"""
        with patch('src.tourque.entities.getTourqueEntities.CrawlerProcess'):
            crawler = TourqueEntitiesCrawler()
            return crawler

    def test_loads_input_file(self, temp_dir, mock_crawler):
        """Test that input file is loaded correctly"""
        # Create input file
        input_data = [
            {"id": "123_R_001", "url": "https://example.com/1"},
            {"id": "123_R_002", "url": "https://example.com/2"},
        ]
        input_file = temp_dir / "input.json"
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        output_dir = temp_dir / "output"

        # Mock the fetch method to avoid actual crawling
        with patch.object(mock_crawler, 'fetch', return_value=[]):
            mock_crawler(input_file, output_dir)

            # fetch should have been called with the data
            mock_crawler.fetch.assert_called_once()
            call_args = mock_crawler.fetch.call_args[0][0]
            assert len(call_args) == 2

    def test_skips_already_fetched_entities(self, temp_dir, mock_crawler):
        """Test that already fetched entities are not re-fetched"""
        # Create input file with 3 entities
        input_data = [
            {"id": "123_R_001", "url": "https://example.com/1"},
            {"id": "123_R_002", "url": "https://example.com/2"},
            {"id": "123_R_003", "url": "https://example.com/3"},
        ]
        input_file = temp_dir / "input.json"
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        output_dir = temp_dir / "output"

        # Create an existing entity
        existing_path = output_dir / "123" / "123_R_001.json"
        existing_path.parent.mkdir(parents=True, exist_ok=True)
        with open(existing_path, "w") as f:
            json.dump({"id": "123_R_001"}, f)

        # Mock the fetch method
        with patch.object(mock_crawler, 'fetch', return_value=[]):
            mock_crawler(input_file, output_dir)

            # fetch should be called with only 2 entities (skipping existing one)
            call_args = mock_crawler.fetch.call_args[0][0]
            assert len(call_args) == 2
            assert all(item["id"] != "123_R_001" for item in call_args)

    def test_saves_fetched_entities(self, temp_dir, mock_crawler):
        """Test that fetched entities are saved correctly"""
        # Create input file
        input_data = [
            {"id": "123_R_001", "url": "https://example.com/1"},
        ]
        input_file = temp_dir / "input.json"
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        output_dir = temp_dir / "output"

        # Mock fetch to return a processed entity
        fetched_entity = {
            "id": "123_R_001",
            "name": "Test Restaurant",
            "rating": 4.5
        }

        with patch.object(mock_crawler, 'fetch', return_value=[fetched_entity]):
            mock_crawler(input_file, output_dir)

            # Verify entity was saved
            expected_path = output_dir / "123" / "123_R_001.json"
            assert expected_path.exists()

            with open(expected_path, "r") as f:
                saved_entity = json.load(f)
            assert saved_entity["id"] == "123_R_001"
            assert saved_entity["name"] == "Test Restaurant"


class TestFetchMethod:
    """Tests for the fetch method"""

    def test_fetch_initializes_progress_bar(self):
        """Test that fetch initializes tqdm progress bar with correct total"""
        with patch('src.tourque.entities.getTourqueEntities.CrawlerProcess'):
            crawler = TourqueEntitiesCrawler()

            test_data = [
                {"id": "123_R_001", "url": "https://example.com/1"},
                {"id": "123_R_002", "url": "https://example.com/2"},
            ]

            with patch('src.tourque.entities.getTourqueEntities.tqdm.tqdm') as mock_tqdm:
                with patch.object(crawler.process, 'crawl'):
                    with patch.object(crawler.process, 'start'):
                        mock_bar = MagicMock()
                        mock_tqdm.return_value = mock_bar

                        crawler.fetch(test_data)

                        # Verify tqdm was called with correct total
                        mock_tqdm.assert_called_once_with(total=2)

    def test_fetch_filters_by_entity_type(self):
        """Test that fetch correctly distributes entities to different crawlers"""
        with patch('src.tourque.entities.getTourqueEntities.CrawlerProcess'):
            crawler = TourqueEntitiesCrawler()

            test_data = [
                {"id": "123_R_001", "url": "https://tripadvisor.com/r1"},
                {"id": "123_R_002", "url": "https://tripadvisor.com/r2"},
                {"id": "123_H_001", "url": "https://booking.com/h1"},
                {"id": "123_A_001", "url": "https://tripadvisor.com/a1"},
            ]

            with patch.object(crawler.process, 'crawl') as mock_crawl:
                with patch.object(crawler.process, 'start'):
                    with patch('src.tourque.entities.getTourqueEntities.tqdm.tqdm'):
                        with patch('src.tourque.entities.getTourqueEntities.dispatcher.connect'):
                            crawler.fetch(test_data)

                            # Verify crawl was called 3 times (one for each type)
                            assert mock_crawl.call_count == 3

                            # Get the items passed to each crawler
                            calls = mock_crawl.call_args_list

                            # Check that correct number of items were passed
                            items_lists = [call.kwargs['items'] for call in calls]
                            items_counts = [len(items) for items in items_lists]

                            assert 2 in items_counts  # 2 restaurants
                            assert 1 in items_counts  # 1 hotel
                            assert 1 in items_counts  # 1 attraction
