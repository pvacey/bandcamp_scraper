#!venv/bin/python
import re,json,os,sys
import time
import requests
from pymongo import MongoClient

def get_tags():
    url = 'https://bandcamp.com/tags'
    taglist =[]
    tagpage = requests.get(url).text
    tmp = re.findall('tags_cloud">([\w\W]+?)(<\/div>)',tagpage)
    tmptags = re.findall('href="\/tag\/([^"]+)', tmp[0][0])
    for tag in tmptags:
        taglist.append(tag)
    return taglist

def get_album_links(tag):
    albums =[]
    #loop through 10 pages of ablums for each tag
    for i in range(1,11):
        url = 'https://bandcamp.com/tag/'+tag+'?page='+str(i)
        tagpage= requests.get(url).text
        #find all of the album links and append them to a list
        tmp = re.findall('href="(.+?)"\s+title',tagpage)
        for a in tmp:
            albums.append(a)
        time.sleep(2)
    return albums

def get_album_info(url):
    print url
    #grab the html of the album page
    html = requests.get(url).text
    #grab album title
    tmp = re.findall('current:\s({.+(?=},)}),',html)
    albumdetails = json.loads(tmp[0])
    albumtitle = albumdetails['title']
    #grab artist name, this does not use json because of bad formatting on the page
    tmp = re.findall('artist: "([^"]+)"',html)
    artist = tmp[0]
    # grab the array of tracks
    tmp = re.findall('trackinfo\s*:\s*(\[.*}])', html)
    trackinfo = json.loads(tmp[0])
    # grab all tags on the page
    tags = re.findall('bandcamp.com\/tag\/([^"]+)', html)

    print 'Album: '+albumtitle
    print 'Artist: '+artist

    tracks =[]
    trackno = 1
    for track in trackinfo:
        tracktitle = track['title']
        print '    '+str(trackno)+'. '+tracktitle
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
    print db.albums.insert_one(album)
    print '-------------------------------'
    return

client = MongoClient()
db = client.music

tags = get_tags()
for tag in tags:
    #get all of the album links for this tag
    alllinks = get_album_links(tag)
    #query the DB for all matching links
    existinglinks = []
    cur = db.albums.find({"url":{"$in":alllinks}})
    for c in cur:
        existinglinks.append(c['url'])

    #make a list of links that are not in the DB yet
    newlinks= set(alllinks) - set(existinglinks)
    #add them all to the DB
    for link in newlinks:
        get_album_info(link)

    print 'Found '+str(len(alllinks))+' '+tag+' albums, attempted to add '+str(len(newlinks))
    print '-------------------------------'
