from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
from nbconvert.exporters.export import *
import base64
import json
import os.path
import requests
import urllib.request
import shutil
import tornado
import os

# This handler will save out the notebook to GitHub gists in either a new Gist 
# or it will create a new revision for a gist that already contains these two files.
class GistHandler(IPythonHandler):
    client_id = None
    client_secret = None
    def get(self):
        print("Extracting code . . .")
        args = self.request.arguments
        access_code = args["code"][0].decode('ascii')
        response = requests.post("https://github.com/login/oauth/access_token",
            data = {
                "client_id": self.client_id,
                "client_secret" : self.client_secret,
                "code" : access_code
            },
            headers = {"Accept" : "application/json"})

        nb_path = base64.b64decode(args["nb_path"][0]).decode('utf-8').lstrip("/")

        args = json.loads(response.text)
        print(args)
        print("Building request. . .")

        # TODO: change these to .get to prevent exceptions
        access_token = args["access_token"]
        token_type = args["token_type"]
        scope = args["scope"]

        github_headers = { "Accept" : "application/json",
                            "Authorization" : "token " + access_token }

        print("Extracting file contents")
        filename = os.path.basename(nb_path)
        ext_start_ind = filename.rfind(".")
        if ext_start_ind == -1:
            filename_no_ext = filename
        else:
            filename_no_ext = filename[:ext_start_ind]
        notebook_output, _ = export_by_name("notebook", nb_path)
        python_output, _ = export_by_name("python", nb_path)

        filename_with_py = filename_no_ext + ".py"
        py_files = {
            "description": filename_no_ext,
            "public": False,
            "files": {
                filename : {"filename" : filename, "content": notebook_output},
                filename_with_py : { "filename" : filename_with_py,
                                "content": python_output }
            }
        }

        # Get the list of user's gists to see if this gist exists already
        response = requests.get("https://api.github.com/gists",
            headers = github_headers)
        args = json.loads(response.text)

        match_counter = 0;
        matchID = None

        for gist in args:

            gist_contents = gist["files"]
            if filename in gist_contents and filename_with_py in gist_contents:
                match_counter += 1
            
                if "id" in gist:
                    matchID = gist["id"]

        if matchID == None:

            print("Saving gist. . .")
            # TODO: Validate the token
            response = requests.post("https://api.github.com/gists",
                data = json.dumps(py_files),
                headers = github_headers)

        # If we have another gist with the same files, create a new revision
        elif match_counter == 1: 
            # create new rev for existing gist
            print ("Revising gist with id " + matchID)

            response = requests.patch("https://api.github.com/gists/" + matchID,
                data = json.dumps(py_files),
                headers = github_headers)

        # TODO: Some sort of error message if we have more than 1 gist with the same files
        else:
            print("OOPS")
            # put stuff here
            
        print("Redirecting...")
        self.redirect(response.json()["html_url"])

        print("All done. . .")


class DownloadGistHandler(IPythonHandler):
    def post(self):
        post_data = tornado.escape.json_decode(self.request.body) 

        nb_url = post_data["nb_url"]
        nb_name = post_data["nb_name"]

        file_path = os.path.join(os.getcwd(), nb_name)

        with urllib.request.urlopen(nb_url) as response, open(file_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        self.write(nb_name)
        self.flush()


def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    # Extract our gist client details from the config:
    cfg = nb_server_app.config["NotebookApp"]
    GistHandler.client_id = cfg["oauth_client_id"]
    GistHandler.client_secret = cfg["oauth_client_secret"]

    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/create_gist')
    download_gist_route_pattern = url_path_join(web_app.settings['base_url'], '/download_gist')


    web_app.add_handlers(host_pattern, [(route_pattern, GistHandler), (download_gist_route_pattern, DownloadGistHandler)])


