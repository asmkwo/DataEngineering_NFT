FROM python:3.8

COPY requirements.txt /app/
COPY nft_spider_aleatoire.csv /app

RUN pip install -r /app/requirements.txt

WORKDIR /app

ENV FLASK_APP=nft_dash

CMD python -m flask run