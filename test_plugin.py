import unittest
from unittest.mock import MagicMock, patch

class MockMetadata:
    def __init__(self, title=None, authors=None):
        self.title = title
        self.authors = authors

class MockMetadataReaderPlugin:
    pass


import sys
sys.modules["PIL"] = MagicMock()

sys.modules["calibre"] = MagicMock()
sys.modules["calibre.ebooks"] = MagicMock()
sys.modules["calibre.ebooks.metadata"] = MagicMock()
sys.modules["calibre.ebooks.metadata.book"] = MagicMock()
sys.modules["calibre.ebooks.metadata.book.base"] = MagicMock()
sys.modules["calibre.ebooks.metadata.book.base"].Metadata = MockMetadata
sys.modules["calibre.customize"] = MagicMock()

sys.modules["calibre_plugins"] = MagicMock()
sys.modules["calibre_plugins.audiobook_metadata"] = MagicMock()
sys.modules["calibre_plugins.audiobook_metadata.tinytag"] = MagicMock()
sys.modules["calibre_plugins.audiobook_metadata.__version__"] = MagicMock()


# Replace the mocked MetadataReaderPlugin with the real one for the test
sys.modules["calibre.customize"].MetadataReaderPlugin = MockMetadataReaderPlugin

from __init__ import *


class TestAudioBookPlugin(unittest.TestCase):

    def setUp(self):
        self.plugin = AudioBookPlugin()


    @patch("calibre_plugins.audiobook_metadata.tinytag.TinyTag.get")
    def test_get_metadata_with_metadata_without_cover(self, mock_tinytag_get):
        # Mocking TinyTag behavior
        mock_tag = MagicMock()
        mock_tag.albumartist = "Author Name"
        mock_tag.artist = "Artist Name"
        mock_tag.composer = "Composer Name"
        mock_tag.album = "Book Title"
        mock_tag.title = None
        mock_tag.year = "2023"
        mock_tag.get_image.return_value = None
        mock_tag.extra = {"copyright": "Copyright Info"}
        mock_tag.genre = "Fiction, Mystery"
        mock_tag.comment = "Some comment"
        mock_tinytag_get.return_value = mock_tag

        # Creating a fake file stream
        fake_stream = MagicMock()
        fake_stream.name = "test.m4b"

        # Call the method
        metadata = self.plugin.get_metadata(fake_stream, "m4b")

        # Assertions
        self.assertEqual("Book Title", metadata.title)
        self.assertEqual(["Author Name", "Artist Name", "Composer Name"], metadata.authors)
        self.assertEqual(date(2023, 1, 1), metadata.pubdate)
        self.assertEqual("Copyright Info", metadata.rights)
        self.assertEqual(("Fiction", "Mystery"), metadata.tags)
        self.assertEqual("Some comment", metadata.comments)
        self.assertEqual("Composer Name", metadata.performer)

    def test_join_strings_ignore_none(self):
        # Test cases for join_strings_ignore_none
        self.assertEqual("A, B, C", join_strings_ignore_none(["A", "B", None, "C"], delimiter=", "))
        self.assertEqual("", join_strings_ignore_none([None, None]))
        self.assertEqual("A", join_strings_ignore_none(["A", None]))
        self.assertEqual("A", join_strings_ignore_none([None, "A"]))
        self.assertEqual("", join_strings_ignore_none([], delimiter=" | "))

    def test_get_title_form_tag(self):
        # Mocking a tag with album and title
        mock_tag = MagicMock()
        mock_tag.album = "Title with Album"
        mock_tag.title = None
        self.assertEqual(get_title_form_tag(mock_tag), "Title with Album")

        # Mocking a tag with title only
        mock_tag.album = None
        mock_tag.title = "Only Title"
        self.assertEqual("Only Title", get_title_form_tag(mock_tag))

        # Mocking a tag with title ending in (Unabridged)
        mock_tag.title = "Title (Unabridged)"
        self.assertEqual("Title", get_title_form_tag(mock_tag))

        # Mocking a tag with no album or title
        mock_tag.album = None
        mock_tag.title = None
        self.assertIsNone(get_title_form_tag(mock_tag))

    def test_issue_1_should_not_cut_title_short(self):
        mock_tag = MagicMock()
        mock_tag.album = "You Are a Badass: How to Stop Doubting Your Greatness and Start Living an Awesome Life"
        mock_tag.title = None
        self.assertEqual(get_title_form_tag(mock_tag), "You Are a Badass: How to Stop Doubting Your Greatness and Start Living an Awesome Life")


if __name__ == "__main__":
    unittest.main()
