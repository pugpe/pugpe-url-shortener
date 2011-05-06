
'''
PugPE Url Shortener

'''
__author__ = 'caraciol@gmail.com'


from google.appengine.ext import db
from google.appengine.api import memcache
import logging

class PugPe(db.Model):
    href = db.LinkProperty(required=True)
    created_at = db.DateTimeProperty(auto_now_add=True)
    
    KEY_BASE = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    BASE = 64
    
    def code(self):
        '''
        Return our base-62 encoded id
        '''
        if not self.is_saved():
            return None
        
        nid = self.key().id()
        s = []
        while nid:
            nid, c = divmod(nid,PugPe.BASE)
            s.append(PugPe.KEY_BASE[c])
        s.reverse()
        return "".join(s)   

    def to_text(self):
        return 'http://pugpe.appspot.com/%s' % self.code()

    def to_json(self):
        return "{\"code\":\"%s\",\"href\":\"%s\"}\n" % ('http://pugpe.appsot.com/' + self.code(), self.href)

    def save_in_cache(self):
        """We don't really care if this fails"""
        memcache.set(self.code(), self)

    @staticmethod
    def find_or_create_by_href(href):
        query = db.Query(PugPe)
        query.filter('href =', href)
        u = query.get()
        if not u:
            u = PugPe(href=href)
            u.put()
            u.save_in_cache()
        return u

    @staticmethod
    def code_to_id(code):
        aid = 0L
        for c in code:
            aid *= PugPe.BASE 
            aid += PugPe.KEY_BASE.index(c)
        return aid

    @staticmethod
    def find_by_code(code):
        try:
            u = memcache.get(code)
        except:
            # http://code.google.com/p/googleappengine/issues/detail?id=417
            logging.error("PugPe.find_by_code() memcached error")
            u = None

        if u is not None:
            logging.info("PugPe.find_by_code() cache HIT: %s", str(code))
            return u        

        logging.info("PugPe.find_by_code() cache MISS: %s", str(code))
        aid = PugPe.code_to_id(code)
        try:
            u = PugPe.get_by_id(int(aid))
            if u is not None:
                u.save_in_cache()
            return u
        except db.BadValueError:
            return None