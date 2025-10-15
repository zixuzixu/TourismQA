"""
Integration tests for TourismQA
Tests that verify multiple components work together
"""
import json
import pytest
from pathlib import Path
from utils import common
from utils.crawlers.Processor import Processor as EntityProcessor
from src.custom.process.Processor1 import Processor as PostProcessor


class TestEntityProcessingPipeline:
    """Integration tests for entity processing pipeline"""

    def test_full_entity_processing(self, temp_dir, sample_entity):
        """Test complete entity processing and saving"""
        # Save raw entity data
        input_file = temp_dir / "raw_entity.json"
        common.dumpJSON(sample_entity, input_file)

        # Load and process
        raw_data = common.loadJSON(input_file)
        processor = EntityProcessor()
        processed_entity = processor.processEntityItem(raw_data)

        # Save processed data
        output_file = temp_dir / "processed_entity.json"
        common.dumpJSON(dict(processed_entity), output_file)

        # Verify
        final_data = common.loadJSON(output_file)
        assert final_data["name"] == "The Grand Hotel"
        assert len(final_data["properties"]) == 3
        assert final_data["rating"] == 4.5
        assert "" not in final_data["properties"]


class TestPostFilteringPipeline:
    """Integration tests for post filtering pipeline"""

    def test_valid_posts_pass_through(self, temp_dir, sample_post, average_post_length):
        """Test that valid posts pass through processing"""
        # Save posts
        posts_file = temp_dir / "posts.json"
        posts = [sample_post]
        common.dumpJSON(posts, posts_file)

        # Load and process
        loaded_posts = common.loadJSON(posts_file)
        processor = PostProcessor(average_post_length)

        valid_posts = []
        for post in loaded_posts:
            try:
                processor(post)
                valid_posts.append(post)
            except Exception:
                pass

        assert len(valid_posts) == 1
        assert valid_posts[0]["title"] == sample_post["title"]

    def test_filtering_mixed_posts(self, temp_dir, average_post_length):
        """Test filtering a mix of valid and invalid posts"""
        posts = [
            {
                "url": "http://example.com/1",
                "title": "Good hotel?",
                "question": "Looking for a nice hotel",
                "answers": [{"body": "Try the Grand Hotel"}]
            },
            {
                "url": "http://example.com/2",
                "title": "TR My Paris Trip",  # Trip report - should be filtered
                "question": "Had a great time",
                "answers": [{"body": "Sounds great!"}]
            },
            {
                "url": "http://example.com/3",
                "title": "Hotel A vs Hotel B",  # Irrelevant - should be filtered
                "question": "Which is better?",
                "answers": [{"body": "Go with A"}]
            },
            {
                "url": "http://example.com/4",
                "title": "Restaurant recommendations",
                "question": "Any good restaurants?",
                "answers": [{"body": "Try the Italian place"}]
            }
        ]

        processor = PostProcessor(average_post_length)

        filtered_posts = []
        for post in posts:
            try:
                processor(post)
                filtered_posts.append(post)
            except Exception:
                pass

        # Should keep posts 1 and 4, filter out 2 and 3
        assert len(filtered_posts) == 2
        assert filtered_posts[0]["url"] == "http://example.com/1"
        assert filtered_posts[1]["url"] == "http://example.com/4"


class TestDataPersistence:
    """Integration tests for data loading and saving"""

    def test_json_roundtrip_preserves_data(self, temp_dir):
        """Test that data survives JSON save/load cycle"""
        original_data = {
            "string": "test",
            "number": 42,
            "float": 3.14,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
            "unicode": "Hello 世界"
        }

        file_path = temp_dir / "data.json"
        common.dumpJSON(original_data, file_path)
        loaded_data = common.loadJSON(file_path)

        assert loaded_data == original_data

    def test_nested_directory_creation(self, temp_dir):
        """Test creating nested directories for data storage"""
        deep_path = temp_dir / "level1" / "level2" / "level3" / "data.json"
        data = {"test": "data"}

        common.dumpJSON(data, deep_path)

        assert deep_path.exists()
        loaded = common.loadJSON(deep_path)
        assert loaded == data

    def test_update_merges_data_structures(self):
        """Test that update function properly merges complex structures"""
        base_data = {
            "entities": {
                "hotels": ["Hotel A", "Hotel B"],
                "restaurants": ["Restaurant X"]
            },
            "cities": ["New York", "Paris"]
        }

        new_data = {
            "entities": {
                "restaurants": ["Restaurant Y", "Restaurant Z"]
            },
            "cities": ["London"]
        }

        result = common.update(base_data, new_data)

        # Verify hotels list is preserved
        assert "Hotel A" in result["entities"]["hotels"]
        # Verify restaurants are merged
        assert "Restaurant X" in result["entities"]["restaurants"]
        assert "Restaurant Y" in result["entities"]["restaurants"]
        # Verify cities are merged
        assert len(result["cities"]) == 3
        assert "London" in result["cities"]
