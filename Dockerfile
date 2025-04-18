FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
COPY serp_bot.py ./app.py
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Expose port 5000
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Run the application with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]