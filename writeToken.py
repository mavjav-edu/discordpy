import re
from cryptography.fernet import Fernet

try: # try-catch block for error `IOError`
    
    key = open("key",'wb+') # attempts to create/open a 'key' file where we store the Fernet key (wb+ means Write Binary to file with additional read privileges)
    token = open("token",'wb') # attempts to create/open a 'token' file where we store the encrypted Discord token (we don't need to read from 'token' here, so we only need write privileges)
    key.write(Fernet.generate_key()) # generates a Fernet key and saves that key to the 'key' file
    key.seek(0) # return the file pointer to the beginning (point 0) of the 'key' file (because the 'write(...)' command leaves the file pointer where it left off -- at the end of the file)
    f = Fernet(key.read()) # creates a Fernet object to do the encryption using our key generated above

    token.write(f.encrypt(str.encode(input("What is the discord bot token?> ")))) # asks the user for the Discord token, then encodes as binary, then encrypts the binary, and then writes binary to 'token' file

    try: # reading and write `.gitignore` to make sure we don't accidentally upload key or token
        gitignoref = open(".gitignore",'r') # opens `.gitignore` as a read only
        gitignore = gitignoref.read() # stores the content of `.gitignore`
        gitignoref = open(".gitignore",'a') # opens `.gitignore` append mode (write starting at the end of the file)
        keyRE = re.compile("key",re.MULTILINE) # regular expression pattern matching the word 'key' anywhere
        tokenRE = re.compile("token",re.MULTILINE) # regular expression pattern matching the word 'token' anywhere
        if(None == re.search(keyRE,gitignore)): # if the word 'key' is not found in the content of `.gitignore`
            gitignoref.write("\nkey") # then add 'key' to the next line in `.gitignore`
        if(None == re.search(tokenRE,gitignore)): # if the word 'token' is not found in the content of `.gitignore`
            gitignoref.write("\ntoken") # then add 'key' to the next line in `.gitignore`
    except IOError as error: # catches `IOError` from trying to open `.gitignore`
        pass
    finally: # Below code will run in any event (whether there is an error or not)
        gitignoref.close() # close the file `.gitignore`
except IOError as error:
    pass # This is the part where we recover from error `IOError`
finally: # Below code will run in any event (whether there is an error or not)
    key.close() # close the file `key`
    token.close() # close the file `token`