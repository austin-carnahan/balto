FROM python:3.8
WORKDIR /src
COPY requirements.txt .
RUN apt-get update && apt-get install -y python3-dev
RUN pip install -r requirements.txt
COPY ./src /src
EXPOSE 5000
CMD python server.py
 
