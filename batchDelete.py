import pandas as pd
from app.DNS import DNS_Zone
from dotenv import load_dotenv
import os, random, string, datetime
import json
# Load .env file
load_dotenv(".env")

HEZTNER_DNS_TOKEN = os.getenv("HETZNER_DNS_TOKEN")
DOMAIN = os.getenv("DOMAIN")

zone = DNS_Zone(HEZTNER_DNS_TOKEN, DOMAIN, synchronous=False)

# batch create records
random_record_dict = []

size = 200


# delete records older than 2023-06-11 00:00:00
dateformat = "%Y-%m-%d %H:%M:%S"
