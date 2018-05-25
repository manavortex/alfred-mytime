#!/usr/bin/python
# encoding: utf-8

import sys  
import re
import urllib2
import json
import csv
import codecs
import os
import socket
from workflow import (Workflow3, ICON_INFO, ICON_WARNING, ICON_ERROR, ICON_WEB,
                      ICON_SETTINGS, ICON_SYNC)
from time import gmtime, strftime
from workflow.background import is_running, run_in_background
from pprint import pprint


UPDATE_SETTINGS = {'github_slug': 'manavortex/alfred-mytime'}


# TODO: Understand https://git.deanishe.net/deanishe/alfred-unwatched-videos/src/master/src/thumbnails.py Why did I take Python again?


class TimeToMyTime(object):
    """Workflow controller."""

    def __init__(self):
        """Create new `SmartFolders` object."""
        self.wf = Workflow3(update_settings=UPDATE_SETTINGS)
        args = self.wf.args
        # Perform search
        try: 
            self.query = self.wf.decode(args[0])
        except IndexError: 
            self.query = 'query'

        #log = self.wf.logger

    def search(self):
        querystring = "http://api.genius.com/search?q=" + urllib2.quote(self.query)
        request = urllib2.Request(querystring)
        request.add_header("Authorization", "Bearer " + "XrgFo2k9c6FR0x1nNimiHfHyzHqNSth10zhj1Jtwhxkai1qNtG_rvkAGUQl_uF1X")   
        request.add_header("User-Agent", "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)") #Must include user agent of some sort, otherwise 403 returned
        while True:
            try:
                response = urllib2.urlopen(request, timeout=4) #timeout set to 4 seconds; automatically retries if times out
                raw = response.read()
            except socket.timeout:
                print("Timeout raised and caught")
                continue
            break
        json_obj = json.loads(raw)
        body = json_obj["response"]["hits"]
        return body

    def run(self, wf):
        """Run workflow."""
        
        args = self.wf.args # check for magic args

        

        body = self.search()
        
        for result in body:
            
            header_image_url = result["result"]["song_art_image_thumbnail_url"]
            title=result["result"]["title"]
            subtitle= result["result"]["primary_artist"]["name"]
            url=result["result"]["url"]
            self.wf.add_item(result["result"]["title"], subtitle=subtitle,
                 arg=url, autocomplete=None, valid=True,
                 icon=header_image_url, icontype='path')
            
        self.wf.send_feedback()
        # Handle thumbnail queue
        t = thumbs()
        t.save_queue()
        if t.has_queue:
            if not is_running('generate_thumbnails'):
                run_in_background('generate_thumbnails',
                                  ['/usr/bin/python',
                                   wf.workflowfile('thumbnails.py')])    
        


if __name__ == '__main__':
    
    time = TimeToMyTime()
    sys.exit(time.run(time.wf.run))
