'''
Functionality allowing the user to choose which metadata should be bulked


'''

# Additional libraries used
import re # for regex
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
import shutil
import json
import time # for lags in printing messages


# Data frame with meta data  info 
def create_meta_info(
    meta_vars= ["project", "author", "apparatus_used", "composition", "treat_therm_hist", "etchant", "size", "scale", "micro_comp"],
    meta_instr = ['Enter project name: ','Enter your first and last name: ', 'Enter apparatus used: ', 'Enter composition: ', 'Enter (thermomechanical) treatment/material history: ','Enter etchant: ', 'Enter size of picture (cm x cm): ', 'Enter ruler length (cm): ', 'Enter microstructural components/phases: ' ],
    meta_field_txt = ['Project: ','Author: ', 'Apparatus Used: ',  'Composition: ','Thermomechanical Treatment / Material History: ','Etchant:','Size of Picture: ','Scale (Ruler Length): ','Microstructural Components / Phases: ' ],
    meta_field_json = ['project','author' ,'apparatus_used', 'composition' ,'treat_therm_hist' , 'etchant' , 'picture_size' ,'ruler_length' ,'micro_components_phases'  ]
    ):
    '''
    Function creates an auxiliary dataframe with metadata names and input instructions 

    Parameters
    ----------
    meta_vars : list 
     List of metadata fields 
    meta_instr : list
     List of input instructions 
    '''
    meta_info = {'meta_vars': meta_vars , 'meta_instr': meta_instr, 'meta_field_txt': meta_field_txt, 'meta_field_json': meta_field_json  }
    meta_info = pd.DataFrame(data=meta_info)
    return(meta_info)

# Give user choice to enter metadata in a bulk
def choose_entry_mode():
    '''
    Function requests an input from the user regarding the bulk input of the metadata and returns it in a clean format 
    
    '''

    joint_meta = input("Do you want some of the metadata to be the same for all the files in the folder? [Y/N]:") 
    # Clean input
    joint_meta_clean = re.sub("[^a-z]","",joint_meta.lower())
    
    # Allow only y/yes n/no 
    assert joint_meta_clean in ['y', 'yes', 'n', 'no'] ,'I did not understand your selection. Please try again.'

    # Return only the first character
    return(joint_meta_clean[0])
            
# Give user choice of which meta data to enter in a bulk 
def choose_meta_fields(auto, meta_info):
    '''
    If the user selected bulk input, function prompts the question on the fields to be bulk-filled and returns meta data info data frame with a column flaggin fields to be ntered in bulk. 
    If only manual input - does nothing.
    
    Parameters
    ----------
    auto : str
     Automated input. If 'y' -  prompts question about which inputs should be bulked
    meta_info = data frame
     Data frame holding information on metadata 
    '''
    n_meta = meta_info.shape[0] # number of metadata fields to be input
    which_bulk = [0] * n_meta  # list pointing to the position of fields to be bulked
    if auto == 'y':
        # Preparing the string to be prompted 
        i = -1 
        input_string = ''
    
        for var in meta_info.meta_vars:
            i += 1
            input_string += '\n'+ str(i) + '-' + var  
        input_string = "Which metadata should be the same for all the files? Type in corresponding numbers:" + input_string + '\n'

        which_meta = input( input_string ) 
        which_meta_clean = re.sub("[^0-8]","",which_meta ) #  clean from unwanted characters

        # Add a warning message, if no digits were selected
        if which_meta_clean == '':
            print("ATTENTION! You have not chosen any of the metadata fields. The input will be requested for each file.")
            time.sleep(0.6) # not to have all printed to the terminal at once
        
        # filtering metadata fields selected by the user
        for i in range(0, n_meta ):
            which_bulk[i] = int(which_meta_clean.find(str(i)) != -1) # flags positions of metafields that are to be bulked 

    # Append the flag to the data frame    
    meta_info_out = meta_info.copy()
    meta_info_out['which_bulk'] = which_bulk
    return(meta_info_out)

# Function that prompts questions about the metadata entries: 
def input_bulk_metadata (meta_info_df): 
    '''
    Function that prompts the input questions for metadata fields to be filled in bulk and returns the updated metadata data.frame with inputs for these fields.
    
    Parameters
    ----------
    auto : str
     Automated input. If 'y' -  prompts question about which inputs should be bulked
    meta_info = data frame
     Data frame holding information on metadata ( including which one should be entered in bulk ) 
    '''
    # Add 'inputs' column to the metdata dataframe - place holder for user inputs of metadata fields
    bulk = meta_info_df.copy()
    bulk['inputs'] = ''

    # Whenever the bulk flag is present, prompt the input from the user
    for input_string in bulk[bulk['which_bulk']==1].meta_instr:
        bulk.at[bulk['meta_instr']== input_string, 'inputs'] = input(input_string)
    
    # Return the metadatafile with the column with inputs filled  for 'bulked' entries
    return(bulk)    


def all_meta_entry (meta_info_df,  path_sidecar, path_raw_images, local_path):
    filenames = os.listdir(local_path) # all files in the selected driectory
    n_meta = meta_info_df.shape[0]
    
    # Iterate through files in the selected directory  and request user to input metadata (per file)
    for count, file in enumerate(filenames): # Enumerate to introduce the iteration counter
        fname = file
        print("\nINPUT METADATA FOR FILE: "+ local_path + '\\' + fname)
        fpath = path_sidecar + file
        entry_date = datetime.today().strftime('%Y-%m-%d')
        no_ext = os.path.splitext(fname)[0]
        
        # for each metadata field, the user input is saved in the temporary table ( either from bulk input or from filewise procedure)
        tmp_list = [] # temporary list to hold the user inputs
        for i in range(n_meta):
            if meta_info_df.loc[i].which_bulk == 1: #if the field was entered in bulk - the metadata field is filled from the saved input
                tmp_list.append( meta_info_df.loc[i].inputs )
            else: 
                tmp_list.append( input( meta_info_df.loc[i].meta_instr ) ) # otherwise, it is taken from the filewise procedure input
        print("Generating sidecar file...")

        # Clean input ( convert to lower case ):
        tmp_list =  [each_string.lower() for each_string in tmp_list]

        # create sidecar .txt file and store in MSDB/sidecar/text folder on Project Drive
        with open(path_sidecar+'text/'+no_ext+'_sidecar.txt', 'w') as file:
            meta = ['File Name: ' + fname,'Path: ' + fpath, 'Entry date: '+ entry_date] + list(map(''.join, zip(meta_info_df.meta_field_txt.tolist(), tmp_list)))
            file.writelines("% s \n" % data for data in meta)

        print("Successfully saved "+no_ext+'_sidecar.txt'+' in '+ path_sidecar+"text.")

        # create sidecar json file and store in MSDB/sidecar/json folder on Project Drive
        metadata = {}
        metadata['images'] = []
        zip_iterator = zip(['file_name', 'file_path', 'entry_date'] + meta_info_df.meta_field_json.tolist(), [fname,fpath,entry_date] + tmp_list)
        metadata['images']  =  dict(zip_iterator)


        with open(path_sidecar+'json/'+no_ext+'_sidecar.json', 'w') as file:
            json.dump(metadata, file)

        #copy image file to MSDB/images/
        print("Copying raw image file to Project Drive...")
        shutil.copy(local_path+'/'+fname, path_raw_images+fname)
        print("Successfully copied "+fname+" to "+ path_raw_images+".")

        # Write a 'moving on to the next file' only if there is a next file
        if count < len(filenames) - 1: 
             print("...MOVING ON TO NEXT FILE...")



   
