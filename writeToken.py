import re
from cryptography.fernet import Fernet

try: # try-catch block for error `IOError`
    f=None
    try: # This is for when the 'key' file already exists
        key = open("key",'rb') # attempts to open a 'key' file where we store the Fernet key (rb means Read Binary from file)
        f=Fernet(key.read()) # creates a Fernet object to do the encryption using our key generated above
    except IOError as error: # This is for when the 'key' file doesn't exist or was deleted
        key = open("key",'wb+') # attempts to create/open a 'key' file where we store the Fernet key (wb+ means Write Binary to file with additional read privileges)
        key.write(Fernet.generate_key()) # generates a Fernet key and saves that key to the 'key' file
        key.seek(0) # return the file pointer to the beginning (point 0) of the 'key' file (because the 'write(...)' command leaves the file pointer where it left off -- at the end of the file)
        f = Fernet(key.read()) # creates a Fernet object to do the encryption using our key generated above 
   
    tokenFilename = input("What is the filename?> ")
    token = open(tokenFilename,'wb') # attempts to create/open a 'tokenFilename' file where we store the encrypted Discord token (we don't need to read from 'tokenFilename' here, so we only need write privileges)
    token.write(f.encrypt(str.encode(input("What is the secret?> ")))) # asks the user for the Discord token, then encodes as binary, then encrypts the binary, and then writes binary to 'token' file

    try: # reading and write `.gitignore` to make sure we don't accidentally upload key or token
        gitignoref = open(".gitignore",'r') # opens `.gitignore` as a read only
        gitignore = gitignoref.read() # stores the content of `.gitignore`
        gitignoref = open(".gitignore",'a') # opens `.gitignore` append mode (write starting at the end of the file)
        keyRE = re.compile("key",re.MULTILINE) # regular expression pattern matching the word 'key' anywhere
        tokenRE = re.compile(tokenFilename,re.MULTILINE) # regular expression pattern matching the word 'token' anywhere
        if(None == re.search(keyRE,gitignore)): # if the word 'key' is not found in the content of `.gitignore`
            gitignoref.write("\nkey") # then add 'key' to the next line in `.gitignore`
        if(None == re.search(tokenRE,gitignore)): # if the word 'token' is not found in the content of `.gitignore`
            gitignoref.write("\n"+tokenFilename) # then add 'key' to the next line in `.gitignore`
    except IOError as error: # catches `IOError` from trying to open `.gitignore`
        pass
    finally: # Below code will run in any event (whether there is an error or not)
        gitignoref.close() # close the file `.gitignore`
except IOError as error:
    pass # This is the part where we recover from error `IOError`
finally: # Below code will run in any event (whether there is an error or not)
    key.close() # close the file `key`
    token.close() # close the file `token`

#after using this script, the `token` file will be useable like this:
"""
key=open("key",'rb')
fernet=Fernet(key.read())
token=open("token",'rb')
client.run((fernet.decrypt(token.read())).decode())
"""