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


class StoreManager(tweepy.StreamListener):
    def __init__(self):
        tweepy.StreamListener.__init__(self)
        self.buffer = deque()

    def savebuffer(self):
        f = open('tweets.txt','a+')
        while len(self.buffer):
            status = self.buffer.popleft()
            dic = self.status2dic(status)    
            dicstr = '%s\n' % json.dumps(dic)
            f.write(dicstr)
            
        f.close()

    def on_status(self, status):
        print '%s: %s' % (status.author.screen_name, status.text)
        self.buffer.append(status)
        if len(self.buffer) > 10:
            self.savebuffer()

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
                    created_at='%s' % status.created_at,
                    geo=status.geo or {})


store = StoreManager()

setTerms=['sxmedialab']
lines = open('credentials.txt').readlines()

creds = dict(
    CONSUMER_KEY=lines[0].split()[1].strip(),
    CONSUMER_SECRET=lines[1].split()[1].strip(),
    ACCESS_KEY=lines[2].split()[1].strip(),
    ACCESS_SECRET=lines[3].split()[1].strip()
)

auth = tweepy.OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
auth.set_access_token(creds['ACCESS_KEY'], creds['ACCESS_SECRET'])
stream = tweepy.Stream(auth=auth, listener=store, timeout=None)
stream.filter(track=setTerms)

print 'search terms', setTerms


