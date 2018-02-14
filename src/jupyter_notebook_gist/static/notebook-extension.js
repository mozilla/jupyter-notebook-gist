
define([
    'base/js/namespace',
    'nbextensions/jupyter-notebook-gist/common'
], function (Jupyter, common) {
    var gist_notebook = function() {
        // Save the notebook and create a checkpoint to ensure that we create
        // the gist using the most up-to-date content
        Jupyter.notebook.save_checkpoint();

        var github_client_id = Jupyter.notebook.config.data.oauth_client_id;
        // Get notebook path and encode it in base64
        // Characters like # get decoded by the github API and will mess up
        // getting the file path on the server if we use URI percent encoding,
        // so we use base64 instead
        var nb_path = window.btoa(Jupyter.notebook.base_url + Jupyter.notebook.notebook_path);

        // Start OAuth dialog
        window.open("https://github.com/login/oauth/authorize?client_id=" + github_client_id +
                    "&scope=gist&redirect_uri=" + common.github_redirect_uri +
                    "?nb_path=" + nb_path);
    }

    var create_gist_buttons = function () {
        if (!Jupyter.toolbar) {
            $([Jupyter.events]).on("app_initialized.NotebookApp", create_gist_buttons);
            return;
        }

        common.get_client_id(function(client_id) {
            if (!common.is_valid_client_id(client_id)) {
                Jupyter.toolbar.add_buttons_group([{
                    'label':    'jupyter-notebook-gist setup',
                    'icon':     'fa-github',
                    'callback': common.setup_info,
                    'id':       'setup_info'
                }]);

                return;
            }

            if ($("#gist_notebook").length === 0) {
                Jupyter.toolbar.add_buttons_group([
                    {
                        'label'   : 'save notebook as gist',
                        'icon'    : 'fa-github',
                        'callback': gist_notebook,
                        'id'      : 'gist_notebook'
                    }, {
                        'label'   : 'load notebook from URL',
                        'icon'    : 'fa-link',
                        'callback': common.load_from_url,
                        'id'      : 'load_notebook_from_url'
                    }, {
                        'label'   : 'load public user gists',
                        'icon'    : 'fa-list-alt',
                        'callback': common.load_public_user_gists,
                        'id'      : 'load_public_user_gists',
                    }, {
                        'label'   : 'load all user gists',
                        'icon'    : 'fa-list',
                        'callback': common.load_all_user_gists,
                        'id'      : 'load_all_user_gists',
                    }
                ]);
            }
        });
    };

    var load_ipython_extension = function () {
        create_gist_buttons();
    };

    return {
        load_ipython_extension: load_ipython_extension
    };
});
