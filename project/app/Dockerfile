FROM python:3.8-alpine
WORKDIR /src
COPY requirements.txt .
RUN apk update
RUN apk add make automake gcc g++ subversion python3-dev
RUN pip install -r requirements.txt
COPY ./src /src
EXPOSE 5000
CMD python server.py
 
