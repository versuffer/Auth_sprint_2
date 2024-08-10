FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
COPY uwsgi.ini uwsgi.ini

RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY . .

EXPOSE 8002

ENTRYPOINT ["sh", "-c", "python manage.py migrate && uwsgi --strict --ini uwsgi.ini"]

LABEL author="Dmitrii Ansjaw"
