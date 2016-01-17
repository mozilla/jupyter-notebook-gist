from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
from nbconvert.exporters.export import *
import base64
import json
import requests
import tornado
import os

def raise_error(msg):
    raise tornado.web.HTTPError(500, "ERROR: " + msg)

def raise_github_error(msg):
    raise tornado.web.HTTPError(500, "ERROR: Github returned the following: " + msg)

# This handler will save out the notebook to GitHub gists in either a new Gist 
# or it will create a new revision for a gist that already contains these two files.
class GistHandler(IPythonHandler):
    client_id = None
    client_secret = None

    def get(self):

        # Extract access code
        access_code_args = self.request.arguments

        access_code_error = access_code_args.get("error_description", None)
        if access_code_error is not None:
            if (len(access_code_error) >= 0):
                raise_github_error(access_code_error)

        access_code = access_code_args.get("code", None)
        if access_code is None or len(access_code) <= 0:
            raise_error("Couldn't extract github authentication code from response"),
        path_bytes = access_code_args.get("nb_path", None)
        if path_bytes is None or len(path_bytes) <= 0:
            raise_error("Couldn't extract notebook path from response")

        # Extract notebook path
        nb_path = base64.b64decode(path_bytes[0]).decode('utf-8').lstrip("/")
        access_code = access_code[0].decode('ascii')

        # Request access token from github
        token_response = requests.post("https://github.com/login/oauth/access_token",
            data = {
                "client_id": self.client_id,
                "client_secret" : self.client_secret,
                "code" : access_code
            },
            headers = {"Accept" : "application/json"})

        token_args = json.loads(token_response.text)

        token_error = token_args.get("error_description", None)
        if token_error is not None:
            raise_github_error(token_error)

        # Extract token and scope info from github response
        access_token = token_args.get("access_token", None)
        token_type = token_args.get("token_type", None)
        scope = token_args.get("scope", None)
        if access_token is None or token_type is None or scope is None:
            raise_error(token_args, "Couldn't extract needed info from github access token response")

        github_headers = { "Accept" : "application/json",
                            "Authorization" : "token " + access_token }

        # Extract file contents given the path to the notebook
        filename = os.path.basename(nb_path)
        ext_start_ind = filename.rfind(".")
        if ext_start_ind == -1:
            filename_no_ext = filename
        else:
            filename_no_ext = filename[:ext_start_ind]
        notebook_output, _ = export_by_name("notebook", nb_path)
        python_output, _ = export_by_name("python", nb_path)

        # Prepare and send our github request to create the new gist
        filename_with_py = filename_no_ext + ".py"
        gist_contents = {
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
        get_gists_args = json.loads(response.text)

        match_counter = 0;
        matchID = None
        for gist in get_gists_args:
            gist_files = gist.get("files", None)
            if (gist_files is not None and filename in gist_files
                    and filename_with_py in gist_files):
                match_counter += 1
                if "id" in gist:
                    matchID = gist["id"]

        # If no gist with this name exists yet, create a new gist
        if matchID == None:
            gist_response = requests.post("https://api.github.com/gists",
                data = json.dumps(gist_contents),
                headers = github_headers)

        # If we have another gist with the same files, create a new revision
        elif match_counter == 1: 
            gist_response = requests.patch("https://api.github.com/gists/" + matchID,
                data = json.dumps(gist_contents),
                headers = github_headers)

        # TODO: This probably should actually be an error
        # Instead, we should ask the user which gist they meant?
        else:
            raise_error("You had multiple gists with the same name as this notebook. Aborting.")

        gist_response_json = gist_response.json()
        update_gist_error = gist_response_json.get("error_description", None)
        if update_gist_error is not None:
            raise_github_error(update_gist_error)
            
        gist_url = gist_response_json.get("html_url", None)
        if gist_url is None:
            raise_error("Couldn't get the url for the gist that was just updated")

        self.redirect(gist_url)


class DownloadNotebookHandler(IPythonHandler):
    def post(self):
        # url and filename are sent in a JSON encoded blob
        post_data = tornado.escape.json_decode(self.request.body) 

        nb_url = post_data["nb_url"]
        nb_name = base64.b64decode(post_data["nb_name"]).decode('utf-8')

        file_path = os.path.join(os.getcwd(), nb_name)

        r = requests.get(nb_url, stream=True)
        with open(file_path, 'wb') as fd:
            for chunk in r.iter_content(1024): # TODO: check if this is a good chunk size
                fd.write(chunk)

        self.write(nb_name)
        self.flush()


def load_jupyter_server_extension(nb_server_app):

    # Extract our gist client details from the config:
    cfg = nb_server_app.config["NotebookApp"]
    GistHandler.client_id = cfg["oauth_client_id"]
    GistHandler.client_secret = cfg["oauth_client_secret"]

    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/create_gist')
    download_notebook_route_pattern = url_path_join(web_app.settings['base_url'], '/download_notebook')


    web_app.add_handlers(host_pattern, [(route_pattern, GistHandler), (download_notebook_route_pattern, DownloadNotebookHandler)])


