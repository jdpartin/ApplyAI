# Use Python 3.10+ base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
