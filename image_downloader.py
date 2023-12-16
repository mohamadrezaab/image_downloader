import aiohttp
import asyncio
import asyncpg
from google_images_search import GoogleImagesSearch
from io import BytesIO
from PIL import Image

async def fetch_image(session, url):
    async with session.get(url) as response:
        return await response.read()

async def download_and_store_image(session, url, target_size, connection):
    try:
        image_data = await fetch_image(session, url)
        img = Image.open(BytesIO(image_data))

        # Resize image
        img = img.resize(target_size)

        # Convert image to binary data
        img_byte_array = BytesIO()
        img.save(img_byte_array, format='JPEG')
        img_binary = img_byte_array.getvalue()

        # Insert image data into the database
        await connection.execute(
            "INSERT INTO images (image_data) VALUES ($1)",
            img_binary
        )

        print(f'Saved image to the database: {url}')
    except Exception as e:
        print(f'Error downloading or storing image: {e}')

async def google_image_search_async(query, num_images=10):
    gis = GoogleImagesSearch('youre api key', 'yore cx')  # Replace with your actual API key and CX
    search_params = {'q': query, 'num': num_images}
    gis.search(search_params)
    return [image.url for image in gis.results()]

async def main():
    # Connect to the PostgreSQL database (replace with your actual details)
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port='5432',
        user='postgres',
        password='postgres',
        database='images_downloader'
    )

    # Ensure the images table exists
    await connection.execute('DROP TABLE IF EXISTS images;')
    await connection.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            image_data BYTEA NOT NULL
        );
    ''')

    # Perform Google Image Search asynchronously
    search_query = input("Enter search query: ")
    num_images = int(input("Enter the number of images to fetch: "))
    image_urls = await google_image_search_async(search_query, num_images)

    # Download and store images asynchronously
    target_size = (300, 300)
    async with aiohttp.ClientSession() as session:
        tasks = [download_and_store_image(session, url, target_size, connection) for url in image_urls]
        await asyncio.gather(*tasks)

    # Close the database connection
    await connection.close()

if __name__ == "__main__":
    asyncio.run(main())
