from turtle import shape
import requests
import json
import hashlib
import os
import re
import sys
import pandas as pd
import time
from operator import itemgetter
#from config import AW_KEY, AW_KEY_SAND
from gefreader import Gef2OpenClass, is_number


# ToDo 05/09: 
# - create filters for the download - update filters based on dataframe content
# - switch on download functionality
# - document all the things that are hardcoded / need to be adapted : collection names; collection IDs; categories;  <- or moved to the config file
# - Suggest adapting GEF files: add authors
# - Document how to launch (conda env, shiny run etc.)
# - Start working on a map
# if

# Auxiliary functions
def yes_no_input(user_input):
    '''
    Function that cleans out the Yes/No input and asserts that it is inserted correctly
   
    Parameters
    -----------
    user_input : str
        String provided by the user as an answer to a Yes or No question

    Returns
    ------------
    user_input_clean: str
        Returns a cleaned, lower-case version of the user input
    '''

        # Clean input
    user_input_clean = re.sub("[^a-z]","",user_input.lower())
    
    # Allow only y/yes n/no 
    assert user_input_clean in ['y', 'yes', 'n', 'no'] ,'I did not understand your selection. Please try again.'
    return(user_input_clean[0])

def choose_one_option(choice_list):
    '''
    Function allows the user to choose one action from the provided list

    Paramters
    ----------
    choice_list: list
        List of choices to present to a user
    Returns
    ----------
    action_chosen: str
        The action the user wants to perform within the program

    '''

    input_string = ''
    for i, var in enumerate(choice_list):
        input_string += '\n'+ str(i) + '-' + var  
    input_string = 'Choose one option [Type in option number] \n' + input_string + '\n'
    choosen_action = input(input_string)
    choosen_action_clean = int(re.sub("[^0-9]","", choosen_action.lower() )) #  clean from unwanted characters
    
    assert  choosen_action_clean in list(range(0, len(choice_list) )), 'Wrong selection.'
    
    action_chosen = choice_list[choosen_action_clean]

    return(action_chosen)

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
    Function requests the user to provide input regarding the collection he wants to upload the data to or retrieve data from,
    asserts the selected choice and retruns the selection in form of a string 
    
    '''
    col_choices = ['grout', 'xxx', 'yyy', 'zzz']
    input_string = ''
    
    for i, var in enumerate(col_choices):
         input_string += '\n'+ str(i) + '-' + var  
    
    input_string = "Which collection are you interested in?" + input_string + '\n'
    coll_type = input(input_string)
    
    coll_type_clean = int(re.sub("[^0-9]","", coll_type.lower() )) #  clean from unwanted characters
    
    assert coll_type_clean in list(range(0, len(col_choices)-1 )), 'Wrong selection.'
    
    collection_chosen = col_choices[coll_type_clean]

    return(collection_chosen)

def get_file_format(collection_chosen):
    '''
    Returns the file format, depending on the collection chosen

    Parameters
    -----------
    collection_chosen : str
        The chosen collection (e.g. 'grout')

    Returns
    ------------
    file_format: str
        The file format depending on a collection chosen
    '''

    coll_data_formats = {'grout':'GEF', 'xxx': 'foo', 'yyy': 'bar', 'zzz': 'baz'} 
    file_format = coll_data_formats[collection_chosen] # data format depending on the chosen collection

    return(file_format)  
   
def choose_multiple(choice_list):
    input_string = ''
    n_choice = len(choice_list)
    #which_chosen = [0] * n_choice

    for i, var in enumerate(choice_list):
        input_string += '\n'+ str(i) + '-' + var  
         
    input_string = "Which option you want to choose? \nType in corresponding numbers, separated by coma:" + input_string + '\n'

    which_choice = input( input_string ) 
    which_choice_clean = re.findall(r'\b\d{1,3}(?:,\d{3})*(?!\d)', which_choice) # Source: https://stackoverflow.com/questions/63714217/how-can-i-extract-numbers-containing-commas-from-strings-in-python
    which_choice_clean = [int(y) for y in which_choice_clean if int(y) <= n_choice-1 ]
    if which_choice_clean == []:
        chosen_list = which_choice_clean
    else:
        chosen_list = list(itemgetter(*which_choice_clean)(choice_list))

    return(chosen_list)


# Overarching functions 
def choose_entry_mode(sbox_choice):
    '''
    Function allows the user to choose between the Sandbox and main 4TU environment 
    
    '''
    #sbox_choice = input("Do you want to continue in the Sandbox environment? [Y/N]:") 
    # Clean input
    sbox_choice_clean = yes_no_input(sbox_choice)
    
    if sbox_choice_clean == 'y':
        env_choice = "sandbox" 
        print('Sandbox environment chosen')
    else: 
        env_choice = "4TU"
        print('Production environment chosen')

    return(env_choice)

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
    
def get_token(env_choice):
    '''
    The function requests the personal token from the user 
    
    Parameters
    ----------
    env_choice : str
        The environment the programme is to interact with ('4TU' or 'sandbox')
        '''

    assert env_choice in {'4TU' , 'sandbox'}, 'No valid environment chosen.'

    api_token = input("Provide your presonal token for the " + env_choice + " environment: ")
    
    # Return the right api
  
    return(api_token)

# Functions to upload files
def get_file_path(collection_chosen):
    '''
    Requests information about file_path where the datasets are placed and checks if the path exists and holds the file formats adequate for the collection chosen 

   Parameters
    -----------
    collection_chosen : str
        The chosen collection (e.g. 'grout')

    Returns
    ------------
    file_path: list
        The list of files (together with path) chosen by the user and to be uploaded

    '''
    file_path = input("Please provide the path to the files: ")
    coll_format = get_file_format(collection_chosen)

    #file_list =  []
    #If the path provided is a single file 
    if os.path.isfile(file):       
                # If it 
                if file_path.endswith(coll_format):
                        # Retrieve the file_name of the path
                        file_name = os.path.basename(file_path)
                        file_list = [file_path]
                else: 
                    sys.exit("The format of the file: " + os.path.splitext(file_path)[1] +" does not match the selected collection format: "+ coll_format)
    else:
        assert os.path.isdir(file_path) , "Invalid directory"
    
        for file in os.listdir(file_path):
            if file.endswith(coll_format):
                file_list.append( os.path.join(file_path, file))

    assert len(file_list)>0 , "No files in the directory match the selected collection format: "+ coll_format

    input_string = ''
    for file in file_list:
        input_string += '\n'+  '- ' + os.path.basename(file)  

    print('The files selected in upload: ' + input_string + '\n')

    return(file_list)

def request_authors(file_list):
    ''' 
    Requests information about additional authors 
    Parameters
    -----------
        file_list: list 
            list of files to be uploaded to the repository
    Returns
    -----------
        art_authors: list
            list of dictionaries with authors' names
    
    '''
    authors_list = []
    for i, file in enumerate(file_list):
        file_name = os.path.basename(file)
        # Verify if there are additional authors 
        add_authors =input("Does the dataset " + file_name + " have any additional authors, apart from you [Y/N]?" )
        # Clean input
        add_authors_clean = yes_no_input(add_authors)
        # If additional authors - ask for input and write as a list of dictionaries
        art_authors = []
        if add_authors_clean == 'y':
            authors_input = input("Provide author names, separated by a coma: ") 
            authors_input_list = authors_input.split(sep = ',')
            authors_input_list_clean = list(map(str.strip, authors_input_list))
            for author in authors_input_list_clean:
                info = {"name": author }
                art_authors.append(info)
        else:
            print("Understood, no additional authors.")
        
        authors_list.append(art_authors)
        
    return(authors_list)

def retrieve_metadata(file):
    ''' Retrieves metadata fields used in 4TU upload from the .GEF file

    Parameteres
    --------
    gef_file: str
        Name of the GEF file used for metadata extraction 

    Returns
    --------
    retrieved_dict: dict 
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
    keywords = re.compile(r'TESTTYPE= |ANCHORTYPE= |LOCATIONNAME= |LOCATIONX= |LOCATIONY= |LOCATIONZ= ')
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
    
    # Figshare API doesn't accept long lon/lat numbers
    geo_lat = str(round(float(geo_lat), 4))
    geo_lon = str(round(float(geo_lon), 4))


    retrieved_fields = [art_title, art_description, art_keywords, art_date, art_location,geo_lon, geo_lat,  company ]
    meta_names= ['title', 'description' , 'keywords' , 'date'  , 'location' , 'geo_lon' , 'geo_lat' , 'company' ]

    retrieved_dict = dict(zip(meta_names, retrieved_fields))
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
   if env_choice == 'sandbox':
       art_license = 50
   else: 
       art_license = 1
        
    # verify if can be hardcoded (per collection?)

   # the spelling of the license endpoint differs between the sandbox and production: 
   if env_choice == 'sandbox':
       lic_endpoint = 'licence'
   else: 
       lic_endpoint = 'license'
        

   # 4. Key words
   retrieved_dict['keywords'].append('collection-'+collection_chosen)
   art_keywords = retrieved_dict['keywords']
   # 5. Formats
   art_format = get_file_format(collection_chosen) # data format depending on the chosen collection

   art_description = retrieved_dict['description']  

   if env_choice == 'sandbox':
       art_categories =  [79, 23094] # Geophysics, Geodesy 
   else: 
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
                 "authors": add_authors
                }
   return(article_metadata)
              
def create_article(api_url, metadata_dict, api_token):
    ''' Sends the POST request to create the article
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
        url    = f"{api_url}/account/articles",
        data   = json.dumps(metadata_dict) ,
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

def reserve_doi(article_url, api_token):
    ''' Sends the POST request to reserve a DOI for the article
    Parameters 
    ---------
    article_url: str
        URL of the article 
    api_token:
        Personal token to access API

    Returns 
    -----------
    article_doi: str
        DOI reserved for the article    
     '''
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

def upload_dataset(article_url, api_token, file_path, file_name):
    '''
    Uploads file to a selected article

    Parameters
    ----------
    article_url: str
        URL of the article 
    api_token: str
        Personal token to access API
    file_path: str
        Name of the file to be uploaded to the article    
    ''' 
    # Make sure that file exists 
    assert os.path.isfile(file_path), "Cannot access the file. Please verify the given path or try reconnecting to the drive"
    
    # # Retrieve the file_name of the path
    # file_name = os.path.basename(file_path)

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
                    "name": file_name,
                    "md5":  computed_md5,
                    "size": file_size
                    }),
                headers = {
                    "Authorization": f"token {api_token}",
                    "Accept":       "application/json",
                    "Content-Type": "application/json"
                    })
                    
    
    file_url = None
    if response.status_code == 201:
        file_url = response.headers["Location"]
    else:
        sys.exit("Couldn't create file.")

## GET UPLOAD METADATA
    response = requests.get(
        url   = file_url,
        headers = {
            "Authorization": f"token {api_token}",
            "Accept":       "application/json",
        })

    file_data = response.json()
    file_id      = file_data["id"]
    upload_token = file_data["upload_token"]
    upload_url   = file_data["upload_url"]

    response = requests.get(
        url = upload_url,
        headers = {
            "Authorization": f"token {api_token}",
            "Accept":       "application/json",
        })
        
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
                "Authorization": f"token {api_token}",
                "Accept":       "application/json",
            },
            data = chunk)

    file_stream.close()


# CHECK NEW FILE STATUS
    response = requests.get(
        url = upload_url,
        headers = {
            "Authorization": f"token {api_token}",
            "Accept":       "application/json",
            })
    upload_metadata = response.json()

# FINALIZE UPLOAD
    response = requests.post(
        url     = f"{article_url}/files/{file_id}",
        headers = {
            "Authorization": f"token {api_token}",
            "Accept":       "application/json",
        })

            
    if response.status_code == 202 :
        return(f"Upload of file {file_name} complete")
    else:
        return(f"Couldn't upload file {file_name}")

def publish_article(article_url, api_token):
    '''
    Requests the article to be published

    NOTE 
    When an article is published, a new public version will be generated.
    Any further updates to the article will affect the private article data.
    In order to make these changes publicly visible, an explicit publish operation is needed.

    Parameters
    ----------
    article_url: str
        URL of the article 
    api_token: str
        Personal token to access API    
    ''' 
    
    response = requests.post(
        url = f"{article_url}/publish",
        headers = {"Authorization": f"token {api_token}"}
        )

    if response.status_code == 201: 
         return("Publishing request sent successfully.") 
    else:
        return("Couldn't publish the article.") 

def add_to_collection( collection_chosen, article_url, api_token, env_choice):
    '''
    Requests the article to be added to a collection

    NOTE 
    Whenever a collection is altered, it needs to be republished for the changes to be seen publicly.  

    NOTE 
    The collection IDs are hardcoded - need to ba altered when a collection is created

    Parameters
    ----------
    collection_chosen: str
        Collection the aticle should be added to
    article_url: str
        URL of the article 
    api_token: str
        Personal token to access API 

    Returns
    ---------
    colection_url: str
        URL of the collection the article is published to    
    ''' 
  
    # Input for the collection update
    if env_choice == 'sandbox':
       collection_IDs = {'grout':2977400, 'xxx': 0, 'yyy': 0, 'zzz': 0} # 2977400 is awilczynski's test  collection in sandbox
    else: 
       collection_IDs = {'grout':6036302, 'xxx': 0, 'yyy': 0, 'zzz': 0}
    
    
    collection_id = collection_IDs[collection_chosen] # data format depending on the chosen collection
    
    # Retrieve article ID and api_url from the article_url
    searches = re.search('(.*)(articles/)([0-9]+)$', article_url)
    article_id = [int(searches.group(3))]
    api_url = searches.group(1)

    collection_url = f"{api_url}collections/{collection_id}/" 


    # ADD THE ARTICLE TO A PRIVATE COLLECTION
    response = requests.post(
        url = f"{collection_url}articles",
        data   = json.dumps({  "articles": article_id}),
        headers = {"Authorization": f"token {api_token}",
                    "Accept":       "application/json",
                    "Content-Type": "application/json"
                    })


    if response.status_code == 201: 
         print ("Article added to the "+ collection_chosen + " collection.") 
         return(collection_url)
    else:
        print ("Couldn't add the article to the collection.") 

def publish_collection( collection_url, api_token):
    '''
    Requests the collection to be (re)published

    NOTE 
    Whenever a new article/dataset is added to a collection it needs to be republished. This creates a new version of the public collection and DOI, e.g.:
        - https://doi.org/10.5074/c.2977400.v1
        - https://doi.org/10.5074/c.2977400.v2
        - https://doi.org/10.5074/c.2977400

    The latest version of the collection has not .vX appendix    

    Parameters
    ----------
    article_url: str
        URL of the article 
    api_token: str
        Personal token to access API    
    ''' 
    response = requests.post(
        url = f"{collection_url}publish",
        headers = {"Authorization": f"token {api_token}"}
        )

    if response.status_code == 201: 
         print ("Publishing request sent successfully.") 
         return(collection_url)
    else:
        print ("Couldn't publish the collection.") 

def test_gef_anchor(GEF_file):
    ''' Tests if GEF type is correct

    Parameters
    ----------
    GEF_file: str
        Path to the file 
    
    '''
    myGef = Gef2OpenClass()
    myGef.read_gef(GEF_file)
    if myGef.test_gef():
        print('Datafile adheres to {} convention'.format(myGef.headerdict['REPORTCODE'][0]))

    assert 'LOCATIONAME' in myGef.headerdict , 'File ' + os.path.basename(GEF_file) + ': field LOCATIONAME missing'
    assert 'LOCATIONX'   in myGef.headerdict , 'File ' + os.path.basename(GEF_file) + ': field LOCATIONX missing'
    assert 'LOCATIONY'   in myGef.headerdict , 'File ' + os.path.basename(GEF_file) + ': field LOCATIONY missing'
    assert 'LOCATIONZ'   in myGef.headerdict , 'File ' + os.path.basename(GEF_file) + ': field LOCATIONZ missing'
    assert 'TESTTYPE'    in myGef.headerdict , 'File ' + os.path.basename(GEF_file) + ': field TESTTYPE missing'
    assert 'STARTDATE'   in myGef.headerdict , 'File ' + os.path.basename(GEF_file) + ': field STARTDATE missing'
    assert 'ANCHORTYPE'  in myGef.headerdict , 'File ' + os.path.basename(GEF_file) + ': field ANCHORTYPE missing'

    assert re.search('[a-zA-Z]+',  myGef.headerdict['LOCATIONAME'][0] ), 'File ' + os.path.basename(GEF_file) + ': field LOCATIONAME cannot be empty'
    assert is_number(myGef.headerdict['LOCATIONX'][0]),   'File ' + os.path.basename(GEF_file) + ': field LOCATIONX should be a number'
    assert myGef.headerdict['LOCATIONX'][0]>=-180 and myGef.headerdict['LOCATIONX'][0]<=180,   'File ' + os.path.basename(GEF_file) + ': field LOCATIONX should be within a range of -180 to 180'
    assert is_number(myGef.headerdict['LOCATIONY'][0]),   'File ' + os.path.basename(GEF_file) + ': field LOCATIONY should be a number'
    assert myGef.headerdict['LOCATIONY'][0]>=-90 and myGef.headerdict['LOCATIONY'][0]<=90,   'File ' + os.path.basename(GEF_file) + ': field LOCATIONY should be within a range of -90 to 90'
    assert is_number(myGef.headerdict['LOCATIONZ'][0]),   'File ' + os.path.basename(GEF_file) + ': field LOCATIONZ should be a number'
    assert re.search('investigation|suitability|acceptance',  myGef.headerdict['TESTTYPE'][0] ), 'File ' + os.path.basename(GEF_file) + ': field TESTTYPE should have one of the following values: \n - investigation\n - suitability\n - acceptance'
    assert re.search('self-drilling|stranded|screw injection',  myGef.headerdict['ANCHORTYPE'][0] ), 'File ' + os.path.basename(GEF_file) + ': field ANCHORTYPE should have one of the following values: \n - self-drilling\n - stranded\n - screw injection'

# Functions to browse and retrieve files
def browse_collection(collection_chosen, api_url, api_token):
    '''
    Provides a dataframe of articles available in the collection chosen by the user

    Parameters
    ----------
    collection_chosen: str
        Collection the aticle should be added to
    article_url: str
        URL of the article 
    api_token: str
        Personal token to access API 

    Returns
    ---------
    article_ids: list
        List of article IDs in the collection        
    '''
    
    # Keyword identifying collection
    coll_keyword = '\"collection-' + collection_chosen + '\"'

    params={
    "search_for":":keyword: " + coll_keyword,
    #"institution": 898, #unique 4tu code  <- only production env. need to adapt so that the sandbox included too 
    "item_type": 3, #item type is dataset
    "page": 1,
    "page_size": 1000 #adjust to number larger than anticipated search results

    }
    
    #request articles based on search parameters set above
    response = requests.post(
        url = f"{api_url}/articles/search",
        json = params,
        headers = {"Authorization": f"token {api_token}"} 
    )
    

    if response.status_code == 200 and response.json() != [] : 
         print ("Collection articles retrieved. \n.") 
         articles = response.json()
         collection_articles = pd.DataFrame.from_dict(articles)[['id', 'title', 'doi', 'published_date', 'defined_type_name', 'resource_doi']]
         article_ids = collection_articles['id'].tolist()
         return(article_ids) 
    
    elif response.status_code == 200 and response.json() == []:
        print ("No collection items found.") 

    else :
        print ("Couldn't retrieve the collection.")     

def get_article_details(article_ids,api_url, api_token ):
    '''
    Provides details of articles from a collection

    Parameters
    ----------
    article_ids: list
        List of article IDs 
    api_url: str
        Figshare API URL  
    api_token: str
        Personal token to access API  
    Returns
    ---------
    articles: pandas.DataFrame
        A DataFrame holding details on articles of the collection 
    '''
    art = []
    for art_id in article_ids:
        response = requests.get(
            url = f"{api_url}/articles/" + str(art_id),
            headers = {"Authorization": f"token {api_token}"})
        art.append(pd.json_normalize(response.json()))
   
    if response.status_code >= 200 & response.status_code < 300 :  
        article_details = pd.concat(art)[['id','files','tags','categories','custom_fields','authors','description','license.name', 'title', 'doi', 'published_date', 'defined_type_name', 'resource_doi']]   
        return(article_details)
    else: 
        print ("Couldn't retrieve the article details.")

def curate_article_details(article_details):  
    '''
    Curates the article detailes to provide all the information needed

    Parameters
    ----------
    article_details: pandas.DataFrame
        A DataFrame holding details on articles of the collection
    Returns
    ---------
    art: pandas.DataFrame
        A DataFrame holding all the useful information on articles of the collection, 
    '''

    article_ids = article_details['id'].tolist()

    # retrieve data from dictionaries nested in the art dataframe
    file_names=[]
    files=[]
    custom_fields_df = []
    author_names =[]
    categories=[]

    for art_id in article_ids:  
        #files
        tmp_files = pd.json_normalize(article_details[article_details['id']==art_id].iloc[0]['files'])[['id', 'name', 'is_link_only', 'download_url']]
        tmp_files = tmp_files.assign(article_id = art_id)
        files.append(tmp_files)
        tmp_filename = ', '.join(tmp_files["name"])
        file_names.append(tmp_filename)
    
        #custom fields
        custom_fields = ['Geolocation', 'Time coverage', 'Geolocation Longitude', 'Geolocation Latitude']
        tmp_custom_fields_df = pd.json_normalize(article_details[article_details['id']==art_id].iloc[0]['custom_fields'])
        tmp_custom_fields_df = tmp_custom_fields_df[tmp_custom_fields_df['name'].isin(custom_fields)]
        tmp_custom_fields_df = tmp_custom_fields_df.set_index('name').T
        tmp_custom_fields_df = tmp_custom_fields_df.assign(id = art_id)
        custom_fields_df.append(tmp_custom_fields_df)

        #authors 
        tmp_authors = pd.json_normalize(article_details[article_details['id']==art_id].iloc[0]['authors'])[['full_name']]
        tmp_authorname = ', '.join(tmp_authors["full_name"])
        author_names.append(tmp_authorname)
    
        #categories 
        tmp_categories = pd.json_normalize(article_details[article_details['id']==art_id].iloc[0]['categories'])[['title']]
        tmp_categoryname = ', '.join(tmp_categories["title"])
        categories.append(tmp_categoryname)


          
    art = article_details.assign(files = file_names)   
    custom_fields_df = pd.concat(custom_fields_df)
    art = pd.merge(art, custom_fields_df, how="inner", on=["id"])
    art = art.assign(authors = author_names)  
    art = art.assign(categories = categories)  

   
    #keywords 

    # sort the lists of keywords
    art['tags'] = [sorted(l, key=str.casefold) for l in art['tags']]
    
    # ceate a separate dataframe only with the datasets' keywords
    tags_tmp = pd.DataFrame(art.tags.tolist(), index= art.index)

    # extract the names of the metadata
    tag_names = tags_tmp.apply(lambda x: x.str.extract(r'(^[A-Za-z]+)=', expand = False))
    # get the metadata values (after '=')
    tags_tmp = tags_tmp.apply(lambda x: x.str.extract(r'^[A-Za-z]+=([a-zA-Z0-9\-\.\,]+)', expand = False))
    
    # Remove any columns that do not follow the metadata pattern ('name=value')
    tags_tmp = tags_tmp.dropna(axis=1, how='all')
    
    # change names to lower case
    tag_names = tag_names.apply(lambda x: x.str.lower())
    tag_names = tag_names.dropna(axis=1, how='all')
    tag_names = tag_names.drop_duplicates()
    
    # if there's only one row in the dataset - 
    if tag_names.shape[0] == 1:
        tag_names = tag_names.iloc[0]
        tags_tmp.columns = tag_names
        art = pd.concat([art, tags_tmp], axis=1)
        last_cols = tags_tmp.columns.values.tolist()  
    # else add the 'keywords' variable
    else: 
        # Convert tags' list into coma separated string
        art['keywords'] = [', '.join(map(str, l)) for l in art['tags']]
        last_cols = ['keywords']

    
    # Get only the date from the date string
    art["published_date"] = art["published_date"].map(lambda x: x[0:10])



    art = art[['title',
    #'id',
    #'keywords',
    'published_date',
    'files',
    'categories',
    'authors',
    #'description',
    'license.name',
    'doi',
    'Time coverage',
    'Geolocation',
    'Geolocation Latitude',
    'Geolocation Longitude']+last_cols]

    art.columns = ['title',
    #'id',
    #'keywords',
    'published_date',
    'files',
    'categories',
    'authors',
    #'description',
    'license',
    'doi',
    'time_cov',
    'location',
    'locationx',
    'locationy'] + last_cols

    # remove columns with duplicated names
    art = art.loc[:,~art.columns.duplicated()].copy()

    return(art)

def get_file_details(article_details):
    '''
    Curates the article detailes to provide all the information needed

    Parameters
    ----------
    article_details: pandas.DataFrame
        A DataFrame holding details on articles of the collection
    Returns
    ---------
    files: pandas.DataFrame
        A DataFrame holding all the useful information on files of the collection, 
    '''

    article_ids = article_details['id'].tolist()

    # retrieve data from dictionaries nested in the art dataframe
    files=[]

    for art_id in article_ids:  
        #files
        tmp_files = pd.json_normalize(article_details[article_details['id']==art_id].iloc[0]['files'])[['id', 'name', 'is_link_only', 'download_url']]
        tmp_files = tmp_files.assign(article_id = art_id)
        files.append(tmp_files)

    files = pd.concat(files)

    return(files)

def download_files(files, api_url, api_token):
    '''
    Download selected files

    Parameters
    ----------
    files: pandas.DataFrame
        A DataFrame holding all the useful information on files of the collection, 
    Returns
    ---------
    
    '''  
    file_location = input("Provide the file download location:")
    assert os.path.isdir(file_location) , "Invalid directory"

    file_ids = files['id'].tolist()

    for index, file in files.iterrows():
        file_name = file['name']
        response = requests.get(
            url = f"{api_url}/file/download/" + str(file['id']),
            headers = {"Authorization": f"token {api_token}"})
        if response.status_code == 200: 
            open(os.path.join(file_location, file_name) , "wb").write(response.content)
            if os.path.exists(os.path.join(file_location, file_name)): 
                print("The file ID ", file['id'], ": ", file_name, " saved correctly.") 
            else: 
                print("The file ID ", file['id'], ": ", file_name, " couldn't be saved.")         
        else:    
            print("The file ID ", file['id'], ": ", file_name, " couldn't be retrieved.")    

def choose_filter(filter_name, choice_list):
    '''
    Function to filter the results by specific keyword
   
    Parameters
    -----------
    filter_name : str
        Name of one of the filters available in the GEF file keyword
    choice_list: list
        List of choices to present to a user     

    Returns
    ------------
    chosen_filter : str
        Filter option chosen by the user
    '''
    input_string = "Would you like to filter the datasets by " + filter_name +"? [Y/N]: "

    filter_choice = input(input_string) 
    
    # Clean input
    filter_choice_clean = yes_no_input(filter_choice)
    
    if filter_choice_clean == 'y':
        chosen_filter = choose_one_option(choice_list)
        chosen_filter = filter_name.upper() + '=' + chosen_filter
    else:
        chosen_filter = []
    
    return(chosen_filter)

def filter_articles(collection_chosen, article_url, api_token):    
    '''
    Provides a list of articles available in the collection chosen by the user, filtered by specific criteria

    Parameters
    ----------
    collection_chosen: str
        Collection the aticle should be added to
    article_url: str
        URL of the article 
    api_token: str
        Personal token to access API 

    Returns
    ---------
    collection_articles: pandas.DataFrame
        A DataFrame holding articles of the collection        
    '''

    coll_keyword = 'colection-'+collection_chosen

    params={
    "search_for":":keyword: " + coll_keyword,
    # "search_for": "":description: " # w/o quotes will match any of the words included in the description field
    "institution": 898, #unique 4tu code
    "item_type": 3, #item type is dataset
    "page": 1,
    "page_size": 1000 #adjust to number larger than anticipated search results
    }

    #request articles based on search parameters set above
    response = requests.post(
        url = article_url,
        json = params,
        headers = {"Authorization": f"token {api_token}"} 
    )

    #store response as a json object
    j = response.json()
    # query in blocks of 10, while loop that continues until you get less than 10, so you know it's the last

    #full list of search terms available at https://docs.figshare.com/#articles_search
