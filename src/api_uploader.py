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

def yes_no_input(user_input):
        # Clean input
    user_input_clean = re.sub("[^a-z]","",user_input.lower())
    
    # Allow only y/yes n/no 
    assert user_input_clean in ['y', 'yes', 'n', 'no'] ,'I did not understand your selection. Please try again.'
    return(user_input_clean[0])

# Give user choice to choose between the sandbox and 4TU
def choose_entry_mode():
    '''
    Function allows the user to choose between the Sandbox and main 4TU environment 
    
    '''
    sbox_choice = input("Do you want to continue in the Sandbox environment? [Y/N]:") 
    # Clean input
    sbox_choice_clean = yes_no_input(sbox_choice)
    
    if sbox_choice_clean == 'y':
        env_choice = "sandbox" 
        print('Sandbox environment chosen')
    else: 
        env_choice = "4TU"
        print('Production environment chosen')

    
    return(env_choice)

# Get the right URL
def get_url(env_choice):
    '''
    The function returns the API URL depending on which environment the user chose to upload the files 
    
    Parameters
    ----------
    env_choice : str
        The environment the programme is to interact with ('4TU' or 'sandbox')
        '''

    assert env_choice in {'4TU' , 'sandbox'}, 'No valid environment chosen.'

    # Get the right API depending on the environment ( 4TU, Sandbox)
    if env_choice == 'sandbox':
        api_url = "https://api.figsh.com/v2/" 
    else: 
        api_url = "https://api.figshare.com/v2/"

    # Return the right api
    return(api_url)
    
# Request the personal token of the user 
def get_token(env_choice):
    '''
    The function requests the personal token from the user 
    
    Parameters
    ----------
    env_choice : str
        The environment the programme is to interact with ('4TU' or 'sandbox')
        '''

    assert env_choice in {'4TU' , 'sandbox'}, 'No valid environment chosen.'

    api_token = input("Provide your presonal token for the" + env_choice + " environment")
    
    # Return the right api
    return(api_token)

# Function to get a list of licences available at 4TU 
def get_licences(api_url, api_token ):
    '''
    Function retrieves the list of licences available in the repository depending on the environment chosen
    
    Parameters
    ----------
    api_url : str
        The URL, depending on the choice of the environment
    api_token : str
        The personal token of the user    
    ''' 
    response = requests.get(
        url = api_url+"account/licenses", # private licences list
        headers = {"Authorization": f"token {api_token}"}
        )
    
    # Retrun list of licences available together with thier IDs ( needed for metadata)   
    return(response.json() )

# Function to get a list of licences available at 4TU 
def get_categories(api_url, api_token ):
    '''
    Function retrieves the list of categories available in the repository depending on the environment chosen
    
    Parameters
    ----------
    api_url : str
        The URL, depending on the choice of the environment
    api_token : str
        The personal token of the user    
    ''' 
    response = requests.get(
        url = api_url+"account/categories",
        headers = {"Authorization": f"token {api_token}"}
        )

    # Retrun list of licences available together with thier IDs ( needed for metadata)   
    return( response.json() )

def get_collection_type():
    '''
    Function requests the user to provide input regarding the collection he wants to upload the data to,
    asserts the selected choice and retruns the selection in form of a string 
    
    '''
    col_choices = ['grout', 'XXX', 'YYY', 'ZZZ']
    input_string = ''
    
    for i, var in enumerate(col_choices):
         input_string += '\n'+ str(i) + '-' + var  
    
    input_string = "Which collection would you upload the datasets to?" + input_string + '\n'
    coll_type = input(input_string)
    
    coll_type_clean = int(re.sub("[^0-9]","",coll_type )) #  clean from unwanted characters
    
    assert coll_type_clean in list(range(0, len(col_choices) )), 'Wrong selection. Try again.'
    
    collection_chosen = col_choices[coll_type_clean]

    return(collection_chosen)

def request_authors():
    ''' 
    Requests information about additional authors 

    Returns
    -----------
        art_authors: list
            list of dictionaries with authors' names
    
    '''
    # Intro 
    print("You're a few steps away from publishing your dataset. Before that, you need to provide some additional information about your dataset....")

    # Verify if there are additional authors 
    add_authors =input("Does this dataset have any additional authors, apart from you (Y/N)?" )
 
    # Clean input
    add_authors_clean = yes_no_input(add_authors)

    # If additional authors - ask for input and write as a list of dictionaries
    art_authors = []

    if add_authors_clean == 'y':
        authors_input = input("Provide author names, separated by a coma") 
        authors_input_list = authors_input.split(sep = ',')
        authors_input_list_clean = list(map(str.strip, authors_input_list))
        for author in authors_input_list_clean:
            info = {"name": author }
        art_authors.append(info)
    else:
        print("Understood, no additional authors.")
    
    return(art_authors)

def retrieve_metadata(file):
    ''' Retrieves metadata fields used in 4TU upload from the .GEF file

    Parameteres
    --------
    gef_file: str
        Name of the GEF file used for metadata extraction 

    Returns
    --------
    retrieved_dict: list 
        Metadata fields retrieved from a gef file: description
    '''

# - all metadata pulled from the .GEF file), LOCATIONAME
#    geo_long : float 
#        Geographic longitude in decimal degrees; East is positive, West is negative; Values: -180 to 180 (LOCATION X)
#    geo_lat : float
#            Geographic longitude in decimal degrees; North is positive, South is negative; Values: -90 to 90 (LOCATION Y)
#    dataset_date : date
#        Data gathering date as indicated in the .GEF file  (STARTDATE)
#    org: str
#        Organisation contributing to the collection  (COMPANYID)
#    anchortype: str
#        self-drilling, stranded or screw injection (ANCHORTYPE)
#    testtype: str
#        investigation, suitability or acceptance (TESTTYPE)
#    locationz : float
#        The depth of drilling? (LOCATIONZ)
        
    #set up empty variables
    art_title = ''
    art_description = ''
    art_keywords = []
    art_date = ''
    art_location = ''
    geo_lon = ''
    geo_lat = ''
    company = ''

    # create patterns to search text
    title = re.compile(r'#PROJECT')
    keywords = re.compile(r'TESTTYPE= |ANCHORTYPE= |LOCATIONZ= ')
    date = re.compile(r'#STARTDATE=')
    location = re.compile(r'#LOCATIONAME= ')
    lon = re.compile(r'#LOCATIONY= ')
    lat = re.compile(r'#LOCATIONX= ')
    companyid = re.compile(r'#COMPANYID= ')

    #save metadata as description
    with open (file, 'rt') as myfile:
        art_description = myfile.read().split('#EOH=',1)[0]

    # save metadata values as variables
    with open (file, 'rt') as myfile:
        for line in myfile:
            if keywords.search(line) != None:
                string = re.sub(r" ", "", line)
                art_keywords.append(string.rstrip('\n').replace('#',""))
            if title.search(line) != None:
                art_title = line.rstrip('\n').replace('#PROJECT= ',"")
            if date.search(line) != None:
                dstring = re.sub(r", ", "-", line)
                art_date = dstring.rstrip('\n').replace('#STARTDATE= ',"")
            if location.search(line) != None:
                art_location = line.rstrip('\n').replace('#LOCATIONAME= ',"")
            if lon.search(line) != None:
                geo_lon = line.rstrip('\n').replace('#LOCATIONY= ',"")
            if lat.search(line) != None:
                geo_lat = line.rstrip('\n').replace('#LOCATIONX= ',"")
            if companyid.search(line) != None:
                company = line.rstrip('\n').replace('#COMPANYID= ',"")
    
    retrieved_meta = [art_title, art_description, art_keywords, art_date, art_location,geo_lon, geo_lat,  company ]
    meta_names= ['title', 'description' , 'keywords' , 'date'  , 'location' , 'geo_lon' , 'geo_lat' , 'company' ]

    retrieved_dict = dict(zip(meta_names, retrieved_meta))

    return(retrieved_dict)

def compile_metadata(collection_chosen, retrieved_dict, add_authors, env_choice):
   ''' Function gathers the needed metadata ( not retrieved from GEF file ) and returns a json file needed for the POST request
  
   Parameters
    ----------
    collection_chosen : str
        The chosen collection (e.g. 'grout')
    retrieved_dict : dict
        Metadata retrieved from the GEF file
    add_authors : list
        list of additional authors
    env_choice : str
        Either sandbox or production ('4TU')    
    

  Returns: 
   ----------
    article_metadata: dict
        Dictionary with full metadata 

   ''' 
   # Define metadata
   

   # 1. Title for the moment as an inputation - can be retrieved from the GEF file directly
   art_title = retrieved_dict['title']  #input('\nDataset title:')
   # 2. Licence
   art_license = 50 # verify if can be hardcoded (per collection?)

   # the spelling of the license endpoint differs between the sandbox and production: 
   if env_choice == 'sandbox':
       lic_endpoint = 'licence'
   else: 
       lic_endpoint = 'license'
        

   # 4. Key words
   art_keywords = [ collection_chosen , retrieved_dict['keywords']  ]

   # 5. Formats
   coll_data_formats = {'grout':'GEF', 'XXX': 'foo', 'YYY': 'bar', 'ZZZ': 'baz'} 
   art_format = coll_data_formats[collection_chosen] # data format depending on the chosen collection

   art_description = retrieved_dict['description']  
   art_categories =  [ 13555, 13554 ] # Geophysics, Geodesy 
   
   art_org = "TU Delft - Delft University of Technology;\nTU Delft, Faculty of Civil Engineering and Geosciences;\n" + retrieved_dict['company']

   art_custom_fields = {"Organizations": art_org,
                 "Time coverage": retrieved_dict['date'] ,
                 "Geolocation"  : retrieved_dict['location'] ,
                 "Geolocation Longitude": retrieved_dict['geo_lon'],
                 "Geolocation Latitude" : retrieved_dict['geo_lat'],
                 "Format": "media types: application/"+ art_format
                 }
    # Dictionary with the full list of the metadata fields to be uploaded together with the article 
   article_metadata = {"title": art_title, 
                 lic_endpoint: art_license, # <- this notation results in 201 response, but licence is not altered on the website
                 "tags": art_keywords,
                 "description": art_description, 
                 "custom_fields": art_custom_fields,
                 "categories": art_categories, # <- this notation results in a 404 ( not found) response,
                 "authors": art_authors
                }
   
   return(article_metadata)
                 

def create_article(api_url, metadata_dict, api_token):
    ''' Sends the POST response to create the article
    Parameters 
    ---------
    api_url: str
        API URL
    metadata_dict:
        dictionary with all the metadata fields
    api_token:
        Personal token to access API

    Returns 
    -----------
    article_url: str
        URL of the newly created article    
     '''
    response = requests.post(
        url    = f"{api_token}/account/articles",
        data   = json.dumps({ metadata_dict }),
        headers = {
        "Authorization": f"token {api_token}",
        "Accept":       "application/json", 
        "Content-Type": "application/json" 
        })
        
        # Get the article URL
    article_url = None
    
    if response.status_code == 201: 
         article_url = response.headers["Location"]
    else:
        print ("Couldn't create article.")

    return(article_url)

## -----------------------------------------------------------------------------
# Reserve DOI
## -----------------------------------------------------------------------------
def reserve_doi(article_url, api_token):
    response = requests.post(
        url = f"{article_url}/reserve_doi",
        headers = {"Authorization": f"token {api_token}"}
        )
    
    article_doi = None
    if response.status_code == 200: 
         article_doi = response.json()['doi']
    else:
        print ("Couldn't reserve DOI.") 

    return(article_doi)


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