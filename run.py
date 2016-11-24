#!venv/bin/python
import scrapebandcamp
from pymongo import MongoClient
bc = scrapebandcamp

# set up mongo client
client = MongoClient()
db = client.music

tags = bc.get_tags()
for tag in tags:
    # get a list of fresh album links from band camp
    #links = bc.get_album_links('retrowave',2)
    links = bc.get_album_links(tag,1)
    # query the mongoDB for all matching links
    existinglinks = []
    cur = db.albums.find({"url":{"$in":links}})
    for c in cur:
        existinglinks.append(c['url'])

    # dedup links
    links = set(links)
    print '-\ntotal found: {}'.format(len(links))
    print 'matches found: {}'.format(len(existinglinks))
    # remove all existing links they are skipped
    links = set(links) - set(existinglinks)
    print 'new links to ingest: {}'.format(len(links))

    # loops through links, fetches info, insert into mongo
    for link in links:
        album = bc.get_album_info(link)
        db.albums.insert_one(album)
