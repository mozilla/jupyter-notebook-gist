### jupyter-notebook-gist

Create a gist from the Jupyter Notebook UI.

To install, simply run `pip install jupyter-notebook-gist`. Alternatively, clone/download the project and run `pip install .` from a shell in the project's root directory.

After installing, edit your `jupyter_notebook_config.py` file to specify the github client id and secret:

If your `jupyter_notebook_config.py` file does not exist, you can create one by running `jupyter notebook --generate-config`. You can check the location of this file by running `jupyter --config-dir`.

```python
from notebook.services.config import ConfigManager
c = get_config()
cm = ConfigManager()
c.NotebookApp.oauth_client_id = "my_client_id"         # FIXME
c.NotebookApp.oauth_client_secret = "my_client_secret" # FIXME
cm.update('notebook', {"oauth_client_id": c.NotebookApp.oauth_client_id})
```

Replace the vars above with a working client_id / secret. You can create one
[here](https://github.com/settings/applications). Here's an [example of an OAuth application](https://cloud.githubusercontent.com/assets/969479/14916551/add90efc-0df0-11e6-8cfb-277754a48b66.png) created by @mreid-moz for testing.

Then run `jupyter notebook` from the repo root.

NOTE: Uninstalling jupyter-notebook-gist via `pip uninstall jupyter-notebook-gist` will uninstall the server extension but leave the client extension in a partially installed state. To fully remove the extension:

1. Run `pip uninstall jupyter-notebook-gist`
2. Delete `gist.js` from your `nbextensions` folder.
3. Delete any references to `jupyter-notebook-gist.create_gist` in `jupyter_notebook_config.json` (in your .jupyter directory)
4. Delete any references to `gist` in `notebook.json` (in .jupyter/nbconfig)
