from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
import requests

class AuthorizeHandler(IPythonHandler):
    def get(self):
        print("Extracting code . . .")

        args = self.request.arguments
       
        access_code = args["code"]

        req = requests.post("https://github.com/login/oauth/access_token", 
            data = {"client_id":"bd8256a4bcc8042c8152", 
            "client_secret" : "5a80adf6f71a9c894345102fa74b6fad90fbdc54",
            "code" : access_code,
            "redirect_uri" : "http://localhost:8888/save_gist"})


"""class SaveGistHandler(IPythonHandler):
    def get(self):
        print("Saving gist. . .")

        args = self.request.arguments
       
        access_token = args["access_token"]
        token_type = args["token_type"]
        scope = args["scope"]

        tokenDict = { "Authorization" : "token " + access_token }

        pyFiles = {
            'description' : 'My python file',
            'public' : 'true',
            'files' : {
                "a.txt" : {
                    "content" : "I am a python file"
                    },
                "b.txt" : {
                    "content" : "I am also a python file"
                }
        }

        # TODO : Validate the token
        req = requests.get("https://api.github.com/gists", 
            data = pyFiles,
            headers = tokenDict)


        print("Saving gist. . .")* """


def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern1 = url_path_join(web_app.settings['base_url'], '/authorize')
    web_app.add_handlers(host_pattern, [(route_pattern1, AuthorizeHandler)])
    print("I am here")
    route_pattern2 = url_path_join(web_app.settings['base_url'], '/save_gist')
    web_app.add_handlers(host_pattern, [(route_pattern2, SaveGistHandler)])