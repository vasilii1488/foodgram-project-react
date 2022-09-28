FROM python:3.7-slim

WORKDIR /backend

COPY requirements.txt .

RUN pip install --upgrade pip --no-cache-dir

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

RUN pip install -r ./requirements.txt --no-cache-dir


COPY . .

CMD ["python", "manage.py", "runserver", "0:8000"]
# CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]


