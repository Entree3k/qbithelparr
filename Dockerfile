FROM python:3.9-alpine

ADD requirements.txt /

RUN pip install -r requirements.txt

ADD main.py /

CMD [ "python3", "./main.py" ] 