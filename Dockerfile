FROM python:3

RUN pip install pymongo
RUN pip install flask
RUN pip install redis
RUN pip install Flask-HTTPAuth

COPY http_server.py /

ENTRYPOINT ["python", "http_server.py"]