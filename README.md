## Platefetcher

![](https://img.shields.io/badge/raspberrypi-4B-red?style=flat-square&logo=raspberrypi&logoColor=red) ![](https://img.shields.io/badge/python-3-red?style=flat-square&logo=python&logoColor=blue) ![](https://img.shields.io/badge/opencv-red?style=flat-square&logo=opencv&logoColor=purple) ![](https://img.shields.io/badge/flask-red?style=flat-square&logo=flask&logoColor=yellow) ![](https://img.shields.io/badge/aws-red?style=flat-square&logo=amazon&logoColor=green) ![](https://img.shields.io/badge/docker-red?style=flat-square&logo=docker&logoColor=black)

Scan the number plate and get all the details of the vehicle!

## Usage

### 🛠️ Building the image

```
$ sudo docker build --platform linux/arm64/v8 -t <IMAGE-NAME> .
```

### 🏃🏻‍♂️ Running the container

```
$ sudo podman run --platform linux/arm64/v8 -dit -p <PORT>:2400 --device /dev/video0 --name <NAME> \
       docker.io/yashindane/platefetch:arm64v8  --aak="<AWS_ACCESS_KEY>" --ask="<AWS_SECRET_KEY>" \
       --region="<DEFAULT_REGION>" --bucketname="<BUCKET_NAME>"
```

### Prerequisites

Create a publically accessible bucket with the ```IAM``` user in AWS. The user must have ```PowerUser``` and ```AdminUser``` access.

Configure this bucket policy-

```
{
  "Id": "Policy1664186300628",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1664186298804",
      "Action": "s3:*",
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::<BUCKET-NAME>/*",
      "Principal": "*"
    }
  ]
}
```

## Reference

[1] Ravi Kiran Varma Pa*, Srikanth Gantaa, Hari Krishna Bb, Praveen SVSRKc "A Novel Method for Indian Vehicle Registration Number Plate Detection and Recognition using Image Processing Techniques", International Conference on Computational Intelligence and Data Science (ICCIDS 2019)