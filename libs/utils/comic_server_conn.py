import json
from kivy.app import App
from kivy.logger import Logger
from kivy.network.urlrequest import UrlRequest
import inspect


class ComicDataType:
    Arc = 'arc'
    Issue = 'issue'
    Publisher = 'publisher'
    Series = 'series'
    ReadingLists = 'readinglists'


class ComicServerConn():
    def __init__(self, **kwargs):
        self.app = App.get_running_app()
        self.base_url = self.app.base_url

    def get_page_size_data(self, req_url, callback):
        username = self.app.config.get('Server', 'username')
        api_key = self.app.config.get('Server', 'api_key')
        str_cookie = f'API_apiKey={api_key}; BCR_username={username}'
        head = {'Content-Type': "application/json",
                'Accept': "application/json", 'Cookie': str_cookie
                }
        req = UrlRequest(req_url, req_headers=head, on_success=callback,
                         on_error=self.got_error,
                         on_redirect=self.got_redirect,
                         on_failure=self.got_error
                         )

    def update_progress(self, req_url, index, callback):
        data = f'CurrentPage={index}'
        username = self.app.config.get('Server', 'username')
        api_key = self.app.config.get('Server', 'api_key')
        str_cookie = f'API_apiKey={api_key}; BCR_username={username}'
        head = {'Content-Type': "application/x-www-form-urlencoded",
                'Accept': "application/json", 'Cookie': str_cookie
                }
        req = UrlRequest(req_url, req_headers=head,
                         req_body=data,
                         on_success=callback,
                         on_error=self.got_error,
                         on_redirect=self.got_redirect,
                         on_failure=self.got_error
                         )

    def get_server_data_callback(self, req_url, callback):
        print(req_url)
        username = self.app.config.get('Server', 'username')
        api_key = self.app.config.get('Server', 'api_key')
        str_cookie = f'API_apiKey={api_key}; BCR_username={username}'
        head = {'Content-Type': "application/json",
                'Accept': "application/json",
                'Cookie': str_cookie

                }

        req = UrlRequest(req_url, req_headers=head,
                         on_success=callback,
                         on_error=self.got_error,
                         on_redirect=self.got_redirect,
                         on_failure=self.got_error
                         )

    def get_server_data(self, req_url, instance):

        username = self.app.config.get('Server', 'username')
        api_key = self.app.config.get('Server', 'api_key')
        str_cookie = f'API_apiKey={api_key}; BCR_username={username}'
        head = {'Content-Type': "application/json",
                'Accept': "application/json",
                'Cookie': str_cookie

                }

        req = UrlRequest(req_url, req_headers=head,
                         on_success=instance.got_json,
                         on_error=self.got_error,
                         on_redirect=self.got_redirect,
                         on_failure=self.got_error
                         )

    def get_api_key(self, req_url, username, password, callback):

        head = {'Content-type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'}
        strbody = f'username={username}&password={password}&rememberMe=True'
        req = UrlRequest(req_url, req_headers=head,
                         req_body=strbody, method="POST",
                         on_success=callback,
                         on_error=self.got_error,
                         on_redirect=self.got_redirect,
                         on_failure=self.got_error
                         )

    def get_list_count(self, req_url, instance):
        username = self.app.config.get('Server', 'username')
        api_key = self.app.config.get('Server', 'api_key')
        str_cookie = f'API_apiKey={api_key}; BCR_username={username}'
        head = {'Content-Type': "application/json",
                'Accept': "application/json",
                'Cookie': str_cookie

                }
        req = UrlRequest(req_url, req_headers=head,
                         on_success=instance.got_count,
                         on_error=self.got_error,
                         on_redirect=self.got_redirect,
                         on_failure=self.got_error
                         )

    def get_server_file_download(self, req_url, callback, file_path):
        def update_progress(request, current_size, total_size):
            print(current_size/total_size)
        print(req_url)
        username = self.app.config.get('Server', 'username')
        api_key = self.app.config.get('Server', 'api_key')
        str_cookie = f'API_apiKey={api_key}; BCR_username={username}'
        head = {'Content-Type': "application/json",
                'Accept': "application/json",
                'Cookie': str_cookie

                }

        req = UrlRequest(req_url, req_headers=head,
                         on_success=callback,
                         on_error=self.got_error,
                         on_redirect=self.got_redirect,
                         on_failure=self.got_error,
                         file_path=file_path
                         )

    def got_json(self, req, result):

        return result['results']

    def got_error(self, req, results):
        Logger.critical('ERROR in %s %s' % (inspect.stack()[0][3], results))

    def got_time_out(self, req, results):
        Logger.critical('ERROR in %s %s' % (inspect.stack()[0][3], results))

    def got_failure(self, req, results):
        Logger.critical('ERROR in %s %s' % (inspect.stack()[0][3], results))

    def got_redirect(self, req, results):
        Logger.critical('ERROR in %s %s' % (inspect.stack()[0][3], results))


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
