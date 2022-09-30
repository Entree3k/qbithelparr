FROM python:3.9-alpine

WORKDIR /usr/app

ADD requirements.txt /
ADD config.ini /
RUN pip install -r requirements.txt

ADD main.py /

VOLUME [ "/usr/app/config" ]

CMD [ "python3", "./main.py" ]
