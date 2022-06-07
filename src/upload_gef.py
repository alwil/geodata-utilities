
import sys
from datetime import datetime
#from bulk_entry import *
from api_uploader import *
from gefreader import test_gef

def main(netID):
    """
    1. Verify if the user has the right credentials
    2. Check which collection the user wants to contribute to
    3. Iterate through a directory of images on local machine to: test input files against the GEF standard
    4. Request additional input from the the user regarding the 4TU metadata
    5. Upload the file to the data collection hosted on 4TU 

    Usage: 
    `cd local/folder/containing/python/script`
    `python upload_gef.py netID`

    Parameters
    ----------
    netID : str
        netID of the user
    """

    # Authorisation step    
    valid_users = {'awilczynski', 'acryan', 'mvankoningsveld', 'fedorbaart'}
    netID = netID.lower()
    assert netID in valid_users, "You do not have sufficient permissions to use this programme."

    # Intro 
    print("You're a few steps away from publishing your dataset. Before that, you need to provide some additional information about your dataset(s) ....")

    # Choose the Sandbox or production
    env_choice =  choose_entry_mode()
    api_token = get_token(env_choice)
    api_url = get_url(env_choice)
    collection_chosen = get_collection_type()
    file_format = get_file_format(collection_chosen)
    file_list = get_file_path(collection_chosen)
    
    retrieved_meta = []
    article_meta = []
    for i, file in enumerate(file_list):
        test_gef()
        art_authors = request_authors(file)
        retrieved_meta.append(retrieve_metadata(file))
        article_meta.append(compile_metadata(collection_chosen, retrieved_meta[i], art_authors, env_choice))
        article_url = create_article(api_url, article_meta[i], api_token)
        #article_doi = reserve_doi(article_url, api_token)
        upload_dataset(article_url, api_token, file)
        #publish_article(article_url, api_token)
        collection_url = add_to_collection( collection_chosen, article_url, api_token)
        #publish_collection( collection_url, api_token)














if __name__ == "__main__":
     

    try:
        netID = sys.argv[1]
    except IndexError:
        print("No NetID specified")
        sys.exit(1)          

    main(netID)
