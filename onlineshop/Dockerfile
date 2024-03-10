# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE onlineshop.settings

# Set the working directory to /app
WORKDIR /app

# Copy the project files from the root directory into the container at /app
COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose port 8000 for the Django development server
EXPOSE 4040

# Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:4040"]

