import json
import requests
from kivy.app import App
from base64 import b64encode
from kivy.logger import Logger
from kivy.network.urlrequest import UrlRequest
from kivy.storage.jsonstore import JsonStore
import inspect
class ComicDataType:
    Arc = 'arc'
    Issue = 'issue'
    Publisher = 'publisher'
    Series = 'series'
    ReadingLists = 'readinglists'

class ComicServerConn():
    def __init__(self,**kwargs):
        self.app = App.get_running_app()
        self.base_url = self.app.base_url

    def set_leaf(self):
            req_url  = '%s/issue/80-page-giant-009-1965/'% (self.base_url)
                      
            data={}
            data['leaf'] = 2
            data['status'] = 0
            headers = {'Content-Type': "application/json", 'Accept': "application/json"}
            res = requests.patch(req_url, json=data, headers=headers, auth=('gwhittey', 'kiskis1234'))
       
           
    
    def get_server_data(self,req_url,instance): 
        
        username = self.app.config.get('Server', 'username')
        api_key = self.app.config.get('Server', 'api_key') 
        str_cookie = f'BCR_apiKey={api_key}; BCR_username={username}'
        head = {'Content-Type': "application/json", 
                'Accept': "application/json",
                'Cookie': str_cookie
                
            }
        req = UrlRequest(req_url,req_headers=head, on_success=instance.got_json, on_error=self.got_error,on_redirect=self.got_redirect,
                            on_failure=self.got_error
                            )

    def get_api_key(self,req_url,username,password,instance):
        
        
        head ={'Content-type': 'application/x-www-form-urlencoded',
              'Accept': 'application/json'}    
        
        strbody = f'username={username}&password={password}&rememberMe=True'
        print(req_url)
        print(strbody)
        req = UrlRequest(req_url,req_headers=head, req_body = strbody,method="POST",on_success=instance.got_api, on_error=self.got_error,on_redirect=self.got_redirect,
                        on_failure=self.got_error
                        )
    
    
    def got_json(self,req, result):
        
        return result['results']      
 
    def got_error(self,req, results):
        print ('got_error')
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    def got_time_out(self,req, results):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    def got_failure(self,req, results):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    def got_redirect(self,req, results):
        print(results)
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))      


class JsonToObject:

    def __init__(self, json_object):
        self.json_object = json_object
        self.keys = json_object.keys()
        self.setup(json_object)

    def setup(self, d):
        for key, item in d.items():
            if isinstance(item, dict):
                new_object = JsonToObject(item)
                setattr(self, key, new_object)
            else:
                setattr(self, key, item)