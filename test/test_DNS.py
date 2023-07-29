import random, string, json, pytest, sys
sys.path.append("..")
from dotenv import load_dotenv
from os import environ
from app.DNS import DNS_Zone
import requests as req



# Load .env file
load_dotenv(".env")
hetzner_dns_token = environ.get("HETZNER_DNS_TOKEN")
domain = "mjwcodr.de"

# a random string to test the create_record function
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

random_ip = f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
random_ttl = random.randint(0, 10000)

record_types = ["A", "AAAA", "CNAME", "MX", "TXT", "SRV", "TLSA", "CAA"]

def test_dns_token():
    assert hetzner_dns_token is not None
    test_dns_token_works = req.get(
        url="https://dns.hetzner.com/api/v1/zones",
        headers={
            "Auth-API-Token": hetzner_dns_token
        }
    )
    assert test_dns_token_works.status_code == 200

def test_init_DNS_Zone_non_empty_zone():
    zone = DNS_Zone(hetzner_dns_token, domain)
    assert zone != None
    assert zone.hcloud_dns_token == hetzner_dns_token
    assert zone.domain == domain
    assert zone.id != None
    assert zone.zonefile != None
    assert zone.records != None

zone = DNS_Zone(hetzner_dns_token, domain)

def test_get_zone_working():
    zone.get_zone()
    assert zone != None
    assert zone.id != None

def test_get_zone_not_working():
    with pytest.raises(Exception):
        zone = DNS_Zone(hetzner_dns_token, "non-existent-domain.com")
        zone.get_zone()

def test_get_zonefile():
    test_zonefile = zone.get_zonefile()
    assert test_zonefile != None

def test_get_records():
    test_records = zone.get_records()
    assert test_records != None
    assert type(test_records) == list
    assert len(test_records) > 0
    assert record_type in test_records[0]["type"]
    assert test_records[0]["name"] != None
    

def test_get_recordByID():
    # This test gets the first record from the zone and then gets the record by ID
    zone_record = zone.get_records()[0]
    record_id = zone_record["id"]

record_type = "A"

def test_create_record():
    zone.create_record(random_string, record_type, random_ip, random_ttl)
    test_records = zone.get_records()
    for i in test_records:
        if i["name"] == random_string and i["type"] == record_type:
            assert i["name"] == random_string
            assert i["type"] == record_type
            assert i["value"] == random_ip
            assert i["ttl"] == random_ttl
    get = req.get(
        url=f"https://dns.hetzner.com/api/v1/records",
        headers={
            "Auth-API-Token": hetzner_dns_token,
        },
        params={
            "zone_id": zone.id
        }
    )

    for i in get.json()["records"]:
        if i["name"] == random_string and i["type"] == record_type:
            delete = req.delete(
                url=f"https://dns.hetzner.com/api/v1/records/{i['id']}",
                headers={
                    "Auth-API-Token": hetzner_dns_token,
                }
            )
            assert delete.status_code == 200
    
def test_delete_record():
    zone.create_record(random_string, record_type, random_ip, random_ttl)
    test_records = zone.get_records()
    
    for i in test_records:
        if i["name"] == random_string and i["type"] == record_type:
            zone.delete_record(i["id"])

def test_create_records():
    
    for i in record_types:
        zone.create_record(random_string, i, random_ip, random_ttl)
        test_records = zone.get_records()
        for j in test_records:
            if j["name"] == random_string and j["type"] == i:
                assert j["name"] == random_string
                assert j["type"] == i
                assert j["value"] == random_ip
                assert j["ttl"] == random_ttl

def test_delete_records():
    
    for i in record_types:
        zone.create_record(random_string, i, random_ip, random_ttl)
        test_records = zone.get_records()
        for j in test_records:
            if j["name"] == random_string and j["type"] == i:
                zone.delete_record(j["id"])
                test_records = zone.get_records()
                for k in test_records:
                    if k["name"] == random_string and k["type"] == i:
                        assert False

def test_create_record_with_existing_name():
    zone.create_record(random_string, record_type, random_ip, random_ttl)
    with pytest.raises(Exception):
        zone.create_record(random_string, record_type, random_ip, random_ttl)
    
record_id = zone.get_record_by_name_and_type(random_string, record_type)
zone.delete_record(record_id)

def test_create_record_with_existing_name_and_type():
    zone.create_record(random_string, record_type, random_ip, random_ttl)
    with pytest.raises(Exception()):
        zone.create_record(random_string, record_type, random_ip, random_ttl)



def test_update_record():
    record_id = zone.create_record(random_string, record_type, random_ip, random_ttl)["id"]
    
    new_random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    new_random_ip = f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
    new_random_ttl = random.randint(0, 10000)

    zone.update_record(record_id, new_random_string, record_type, new_random_ip, new_random_ttl)    
    test_record, void = zone.get_records()
   
    assert test_record != None
    assert type(test_record) == json
    assert len(test_record) > 0
    assert test_record["name"] == new_random_string
    assert test_record["type"] == record_type
    assert test_record["value"] == new_random_ip
    assert test_record["ttl"] == new_random_ttl