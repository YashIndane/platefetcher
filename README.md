<div align="center">

   ![plateff](https://user-images.githubusercontent.com/53041219/196192426-ad2033d6-798e-4f6e-9e08-2f1d2d7ad0d7.png)

   

   ![](https://img.shields.io/badge/raspberrypi-4B-red?style=flat-square&logo=raspberrypi&logoColor=red)
   ![](https://img.shields.io/badge/python-3-red?style=flat-square&logo=python&logoColor=blue)
   ![](https://img.shields.io/badge/opencv-red?style=flat-square&logo=opencv&logoColor=purple)
   ![](https://img.shields.io/badge/flask-red?style=flat-square&logo=flask&logoColor=yellow)
   ![](https://img.shields.io/badge/aws-red?style=flat-square&logo=amazon&logoColor=green)
   ![](https://img.shields.io/badge/docker-red?style=flat-square&logo=docker&logoColor=black)
   <br>
   ![](https://img.shields.io/badge/podman-blue?style=flat-square&logo=podman&logoColor=purple)
   ![](https://img.shields.io/badge/License-MIT-green?style=flat-square)
   ![](https://img.shields.io/badge/arm64-v8-yellow?style=flat-square&logo=arm)
   ![](https://img.shields.io/badge/powered%20by-RPI%20OS-pink?style=flat-square)
   
</div>


## Platefetcher

Scan the number plate and get all the details of the vehicle!

<div align="center">

   ![](https://github.com/YashIndane/repo-images/blob/main/platefetcher-gif.gif) ![](https://github.com/YashIndane/repo-images/blob/main/ras1.png)
   
</div>

## Usage

### 🛠️ Building the image

```
$ sudo docker build --platform linux/arm64/v8 -t <IMAGE-NAME> .
```

### ▶️ Running the container

```
$ sudo podman run --platform linux/arm64/v8 -dit -p <PORT>:2400 --device /dev/video0 --name <NAME> \
       docker.io/yashindane/platefetch:arm64v8  --aak="<AWS_ACCESS_KEY>" --ask="<AWS_SECRET_KEY>" \
       --region="<DEFAULT_REGION>" --bucketname="<BUCKET_NAME>" --user="<REG_CHECK_USER>"
```

### Prerequisites

1. Create a publically accessible bucket with the ```IAM``` user in AWS. The user must have ```PowerUser``` and ```AdminUser``` access.

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

2. Create a account on ```http://www.regcheck.org.uk``` and pass that username with ```--user=```

## Working

![dia](https://user-images.githubusercontent.com/53041219/196134284-fbabf6fb-1793-47c2-a190-ab565cff2233.png)

1. Using image proccesing the region of interest, ie the plate is extracted.
2. The detected plate image is uploaded to Amazon S3.
3. AWS textract uses that image to extract the numbers.
4. Raspberry Pi receives the extracted numbers.
5. Using https://www.regcheck.org.uk API the Pi gets the vehical details using the plate number.
6. The results are printed on the Phone.

## Reference

[1] Ravi Kiran Varma Pa*, Srikanth Gantaa, Hari Krishna Bb, Praveen SVSRKc "A Novel Method for Indian Vehicle Registration Number Plate Detection and Recognition using Image Processing Techniques", International Conference on Computational Intelligence and Data Science (ICCIDS 2019)