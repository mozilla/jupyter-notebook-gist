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

function get_base_path() {
    var loc = window.location;
    var proto = loc.protocol;
    var host = loc.hostname;
    var port = loc.port;

    var base = proto + "//" + host;
    if (parseInt(port) != 80) {
        base += ":" + port;
    }
    console.log("Base path: " + base);
    return base;
}

function url_path_split(path) {
    var idx = path.lastIndexOf('/');
    if (idx === -1) {
        return ['', path];
    } else {
        return [ path.slice(0, idx), path.slice(idx + 1) ];
    }
}

define(function () {
    var github_redirect_uri = get_base_path() + "/create_gist";
    var gist_notebook = function () {
        // save the notebook and create a checkpoint
        Jupyter.notebook.save_checkpoint();

        var github_client_id = Jupyter.notebook.config.data.oauth_client_id;
        // get notebook path and encode it in base64

        // Characters like # get decoded by the github API and will mess up
        // getting the file path on the server if we use URI percent encoding,
        // so we use base64 instead
        var nb_path = window.btoa(Jupyter.notebook.base_url + Jupyter.notebook.notebook_path);

        // start OAuth dialog
        window.open("https://github.com/login/oauth/authorize?client_id=" + github_client_id +
          "&scope=gist&redirect_uri=" + github_redirect_uri + "?nb_path=" + nb_path);
    };

    var load_from_url = function() {
        var gist_url = prompt("Enter a Gist URL");
        // TODO: check that it's a valid URL

        var gist_url_parts = gist_url.split('/');
        var gist_id = gist_url_parts[gist_url_parts.length-1];

        var url = "https://api.github.com/gists/" + gist_id;

        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4 && xhr.status == 200) {
                var res = JSON.parse(xhr.responseText);

                for (var filename in res.files) {
                    if (!res.files.hasOwnProperty(filename)) continue;

                    if (filename.endsWith('.ipynb')) {
                        var post_xhr = new XMLHttpRequest();

                        var nb_info = {
                            nb_url: res.files[filename].raw_url,
                            nb_name: filename
                        }
                        post_xhr.open("POST",  "/download_gist", true);
                        post_xhr.setRequestHeader('Content-Type', 'application/json');
                        post_xhr.onload = function () {
                            console.log(this.responseText);
                            window.open(url_path_split(Jupyter.notebook.notebook_path)[0] + this.responseText);
                        };
                        post_xhr.send(JSON.stringify(nb_info));



                    }
                }

                console.log(res);
            } else if (xhr.readyState == 4 && xhr.status == 404) {
                alert("Gist not found")
            } else if (xhr.readyState == 4) {
                alert("Couldn't load Gist.")
            }
        }
        xhr.open("GET", url, true);
        xhr.send(null);
    }

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
                }, {
                    'label'   : 'load notebook from gist URL',
                    'icon'    : 'fa-link',
                    'callback': load_from_url,
                    'id'      : 'load_gist_from_url'
                }
            ]);
        }
    };

    var load_ipython_extension = function () {
        gist_button();
    };

    return {
        load_ipython_extension: load_ipython_extension
    };
}

);
