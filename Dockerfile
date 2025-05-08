FROM python:3.10-slim
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Ensure 'uploads' directory exists
RUN mkdir -p /app/uploads

# Install Gunicorn
RUN pip install gunicorn

COPY app/ ./


# Copy application code
COPY app/serp_bot.py ./app.py

# Expose port 5000
EXPOSE 5000

# Run the application with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]