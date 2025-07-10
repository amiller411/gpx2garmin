"""
Upload a GPX or FIT file to Garmin Connect

Usage:
    # Ensure your .env or environment has:
    #   GARMIN_USERNAME=you@example.com
    #   GARMIN_PASSWORD=yourpassword
    python garmin_uploader.py -f <path_to_gpx_or_fit_file>
    python garmin_uploader.py --file <path_to_gpx_or_fit_file>
"""
import os
import sys
import argparse
from dotenv import load_dotenv
from garminconnect import Garmin
from generate_run_gpx import generate_run_gpx


def upload_to_garmin(file_path: str):
    """Uploads the given GPX or FIT file to Garmin Connect as a run."""
    # Load credentials
    load_dotenv()
    username = os.getenv('GARMIN_USERNAME')
    password = os.getenv('GARMIN_PASSWORD')
    if not username or not password:
        print('Error: GARMIN_USERNAME and GARMIN_PASSWORD must be set in environment', file=sys.stderr)
        sys.exit(1)

    # Authenticate
    client = Garmin(username, password)
    try:
        client.login()
    except Exception as e:
        print(f'Login failed: {e}', file=sys.stderr)
        sys.exit(1)
    print('✅ Logged in to Garmin Connect')

    # Determine data type
    ext = os.path.splitext(file_path)[1].lower()
    if ext != '.fit' and ext != '.gpx':
        print('Error: File must be .gpx or .fit', file=sys.stderr)
        sys.exit(1)

    # Upload activity
    print(f'Uploading {file_path} as a running activity...')
    try:
        client.upload_activity(file_path)
    except Exception as e:
        print(f'Upload failed: {e}', file=sys.stderr)
        sys.exit(1)
    print('✅ Upload complete!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload GPX/FIT to Garmin Connect')
    parser.add_argument('--file', '-f', help='Path to existing .gpx or .fit file')
    args = parser.parse_args()

    if args.file:
        path = args.file
        if not os.path.isfile(path):
            print(f'Error: file not found: {path}', file=sys.stderr)
            sys.exit(1)
    else:
        path = generate_run_gpx()

    upload_to_garmin(path)
