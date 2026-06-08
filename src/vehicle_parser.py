#File for hitting the RegCheck API, and getting vehicle details

import json
import requests
import xml.etree.ElementTree as ET

from typing import Dict
from tenacity import (
    retry,
    wait_fixed, 
    stop_after_attempt,
    retry_if_exception_type,
)

IGNORED_FIELDS = {"MakeDescription"}

FIELD_MAP = {
    "Description":                  "Description",
    "RegistrationYear":             "Registration Year",
    "CarMake":                      "Car Make",
    "CarModel":                     "Car Model",
    "Variant":                      "Variant",
    "EngineSize":                   "Engine Size",
    "EngineNumber":                 "Engine Number",
    "FuelType":                     "Fuel Type",
    "ModelDescription":             "Model Description",
    "NumberOfSeats":                "Number of Seats",
    # API typo preserved
    "VechileIdentificationNumber":  "VIN",
    "RegistrationDate":             "Registration Date",
    "Owner":                        "Owner",
    "Fitness":                      "Fitness",
    "Insurance":                    "Insurance",
    "PUCC":                         "PUCC",
    "VehicleType":                  "Vehicle Type",
    "Location":                     "Location",
    "ImageUrl":                     "Image URL",
}


def _get_value(obj, key: str) -> str | None:
    """Extracts a value from a dict, handling plain strings
    and CurrentTextValue dicts.

    Args:
        obj: The dict to extract from.
        key: The key to look up.

    Returns:
        Stripped string value, or None if missing or empty.
    """

    val = obj.get(key)
    if isinstance(val, dict):
        return val.get("CurrentTextValue", "").strip() or None
    if isinstance(val, str):
        return val.strip() or None
    return None


def parse_vehicle_json(raw_json: str) -> Dict:
    """Parses the vehicleJson string into a labelled dict, ignoring MakeDescription.

    Args:
        raw_json: Raw JSON string from the vehicleJson API field.

    Returns:
        Dict of labelled vehicle fields mapped from FIELD_MAP.

    Raises:
        ValueError: If raw_json is not valid JSON.
        LookupError: If the plate is not found (empty fields or lookup failed response).
    """

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid vehicleJson: {e}")
 
    # Case 1: Plain string response e.g. "Indian lookup failed"
    if isinstance(data, str):
        if "lookup failed" in data.lower():
            raise LookupError("PLATE_NOT_FOUND")
 
    # Case 2: Empty key fields
    description = data.get("Description", "").strip()
    car_make = data.get("CarMake", {}).get("CurrentTextValue", "").strip()
    car_model = data.get("CarModel", {}).get("CurrentTextValue", "").strip()
 
    if not description and not car_make and not car_model:
        raise LookupError("PLATE_NOT_FOUND")
 
    result = {}
    for api_key, label in FIELD_MAP.items():
        if api_key in IGNORED_FIELDS:
            continue
        result[label] = _get_value(data, api_key)
 
    return result


def extract_vehicle_json(xml_text: str) -> str:
    """Extracts the raw vehicleJson string from the XML API response.

    Args:
        xml_text: Raw XML response string from the RegCheck API.

    Returns:
        Raw vehicleJson string extracted from the XML.

    Raises:
        ValueError: If the XML is malformed or vehicleJson element is not found.
    """

    try:
        root = ET.fromstring(xml_text.strip())
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {e}")

    # Namespace-agnostic search
    for el in root.iter():
        if el.tag.endswith("vehicleJson"):
            if el.text:
                return el.text.strip()

    raise ValueError("vehicleJson element not found in response.")


@retry(
    retry=retry_if_exception_type(requests.exceptions.Timeout),
    stop=stop_after_attempt(3),   # try max 3 times
    wait=wait_fixed(2),           # wait 2 seconds between retries
)
def fetch_and_parse(number: str, rcu: str) -> Dict:
    """Fetches vehicle data from the RegCheck API and parses the response.

    Retries up to 3 times on timeout, with a 2 second wait between attempts.

    Args:
        number: Vehicle registration number to look up.
        rcu: RegCheck API username.

    Returns:
        Dict of labelled vehicle fields.

    Raises:
        RetryError: If the API times out after all 3 retry attempts.
        PermissionError: If the RegCheck account is out of credits.
        LookupError: If the plate is not found in the database.
        ValueError: If the API response is malformed or unparseable.
    """

    url = (
        f"http://www.regcheck.org.uk/api/reg.asmx/CheckIndia"
        f"?RegistrationNumber={number}&username={rcu}"
    )
    response = requests.get(url, timeout=10)

    # ── Credit exhausted ──
    if response.status_code == 500:
        if "out of credit" in response.text.lower():
            raise PermissionError("OUT_OF_CREDIT")

    response.raise_for_status()
    raw_json = extract_vehicle_json(response.text)
    return parse_vehicle_json(raw_json)
