FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn (if not already in requirements.txt)
RUN pip install gunicorn

# Copy the whole app (this includes uploads, certs, etc.)
COPY app/ ./app/
COPY app/serp_bot.py ./app.py
COPY certs/ ./certs/

# Ensure uploads directory exists (will overwrite if missing)
RUN mkdir -p /app/app/uploads

# Expose the Flask port
EXPOSE 5000

# Run the app using Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
