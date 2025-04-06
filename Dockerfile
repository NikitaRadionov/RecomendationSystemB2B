FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y gcc libpq-dev libgomp1 \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y gcc \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /usr/local/nltk_data \
    && python -c "import nltk; nltk.data.path.append('/usr/local/nltk_data'); nltk.download('punkt_tab', download_dir='/usr/local/nltk_data')"

ENV NLTK_DATA=/usr/local/nltk_data

# CMD ["sh", "-c", "mkdir -p /app/logs && touch /app/logs/app.log && chmod 777 /app/logs/app.log && cd /app/APIHub && python manage.py migrate && python manage.py runscript api.scripts.set_passwords && python manage.py runserver 0.0.0.0:8000"]

CMD ["sh", "-c", "mkdir -p /app/logs && touch /app/logs/app.log && chmod 777 /app/logs/app.log && cd /app/APIHub && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

# CMD ["sh", "-c", "mkdir -p /app/logs && touch /app/logs/app.log && chmod 777 /app/logs/app.log && tail -f /dev/null"]
