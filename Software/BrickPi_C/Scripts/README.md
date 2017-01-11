###README.md
 
This script is intended for updating the Software packages on the Raspberry Pi Image so the the BrickPi programs work with C.
 
Before running the script make sure that you are using the ** image of the Dexter Industries Raspbian Flavour**  from here: http://sourceforge.net/projects/dexterindustriesraspbianflavor/
 
Run as root (sudo).
First update the BrickPi C repository:
- Go the the BrickPi_C folder
    > cd BrickPi_C
- Commit your changes and do a git fetch
    > git fetch origin
- Do a git merge
    > git merge origin/master
    
- If you are unable to do this then Clone the BrickPi_C repository
    > git clone https://github.com/DexterInd/BrickPi_C.git
        
- Now make the script in the **/BrickPi_C/Scripts** folder executable:
    > sudo chmod +x brick_pi_c_debug.sh
    
- Run the script:
    > ./brick_pi_c_debug.sh
    
Now sit back, it'll take some time for the script to complete. You'll be prompted a few time for continuing and overwriting files. Select "**Overwrite All**" if you are prompted.
 
Once the script finishes, the Raspberry Pi will restart and your C programs should work fine.
 
**NOTE**: If you image is heavily modified or customized, in that case the the C code might still not run and you'll have to use a fresh image.