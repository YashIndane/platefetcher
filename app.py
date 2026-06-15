#!/usr/bin/python3

# Platefetcher App
# Author: Yash Indane
# Email: <yashindane46@gmail.com>
# License: MIT

from __future__ import annotations

import io
import base64
import logging
import argparse

from PIL import Image
from typing import Dict
from tenacity import RetryError
from src.db_pool import DBManager
from src.vehicle_parser import fetch_and_parse
from src.extract_reg_number_multi import extract
from flask import Flask, request, render_template


app, logger = Flask(__name__), logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Suppress noisy third-party loggers
for service in [
    'werkzeug',
    'urllib3',
    'openai',
    'httpx',
]:
    logging.getLogger(service).setLevel(logging.WARNING)


@app.route('/platescan', methods=['GET'])
def input():
    return render_template(
        'input.html',
        title='Demo',
    )


@app.route('/submit', methods=['POST'])
def submit():
    # base64 JPEG string
    image_data = request.form['image_data']
    vehicle_type = request.form['type']
    save_to_db = request.form.get('save_to_db', '0') == '1'

    logging.info(f"Vehicle Type: {vehicle_type}, DB Save: {save_to_db}")

    #process image to save
    #strip the base64 header (e.g. "data:image/jpeg;base64,...")
    _, encoded = image_data.split(',', 1)

    #decode and save
    image_bytes = base64.b64decode(encoded)
    image = Image.open(io.BytesIO(image_bytes))
    image.save('vehicle.png')

    try:
       #get the registration number from saved frame
        reg_number: str = extract(
            image_path='vehicle.png',
            type=vehicle_type,
            api_key=apikey,
        )

        info: Dict = fetch_and_parse(reg_number, rcuser)

        if save_to_db:
            db_instance.insertData(reg_number, info)

        return render_template('output.html', vehicle=info, regnum=reg_number)

    except RetryError:
        return render_template('error.html',
            message="⚠️ API not responding/number plate not found in DB."
        ), 503

    except PermissionError as e:
        if str(e) == "OUT_OF_CREDIT":
            return render_template('error.html',
                message="⚠️ Out of credits. Recharge your RegCheck account."
            ), 402
    
    except LookupError:
       return render_template('error.html',
            message="❌ Number plate not found in database."
        ), 404
    
    except ValueError as e:
        if str(e) == "NO_PLATE_DETECTED_IN_FRAME":
            return render_template('error.html',
                message="❌ No number plate detected, please try again."
            ), 400
    
    except RuntimeError as e:
        if str(e) == "INSERT_DATA_FAILURE":
            return render_template('error.html',
                message="❌ Could not insert data to Table."
            ), 400

    except Exception as e:
        #for any other unhandled exception
        return render_template('error.html', message=str(e)), 500


def parseargs() -> None:
    """Argument parser"""

    global dbhost, dbuser, dbpass, apikey, rcuser

    parser = argparse.ArgumentParser(
        add_help="Argument parser for Plate-fetcher"
    )

    _argument_map = {'--dbhost': "The hostname of the DB instance",
                     '--dbuser': "Username of DB instance",
                     '--dbpass': "Password of DB instance",
                     '--apikey': "API key for openai API platform",
                     '--rcuser': "Regcheck username"}
    
    for arg, description in _argument_map.items():
        parser.add_argument(arg, help=description, required=True)

    args = parser.parse_args()

    dbhost = args.dbhost
    dbuser = args.dbuser
    dbpass = args.dbpass
    apikey = args.apikey
    rcuser = args.rcuser


def initialize_db() -> None:
    """Initialize DB instance and create table"""

    global db_instance

    db_instance = DBManager(
        host=dbhost, port=3306, user=dbuser, password=dbpass)

    db_instance.connectToInstance()
    logging.info(" Connected to DB instance!")

    db_instance.createDB()
    logging.info(" Created DB")

    db_instance.createTable()
    logging.info(" Created table inside DB")


def run() -> None:
    parseargs()
    initialize_db()
    app.run(host='0.0.0.0', port=4000)


if __name__ == '__main__':
    run()
