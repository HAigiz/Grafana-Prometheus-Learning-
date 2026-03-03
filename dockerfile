FROM python:3.9-slim

RUN apt-get update && apt-get install -y nginx supervisor gcc python3-dev && \
    pip install uwsgi

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
COPY nginx_inner.conf /etc/nginx/sites-available/default
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN touch /tmp/uwsgi.sock && chmod 666 /tmp/uwsgi.sock

CMD ["/usr/bin/supervisord"]
