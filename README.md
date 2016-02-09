### jupyter-notebook-gist

Create a gist from the Jupyter Notebook UI.

To install, simply run `pip install jupter-notebook-gist`. Alternatively, clone/download the project and run `pip install .` from a shell in the project's root directory.

If you have previously installed jupyter-notebook-gist using the old method (which involved manually copying `gist.js` into the
right directory), clean out the following before installing:

- Any jupyter-notebook-gist data in `jupyter_notebook_config.py` (if the file exists) that is not in the config code below
- `gist.js`, which is located in one of your nbextensions directories

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
[here](https://github.com/settings/applications).

Then run `jupyter notebook` from the repo root.

For developers, you can uninstall the extension by deleting the jupyter-notebook-gist directory and `.egg-info` file from your
Python installation's `site-packages` folder.
