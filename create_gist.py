from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
import requests
import json
import config

class GistHandler(IPythonHandler):
    def get(self):
        print("Extracting code . . .")
        args = self.request.arguments
        access_code = args["code"][0].decode('ascii')
        response = requests.post("https://github.com/login/oauth/access_token",
            data = {
                "client_id": config.OAUTH_CLIENT_ID,
                "client_secret" : config.OAUTH_CLIENT_SECRET,
                "code" : access_code
            },
            headers = {"Accept" : "application/json"})

        nb_path = base64.b64decode(args["nb_path"][0]).decode('utf-8')
        print(nb_path)

        args = json.loads(response.text)
        print(args)
        print("Building request. . .")

        # TODO: change these to .get to prevent exceptions
        access_token = args["access_token"]
        token_type = args["token_type"]
        scope = args["scope"]

        tokenDict = { "Authorization" : "token " + access_token }

        print(tokenDict)
        pyFiles = {
            "description": "My example notebook",
            "public": False,
            "files": {
                "a.txt" : {"content": "I am a python file"},
                "b.txt" : {"content": "I am also a python file"}
            }
        }
        print("Saving gist. . .")
        print(json.dumps(pyFiles))
        # TODO: Validate the token
        response = requests.post("https://api.github.com/gists",
            data = json.dumps(pyFiles),
            headers = tokenDict)

        print(response.content)

        print("Redirecting...")
        self.redirect(response.json()["html_url"])

        print("All done. . .")


def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/create_gist')
    web_app.add_handlers(host_pattern, [(route_pattern, GistHandler)])
