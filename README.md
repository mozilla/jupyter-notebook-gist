### jupyter-notebook-gist

Create a gist from the Jupyter Notebook UI.

Edit your `jupyter_notebook_config.py` file to add:

```python
import os
import sys
sys.path.append(os.getcwd())
c = get_config()
c.NotebookApp.server_extensions = [
    'create_gist'
]
```

Then run `jupyter notebook`
