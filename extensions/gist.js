/*
Add this file to $(jupyter data-dir)/nbextensions/gist.js
And load it with:

require(["nbextensions/gist"], function (gist_extension) {
    console.log('gist extension loaded');
    gist_extension.load_ipython_extension();
});

or add the following to your jupyter_notebook_config.py to
load for every notebook

from notebook.services.config import ConfigManager
cm = ConfigManager()
cm.update('notebook', {"load_extensions": {"gist": True}})

*/
define( function () {
    
    var github_client_id = "bd8256a4bcc8042c8152";
    var github_redirect_uri = "http://localhost:8888/authorize";

    var gist_notebook = function () {
        window.open("https://github.com/login/oauth/authorize?client_id=" + github_client_id +
          "&scope=gist&redirect_uri=" + github_redirect_uri);
    };

    var gist_button = function () {
        if (!IPython.toolbar) {
            $([IPython.events]).on("app_initialized.NotebookApp", gist_button);
            return;
        }
        if ($("#gist_notebook").length === 0) {
            IPython.toolbar.add_buttons_group([
                {
                    'label'   : 'Save Notebook as gist',
                    'icon'    : 'fa-github',
                    'callback': gist_notebook,
                    'id'      : 'gist_notebook'
                },
            ]);
        }
    };
    
    var load_ipython_extension = function () {
        gist_button();
    };
    
    return {
        load_ipython_extension: load_ipython_extension
    }; 
});
