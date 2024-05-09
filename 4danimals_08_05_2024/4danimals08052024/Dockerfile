# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install Flask Flask_SQLAlchemy

# Set environment variable in Dockerfile
ENV USER_HASH "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
ENV PASSWORD_HASH "a109e36947ad56de1dca1cc49f0ef8ac9ad9a7b1aa0df41fb3c4cb73c1ff01ea"

# Copy and set permissions for the entrypoint script
RUN chmod +x startup.sh

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV FLASK_APP=app.py

# Run the entrypoint script
ENTRYPOINT ["./startup.sh"]

# Command to run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]