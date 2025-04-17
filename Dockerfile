FROM python:3.10-slim
WORKDIR /app
COPY serp_bot.py .
RUN pip install flask flask-cors
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
