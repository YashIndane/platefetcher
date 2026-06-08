# Vehicle Registration Number Extractor  (GPT-4o Vision)
# =======================================================
# Extracts the registration / licence plate number from ANY vehicle image.

# Supported vehicles : car, truck, bus, motorcycle, bike, auto-rickshaw,
#                      tractor, van, scooter, taxi, ambulance, … (any road vehicle)
# Supported views    : front, rear, side, angled, partial
# Supported sources  : local image file  OR  public image URL
# Image formats      : JPG, JPEG, PNG, GIF, WEBP, BMP, TIFF


import os
import re
import sys
import json
import base64
import argparse

from pathlib import Path
from typing import List, Dict, Tuple

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed.  Run: pip install openai",
          file=sys.stderr)
    sys.exit(1)


# Supported formats
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", 
                        ".webp", ".bmp", ".tiff", ".tif"}

MEDIA_TYPE_MAP = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".gif":  "image/gif",
    ".webp": "image/webp",
    ".bmp":  "image/bmp",
    ".tiff": "image/tiff",
    ".tif":  "image/tiff",
}

# Vehicle types the user can hint at
VEHICLE_TYPES = [
    "any", "car", "truck", "bus", "motorcycle", "bike", "scooter",
    "auto-rickshaw", "tractor", "van", "taxi", "ambulance", "trailer",
]

# Prompts
SYSTEM_PROMPT = """\
You are an expert, highly accurate vehicle registration / licence plate reader.
You can read plates from ANY road vehicle — cars, trucks, buses, motorcycles,
scooters, auto-rickshaws, tractors, vans, taxis, ambulances, trailers, and more.
The image may show the vehicle from the front, rear, side, or at an angle.
Plates may be rectangular, square, two-line, embossed, stickered, or partially obscured.

Output rules (strictly follow):
1. Return ONLY the plate number(s) — no explanation, no label, no extra text.
2. Uppercase all letters; preserve hyphens or spaces that are part of the format.
3. If exactly ONE plate is visible (or asked for), output just that number.
4. If asked for ALL plates (--multi mode), output a JSON array of strings, e.g. ["MH12AB1234","DL3CAF0001"].
5. If no plate can be read at all, output exactly: NOT_FOUND
"""

def _build_user_prompt(vehicle_type: str, multi: bool) -> str:
    """Builds a user prompt string for licence plate extraction from a vehicle image.

    Constructs a prompt tailored to either single or multiple plate detection,
    optionally filtered by vehicle type.

    Args:
        vehicle_type: The type of vehicle in the image (e.g. "car", "bus").
            Pass "any" to skip vehicle type filtering.
        multi: If True, prompt requests ALL visible plates in the image
            (front, rear, side sticker, etc.) returned as a JSON array.
            If False, prompt requests only a single plate number.

    Returns:
        A prompt string to be sent to the LLM for plate extraction.
        - If multi is True, the LLM is expected to return a JSON array of strings.
        - If multi is False, the LLM is expected to return only the plate number.
    """

    vtype = "" if vehicle_type == "any" else f" ({vehicle_type})"

    #for multiple vehicles in frame, and to get all the vehicle scans
    if multi:
        return (
            f"This image shows a vehicle{vtype}. "
            "Find ALL registration / licence plate numbers visible anywhere in the image "
            "(front plate, rear plate, side sticker, etc.). "
            "Return them as a JSON array of strings. If none found, return [\"NOT_FOUND\"]."
        )
    
    #for single plate number scan of any vehicle
    return (
        f"This image shows a vehicle{vtype}. "
        "Extract the registration / licence plate number. "
        "The plate may be on the front, rear, or side. "
        "Return ONLY the plate number, nothing else."
    )


def is_url(s: str) -> bool:
    """Checks if a given string is a URL.

    Args:
        s: The string to check.

    Returns:
        True if the string starts with 'http://' or 'https://', False otherwise.
    """

    return s.startswith("http://") or s.startswith("https://")


def encode_local_image(image_path: str) -> Tuple[str, str]:
    """Encodes a local image file to a base64 string with its media type.

    Args:
        image_path: The file path to the image to be encoded.

    Returns:
        A tuple of (base64_encoded_string, media_type), where:
        - base64_encoded_string is the UTF-8 decoded base64 representation of the image.
        - media_type is the MIME type of the image (e.g. 'image/jpeg', 'image/png').

    Raises:
        FileNotFoundError: If the file does not exist at the given path.
        ValueError: If the file extension is not in SUPPORTED_EXTENSIONS.
    """

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported image format '{ext}'.  Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )
    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, MEDIA_TYPE_MAP[ext]


def build_image_content(image_source: str) -> Dict:
    """Builds a vision image content block for the LLM API from a path or URL.

    If the source is a URL, returns a direct image_url block. If it is a
    local file path, encodes the image to base64 and embeds it as a data URI
    with full tile resolution.

    Args:
        image_source: Either a URL (starting with 'http://' or 'https://')
            or a local file path to the image.

    Returns:
        A dict representing the image content block, structured as:
        {
            "type": "image_url",
            "image_url": {
                "url": <url or base64 data URI>,
                "detail": "high"
            }
        }

    Raises:
        FileNotFoundError: If image_source is a local path and the file does not exist.
        ValueError: If image_source is a local path with an unsupported file extension.
    """

    if is_url(image_source):
        return {
            "type": "image_url",
            "image_url": {"url": image_source, "detail": "high"},
        }
    b64, media_type = encode_local_image(image_source)
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:{media_type};base64,{b64}",
             # use full tile resolution
            "detail": "high",
        },
    }


def _clean_single(raw: str) -> str:
    """Uppercases and strips stray punctuation and extra spaces from a plate string.

    Args:
        raw: Raw plate string returned by the LLM.

    Returns:
        Cleaned and uppercased plate string.
    """

    text = raw.strip().upper()
    text = re.sub(r"[\"'`]", "", text)          # remove quotes
    text = re.sub(r"\s{2,}", " ", text)          # collapse spaces
    return text.strip()


def _parse_response(raw: str, multi: bool) -> List[str]:
    """Parses the LLM response into a list of cleaned plate strings.

    Args:
        raw: Raw response string from the LLM.
        multi: If True, expects a JSON array; falls back to splitting on
            newlines or commas. If False, returns a single plate as a list.

    Returns:
        List of cleaned, uppercased plate strings.
    """

    raw = raw.strip()

    if multi:
        # Expect a JSON array
        try:
            # Strip markdown fences if present
            clean = re.sub(r"```[a-z]*", "", raw).strip().strip("`")
            plates = json.loads(clean)
            if isinstance(plates, list):
                return [_clean_single(p) for p in plates if p]
        except json.JSONDecodeError:
            pass
        # Fallback: split on newlines / commas
        parts = re.split(r"[\n,]+", raw)
        return [_clean_single(p) for p in parts if p.strip()]

    # Single plate
    return [_clean_single(raw)]


# Core extraction function
def extract_registration_number(
    *,
    image_source: str,
    api_key: str | None = None,
    vehicle_type: str = "any",
    multi: bool = False,
) -> List[str]:
    """
    Extract registration plate number(s) from any vehicle image.

    Args:
        image_source:  Local file path or public image URL.
        api_key:       OpenAI API key (falls back to OPENAI_API_KEY env var).
        vehicle_type:  Hint about the vehicle type (e.g. "truck", "motorcycle").
                       Use "any" (default) when unknown.
        multi:         If True, return all plates found instead of just the best one.

    Returns:
        List of plate number strings.  ["NOT_FOUND"] if nothing detected.
    """

    client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=150,        # extra room for multi-plate JSON
        temperature=0,         # deterministic
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    build_image_content(image_source),
                    {"type": "text", "text": _build_user_prompt(vehicle_type, multi)},
                ],
            },
        ],
    )

    raw = response.choices[0].message.content or "NOT_FOUND"
    plates = _parse_response(raw, multi)
    return plates if plates else ["NOT_FOUND"]


def extract(*, image_path: str, api_key: str, type: str='other') -> str:
    """Extracts a registration plate number from an image using the OpenAI API.

    Args:
        image_path: Path or URL to the vehicle image.
        api_key: OpenAI API key for authentication.
        type: Vehicle type hint passed to the prompt (default: 'other').

    Returns:
        Cleaned, uppercased registration plate string.

    Raises:
        ValueError: If no plate is detected in the image.
        SystemExit: If api_key is not provided.
    """

    if not api_key:
        print(
            "Error: OpenAI API key not found.\n"
            "  Set OPENAI_API_KEY environment variable  OR  pass --api-key sk-...",
            file=sys.stderr,
        )
        sys.exit(1)

    plates = extract_registration_number(
        image_source=image_path,
        api_key=api_key,
        vehicle_type=type,
    )
    for plate in plates:
        #some function can be implemented here to get proper plate
        plate = plate.replace(' ', '').replace('-', '').upper()
        if plate == 'NOT_FOUND':
            raise ValueError("NO_PLATE_DETECTED_IN_FRAME")
        else:
            print(f"Detected plate in image/frame: {plate}")
            return plate
