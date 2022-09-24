FROM docker.io/arm64v8/amazonlinux:latest

MAINTAINER Yash Indane

LABEL platform="linux/arm64/v8" version="arm64v8"

COPY . /platefetch/

WORKDIR /platefetch

RUN yum install python3 -y && \
    yum install awscli -y && \
    yum install gcc-c++ -y && \
    yum install python3-devel -y && \
    yum install opencv opencv-devel opencv-python -y && \
    pip3 install -r requirements.txt
    
EXPOSE 2400/tcp

ENTRYPOINT ["python3", "appaws.py"]