
from sys import platform
from datetime import datetime
#from bulk_entry import *
from api_uploader import *

def main(netID):
    """

    1. Verify if the user has the right credentials
    2. Check which collection the user wants to contribute to
    3. Iterate through a directory of images on local machine to: test input files against the GEF standard
    4. Request additional input from the the user regarding the 4TU metadata
    5. Upload the file to the data collection hosted on 4TU 

    Usage: 
    `cd local/folder/containing/python/script`
    `python upload_gef.py '/path/to/local/image/directory'`

    Parameters
    ----------
    netID : str
        Path to project drive
    local_path : str
        Path to files that need archiving in the 4TUResearchData
    """
    
# local_path, coll='grout'

 #   assert os.path.isdir(local_path), "Cannot access your local path. Please verify the given path."

    valid_users = {'awilczynski', 'acryan', 'mvankoningsveld', 'fedorbaart'}

    assert netID in valid_users, "You do not have sufficient permission to use this programme."




if __name__ == "__main__":
     

    try:
        netID = sys.argv[1]
    except IndexError:
        print("No NetID specified")
        sys.exit(1)          

    main(netID)
