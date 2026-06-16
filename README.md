<div align="center">

   ![plateff](https://user-images.githubusercontent.com/53041219/196192426-ad2033d6-798e-4f6e-9e08-2f1d2d7ad0d7.png)

   

   ![](https://img.shields.io/badge/raspberrypi-4B-red?logo=raspberrypi&logoColor=red)
   ![](https://img.shields.io/badge/python-3-red?logo=python&logoColor=blue)
   ![](https://img.shields.io/badge/opencv-red?logo=opencv&logoColor=purple)
   ![](https://img.shields.io/badge/flask-red?logo=flask&logoColor=yellow)
   ![](https://img.shields.io/badge/aws-red?logo=amazon&logoColor=green)
   ![](https://img.shields.io/badge/docker-red?logo=docker&logoColor=black)
   <br>
   ![](https://img.shields.io/badge/podman-blue?logo=podman&logoColor=purple)
   ![](https://img.shields.io/badge/License-MIT-green)
   ![](https://img.shields.io/badge/arm64-v8-yellow?logo=arm)
   ![](https://img.shields.io/badge/powered%20by-RPI%20OS-pink)
   <br>
   [![Docker Build/Publish Image](https://github.com/YashIndane/platefetcher/actions/workflows/platefetcher_arm64v8_image_builder.yml/badge.svg)](https://github.com/YashIndane/platefetcher/actions/workflows/platefetcher_arm64v8_image_builder.yml)
   
</div>


## Platefetcher

Scan the number plate and get all the details of the vehicle!

<div align="center">
   <img width="846" height="646" alt="image" src="https://github.com/user-attachments/assets/b1818029-aa90-4318-88f0-95f50fba56af" />
</div>

## Usage

### 🛠️ Building the image

```
$ sudo docker build -t <IMAGE-NAME> .
```

### Pulling the image

```
$ sudo docker pull docker.io/yashindane/platefetcher-llm:v2
```

### ▶️ Running the container

```
$ sudo docker run -dit -p <PORT>:4000 --name <NAME> yashindane/platefetcher-llm:v2 --dbhost="<DB-HOSTNAME>" --dbuser="<DB-USERNAME>" --dbpass="<DB-PASSWORD>" --apikey="<OPENAI-APIKEY>" --rcuser="<REGCHECK-USER>"
````

### Access

| Tool | Path |
| --- | --- |
| `docker` | http://IP:PORT/platescan |


### Prerequisites

1. Installing docker

```
$ sudo curl -fsSL https://get.docker.com -o docker-install.sh
$ sh docker-install.sh
$ sudo usermod -aG docker pi
$ sudo reboot
```

2. (optional) Installing podman

```
$ sudo apt-get -y install podman
```

3. (optional) Installing terraform

```
$ sudo wget https://releases.hashicorp.com/terraform/1.3.7/terraform_1.3.7_linux_arm64.zip
$ sudo unzip <ZIPFILE>
$ sudo mv terraform /usr/bin/
```

4. Create a publically accessible bucket with the ```IAM``` user in AWS. The user must have ```PowerUser``` and ```AdminUser``` access.

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

5. Create a account on http://www.regcheck.org.uk and pass that username with ```--user=```.

6. (optional) Creating a mysql DB instance for all plate details to store in.

7. (optional) Creating the DB and S3 bucket using terraform

(optional) Navigate to ```infra-provisioning``` directory and run below to create DB instance and S3 bucket -

```
$ sudo terraform init
$ sudo terraform validate
$ sudo terraform plan
$ sudo terraform apply -var="access_key=<AWS_ACCESS_KEY>" -var="secret_key=<AWS_SECRET_KEY>" -var="bucket_name=<S3_BUCKET_NAME>" \
  -var="identifier=<DB_IDENTIFIER>" -var="db_username=<DB_USERNAME>" -var="db_pass=<DB_PASSWORD>" -auto-approve
```
