# Use an official lightweight Python image
FROM python:3.12-slim

# Prevent Python from buffering output
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy requirements first (better Docker caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Expose the application port
EXPOSE 5000

# Start the server
CMD ["python", "app.py"]