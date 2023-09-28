FROM python:3.11
LABEL authors="scampbell"

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./nsls2api /code/nsls2api

CMD ["uvicorn", "nsls2api.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]

