# Import libraries
import requests
import json
import hashlib
import os
import re
from config import AW_KEY, AW_KEY_SAND

## ----------------------------------------------------------------------------
# PREP - URL AND TOKENS
## ----------------------------------------------------------------------------

## SANDBOX API URL & Token
sand_url   = "https://api.figsh.com/v2/" 
sand_token = AW_KEY_SAND

# 4TU API URL & Token
fig_url   = "https://api.figshare.com/v2/" 
fig_token = AW_KEY

## ----------------------------------------------------------------------------
# PREP - ADDITIONAL INFO - LICENCE AND CATEGORY IDs
# /licence and category IDs needed to update the metadata/
## ----------------------------------------------------------------------------

##-----------------------------------------------------------------------------
# LICENCES 
##-----------------------------------------------------------------------------

# SANDBOX 
response = requests.get(
    url = sand_url+"account/licenses", # public licences list
    #url = sand_url+"licenses", # private licences list
    headers = {
        "Authorization": f"token {sand_token}"
    })

sand_licences = response.json() # list of licences available together with thier IDs ( needed for metadata)
#sand_licences

# 4TU
response = requests.get(
    url = fig_url+"licenses" ,
    headers = {
        "Authorization": f"token {fig_token}"
    })

fig_licences = response.json() # list of licences available together with thier IDs ( needed for metadata)
#fig_licences



##-----------------------------------------------------------------------------
# CATEGORIES 
##-----------------------------------------------------------------------------

# SANDBOX
response = requests.get(
    url = sand_url+"account/categories",
    headers = {
        "Authorization": f"token {sand_token}"
    })

sand_cat = response.json()
#sand_cat

# 4TU
response = requests.get(
    url = fig_url+"account/categories",
    headers = {
        "Authorization": f"token {fig_token}"
    })

fig_cat = response.json()
sand_cat

## ----------------------------------------------------------------------------
# CREATE AN ARTICLE IN A 4TU
## ----------------------------------------------------------------------------

# Define metadata
art_title = 'GEF test 5'
art_license = 1
art_keywords = ['tag2', 'tag2', 'tag3']
art_description = 'description of my article'  
art_categories =  [ 13555, 13554 ] # Geophysics, Geodesy 
art_custom_fields = {"Organizations": "TU Delft - Delft University of Technology;\nTU Delft, Faculty of Civil Engineering and Geosciences",
                 "Time coverage": "2022-01-01",
                 "Geolocation"  : "Cabauw Experimental Site for Atmospheric Research (CESAR): Meteo mast",
                 "Geolocation Longitude": "4.926",
                 "Geolocation Latitude" : "51.97",
                 "Format"       : "media types: application/x-netcdf"}


# Send the POST response to create the article 
response = requests.post(
    url    = f"{fig_url}/account/articles",
    data   = json.dumps({  "title": art_title, 
                           "description": art_description,
                           "license": art_license,
                           "tags": art_keywords,
                           "custom_fields": art_custom_fields
                           ,"categories": art_categories    # <- this doesn't work either with strings, IDs as strings or numerics; tried also categories_by_source_id, and add them as dictionary 
                        }),
    headers = {
        "Authorization": f"token {fig_token}",
        "Accept":       "application/json", 
        "Content-Type": "application/json" 
    })

# Get the article URL
article_url = None
if response.status_code == 201:
    article_url = response.headers["Location"] # Location header from the response referes to the url  (including article_id); Other interesting headers fields : Date
else:
    print ("Couldn't create article.")


## ----------------------------------------------------------------------------
# CREATE AN ARTICLE IN A SANDBOX ENVIRONMENT
## ----------------------------------------------------------------------------

# Define metadata
art_title = 'GEF test 6'
art_license = 50
#art_license = [{"value": 50}]
art_keywords = ['tag2', 'tag2', 'tag3']
art_description = 'description of my article' 
art_categories =  [ 79, 23094] # Geophysics, Physical Geography and Environmental Geoscience  
#art_categories_str =  [ '26834', '26840'] # Geophysics, Geodesy 
art_custom_fields = {"Organizations": "TU Delft - Delft University of Technology;\nTU Delft, Faculty of Civil Engineering and Geosciences",
                 "Time coverage": "2022-01-01",
                 "Geolocation"  : "Cabauw Experimental Site for Atmospheric Research (CESAR): Meteo mast",
                 "Geolocation Longitude": "4.926",
                 "Geolocation Latitude" : "51.97",
                 "Format"       : "media types: application/x-netcdf"}
art_authors =  [
    {
      "name": 'Trinity'
    },
    {
      "name": 'Neo'
    },
    {
      "name": "John Doe"
    }
  ]


# Send the POST response to create the article 
response = requests.post(
    url    = f"{sand_url}/account/articles",
    data   = json.dumps({  "title": art_title, 
                           # "license": art_license, <- this notation results in a 404 response
                           "licence": art_license, # <- this notation results in 201 response, but licence is not altered on the website
                           "tags": art_keywords,
                           "description": art_description, 
                           "custom_fields": art_custom_fields
                           ,"categories": art_categories # <- this notation results in a 404 ( not found) response
                            #,"categories": art_categories_str # <- this notation results in a 400 (bad request) response 
                           ,"authors": art_authors
                        }),
    headers = {
        "Authorization": f"token {sand_token}",
        "Accept":       "application/json", 
        "Content-Type": "application/json" 
    })

# Get the article URL
article_url = None
if response.status_code == 201:
    article_url = response.headers["Location"] # Location header from the response referes to the url  (including article_id); Other interesting headers fields : Date
else:
    print ("Couldn't create article.")


 # Try to update licence as a separate step <- STILL NOTHING
# response = requests.put(
#    url = article_url,
#    data   = json.dumps({  "licence": art_license}),
#    headers = {
#        "Authorization": f"token {sand_token}",
#        "Accept":       "application/json", 
#        "Content-Type": "application/json" 
#    }
#)   

# Manually add the licence and check the api response body
# response = requests.get(
#    url = article_url,
#    headers = {"Authorization": f"token {sand_token}"}
# )
#
# article_data = response.json()
# license_id      = article_data["license"]
# license_id


## -----------------------------------------------------------------------------
# Reserve DOI
## -----------------------------------------------------------------------------

response = requests.post(
    url = f"{article_url}/reserve_doi",
    headers = {"Authorization": f"token {sand_token}"}
)

# response.status_code 

##-----------------------------------------------------------------------------
# UPLOAD DATASET
##-----------------------------------------------------------------------------

# Define data path 
file_path = 'LBBR_28-1.GEF'


## INITIATE UPLOAD / REGISTER A FILE
file_size    = os.path.getsize(file_path) # checks size of file
md5          = hashlib.md5() # define checksum method

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
        "Authorization": f"token {sand_token}",
        "Accept":       "application/json",
        "Content-Type": "application/json"
    })

file_url = None
if response.status_code == 201:
    file_url = response.headers["Location"]
else:
    print ("Couldn't create file.")

## GET UPLOAD METADATA

response = requests.get(
    url   = file_url,
    headers = {
        "Authorization": f"token {sand_token}",
        "Accept":       "application/json",
    })

file_data = response.json()
file_id      = file_data["id"]
upload_token = file_data["upload_token"]
upload_url   = file_data["upload_url"]

response = requests.get(
    url = upload_url,
    headers = {
        "Authorization": f"token {sand_token}",
        "Accept":       "application/json",
    })

#response.status_code

upload_metadata = response.json()

# UPLOAD PARTS

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
            "Authorization": f"token {sand_token}",
            "Accept":       "application/json",
        },
        data = chunk)

file_stream.close()


# CHECK NEW FILE STATUS

response = requests.get(
    url = upload_url,
    headers = {
        "Authorization": f"token {sand_token}",
        "Accept":       "application/json",
    })

response.status_code
upload_metadata = response.json()
upload_metadata

# FINALIZE UPLOAD

response = requests.post(
    url     = f"{article_url}/files/{file_id}",
    headers = {
        "Authorization": f"token {sand_token}",
        "Accept":       "application/json",
    })



##------------------------------------------
# PUBLISH ARTICLE
##------------------------------------------

##### NOTE #####################################
#
# When an article is published, a new public version will be generated.
# Any further updates to the article will affect the private article data.
# In order to make these changes publicly visible, an explicit publish operation is needed.
#
###############################################

response = requests.post(
    url = f"{article_url}/publish",
    headers = {"Authorization": f"token {sand_token}"}
)

##------------------------------------------
# ADD THE ARTICLE TO A  COLLECTION         <- Adapt private version ; publish - collecion iD stays the same, but the upload will create a new version
##------------------------------------------

# Input for the collection update
collection_id = 2977400 # <-test  collection in sandbox
article_id = [int(re.search('/([0-9]+)$', article_url).group(1))] # retrieve article id from URL
api_url = f"{sand_url}account/collections/{collection_id}/" # url to add article to a private collection


# ADD THE ARTICLE TO A PRIVATE COLLECTION
response = requests.post(
    url = f"{api_url}articles",
    data   = json.dumps({  "articles": article_id}),
    headers = {"Authorization": f"token {sand_token}",
               "Accept":       "application/json",
               "Content-Type": "application/json"}
)

# print('ADD article: ', response.status_code)
    
# PUBLISH THE COLLECTION 
response = requests.post(
    url = f"{api_url}publish",
    headers = {"Authorization": f"token {sand_token}"}
)

# print("Publish collection: ", response.status_code)
    
#response.status_code