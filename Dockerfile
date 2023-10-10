FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./nsls2api /code/nsls2api

CMD ["uvicorn", "nsls2api.main:api", "--proxy-headers", "--host", "0.0.0.0", "--port", "8080", "--workers", "4", "--ssl-keyfile=/etc/nsls2/tls/server.key", "--ssl-certfile=/etc/nsls2/tls/server.cer"]

