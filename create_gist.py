from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
import requests
import iampython
import json

class AuthorizeHandler(IPythonHandler):
    def get(self):
        print("Extracting code . . .")

        args = self.request.arguments
       
        access_code = args["code"][0]
        access_code = access_code.decode('ascii')
        

        response = requests.post("https://github.com/login/oauth/access_token", 
            data = {"client_id":"bd8256a4bcc8042c8152", 
            "client_secret" : "1caf8f68e15e01e49fe52b3259c18cbc714d0438",
            "code" : access_code,
            "redirect_uri" : "http://localhost:8888/save_gist"},
            headers = {"Accept" : "application/json"})

        print("Saving gist. . .")
        args = json.loads(response.text)
        print(args)

        # change these to .get to prevent exceptions
        access_token = args["access_token"]
        token_type = args["token_type"]
        scope = args["scope"]

        tokenDict = { "Authorization" : "token " + access_token }

        print(tokenDict)
        pyFiles = {
            'description' : 'My python file',
            'files' : {
                "a.txt" : {
                    "content" : "I am a python file"
                    },
                "b.txt" : {
                    "content" : "I am also a python file"
                    }
                }
        }
        print("Saving gist. . .")
        # TODO : Validate the token
        response = requests.post("https://api.github.com/gists", 
            data = {
            'description' : 'My python file',
            'files' : {
                "a.txt" : {
                    "content" : "I am a python file"
                    },
                "b.txt" : {
                    "content" : "I am also a python file"
                    }
                }
            },
            headers = { "Authorization" : "token " + access_token })

        print(response.content)


        print("Saving gist. . .")


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