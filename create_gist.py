from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
import requests
import json
import config
import ntpath

from nbconvert.exporters.python import PythonExporter
from nbconvert.exporters.notebook import NotebookExporter
from nbconvert.exporters.export import *

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

        args = json.loads(response.text)
        print(args)
        print("Building request. . .")

        # TODO: change these to .get to prevent exceptions
        access_token = args["access_token"]
        token_type = args["token_type"]
        scope = args["scope"]

        tokenDict = { "Authorization" : "token " + access_token }

        print("Extracting file contents")
        path = "Desktop/Gist Test.ipynb"
        filename = ntpath.basename(path)
        ext_start_ind = filename.rfind(".")
        if ext_start_ind == -1:
            filename_no_ext = filename
        else:
            filename_no_ext = filename[:ext_start_ind]
        notebook_output, _ = export_by_name("notebook", path)
        python_output, _ = export_by_name("python", path)

        pyFiles = {
            "description": "My example notebook",
            "public": False,
            "files": {
                filename : {"content": notebook_output},
                filename_no_ext + ".py" : {"content": python_output}
            }
        }

        print("Saving gist. . .")
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
