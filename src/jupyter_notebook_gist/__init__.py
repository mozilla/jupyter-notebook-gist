from notebook.utils import url_path_join

from .handlers import GistHandler, DownloadNotebookHandler, LoadGistHandler


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        # the path is relative to the `jupyter_notebook_gist` directory
        'src': 'static',
        # directory in the `nbextension/` namespace
        'dest': 'jupyter-notebook-gist',
        # _also_ in the `nbextension/` namespace
        'require': 'jupyter-notebook-gist/extension',
    }]


def _jupyter_server_extension_paths():
    return [{
        'module': 'jupyter_notebook_gist',
    }]


def load_jupyter_server_extension(nbapp):
    # Extract our gist client details from the config:
    config = nbapp.config['NotebookApp']

    web_app = nbapp.web_app
    url = web_app.settings['base_url']
    params = {
        'client_id': config['oauth_client_id'],
        'client_secret': config['oauth_client_secret'],
    }

    web_app.add_handlers(
        r'.*',  # match any host
        [
            (url_path_join(url, '/create_gist'), GistHandler, params),
            (url_path_join(url, '/download_notebook'),
             DownloadNotebookHandler),
            (url_path_join(url, '/load_user_gists'), LoadGistHandler, params),
        ]
    )
