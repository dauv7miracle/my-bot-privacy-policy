FROM python:3.10-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

# Create user_logs directory if it doesn't exist
RUN mkdir -p user_logs

CMD ["python", "bot.py"]
