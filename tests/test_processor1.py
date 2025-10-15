"""
Tests for src/custom/process/Processor1.py
Post filtering logic tests
"""
import pytest
from src.custom.process.Processor1 import Processor


class TestIsTripReport:
    """Tests for isTripReport method"""

    @pytest.fixture
    def processor(self, average_post_length):
        """Create a Processor1 instance"""
        return Processor(average_post_length)

    def test_detects_tr_prefix(self, processor):
        """Test detection of TR prefix variations"""
        trip_report_titles = [
            "TR Paris 2023",
            "TR-Italy vacation",
            "TR/Spain adventure",
            "TR: My London trip",
            "TR. Weekend in NYC"
        ]

        for title in trip_report_titles:
            assert processor.isTripReport(title) is True

    def test_detects_trip_report_phrase(self, processor):
        """Test detection of 'trip report' phrase"""
        assert processor.isTripReport("My trip report from Paris") is True
        assert processor.isTripReport("Trip Report: Italy") is True
        assert processor.isTripReport("TRIP REPORT London") is True

    def test_detects_trip_review_phrase(self, processor):
        """Test detection of 'trip review' phrase"""
        assert processor.isTripReport("My trip review") is True
        assert processor.isTripReport("Trip Review: Amazing journey") is True

    def test_rejects_non_trip_reports(self, processor):
        """Test that normal titles are not detected as trip reports"""
        normal_titles = [
            "Best hotel in Manhattan",
            "Where to stay in Paris",
            "Restaurant recommendations",
            "Transportation options"
        ]

        for title in normal_titles:
            assert processor.isTripReport(title) is False

    def test_case_insensitive_for_phrases(self, processor):
        """Test case insensitivity for trip report/review phrases"""
        assert processor.isTripReport("TRIP REPORT") is True
        assert processor.isTripReport("Trip Report") is True
        assert processor.isTripReport("trip report") is True


class TestIsNotAppropriate:
    """Tests for isNotAppropriate method"""

    @pytest.fixture
    def processor(self, average_post_length):
        """Create a Processor1 instance"""
        return Processor(average_post_length)

    def test_detects_inappropriate_post(self, processor):
        """Test detection of inappropriate posts"""
        answers = [
            {
                "body": "Some text here. This post was determined to be inappropriate by the TripAdvisor community and was removed."
            }
        ]
        assert processor.isNotAppropriate(answers) is True

    def test_accepts_appropriate_posts(self, processor):
        """Test that appropriate posts pass"""
        answers = [
            {"body": "Great hotel, highly recommend!"},
            {"body": "The food was amazing and staff was friendly."}
        ]
        assert processor.isNotAppropriate(answers) is False

    def test_checks_all_answers(self, processor):
        """Test that all answers are checked"""
        answers = [
            {"body": "Good hotel"},
            {"body": "This post was determined to be inappropriate by the TripAdvisor community"},
            {"body": "Nice place"}
        ]
        assert processor.isNotAppropriate(answers) is True

    def test_empty_answers_list(self, processor):
        """Test handling of empty answers list"""
        assert processor.isNotAppropriate([]) is False


class TestIsLongPost:
    """Tests for isLongPost method"""

    def test_detects_long_posts(self, average_post_length):
        """Test detection of posts longer than 1.7x average"""
        processor = Processor(average_post_length=100)

        # 200 characters is > 1.7 * 100
        long_question = "x" * 200
        assert processor.isLongPost(long_question) is True

    def test_accepts_normal_posts(self, average_post_length):
        """Test that normal length posts pass"""
        processor = Processor(average_post_length=100)

        # 150 characters is < 1.7 * 100
        normal_question = "x" * 150
        assert processor.isLongPost(normal_question) is False

    def test_threshold_exactly_170_percent(self):
        """Test threshold at exactly 1.7x average"""
        processor = Processor(average_post_length=100)

        # Exactly 170 characters (at threshold, should be False)
        question_at_threshold = "x" * 170
        assert processor.isLongPost(question_at_threshold) is False

        # 171 characters (just over threshold, should be True)
        question_over_threshold = "x" * 171
        assert processor.isLongPost(question_over_threshold) is True


class TestIsIrrelevantPost:
    """Tests for isIrrelevantPost method"""

    @pytest.fixture
    def processor(self, average_post_length):
        """Create a Processor1 instance"""
        return Processor(average_post_length)

    def test_detects_irrelevant_title_keywords(self, processor):
        """Test detection of irrelevant keywords in title"""
        irrelevant_titles = [
            "Hotel A vs Hotel B",
            "Restaurant A or Restaurant B",
            "Your thoughts on Paris",
            "Best route to airport",
            "Transfer options",
            "How to get to museum",
            "My itinerary for review",
            "Review of my trip"
        ]

        for title in irrelevant_titles:
            assert processor.isIrrelevantPost(title, "Some question") is True

    def test_detects_itinerary_in_question(self, processor):
        """Test detection of 'itinerary' in question"""
        question = "Here is my itinerary for the trip. What do you think?"
        assert processor.isIrrelevantPost("Normal Title", question) is True

    def test_accepts_relevant_posts(self, processor):
        """Test that relevant posts pass"""
        title = "Best hotel in Manhattan"
        question = "I'm looking for a good hotel. Any recommendations?"
        assert processor.isIrrelevantPost(title, question) is False

    def test_case_insensitive(self, processor):
        """Test case insensitivity"""
        assert processor.isIrrelevantPost("HOTEL VS HOTEL", "question") is True
        assert processor.isIrrelevantPost("Title", "MY ITINERARY") is True


class TestProcessorCall:
    """Tests for the Processor __call__ method"""

    @pytest.fixture
    def processor(self, average_post_length):
        """Create a Processor1 instance"""
        return Processor(average_post_length)

    def test_accepts_valid_post(self, processor, sample_post):
        """Test that valid posts pass without exception"""
        try:
            processor(sample_post)
        except Exception as e:
            pytest.fail(f"Valid post should not raise exception: {e}")

    def test_rejects_trip_report(self, processor, sample_post):
        """Test that trip reports are rejected"""
        sample_post["title"] = "TR My Paris Trip"
        with pytest.raises(Exception, match="Trip Report"):
            processor(sample_post)

    def test_rejects_inappropriate_post(self, processor, sample_post):
        """Test that inappropriate posts are rejected"""
        sample_post["answers"] = [
            {"body": "This post was determined to be inappropriate by the TripAdvisor community"}
        ]
        with pytest.raises(Exception, match="Is Not Appropriate"):
            processor(sample_post)

    def test_rejects_long_post(self, sample_post):
        """Test that long posts are rejected"""
        processor = Processor(average_post_length=100)
        sample_post["question"] = "x" * 200  # Much longer than 1.7 * 100
        with pytest.raises(Exception, match="Long Post"):
            processor(sample_post)

    def test_rejects_irrelevant_post(self, processor, sample_post):
        """Test that irrelevant posts are rejected"""
        sample_post["title"] = "Hotel A vs Hotel B"
        with pytest.raises(Exception, match="Irrelevant Post"):
            processor(sample_post)

    def test_checks_filters_in_order(self, sample_post):
        """Test that filters are checked in order (trip report first)"""
        processor = Processor(average_post_length=10)

        # Post fails multiple filters
        sample_post["title"] = "TR vs hotels"  # Trip report + irrelevant
        sample_post["question"] = "x" * 100  # Long post

        # Should fail on first filter (Trip Report)
        with pytest.raises(Exception, match="Trip Report"):
            processor(sample_post)
