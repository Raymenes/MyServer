import urllib.request
import json

def get_info(address):
    api = "http://api.ipstack.com/" + address + "?access_key=6fecd9d8698c599eb609b75d96e85da0"
    try:
        print(api)
        result = urllib.request.urlopen(api).read()
        result = result.decode('utf8')
        result = json.loads(result)
    except Exception as e:
        print(str(e))
        return "ip info not found"
    return result

    print(adress)
    print("IP: ", result["ip"])
    print("Country Name: ", result["country_name"])
    print("Country Code: ", result["country_code"])
    print("Region Name: ", result["region_name"])
    print("Region Code: ", result["region_code"])
    print("City: ", result["city"])
    print("Zip Code: ", result["zip_code"])
    print("Latitude: ", result["latitude"])
    print("Longitude: ", result["longitude"])
    print("Location link: " + "http://www.openstreetmap.org/#map=11/" + str(result["latitude"]) +"/" + str(result["longitude"]))