#!/usr/bin/python3

"""
PLATEFETCHER

A containerized application that detects license plate and
gets the vehical details in real time.

Usage-

  Building the image:

  $ sudo docker build --platform linux/arm64/v8 -t <IMAGE-NAME> .

  Running the container:

    Using podman -

    $ sudo podman run --network=host --platform linux/arm64/v8 -dit --device /dev/video0 --name <NAME> \
      docker.io/yashindane/platefetch:arm64v8 --aak="<AWS_ACCESS_KEY>" --ask="<AWS_SECRET_KEY>" \
      --region="<DEFAULT_REGION>" --bucketname="<BUCKET_NAME>" --user="<REG_CHECK_USER>"

    Using docker -

    $ sudo docker run --platform linux/arm64/v8 -dit -p <PORT>:2400 --device /dev/video0 --name <NAME> \
      docker.io/yashindane/platefetch:arm64v8 --aak="<AWS_ACCESS_KEY>" --ask="<AWS_SECRET_KEY>" \
      --region="<DEFAULT_REGION>" --bucketname="<BUCKET_NAME>" --user="<REG_CHECK_USER>"

  Check for other optional arguments regarding database in README.md


Author: Yash Indane
Email:  yashindane46@gmail.com
"""

#Import libraries

import cv2
import json
import boto3
import subprocess
import argparse
import logging
import requests
import xmltodict
import dbconnector
from flask import Flask, Response, render_template, request


app = Flask("PlateFetch")


#Parsing keyword arguments
def parseargs() -> None:

    global DEFAULT_REGION, BUCKET, REG_CHECK_USER, db

    parser = argparse.ArgumentParser()
    parser.add_argument("--aak", help="AWS access key", required=True)
    parser.add_argument("--ask", help="AWS secret key", required=True)
    parser.add_argument("--region", help="AWS default region", required=True)
    parser.add_argument("--bucketname", help="AWS bucket name", required=True)
    parser.add_argument("--user", help="Reg Check API user", required=True)
    parser.add_argument("--dbhost", help="Host endpoint of DB instance", required=False)
    parser.add_argument("--dbport", help="Port at which DB service running", required=False)
    parser.add_argument("--dbuser", help="DB username", required=False)
    parser.add_argument("--dbpass", help="DB password", required=False)

    args = parser.parse_args()

    AWS_ACCESS_KEY = args.aak
    AWS_SECRET_KEY = args.ask
    DEFAULT_REGION = args.region
    BUCKET = args.bucketname
    REG_CHECK_USER = args.user

    DB_HOST = args.dbhost
    DB_PORT = args.dbport
    DB_USER = args.dbuser
    DB_PASS = args.dbpass
    
    #Write the default region and bucket name so that JS can use it
    with open("vals.txt", "w") as file:
        file.write(f"{BUCKET} {DEFAULT_REGION}")
    file.close()
    
    #Configure aws-CLI
    a, b = subprocess.getstatusoutput(f"aws configure set aws_access_key_id {AWS_ACCESS_KEY}")
    a, b = subprocess.getstatusoutput(f"aws configure set aws_secret_access_key {AWS_SECRET_KEY}")
    a, b = subprocess.getstatusoutput(f"aws configure set default.region {DEFAULT_REGION}")

    logging.info(f"AWS-CLI Configured, with default region : {DEFAULT_REGION}")

    #Setting up db instance
    db = dbconnector.DB_INSTANCE(
         host=DB_HOST,
         port=DB_PORT,
         user=DB_USER,
         password=DB_PASS
    )

    db.connectToInstance()
    db.createDB()
    db.createTable()



#Extract the numbers from the plate
def extract_number_aws() -> str:

  #Putting image in S3
  region = DEFAULT_REGION
  bucket_name = BUCKET
  filename = "static/detected_plate.png"
  s3 = boto3.resource("s3")
  s3.Bucket(bucket_name).upload_file(filename, "detected_plate.png")


  #Calling Textract, to extract characters
  textract = boto3.client("textract", region_name=region)
  response = textract.detect_document_text(
      Document = {
        "S3Object" : {
          "Bucket" : bucket_name,
          "Name" : "detected_plate.png"
         }
     }
  )
  
  number = response["Blocks"][1]["Text"].replace(" ", "")

  q = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  final_string = ""
  for char in number:
    if char in q:
        final_string+=char
  
  if len(final_string)==10:
    write_to_file(final_string)      
    return final_string

  else:
    return ""
   

#Detects the plate using HAAR Cascade
def detect_number_plate(frame):

    """
    Frame Preprocessing
    The below preprocessing has been reffered from the research_paper
    """
    
    #Under Sampling

    #RGB to HSV Conversion 
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #Grayscale extraction, taking V-Channel
    (h,s,v) = cv2.split(hsv)

    #Morphological transformations
    tophat = cv2.morphologyEx(v, cv2.MORPH_TOPHAT, kernel=(5,5))
    blackhat = cv2.morphologyEx(v, cv2.MORPH_BLACKHAT, kernel=(5,5))
    cv2.add(v, tophat)
    cv2.subtract(v, blackhat)
    
    #Gaussian Smoothing
    gaussian_blur = cv2.GaussianBlur(v, (5, 5), 0)
    
    #Plate detection
    plate = plate_classifier.detectMultiScale(gaussian_blur, 1.43, 7)
    for (x, y, w, h) in plate:
        
        #The ratio for indian plates
        r=(y+h/x+w)
        if 400<r<450:
            detected_plate = frame[y:y+h, x:x+w]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (205, 50, 153), 2)
            cv2.imwrite("static/detected_plate.png", detected_plate)
            text = extract_number_aws()
            logging.info(text)
            frame = cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                                1, (0,255,0), 2, cv2.LINE_AA)
    try:
        #return detected_plate
        return frame
    except Exception as e:
        return frame


#Streams the video input
def gen_stream():

    while True:
        ret, frame = cap.read()
        #initial_timestamp = time.time()
        #Processing frames
        detected_plate = detect_number_plate(frame)

        try:
            ret, png = cv2.imencode(".png", detected_plate)
            frame = png.tobytes()
            yield(b'--frame\r\n'
                 b'Content-Type: image/png\r\n\r\n'+frame+b'\r\n\r\n')
        except Exception as e:
            logging.error(e)


#Writes the extracted numbers to number.txt file
def write_to_file(number:str) -> None:

    with open("number.txt", "w") as numfile:
        numfile.write(number)
    numfile.close()


#This route used by JS to get the vehicle details
@app.route("/fetchvehicle", methods=["GET"])
def fvehicle() -> str:

    try:

        number = request.args.get("vnumber")
        req = requests.get(f"http://www.regcheck.org.uk/api/reg.asmx/CheckIndia?RegistrationNumber={number}&username={REG_CHECK_USER}")
        data = xmltodict.parse(req.content)
        jdata = json.dumps(data)
        df = json.loads(jdata)
        df1 = json.loads(df["Vehicle"]["vehicleJson"])

        details = [df1["Description"],
                   df1["RegistrationYear"],
                   df1["EngineSize"]["CurrentTextValue"],
                   df1["NumberOfSeats"]["CurrentTextValue"],
                   df1["VechileIdentificationNumber"],
                   df1["EngineNumber"],
                   df1["FuelType"]["CurrentTextValue"],
                   df1["RegistrationDate"],
                   df1["Location"]]

        ret_string = ""
        
        for x in details:
            if " " in str(x):
                x = "-".join(str(x).split())
            ret_string += str(x) + " " if str(x) else "-" + " "

        db.connectToInstance()
        
        #Inserting data to db
        db.insertData(f"{number} {ret_string[:-1]}")

        return ret_string[:-1]

    except Exception as e:

        logging.error(e)

        db.connectToInstance()

        #Inserting data to db
        db.insertData(f"{number} - - - - - - - - -")

        return "- - - - - - - - -"


#This route used by JS function to read the number.txt file
@app.route("/numberfetch")
def fetch() -> str:

    with open("number.txt", "r") as numfile:
        number = numfile.readlines()
    numfile.close()

    with open("number.txt", "w") as numfile:
        numfile.write("0")
    numfile.close()
    
    try:
      return number[0].replace("\n", "")
    except Exception as e:
        return "0"


#This route used by JS to read bucket name
@app.route("/valsfetch")
def vfetch() -> str:

    with open("vals.txt", "r") as vfile:
        vals = vfile.readlines()
    vfile.close()

    return vals[0].replace("\n", "")


#Route on which footage is streamed
@app.route("/stream")
def stream():

    return Response(gen_stream(), mimetype="multipart/x-mixed-replace; boundary=frame")


#The main page
@app.route("/out")
def out():

    return render_template("out.html")


if __name__=="__main__":
    
    #Parse cmdline kwargs
    parseargs()

    #Load HAAR cascade for number plate
    plate_classifier = cv2.CascadeClassifier("indian_plate.xml")

    #Set logging configuration
    logging.basicConfig(level=logging.NOTSET)

    #Open system camera
    cap = cv2.VideoCapture(0)

    logging.info("Connected to CAM")

    app.run(host="0.0.0.0", port=2400)
