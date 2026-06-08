
FROM plb:v1

MAINTAINER Yash Indane

EXPOSE 4000

RUN mkdir /plf

COPY . /plf

WORKDIR /plf

ENTRYPOINT ["python3", "app.py"]
