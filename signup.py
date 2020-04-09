import sys
from bs4 import BeautifulSoup
import requests
import logzero
from logzero import logger

logzero.logfile("soupLogFile.log",  maxBytes=1e6,  backupCount=2)
def soup():
    ''''
    This function represents the automated registration component of the application
    It will scrape the target webpage and will sign the user up for it while imitiating a browser.
    The scraper will pretent to be a browser by using a header that captures a session cookie and adds a token + session key to the payload
    Data that is not received will be randomly generated(except for the pwd = "P@ssw0rd" and email)
    
    @Author: Alistair
    @Date: April 8th 2020

    @Requires - BS4, Logger, requests, sys
    '''
    page  = requests.get("https://awcoupon.ca/en/register")
    logger.info("======STARTING REGISTRATION======")
    if page.status_code != 200:
        logger.error("Cannot Locate the target coupon server")
        print("Cannot Locate the target server")
        return -1 #Failed to make some soup
    
    soup = BeautifulSoup(page.content,  'html.parser')
    logger.info("Found target! Extracting Form...")
    
    #Extract the target registration form
    token = (soup.find('input',  {'name' : '_token'}).get('value'))
    session_key = (soup.find('input',  {'name' : '_session_key'}).get('value'))
    
    #The operational target
    targetURL = "https://awcoupon.ca/en/register"
    
    #Find the cookies of a real browser
    cookieJar = page.cookies
    cookie_ = page.cookies['october_session']
    cookie = 'october_session=' + cookie_
    logger.info("Setting Target Cookie as:" + cookie) #I'm a real browser now
    
    #Header(What data must be imitated)
    headers = {
        'Host' : 'awcoupon.ca', 
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0', 
        'Accept': '*/*', 
        'Accept-Language': 'en-US,en;q=0.5', 
        'Accept-Encoding' :'gzip, deflate, br', 
        'Referer': 'https://awcoupon.ca/en/register', 
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 
        'X-OCTOBER-REQUEST-HANDLER': 'onRegister', 
        'X-OCTOBER-REQUEST-PARTIALS': '', 
        'X-OCTOBER-REQUEST-FLASH': '1', 
        'X-Requested-With': 'XMLHttpRequest', 
        'Content-Length': '281', 
        'Cookie': cookie, 
        'Connection': 'keep-alive', 
    }
    #POST response form (data is brough to the target)
    response = {
    '_session_key' :  session_key, #yanked from the webpage
    '_token' : token,  #yanked from the webpage
    'name': 'ABC', 
    'email':'sagolof26@ualmail.com', 
    'profile[postal_code]': 'k5g2p1', 
    'password': 'P@ssw0rd', 
    'password_confirmation': 'P@ssw0rd', 
    'profile[user_region]' : '', 
    'profile[lang]': 'en'
    
    }
    logger.info("Header & Response created!")
    
    #POST reqeust to target
    logger.info("Attempting registration...")
    test_response = requests.post(targetURL,  data=response,  headers=headers,  cookies=cookieJar)
    
    #Fetch result
    result = BeautifulSoup(test_response.text,  'html.parser')
    #200 = OK(probably) and anything else needs logged.
    if(test_response.status_code != 200):
        logger.error("User could not be registered. Response code was: " + str(test_response.status_code))
        logger.error("Error was:" + test_response.text)
        logger.info("======ENDING REGISTRATION======")
        return -1
    
    logger.info("Registered the user! :p")
    logger.info("======ENDING REGISTRATION======")
    return 0
   
   #=========End of soup=========#
if __name__ == '__main__':    
    soup()
    sys.exit(0)
