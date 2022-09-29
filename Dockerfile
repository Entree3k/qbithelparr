FROM python:3.9-alpine

VOLUME /config

ADD requirements.txt /
ADD config.ini /
RUN pip install -r requirements.txt

ADD main.py /

CMD [ "python3", "./main.py" ]
