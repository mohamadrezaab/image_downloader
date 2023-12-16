import asyncio
import unittest
from unittest.mock import Mock, patch
from image_downloader import (
    fetch_image,
    download_and_store_image,
    google_image_search_async,
    create_connection,
    print_stored_images,
)

class TestImageDownloader(unittest.TestCase):

    @patch('asyncpg.connect')
    @patch('image_downloader.aiohttp.ClientSession.get')
    @patch('image_downloader.Image.open')
    def test_download_and_store_image(self, mock_open, mock_get, mock_connect):
        mock_session = Mock()
        mock_response = Mock()
        mock_response.read.return_value = b'fake_image_data'
        mock_get.return_value.__aenter__.return_value = mock_response

        mock_img = Mock()
        mock_open.return_value = mock_img
        mock_img.save.side_effect = lambda *args, **kwargs: None

        mock_connection = Mock()
        mock_connection.execute.side_effect = lambda *args, **kwargs: None

        url = 'https://example.com/image.jpg'
        target_size = (300, 300)

        asyncio.run(download_and_store_image(mock_session, url, target_size, mock_connection))

        mock_get.assert_called_once_with(url)
        mock_response.read.assert_called_once()
        mock_open.assert_called_once()
        mock_img.resize.assert_called_once_with(target_size)
        mock_img.save.assert_called_once()
        mock_connection.execute.assert_called_once()

    @patch('asyncpg.connect')
    def test_create_connection(self, mock_connect):
        create_connection()
        mock_connect.assert_called_once()

    @patch('asyncpg.connect')
    async def test_print_stored_images(self, mock_connect):
        mock_connection = await create_connection()
        mock_connection.fetch.return_value = [{'id': 1, 'image_data': b'fake_image_data'}]

        await print_stored_images(mock_connection)

        mock_connection.fetch.assert_called_once_with('SELECT * FROM images;')

    @patch('google_images_search.GoogleImagesSearch.search')
    def test_google_image_search_async(self, mock_search):
        mock_search.return_value = None
        result = asyncio.run(google_image_search_async('cats', 5))
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()
