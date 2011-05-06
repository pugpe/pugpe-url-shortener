#!/usr/bin/env python
'''
Pug.pe  Url Shortener

In the database we have an id and an href. We use base64 that integer id to create 
a short code that represent that url.

/{code}  Redirect to pug.pe with this code
/new?href={href} Create a new urly with this href or return existing one if it already exists.
                 Note special handling for 'new' code when we have a href GET parameter cause
                 ne by itself looks like a code
'''


__author__ = 'caraciol@gmail.com'


import re, os, logging
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from pugpeurl import PugPe
from view import MainView

class MainHandler(webapp.RequestHandler):
    """All non-static requests go through this handler.
    The code and format parameters are pre-populated by
    our routing regex... see main() below.
    """
    
    def get(self,code):
        if code is None:
            MainView.render(self,200,None)
            return
        
        href = self.request.get('href').strip().encode('utf-8')
        title= self.request.get('title').strip().encode('utf-8')
        
        if code == 'new' and href is not None:
            try:
                url = PugPe.find_or_create_by_href(href)
                if url is not None:
                    MainView.render(self,200,url,href,title)
                else:
                    logging.error("Error creating urly by href: %s", str(href))
                    MainView.render(self,400,None,href)
            except db.BadValueError:
                #href parameter is bad
                MainView.render(self,400,None,href)
        else:
            url = PugPe.find_by_code(str(code))
            if url is not None:
                MainView.render(self,200,url)
            else:
                MainView.render(self,400,None)
    
    def head(self,code):
        if code is None:
            self.error(400)
        else:
            url = PugPe.find_by_code(str(code))
            if url is not None:
                self.redirect(url.href)
            else:
                self.error(404)

def main():
    application = webapp.WSGIApplication([('/([a-zA-Z0-9]{1,6})?', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()