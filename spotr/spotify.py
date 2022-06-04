########################################################################################
###################################### spotify.py ######################################
############################ Spotify-api related functions #############################
########################################################################################

########################################################################################
######################################### IMPORTS ######################################
########################################################################################
from pip._vendor import requests #https://stackoverflow.com/questions/48775755/importing-requests-into-python-using-visual-studio-code
from common import logAction
import os
import traceback
from common import ROOT_DIR, waitForGivenTimeIns
from config import spotify_client_id, spotify_client_secret
########################################################################################

########################################################################################
###################################### API REQUESTS ####################################
####################### General procedure for every API request ########################
########################################################################################
def apiReqSpotify(urlExtension):
    pass
########################################################################################




########################################################################################
##################################### AUTHENTICATION ###################################
############ Requests an access token via already obtained refresh token ###############
########################################################################################
def getNewAccessToken():
    '''Load the saved 'refresh_token' from external file'''
    '''return empty string in case of error'''
    '''if everything went ok, nothing (None) is returned'''
    try:
        fileOpen = open(ROOT_DIR + "/static/refresh_token.txt", "r")      
        refresh_token = fileOpen.read()
        fileOpen.close()
    except Exception as ex:
        logAction("err - spotify.py - getNewAccessToken1 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''


    '''--> Assuming a refresh_token has already been received, request new access token with it.
            See spotify api auto documentation: 4. Requesting a refreshed access token; 
            Spotify returns a new access token to your app
    '''


    '''--> Create body params and request parameters'''
    grant_type= 'refresh_token'
    url = 'https://accounts.spotify.com/api/token'
    body_params = {'grant_type': grant_type, 'refresh_token': refresh_token}


    '''--> perform the request'''
    try:
        response = requests.post(url, data=body_params, auth=(spotify_client_id, spotify_client_secret), verify=False)
    except Exception as ex:
        logAction("err - spotify.py - getNewAccessToken2 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''


    '''--> check for error in response'''
    retryCnt = 0
    while (response.status_code != 200) :
        waitForGivenTimeIns(0.5,1)
        logAction("msg - spotify.py - getNewAccessToken3 --> retrying request #" + str(retryCnt))

        if retryCnt >= 10:
            logAction("err - spotify.py - getNewAccessToken4 --> too many retries requesting acces token.")

            '''--> save last result for debugging'''
            with open (ROOT_DIR + "/logs/spotify_getNewAccessToken_LAST.json", 'w') as fi:
                fi.write(str(response.json()))
            return ''

        response = requests.post(url, data=body_params, auth=(spotify_client_id, spotify_client_secret), verify=False)
        retryCnt+=1


    '''--> save last result for debugging'''
    with open (ROOT_DIR + "/logs/spotify_getNewAccessToken_LAST.json", 'w') as fi:
       fi.write(str(response.json()))


    '''--> check if (json-converted) response contains a new refresh_token.
    if so, it needs to be stored!
    '''
    try:
        if hasattr(response.json(), 'refresh_token'):
            fileOpen = open(ROOT_DIR + "/static/refresh_token.txt", 'w')  #'w' = overwrite
            fileOpen.write(response.json()['refresh_token'])
            fileOpen.close()
    except Exception as ex:
        logAction("err - spotify.py - getNewAccessToken5 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''


    '''--> store received access_token also in external file'''
    try:
        fileOpen = open(ROOT_DIR + "/static/access_token.txt", 'w')    #20210723 filopen('access_token.txt, 'w') doesn't seem to work
        fileOpen.write(response.json()['access_token'])
        global gv_access_token      #create global variable
        gv_access_token = response.json()['access_token']
        fileOpen.close()
    except Exception as ex:
        logAction("err - spotify.py - getNewAccessToken6 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''

########################################################################################




# TESTING - - - - - - - - - - -  - - -- - - - - - - - -- - - 
print('starting - - - ')

if getNewAccessToken() == '':
    print('ERR')
elif getNewAccessToken() == None:
    print("NONE")
else:
    print("OK")