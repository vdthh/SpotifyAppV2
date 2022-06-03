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
    while (response.status_code != 200) and (retryCnt < 5):
        waitForGivenTimeIns(0.5,1)
        logAction("msg - spotify.py - getNewAccessToken3 --> retrying request #" + str(retryCnt))

        response = requests.post(url, data=body_params, auth=(spotify_client_id, spotify_client_secret), verify=False)
        retryCnt+=1
    else:HIERGESTOPT 20220603

        
            

########################################################################################

getNewAccessToken()