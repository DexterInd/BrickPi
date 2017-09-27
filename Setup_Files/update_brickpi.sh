# This script updates the the code repos on Raspbian for Robots.

PIHOME=/home/pi
DEXTER=Dexter
DEXTER_PATH=$PIHOME/$DEXTER
RASPBIAN=$PIHOME/di_update/Raspbian_For_Robots
curl --silent https://raw.githubusercontent.com/DexterInd/script_tools/master/install_script_tools.sh | bash

# needs to be sourced from here when we call this as a standalone
source /home/pi/$DEXTER/lib/$DEXTER/script_tools/functions_library.sh

# BrickPi+ Update
feedback "--> Start BrickPi Update."
feedback "##############################"
delete_folder /home/pi/Desktop/BrickPi     # Delete the old location
# Check for a BrickPi directory under "Dexter" folder.  If it doesn't exist, create it.
BRICKPI_DIR=$DEXTER_PATH/BrickPi+
if [ -d "$BRICKPI_DIR" ]; then
    echo "BrickPi Directory Exists"
    cd $DEXTER_PATH/BrickPi+ # Go to directory
    sudo git fetch origin       # Hard reset the git files
    sudo git reset --hard  
    sudo git merge origin/master
else
    cd $DEXTER_PATH
    # the dot at the end is important to avoid a BrickPi+/BrickPi folder structure
    git clone https://github.com/DexterInd/BrickPi BrickPi+
    cd $DEXTER_PATH/BrickPi+
fi
change_branch $BRANCH   

# BrickPi_Python Update
delete_folder /home/pi/Desktop/BrickPi_Python      # Delete the old location
delete_folder /home/pi/Desktop/BrickPi_C   
delete_folder /home/pi/Desktop/BrickPi_Scratch   

sudo bash $DEXTER_PATH/BrickPi+/Setup_Files/install.sh


