FROM python:3.10-slim

# Set working directory to /app
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt



# Install Gunicorn (optional if in requirements.txt)
RUN pip install gunicorn

# Copy app code and certs
COPY app/ ./app/
COPY app/certs/ ./certs/

# Ensure uploads directory exists
RUN mkdir -p /app/app/uploads

# Set working directory to inside the app folder
WORKDIR /app/app

# Expose Flask port
EXPOSE 5000

# Run app via Gunicorn, referencing the app instance inside serp_bot.py
CMD ["gunicorn", "serp_bot:app", "--bind", "0.0.0.0:5000"]
