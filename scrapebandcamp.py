#!venv/bin/python
import re,json,os,sys
import time
import requests
from pymongo import MongoClient

def get_tags():
    '''retrieve the top page of genre/description tags'''
    url = 'https://bandcamp.com/tags'
    taglist =[]
    tagpage = requests.get(url).text
    # regex to isolate tag strings
    tmp = re.findall('tags_cloud">([\w\W]+?)(<\/div>)',tagpage)
    tmp_tags = re.findall('href="\/tag\/([^"]+)', tmp[0][0])
    # build a list of tags from the matches
    [taglist.append(tag) for tag in tmp_tags]
    print 'unique tags found: {}'.format(len(set(taglist)))
    return sorted(set(taglist))


def get_album_links(tag, n):
    '''fetch n number of album links for a tag'''
    albums =[]
    print '------------------\ntag = {}'.format(tag)
    #loop through n number of pages
    for i in range(1,n+1):
        # print status
        print 'fetching page {} of {}...'.format(i,n)
        # retrieve raw html for tag page i
        url = 'https://bandcamp.com/tag/'+tag+'?page='+str(i)
        tag_page = requests.get(url).text
        # find all of the album links and append them to a list
        tmp = re.findall('href="(.+?)"\s+title',tag_page)
        for a in tmp:
            albums.append(a)
        time.sleep(2)
    #print 'Albums:\n {}'.format(albums)
    #print 'total albums: {}'.format(len(albums))
    return albums

def get_album_info(url):
    # grab the html of the album page
    html = requests.get(url).text
    # grab album title
    tmp = re.findall('current:\s({.+(?=},)}),',html)
    albumdetails = json.loads(tmp[0])
    albumtitle = albumdetails['title']
    # grab artist name, this does not use json because of bad formatting on the page
    tmp = re.findall('artist: "([^"]+)"',html)
    artist = tmp[0]
    # grab the array of tracks
    tmp = re.findall('trackinfo\s*:\s*(\[.*}])', html)
    trackinfo = json.loads(tmp[0])
    # grab all tags on the page
    tags = re.findall('bandcamp.com\/tag\/([^"]+)', html)

    #print 'Album: '+albumtitle
    #print 'Artist: '+artist

    tracks =[]
    trackno = 1
    #print url
    for track in trackinfo:
        tracktitle = track['title']
        #print '    '+str(trackno)+'. '+tracktitle
        trackno += 1
        fileurl = ''
        try:
            fileurl = 'http:'+track['file']['mp3-128']
        except:
            #print '    [ERROR] no file for this track'
            pass
        tracks.append({
            "trackno"   : trackno,
            "title"     : tracktitle,
            "url"       : fileurl
        })
    #build the JSON object to store in the mongo collection
    album = {
        "artist" : artist,
        "title"  : albumtitle,
        "url"    : url,
        "tag"    : tags,
        "tracks" : tracks
    }
    print ' + {} - {}'.format(album['artist'].encode('ascii', 'ignore'), album['title'].encode('ascii', 'ignore'))
    return album

