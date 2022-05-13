import requests
import json
import hashlib
import os

## ----------------------------------------------------------------------------
## CONFIGURE SOME SETTINGS
## ----------------------------------------------------------------------------

## Use the 4TU sandbox for this demo => https://sandbox.data.4tu.nl
figshare_url   = "https://api.figsh.com/v2"
figshare_token = "08e4ef797a2c88316057b490e0595e07cef536a9ec8fb25b2df780420e1a5337464b0dcdc7fffd9e8dc6d16f845486e77cac09f88e56715b0552d086d084d7fc"
file_path      = "U:\DMDCC\Geodata\figshare-api-examples"

## ----------------------------------------------------------------------------
## CREATE AN ARTICLE
## ----------------------------------------------------------------------------

response = requests.post(
    url    = f"{figshare_url}/account/articles",
    data   = json.dumps({ "title": "GEF test" }),
    headers = {
        "Authorization": f"token {figshare_token}",
        "Accept":       "application/json",
        "Content-Type": "application/json"
    })

article_url = None
if response.status_code == 201:
    article_url = response.headers["Location"]
else:
    print ("Couldn't create article.")

## ----------------------------------------------------------------------------
## INITIATE UPLOAD / REGISTER A FILE
## ----------------------------------------------------------------------------

file_size    = os.path.getsize(file_path)
md5          = hashlib.md5()

computed_md5 = None
with open (file_path, "rb") as stream:
    for chunk in iter(lambda: stream.read(4096), b""):
        md5.update(chunk)
        computed_md5 = md5.hexdigest()

response     = requests.post(
    url     = f"{article_url}/files",
    data    = json.dumps({
        "name": "LBR_28-1",
        "md5":  computed_md5,
        "size": file_size
    }),
    headers = {
        "Authorization": f"token {figshare_token}",
        "Accept":       "application/json",
        "Content-Type": "application/json"
    })

file_url = None
if response.status_code == 201:
    file_url = response.headers["Location"]
else:
    print ("Couldn't create file.")

file_url

## ----------------------------------------------------------------------------
## GET UPLOAD METADATA
## ----------------------------------------------------------------------------

response = requests.get(
    url   = file_url,
    headers = {
        "Authorization": f"token {figshare_token}",
        "Accept":       "application/json",
    })

response.status_code
file_data = response.json()
file_id      = file_data["id"]
upload_token = file_data["upload_token"]
upload_url   = file_data["upload_url"]

response = requests.get(
    url = upload_url,
    headers = {
        "Authorization": f"token {figshare_token}",
        "Accept":       "application/json",
    })

response.status_code
upload_metadata = response.json()

## ----------------------------------------------------------------------------
## UPLOAD PARTS
## ----------------------------------------------------------------------------

parts_metadata = upload_metadata["parts"]
file_stream    = open(file_path, "rb")

for part in parts_metadata:
    part_number     = part["partNo"]
    start_position  = part['startOffset']
    end_position    = part['endOffset']
    number_of_bytes = end_position - start_position + 1
    print(f"Uploading part {part_number} ({number_of_bytes} bytes).")
    file_stream.seek(start_position)
    chunk    = file_stream.read(number_of_bytes)
    response = requests.put(
        url = f"{upload_url}/{part_number}",
        headers = {
            "Authorization": f"token {figshare_token}",
            "Accept":       "application/json",
        },
        data = chunk)

file_stream.close()

## ----------------------------------------------------------------------------
## CHECK NEW FILE STATUS
## ----------------------------------------------------------------------------

response = requests.get(
    url = upload_url,
    headers = {
        "Authorization": f"token {figshare_token}",
        "Accept":       "application/json",
    })

response.status_code
upload_metadata = response.json()
upload_metadata

## ----------------------------------------------------------------------------
## FINALIZE UPLOAD
## ----------------------------------------------------------------------------

response = requests.post(
    url     = f"{article_url}/files/{file_id}",
    headers = {
        "Authorization": f"token {figshare_token}",
        "Accept":       "application/json",
    })

response.status_code
