
import sys
from datetime import datetime
from api_uploader import *

def main( netID ):
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
    
    # Choose the selection
    collection_chosen = get_collection_type()
    file_format = get_file_format( collection_chosen )

    # Choose the Sandbox or production environment and get the right URL
    env_choice =  choose_entry_mode()
    api_url = get_url( env_choice )

    # Input token for the chosen environment
    api_token = get_token( env_choice )

    # Selection of programme actions 
    action_choices = ['Upload files to 4TU repository', 'Browse and retrieve files from 4TU repository']
    action_chosen = choose_one_option( action_choices )
    
    
    # Programme actions if upload files chosen
    
    if action_chosen == 'Upload files to 4TU repository':

        # Intro 
        print("You're a few steps away from publishing your dataset. Before that, you need to provide some additional information about your dataset(s) ....")

        
        file_list = get_file_path(collection_chosen)

        retrieved_meta = []
        article_meta = []
       
        authors_list = request_authors(file_list)
        for i, file in enumerate(file_list):
            print('\n Preparing file ', i+1 , 'out of ', len(file_list),'\n')
            test_gef_anchor(file)
            #art_authors = request_authors(file)
            retrieved_meta.append(retrieve_metadata(file))
            article_meta.append(compile_metadata(collection_chosen, retrieved_meta[i], authors_list[i], env_choice))
            article_url = create_article(api_url, article_meta[i], api_token)
            #article_doi = reserve_doi(article_url, api_token)
            upload_dataset(article_url, api_token, file)
            #publish_article(article_url, api_token)
            collection_url = add_to_collection( collection_chosen, article_url, api_token, env_choice)
            #publish_collection( collection_url, api_token)

    elif action_chosen == 'Browse and retrieve files from 4TU repository':
        article_ids = browse_collection( collection_chosen, api_url, api_token )

        if article_ids != None:
            article_details = get_article_details( article_ids, api_url, api_token )
            article_printable = curate_article_details(article_details)
            print(article_printable)
            time.sleep(0.6)
            print("What would you like to do next?")
            browsing_options = ['Download all the files', 'Filter by keywords', 'Show the files on the map']
            browsing_chosen = choose_one_option( browsing_options ) 
            if browsing_chosen == 'Download all the files':
                files = get_file_details(article_details)
                download_files(files, api_url, api_token)
            elif browsing_chosen == 'Filter by keywords':
                # filters_closed = ['Test type', 'Anchor type']
                # filters_open = ['Location name', 'Location coordinates (X,Y)', 'Location Z']
                # filters_date = ['Time coverage']
                filters = ['Test type', 'Anchor type', 'Location name', 'Location coordinates (X,Y)', 'Location Z', 'Time coverage']
                filter_type = {
                              'Test type':   {'filter':'choice', 'answers':['investigation','suitability','acceptance'] }, 
                              'Anchor type': {'filter':'choice', 'answers':['self-drilling','stranded','screw injection'] },
                               'Location name': 'text',
                               'Location coordinates (X,Y)': {'range'}, 'Location Z':'range', 'Time coverage':'daterange'}

                chosen_filters = choose_multiple(filters)
                         
                # Add a warning message, if no digits were selected
                if chosen_filters == []:
                    print("ATTENTION! You have not selected any filter.")
                    time.sleep(0.6) # not to have all printed to the terminal at once
                    #return(choice_list)




            elif browsing_chosen == 'Show the files on the map': 
                print('A map will be here')
        else : 
            # potentially looping program actions in the future
            sys.exit()




if __name__ == "__main__":

    try:
        netID = sys.argv[1]
    except IndexError:
        print("No NetID specified")
        sys.exit(1)          

    main( netID )
