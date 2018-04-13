FROM ubuntu:artful

WORKDIR /app
ADD . .

RUN apt-get update && \
    apt-get -y install python3 python3-pip && \
    pip3 install -r requirements.txt

CMD python3 src/worker.py
