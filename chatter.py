#!/usr/bin/python
# -*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.httpclient

import sys, os, time
from optparse import OptionParser

import time
import tweepy
import json
from collections import deque


class serve_index(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class poll(tornado.web.RequestHandler):
    def get(self):
        index = STORE.index
        startfrom = self.get_argument('startfrom', '0')
        startfrom = int(startfrom)
        startfrom = max(startfrom, index-STORE.store.maxlen)
        startfrom = min(startfrom, index)

        

        result = dict(startfrom=startfrom, data=[])
        start = STORE.store.maxlen - (index - startfrom)

        print startfrom, index

        for i in xrange(start, STORE.store.maxlen):
            status = STORE.store[i]
            print i, status
            result['data'].append(status)

        self.write(result)

class setterms(tornado.web.RequestHandler):
    def post(self):
        termsstr = self.get_argument('terms')
        terms = [x.strip() for x in termsstr.split(',')]
        print terms
        STREAM.attach_to_stream(terms)
        dic = dict(terms=terms)
        self.write(dic)


# Managers

class StoreManager(tweepy.StreamListener):
    def __init__(self): 
        tweepy.StreamListener.__init__(self)

        try:
            f = open('tweets.txt')
        except:
            f = open('tweets.txt','w+')

        lines = f.readlines()
        print 'tweets found:', len(lines)

        self.index = 0
        self.store = deque(maxlen=5)
        for line in lines:
            self.store.append(json.loads(line))
            self.index += 1

        self.lastuser = ''
        self.lasttweet = ''
    def on_status(self, status):
        try:
            if self.lastuser == status.author.screen_name and self.lasttweet == status.text:
                return False

            self.lastuser = status.author.screen_name 
            self.lasttweet = status.text

            dic = self.status2dic(status)
            print dic['text']
            self.store.append(dic)
            self.index += 1

            # dicstr = '%s\n' % json.dumps(dic)
            # open('tweets.txt','a').write(dicstr)
        except Exception, e:
            print e

    def on_limit(self, track):
        print 'LIMIT:', track
        return True

    def on_error(self, status_code):
        print 'An error has occured! Status code = %s' % status_code
        return True  # keep stream alive

    def on_timeout(self):
        print 'Snoozing Zzzzzz'

    def status2dic(self, status):
        return dict(text=status.text, 
                    screen_name=status.author.screen_name, 
                    created_at='%s' % status.created_at)


class StreamManager():
    def __init__(self):
        self.stream = None
        self.attach_to_stream()

    def attach_to_stream(self, setTerms=['SXSW']):
        lines = open('credentials.txt').readlines()

        creds = dict(
            CONSUMER_KEY=lines[0].split()[1].strip(),
            CONSUMER_SECRET=lines[1].split()[1].strip(),
            ACCESS_KEY=lines[2].split()[1].strip(),
            ACCESS_SECRET=lines[3].split()[1].strip()
        )

        auth = tweepy.OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
        auth.set_access_token(creds['ACCESS_KEY'], creds['ACCESS_SECRET'])
        if self.stream:
            self.stream.disconnect()
        self.stream = tweepy.Stream(auth=auth, listener=STORE, timeout=None)
        self.stream.filter(track=setTerms, async=True)

        print 'search terms', setTerms

    def disconnect(self):
        self.stream.disconnect()


#########################################

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static",),
    "debug": os.environ.get("SERVER_SOFTWARE", "").startswith("Development/"),
}
application = tornado.web.Application([
    (r"/$", serve_index),
    (r"/poll", poll),
    (r"/setterms", setterms),
], **settings)    

    
if __name__ == "__main__":
    STORE = StoreManager()
    STREAM = StreamManager()

    parser = OptionParser(add_help_option=False)
    parser.add_option("-h", "--host", dest="host", default='')
    parser.add_option("-p", "--port", dest="port", default='10011')
    (options, args) = parser.parse_args()

    HOST    = options.host
    PORT    = int(options.port)

    mode = ''
    if settings['debug']:
        mode = '(debug)'

    print 'MLchatter running at %s:%s using %s' % (HOST,PORT,mode)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(PORT, address=HOST)
    ioloop = tornado.ioloop.IOLoop.instance()

    # poster = Poster()
    # caller = tornado.ioloop.PeriodicCallback(poster.execute, 1000, ioloop)
    # caller.start()

    try:
        ioloop.start()
    except:
        print 'exiting'
        STREAM.disconnect()
    
