from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler

class CreateGistHandler(IPythonHandler):
    def get(self):
        self.finish('TODO: Create a gist')

def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/create_gist')
    web_app.add_handlers(host_pattern, [(route_pattern, CreateGistHandler)])
