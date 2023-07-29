import requests as req
import json
from app.DNS import DNS_Zone
from argparse import ArgumentParser as PARSER
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get arguments
# command: create, update, delete
# command should look like this: python index.py create --name test --type A --value 123.123.123.123
parser = PARSER(description="Hetzner DNS API")
parser.add_argument("command", help="Command to execute", choices=["create", "update", "delete"])
parser.add_argument("--name", "-n", help="Name of the record", required=True)
parser.add_argument("--type", "-t", help="Type of the record", choices=["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SRV", "TLSA", "CAA"], required=True)
parser.add_argument("--value", "-v", help="Value of the record", required=True)
parser.add_argument("--ttl", "-T", help="TTL of the record", default=3600)
parser.add_argument("--domain", "-d", help="Domain of the record")

# Add Helptext
parser.add_argument("--help", "-h", help="Show this help text", action="help")

args = parser.parse_args() 

print(args)

# Get environment variables
HETZNER_DNS_TOKEN = os.getenv("HETZNER_DNS_TOKEN") if os.getenv("HETZNER_DNS_TOKEN") else None
if HETZNER_DNS_TOKEN is None:
    raise Exception("No Hetzner DNS Token supplied")


DOMAIN = os.getenv("DOMAIN") if os.getenv("DOMAIN") else None
if DOMAIN is None:
    raise Exception("No domain supplied")

mjwcodr_de = DNS_Zone(HETZNER_DNS_TOKEN, DOMAIN)
mjwcodr_de.create_record(args.name, args.type, args.value, args.ttl)