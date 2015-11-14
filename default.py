import sys
import urllib
import urllib2
import xbmcgui
import xbmc
import xbmcaddon
import xbmcplugin
import m3u8
import re
import simplejson
import md5

def add_dir(name, url, mode, iconimage, isfolder):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+ mode
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, liz, isfolder)

def get_params():
    param=[]
    paramstring=sys.argv[2]
    print sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]

    return param

addon = xbmcaddon.Addon()
path = xbmc.translatePath(addon.getAddonInfo('path'))
addon_data_path = xbmc.translatePath(addon.getAddonInfo('profile'))
icon = path + "/icon.png"

def add_link(name, url, title, iconimage):
    if iconimage == '':
        iconimage = icon
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": title } )
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)

def userid_hash():
    url = 'http://api.tvnplayer.pl/api2/?v=3.6&platform=Mobile&terminal'\
    '=Android&format=json&authKey=4dc7b4f711fb9f3d53919ef94c23890c&m='\
    'authenticate&login={login}&password={password}'.format(
            login = addon.getSetting('username'),
            password = addon.getSetting('password'))
    opener = urllib2.build_opener()
    response = simplejson.loads(opener.open(url).read())
    return (response['usr_id'], response['usr_token'])

def playlist_hash(userid, usertoken):
    return md5.new(usertoken + '#' + str(userid)).digest().encode("hex")

def playlist_url(userid, usertoken, streamid):
    url = 'http://api.tvnplayer.pl/api2/?v=3.6&platform=Mobile&terminal'\
    '=Android&format=json&authKey=4dc7b4f711fb9f3d53919ef94c23890c&m=getStream'\
    '&id={streamid}&usrId={userid}&hash={userhash}&osVersion=5.0.1'.format(
            streamid = streamid,
            userhash = playlist_hash(userid, usertoken),
            userid = userid)
    opener = urllib2.build_opener()
    response = simplejson.loads(opener.open(url).read())
    stream = response['item']['stream']
    return stream['url'] + '?privData=' + stream['encryption_license_data']

def show_channels():
    (userid, usertoken) = userid_hash()
    add_dir('Eleven', playlist_url(userid, usertoken, 23), 'channel', None, True)
    add_dir('Eleven Sports', playlist_url(userid, usertoken, 25), 'channel', None, True)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def show_streams(url):
    obj = m3u8.load(url)
    for playlist in reversed(obj.playlists):
        bw = playlist.stream_info.bandwidth / 1000,
        label = "%s kbps" % bw
        add_link(label, playlist.uri, label, None)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

params = get_params()

try:
    url=urllib.unquote_plus(params["url"])
except:
    url=None

try:
    mode = params["mode"]
except:
    mode = None

if mode == None or url==None or len(url)<1:
    show_channels()
elif mode == 'channel':
    show_streams(url)
