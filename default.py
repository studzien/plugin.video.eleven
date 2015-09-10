import sys
import urllib
import urllib2
import xbmcgui
import xbmc
import xbmcaddon
import xbmcplugin
import m3u8
import re

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

def show_channels():
    url = 'http://www.elevensports.pl/'
    opener = urllib2.build_opener()
    response = opener.open(url).read()
    players = re.findall("<iframe src='([^']*)'", response)
    links = [ re.search('stream=(.*)', p).group(1) for p in players ]
    urls = [ re.sub('~', '=', l) for l in links ]
    add_dir('Eleven', urls[0], 'channel', None, True)
    add_dir('Eleven Sports', urls[1], 'channel', None, True)
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
