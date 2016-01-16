### jupyter-notebook-gist

Create a gist from the Jupyter Notebook UI.

Edit your `jupyter_notebook_config.py` file to add:

```python
import os
import sys
from notebook.services.config import ConfigManager

# Load extensions from the current directory
sys.path.append(os.getcwd())

# Register our server extension
c = get_config()
c.NotebookApp.server_extensions = [
    'create_gist'
]

# Make the client id and secret available to the server.
c.NotebookApp.oauth_client_id = "my_client_id"         # FIXME
c.NotebookApp.oauth_client_secret = "my_client_secret" # FIXME

# Load the js extension and set some config values
cm = ConfigManager()
cm.update('notebook', {"load_extensions": {"gist": True}})

# Make the client id *only* available to the client.
cm.update('notebook', {"oauth_client_id": c.NotebookApp.oauth_client_id})
```

Replace the vars above with a working client_id / secret.

Then run `jupyter notebook` from the repo root.
