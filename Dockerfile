FROM python:3.11-slim

WORKDIR /app

RUN python -m venv /app/.venv
COPY requirements.txt .
RUN /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y postgresql-client

COPY wait-for-db.sh /usr/local/bin/wait-for-db.sh
RUN chmod +x /usr/local/bin/wait-for-db.sh

COPY . .

EXPOSE 5001
CMD ["/usr/local/bin/wait-for-db.sh", "sh", "-c", "/app/.venv/bin/python -c 'from main import init_db; init_db()' && /app/.venv/bin/python -m gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5001"]

