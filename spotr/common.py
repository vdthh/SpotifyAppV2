########################################################################################
####################################### common.py ######################################
######################## functions used through whole project ##########################
########################################################################################



########################################################################################
######################################### IMPORTS ######################################
########################################################################################
from cmath import log
import datetime
import os
import time
import random
import json
import re
import traceback
from pip._vendor import requests #https://stackoverflow.com/questions/48775755/importing-requests-into-python-using-visual-studio-code
from config import spotify_client_id, spotify_client_secret
########################################################################################



########################################################################################
######################################## VARIABLES #####################################
########################################################################################
'''--> Used for file locating'''
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) #result --> E:\docs\phyton projects\SpotifyWebAppV2.0\spotr
CONFIG_PATH= os.path.join(ROOT_DIR, 'watchlist.py') #result --> E:\docs\phyton projects\SpotifyWebAppV2.0\spotr\common.py
########################################################################################



########################################################################################
######################################### LOGGING ######################################
########################################################################################
def logAction(msg):
    '''--> General log call'''
    fl1 = open(ROOT_DIR + "\logs\log_event.txt", "a", encoding="utf-8")        #https://stackoverflow.com/questions/27092833/unicodeencodeerror-charmap-codec-cant-encode-characters
    timedetail = str(datetime.datetime.now())
    fl1.write('\n' + timedetail + " " + str(msg))
    fl1.close()
########################################################################################



########################################################################################
######################################## FUNCTIONS #####################################
########################################################################################
def waitForGivenTimeIns(secondsMin, secondsMax):
    '''--> Wait for given time in s, timespan between min and max'''
    time.sleep(random.uniform(secondsMin, secondsMax))
########################################################################################



########################################################################################
######################################### SPOTIFY ######################################
########################################################################################
########################################################################################
def apiGetSpotify(urlExtension):
    '''--> General procedure for every Spotify API request <--'''
    '''Returns a valid response in json format (request.responseObject.json())'''
    '''return empty string in case of error'''


    '''--> always request a new access token'''
    result = getNewAccessToken()
    if result == '':
        '''error'''
        logAction("err - spotify.py - apiGetSpotify --> error getNewAccessToken()")
    elif result == None:
        '''ok'''
        pass
    else:
        '''not possible?'''
        logAction("err - spotify.py - apiGetSpotify2 --> something unusual with getNewAccessToken()")


    '''-->  wait given timespan'''
    waitForGivenTimeIns(0.01,0.1)


    '''--> create and perform request'''
    if urlExtension.startswith("https://"):
        url = urlExtension
    else:
        url = 'https://api.spotify.com/v1/' + urlExtension

    headers = {'Authorization': 'Bearer ' + gv_access_token}

    try:
        response = requests.get(url, headers=headers, verify=False)
    except Exception as ex:
        logAction("err - spotify.py - apiGetSpotify3 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''


    '''--> check for error in response'''
    try:
        retryCnt = 0
        while (response.status_code != 200) :
            waitForGivenTimeIns(0.5,1)
            logAction("msg - spotify.py - apiGetSpotify4 --> retrying request #" + str(retryCnt))

            if retryCnt >= 30:
                logAction("err - spotify.py - apiGetSpotify5 --> too many retries requesting acces token.")

                '''--> save last result for debugging'''
                with open (ROOT_DIR + "/logs/spotify_apiGetSpotify_LAST.json", 'w', encoding="utf-8") as fi:
                    fi.write(json.dumps(response.json(), indent = 4))
                return ''

            response = requests.get(url, headers=headers, verify=False)
            retryCnt+=1
    except Exception as ex:
        logAction("err - spotify.py - apiGetSpotify6 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''

    '''--> save last result for debugging'''
    with open (ROOT_DIR + "/logs/spotify_apiGetSpotify_LAST.json", 'w', encoding="utf-8") as fi:
        fi.write(json.dumps(response.json(), indent = 4))

    '''--> finally, return a valid response in json format'''
    return response.json()


########################################################################################
######################################### SPOTIFY ######################################
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
    try:
        retryCnt = 0
        while (response.status_code != 200) :
            waitForGivenTimeIns(0.5,1)
            logAction("msg - spotify.py - getNewAccessToken3 --> retrying request #" + str(retryCnt))

            if retryCnt >= 10:
                logAction("err - spotify.py - getNewAccessToken4 --> too many retries requesting acces token.")

            response = requests.post(url, data=body_params, auth=(spotify_client_id, spotify_client_secret), verify=False)
            retryCnt+=1

            '''--> save last result for debugging'''
            with open (ROOT_DIR + "/logs/spotify_getNewAccessToken_LAST.json", 'w', encoding="utf-8") as fi:
                fi.write(json.dumps(response.json(), indent = 4))
            return ''
    except Exception as ex:
        logAction("err - spotify.py - getNewAccessToken4.5 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''


    '''--> save last result for debugging'''
    with open (ROOT_DIR + "/logs/spotify_getNewAccessToken_LAST.json", 'w', encoding="utf-8") as fi:
       fi.write(json.dumps(response.json(), indent = 4))


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
######################################### SPOTIFY #####################################
def getTrackInfo(trackID, artistsAsList):
    '''--> Get track details via API'''
    '''Returns a dict containing track info:'''
    '''input artistsAsList returns the artist names as list or only the first name'''
    '''{"trackid": string, "title": string, "artists": list of string, "album": string, "href": string, "popularity": string}'''
    '''Returns empty string in case of error'''


    '''--> perform request'''
    logAction("msg - common.py - getTrackInfo --> requesting track info for trackID: " + trackID)  
    track_info = apiGetSpotify('tracks/' + trackID)


    '''--> check response before continuing'''
    if track_info == '':
        logAction("err - common.py - getTrackInfo2 --> empty api response for track " + trackID + "!")
        return ''


    '''--> save last result for debugging'''
    with open (ROOT_DIR + "/logs/common_getTrackInfo_LAST.json", 'w', encoding="utf-8") as fi:
        fi.write(json.dumps(track_info, indent = 4))


    '''--> Extract track ID from the uri to create the url'''
    try:
        regexResult = re.search(":([a-zA-Z0-9]+):([a-zA-Z0-9]+)", str(track_info['uri'])) 
        urlLink = regexResult.group(2)
    except Exception as ex:
        logAction("err - common.py - getTrackInfo3 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''


    '''--> return first artist name or list of all artist names'''
    try:
        artistNames = []
        #get list of artist name(s)
        for artist in track_info["artists"]:
            #create list with artist names
            artistNames.append(artist["name"])
        if artistsAsList:
            return {"trackid": trackID, "title": track_info["name"], "artists": artistNames, "album": track_info["album"]["name"], "href": urlLink, "popularity": track_info["popularity"]}
        else:
            return {"trackid": trackID, "title": track_info["name"], "artists": track_info["artists"][0]["name"], "album": track_info["album"]["name"], "href": urlLink, "popularity": track_info["popularity"]}
    except Exception as ex:
        logAction("err - common.py - getTrackInfo4 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''


########################################################################################
######################################### SPOTIFY #####################################
def getTracksFromLikedList():
    '''--> Return a list with track ID's (with pagination)'''
    '''Returns empty string in case of error'''


    '''--> perform request'''
    logAction("msg - common.py - getTracksFromLikedList --> requesting tracks from liked list.") 
    liked_tracks = apiGetSpotify("me/tracks?offset=0&limit=50")

    
    '''--> check response before continuing'''
    if liked_tracks == '':
        logAction("err - common.py - getTracksFromLikedList2 --> empty api response for liked tracks!")
        return ''


    try:
        '''--> check pagination - fill resultlist'''
        resultList = []
        total = liked_tracks["total"]
        limit = liked_tracks["limit"]
        offset = liked_tracks["offset"]

        while offset < total:
            for track in liked_tracks["items"]:
                if track["track"]["id"]: #check if valid item
                    resultList.append(track["track"]["id"]) #add track ID to resultList
            offset = offset + limit
            if offset < total: #new request
                liked_tracks = apiGetSpotify("me/tracks?offset=" + str(offset) + "&limit=" + str(limit))
                if liked_tracks == '': #invalid api response
                    logAction("err - common.py - getTracksFromLikedList3 --> empty api response for liked tracks!")
                    return ''
                continue

        logAction("msg - common.py - getTracksFromLikedList4 --> finished, returned list of " + str(len(resultList)) + " tracks from liked list.")
        return resultList

    except Exception as ex:
        logAction("err - common.py - getTracksFromLikedList5 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''


########################################################################################
######################################### SPOTIFY ######################################
def getTracksFromArtist(artistID, trackDetails):
    '''--> Returns list with all track ID's or trackdetails for the given artist - pagination taken into account'''
    '''In case of error, '' is returned'''
    '''if trackDetails is TRUE, a list with dicts is returned containing detailed track info.  {id: trackid, artists: list with artists, title: title}'''
    '''if FALSE, a list containing only the track ID's is returned'''


    '''--> perform request, artist albums'''
    logAction("msg - common.py - getTracksFromArtist --> requesting albums from artist " + artistID + ".") 
    artist_albums = apiGetSpotify("artists/" + artistID + "/albums?offset=0&limit=50")


    '''--> check response before continuing'''
    if artist_albums == '':
        logAction("err - common.py - getTracksFromArtist2 --> empty api response for artists albums!")
        return ''


    try:
        '''--> check pagination - fill resultlist'''
        resultList = []
        total = artist_albums["total"]
        limit = artist_albums["limit"]
        offset = artist_albums["offset"]

        while offset < total:
            for album in artist_albums["items"]: #album tracks            
                artist_album_tracks = apiGetSpotify("albums/" + album["id"] + "/tracks")
                if artist_album_tracks != "": #valid api response
                    for track in artist_album_tracks["items"]:
                        if track["id"]: #check if valid item
                            if trackDetails:
                                #detailed track info
                                #grab artist name(s)
                                artist_list = []
                                for artist in track["artists"]:
                                    artist_list.append(artist["name"])
                                artist_trck_dict_obj = {"id" : track["id"], "artists" : artist_list, "title" : track['name']}
                                resultList.append(artist_trck_dict_obj)         
                            else:
                                #only track ID
                                resultList.append(track["id"])
                        else: #invalid track
                            log("err - common.py - getTracksFromArtist3 --> invalid track[\"ID\"] for album " + str(album["id"]) + ".")
                            continue
                else: #invalid api response                  
                    logAction("err - common.py - getTracksFromArtist4 --> empty api response for artist's album tracks (" + album["id"] + ").")
                    return ''

            offset = offset + limit
            if offset < total: #new request
                artist_album_tracks = apiGetSpotify("albums/" + album["id"] + "/tracks?offset=" + str(offset) + "&limit=" + str(limit))
                if artist_album_tracks == '': #invalid api response
                    logAction("err - common.py - getTracksFromArtist5 --> empty api response for artist's album tracks!")
                    return ''
                continue

        logAction("msg - common.py - getTracksFromArtist6 --> finished, returned list of " + str(len(resultList)) + " tracks from artist " + artistID)
        return resultList

    except Exception as ex:
        logAction("err - common.py - getTracksFromArtist7 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''


########################################################################################
######################################### SPOTIFY ######################################
def getTracksFromPlaylist(playlistID, trackDetails):
    '''--> Returns list with all track ID's or trackdetails for the given playlist - pagination taken into account'''
    '''In case of error, '' is returned'''
    '''if trackDetails is TRUE, a list with dicts is returned containing detailed track info.  {id: trackid, artists: list with artists, title: title}'''
    '''if FALSE, a list containing only the track ID's is returned'''


    '''--> perform request, artist albums'''
    logAction("msg - common.py - getTracksFromPlaylist --> requesting tracks from playlist " + playlistID + ".") 
    playlist_trcks = apiGetSpotify("playlists/" + playlistID + "/tracks?offset=0&limit=100")


    '''--> check response before continuing'''
    if playlist_trcks == '':
        logAction("err - common.py - getTracksFromPlaylist2 --> empty api response for playlist tracks!")
        return ''

    
    try:
        '''--> check pagination - fill resultlist'''
        resultList = []
        total = playlist_trcks["total"]
        limit = playlist_trcks["limit"]
        offset = playlist_trcks["offset"]

        while offset < total:          
            if playlist_trcks != "": #valid api response
                for track in playlist_trcks["items"]: #playlist tracks
                    if track["track"]["id"]: #check if valid item
                        if trackDetails: #detailed track info                            
                            #grab artist name(s)
                            artist_list = []
                            for artist in track["track"]["artists"]:
                                artist_list.append(artist["name"])
                            playlist_trck_dict_obj = {"id" : track["track"]["id"], "artists" : artist_list, "title" : track["track"]['name']}
                            resultList.append(playlist_trck_dict_obj)         
                        else: #only track ID                          
                            resultList.append(track["track"]["id"])
                    else: #invalid track
                        logAction("err - common.py - getTracksFromPlaylist3 --> invalid trackID in playlist " + playlistID + ".")
                        continue
            else:#invalid api response                  
                logAction("err - common.py - getTracksFromPlaylist4 --> empty api response for playlist tracks " + playlistID + ".")
                return ''

            offset = offset + limit
            if offset < total: #new request
                playlist_trcks = apiGetSpotify("playlists/" + playlistID + "/tracks?offset=" + str(offset) + "&limit=" + str(limit))
                if playlist_trcks == '': #invalid api response
                    logAction("err - common.py - getTracksFromPlaylist5 --> empty api response for playlist tracks - offset=" + str(offset) + ", limit=" + str(limit) + ".")
                    return ''
                continue

        logAction("msg - common.py - getTracksFromPlaylist6 --> finished, returned list of " + str(len(resultList)) + " tracks from playlist that contains " + str(total) + " tracks.")
        return resultList

    except Exception as ex:
        logAction("err - common.py - getTracksFromPlaylist7 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''


########################################################################################
######################################### SPOTIFY ######################################
def addTracksToPlaylist(playlistID, trackIDList):
    '''--> Add tracks to existing playlist'''
    '''Playlist already has to exist!'''
    '''in case of error, '' is returned'''


    '''--> prepare request'''
    if getNewAccessToken() == "":
        logAction("err - spotify.py - addTracksToPlaylist --> error requesting new access token.")
        return ''

    waitForGivenTimeIns(0.1,1)

    try: #create payload
        headers = {'Authorization': 'Bearer ' + gv_access_token}         
        track_uri_list = [] #List with track uris
        for i in range(len(trackIDList)):
            track_uri_list.append("spotify:track:" + str(trackIDList[i]))

        payload = {"uris":track_uri_list}

    except Exception as ex:
        logAction("err - common.py - addTracksToPlaylist2 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''

    for item in track_uri_list:
        print("ITEM: " + item)


    '''--> perform POST request'''
    try:      
        logAction("msg - common.py - addTracksToPlaylist3 --> about to add a total of " + str(len(trackIDList)) + " tracks to playlist " + playlistID + ".") 
        response = requests.post(url='https://api.spotify.com/v1/playlists/' + playlistID + "/tracks", headers = headers, data = json.dumps(payload), verify=False)

    except Exception as ex:
        logAction("err - common.py - addTracksToPlaylist4 --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return ''


    '''--> save last result for debugging'''
    with open (ROOT_DIR + "/logs/spotify_apiPostSpotify_LAST.json", 'w', encoding="utf-8") as fi:
        fi.write(json.dumps(response.json(), indent = 4))


    '''--> check response'''
    if response.json()["error"]:
        print("err - common.py - addTracksToPlaylist5 --> error from POST request: " + str(response.json()["error"]["status"]) + ", " + str(response.json()["error"]["message"]))
        return ''

    '''--> finally, return a valid response in json format'''
    return response.json()


########################################################################################
