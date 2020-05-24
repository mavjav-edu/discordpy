import re, keyring
from cryptography.fernet import Fernet

try: # try-finally block for error `IOError` on opening `key` file for reading binary
    f=None # Make sure the Fernet object is within scope of future dependencies by setting to here (to nothing, for now)
    try: # This is for when the 'key' file already exists
        key = open("key",'rb') # attempts to open a 'key' file where we store the Fernet key (rb means Read Binary from file)
        f=Fernet(key.read()) # creates a Fernet object to do the encryption using our key generated above
    except IOError as error: # This is for when the 'key' file doesn't exist or was deleted
        key = open("key",'wb+') # attempts to create/open a 'key' file where we store the Fernet key (wb+ means Write Binary to file with additional read privileges)
        key.write(Fernet.generate_key()) # generates a Fernet key and saves that key to the 'key' file
        key.seek(0) # return the file pointer to the beginning (point 0) of the 'key' file (because the 'write(...)' command leaves the file pointer where it left off -- at the end of the file)
        f = Fernet(key.read()) # creates a Fernet object to do the encryption using our key generated above 
    print("[1] Store token in key ring","[2] Store token to disk")
    while not((wantsTokenFile := int(input("Should we store token to disk or keep in keyring? [1-2]> "))) == 1 or wantsTokenFile == 2):
        pass # Keep asking for a 1 or 2
    if(wantsTokenFile == 2):
        tokenFilename = input("What should be the token filename?> ")
        try: # try-finally block for error `IOError` on opening `token` file for writing binary
            token = open(tokenFilename,'wb') # attempts to create/open a 'tokenFilename' file where we store the encrypted Discord token (we don't need to read from 'tokenFilename' here, so we only need write privileges)
            token.write(f.encrypt(str.encode(input("What is the secret?> ")))) # asks the user for the Discord token, then encodes as binary, then encrypts the binary, and then writes binary to 'token' file
        finally:
            token.close() # close the file `token`
    elif(wantsTokenFile == 1):
        keyring.set_password("system", (key.read()),(input("What is the secret?> "))) # asks the user for the Discord token, then writes the token as password into the keyring with the Fernet key as the username
        print("Your token has been stored in the file system keyring!")
    try: # reading and write `.gitignore` to make sure we don't accidentally upload key or token
        gitignoref = open(".gitignore",'r') # opens `.gitignore` as a read only
        gitignore = gitignoref.read() # stores the content of `.gitignore`
        gitignoref = open(".gitignore",'a') # opens `.gitignore` append mode (write starting at the end of the file)
        keyRE = re.compile("key",re.MULTILINE) # regular expression pattern matching the word 'key' anywhere
        if(re.search(keyRE,gitignore) == None): # if the word 'key' is not found in the content of `.gitignore`
            gitignoref.write("\nkey") # then add 'key' to the next line in `.gitignore`
        if(wantsTokenFile == "2"): # if the word 'token' is not found in the content of `.gitignore`
            tokenRE = re.compile(tokenFilename,re.MULTILINE) # regular expression pattern matching the word 'token' anywhere
            if(re.search(tokenRE,gitignore) == None):
                gitignoref.write("\n"+tokenFilename) # then add 'key' to the next line in `.gitignore`
    finally: # Below code will run in any event (whether there is an error or not)
        gitignoref.close() # close the file `.gitignore`
finally: # Below code will run in any event (whether there is an error or not)
    key.close() # close the file `key`