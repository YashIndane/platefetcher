#Dockerfile for platefetcher

FROM docker.io/yashindane/demoplate-base:v1

MAINTAINER Yash Indane <yashindane46@gmail.com>

LABEL platform="linux/arm64/v8" version="arm64v8"

LABEL org.opencontainers.image.source https://github.com/yashindane/platefetcher

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
