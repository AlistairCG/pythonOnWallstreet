import sys
from bs4 import BeautifulSoup
import requests
import logzero
from logzero import logger
''''
This stub program represents the automated registration component of the application
It will scrape the target webpage and will sign the user up for it via POSTing.
@Auth: Alistair
@Date: March 30th 2020

@Requires - BS4, Logger, requests, sys
'''
logzero.logfile("soupLogFile.log",  maxBytes=1e6,  backupCount=2)
def soup():
    page  = requests.get("https://awcoupon.ca/en/register")
    if page.status_code != 200:
        logger.error("Cannot Locate a target coupon server")
        print("Cannot Locate a target server")
        return -1 #Failed to make some soup
    
    soup = BeautifulSoup(page.content,  'html.parser')
    logger.info("Found target! Extracting Form...")
    
    #Extract the target registration form
    print(soup.find_all(id="register-form"))
    
    
    #TODO - Sprint Due Apr 4th 
    '''
    1) Grab the form fields  and set the values based on handed arguements from the main app
    2) Create a JSON Data object using the given args
    3) Grab the CSRF fields of session id and token and append to the JSON Data object
    4) POST the object and check for success
    5) Logger Success :p
    '''
if __name__ == '__main__':    
    soup()
    sys.exit(0)
