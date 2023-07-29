import requests as req
import json
import pandas as pd

class DNS_Zone:
    errs = {
        404: "Record not found",
        403: "Forbidden",
        401: "Unauthorized",
        406: "Not acceptable"
    }

    """ A class to manage DNS Zones on Hetzner Cloud, given a token and a domain name. """
    def __init__(self, hcloud_dns_token, domain, synchronous=False):
        self.hcloud_dns_token = hcloud_dns_token
        self.domain = domain
        self.zone, self.id = self.get_zone()
        self.synchronous = synchronous
        # Get Records and Zonefile only if Zone exists
        # currently, this will fail if the zone doesn't exist yet
        if self.id is not None:
            self.zonefile = self.get_zonefile()
            self.records = self.get_records()
        else:
            raise Exception("Zone doesn't exist yet") # Later, this should create a new zone
        # TODO: Add ability to create a new DNS Zone if it doesn't exist yet

    def update(self):
        """ Update the zonefile and records. """
        self.records = self.get_records()    
    def get_zone(self) -> dict:
        """ Get a DNS Zone from Hetzner Cloud. """
        try:
            response = req.get(
                url="https://dns.hetzner.com/api/v1/zones",
                headers={
                    "Auth-API-Token": self.hcloud_dns_token
                }
            )
            
            if response.status_code != 200:
                raise Exception("HTTP Request failed with status code " + str(response.status_code))
            
            if "zones" not in response.json():
                raise Exception("No zones found")

            for i in response.json()["zones"]:
                zone = None # define zone as None, so that if the domain is not registered, it will return None
                if i["name"] == self.domain:
                    zone = i # Domain is registered, so zonefile exists
                
            if zone is None:
                return None, None
            return zone, zone["id"]
            

        except req.exceptions.RequestException as e:
            print("HTTP Request failed")
    def get_zonefile(self):
        """ Get a DNS Zone from Hetzner Cloud. """
        try:
            response = req.get(
                url=f"https://dns.hetzner.com/api/v1/zones/{self.id}/export",
                headers={
                    "Auth-API-Token": self.hcloud_dns_token,
                    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
                },
                data={}
            )
            zonefile = response.content.decode("utf-8")
            return zonefile

        except req.exceptions.RequestException as e:
            print("HTTP Request failed")
    def get_records(self):
        """ Get all records from a DNS Zone. """
        url_path = f"https://dns.hetzner.com/api/v1/records"
        try:
            response = req.get(
                url=url_path,
                headers={
                    "Auth-API-Token": self.hcloud_dns_token,
                }
            )
            if response.status_code in self.errs:
                raise Exception(self.errs[response.status_code])
            else:
                for i in response.json()["records"]:
                    return pd.DataFrame(response.json()["records"])
        except req.exceptions.RequestException as e:
            print("HTTP Request failed")
    def create_record(self, name, type, value, ttl=3600):
        """ Create a new record in a DNS Zone. """
        # check if record already exists
        if self.records.loc[(self.records["name"] == name) & (self.records["type"] == type)].empty == False:
            raise Exception("Record already exists")
        try:
            response = req.post(
                url=f"https://dns.hetzner.com/api/v1/records",
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Auth-API-Token": self.hcloud_dns_token,
                },
                data=json.dumps({
                    "value": value,
                    "ttl": ttl,
                    "type": type,
                    "name": name,
                    "zone_id": self.id
                })
            )
            if not self.synchronous:
                # create one row dataframe
                response_df = pd.DataFrame(response.json()["record"], index=[0])
                # append to self.records
                self.records = pd.concat([self.records, response_df])
                
            else:
                self.records = self.get_records()
            return response.json()

        except req.exceptions.RequestException as e:
            print("HTTP Request failed")
    def delete_record(self, record_id):
        try:
            response = req.delete(
                url=f"https://dns.hetzner.com/api/v1/records/{record_id}",
                headers={
                    "Auth-API-Token": self.hcloud_dns_token,
                }
            )
            if response.status_code in self.errs:
                raise Exception(self.errs[response.status_code])
            else:
                if self.synchronous:
                    self.records = self.get_zone()
                else:
                    self.records.drop(self.records.loc[self.records["id"] == record_id].index, inplace=True)
                return response.json()
        except req.exceptions.RequestException as e:
            print("HTTP Request failed")
        
    def get_recordByID(self, id):
        """ Get a record by ID. """
        if self.synchronous:
            self.records = self.get_zone()
        if self.records.loc[self.records["id"] == id].empty == False:
            return self.records.loc[self.records["id"] == id].iloc[0]
        else:
            return None
    def get_record_by_name_and_type(self, name, type):
        """ Get a record by name and type. """
        if self.synchronous:
            self.records = self.get_zone()
        
        if self.records.loc[(self.records["name"] == name) & (self.records["type"] == type)].empty == False:
            return self.records.loc[(self.records["name"] == name) & (self.records["type"] == type)].iloc[0]["id"]
        else:
            return None
    def update_record(self, id, name, type, value, ttl=3600):
        """ Update a record by ID. """
        if self.synchronous:
            self.records = self.get_zone()
        try:
            response = req.put(
                url=f"https://dns.hetzner.com/api/v1/records/{id}",
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Auth-API-Token": self.hcloud_dns_token,
                },
                data=json.dumps({
                    "value": value,
                    "ttl": ttl,
                    "type": type,
                    "name": name,
                    "zone_id": self.id
                })
            )
            # update record in self.records
            if not self.synchronous:
                response_df = pd.DataFrame(response.json())
                self.records.loc[self.records["id"] == id] = response_df
            return response.json()
        except req.exceptions.RequestException as e:
            print("HTTP Request failed")
