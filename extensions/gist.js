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

    var github_client_id = "a179eb5f91edcc084d8b";
    var github_redirect_uri = "http://localhost:8888/create_gist";

    var gist_notebook = function () {

        // save the notebook and create a checkpoint
        IPython.notebook.save_checkpoint();

        // get notebook path and encode it in base64
        
        // Characters like # get decoded by the github API and will mess up 
        // getting the file path on the server if we use URI percent encoding,
        // so we use base64 instead
        var nb_path = window.btoa(Jupyter.notebook.base_url + Jupyter.notebook.notebook_path);

        // start OAuth dialog
        window.open("https://github.com/login/oauth/authorize?client_id=" + github_client_id +
          "&scope=gist&redirect_uri=" + github_redirect_uri + "?nb_path=" + nb_path);
    };

    var gist_button = function () {
        if (!Jupyter.toolbar) {
            $([Jupyter.events]).on("app_initialized.NotebookApp", gist_button);
            return;
        }
        if ($("#gist_notebook").length === 0) {
            Jupyter.toolbar.add_buttons_group([
                {
                    'label'   : 'save notebook as gist',
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
