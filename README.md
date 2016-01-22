### jupyter-notebook-gist

Create a gist from the Jupyter Notebook UI.

Edit your `jupyter_notebook_config.py` file to specify the github client id and secret:

```python
from notebook.services.config import ConfigManager
c = get_config()
cm = ConfigManager()
c.NotebookApp.oauth_client_id = "my_client_id"         # FIXME
c.NotebookApp.oauth_client_secret = "my_client_secret" # FIXME
cm.update('notebook', {"oauth_client_id": c.NotebookApp.oauth_client_id})
```

Replace the vars above with a working client_id / secret. You can create one
[here](https://github.com/settings/applications).

Then run `jupyter notebook` from the repo root.
