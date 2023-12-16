# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt 

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable for PostgreSQL connection
ENV PG_HOST=127.0.0.1
ENV PG_PORT=5432
ENV PG_USER=postgres
ENV PG_PASSWORD=postgres
ENV PG_DATABASE=images_downloader

# Run app.py when the container launches
CMD ["python", "image_downloader.py"]
