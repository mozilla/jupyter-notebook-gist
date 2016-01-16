from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
from nbconvert.exporters.export import *
import base64
import json
import os.path
import requests

def handle_error(msg):
    print("Error: ", msg)

class GistHandler(IPythonHandler):
    client_id = None
    client_secret = None

    def get(self):

        # Extract access code and notebook path

        handle_args = self.request.arguments

        access_code = handle_args.get("Code", None)
        if access_code is None or len(access_code) <= 0:
            handle_error("Couldn't extract github authentication code from response")
            return
        path_bytes = handle_args.get("nb_path", None)
        if path_bytes is None or len(path_bytes) <= 0:
            handle_error("Couldn't extract notebook path from response")
            return

        nb_path = base64.b64decode(path).decode('utf-8').lstrip("/")
        access_code = access_code[0].decode('ascii')

        # Request access token from github
        response = requests.post("https://github.com/login/oauth/access_token",
            data = {
                "client_id": self.client_id,
                "client_secret" : self.client_secret,
                "code" : access_code
            },
            headers = {"Accept" : "application/json"})

        token_args = json.loads(response.text)

        # Extract token and scope info from github response
        access_token = token_args.get("access_token", None)
        token_type = token_args.get("token_type", None)
        scope = token_args.get("scope", None)
        if (access_token is None or len(access_token) <= 0
                or token_type is None or len(token_type) <= 0
                or scope is None or len(scope) <= 0):
            handle_error("Couldn't extract needed info from github access token response")
            return

        tokenDict = { "Authorization" : "token " + access_token }

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
        gist_contents = {
            "description": filename_no_ext,
            "public": False,
            "files": {
                filename : {"content": notebook_output},
                filename_no_ext + ".py" : {"content": python_output}
            }
        }
        new_gist_response = requests.post("https://api.github.com/gists",
            data = json.dumps(gist_contents),
            headers = tokenDict)

        # TODO: Check if creating the gist was actually successful
        # TODO: Check for known error responses from each REST call

        # Redirect the client to the github page for the new gist
        new_gist_response_json = new_gist_response.json()
        redirect_url = new_gist_response_json.get("html_url")
        if redirect_url is None:
            handle_error("Didn't receive a url for the new gist")
            return
        self.redirect(redirect_url)


def load_jupyter_server_extension(nb_server_app):

    # Extract our gist client details from the config:
    cfg = nb_server_app.config["NotebookApp"]
    GistHandler.client_id = cfg["oauth_client_id"]
    GistHandler.client_secret = cfg["oauth_client_secret"]

    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/create_gist')
    web_app.add_handlers(host_pattern, [(route_pattern, GistHandler)])
