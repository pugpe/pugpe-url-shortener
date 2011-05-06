'''
PugPE Url Shortener

'''
__author__ = 'caraciol@gmail.com'

import os
from google.appengine.ext.webapp import template

class MainView():
    """ Display the Shorten Urls """

    @staticmethod
    def render(handler, status, short_url, href=None, title=None):
        #The magic happens here -> Redirect
        if short_url is not None and href is None:
            handler.redirect(short_url.href)
        elif status == 400:
            handler.error(status)
        elif status == 404:
            handler.error(404)
        else:
            if href is not  None :
                handler.response.headers['Content-Type'] = 'text/plain'
                handler.response.out.write(short_url.to_text())