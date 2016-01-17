/*
Add this file to $(jupyter --data-dir)/nbextensions/gist.js
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
          "&scope=gist&redirect_uri=" + github_redirect_uri + "?nb_path=" + nb_path);
    };

    var load_from_url = function() {
        var url = prompt("Enter a Gist URL");
        if (url == "" || url == null) {
            // prompt() returns "" if empty value, or null 
            // if user clicked cancel, want to abort in either case
            return;
        }
        // TODO: check that it's a valid URL
        var parser = document.createElement('a');
        parser.href = url;
        if (parser.hostname.indexOf('gist.github.com') > -1) {
            // this is a gist URL, extract the raw_url for the .ipynb file
            var gist_url_parts = url.split('/');
            var gist_id = gist_url_parts[gist_url_parts.length-1];

            var gist_api_url = "https://api.github.com/gists/" + gist_id;

            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
                if (xhr.readyState == XMLHttpRequest.DONE) {
                    if (xhr.status == 200) {
                        var res = JSON.parse(xhr.responseText);
                        for (var filename in res.files) {
                            if (!res.files.hasOwnProperty(filename)) continue;
                            if (filename.endsWith('.ipynb')) {
                                download_nb_on_server(res.files[filename].raw_url, filename, false);
                            }
                        }
                        console.log(res);
                    } else if (xhr.status == 404) {
                        alert("Gist not found")
                    } else {
                        alert("Couldn't load Gist.")
                    }
                }
            }
            xhr.open("GET", gist_api_url, true);
            xhr.send(null);
        } else if (url.indexOf('.ipynb', url.length - '.ipynb'.length) !== -1) {
            // URL is a raw .ipynb file
            var nb_pathname_parts = parser.pathname.split('/');
            var filename = decodeURIComponent(nb_pathname_parts[nb_pathname_parts.length - 1]);
            download_nb_on_server(url, filename, false);
        }
    }

    var download_nb_on_server = function(url, name, force_download) {
        var xhr = new XMLHttpRequest();
        var nb_info = {
            nb_url: url,
            nb_name: window.btoa(name),
            force_download: force_download
        }
        xhr.open("POST",  "/download_notebook", true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function () {
            if (xhr.status == 409) {
                // 409 Conflict
                // used if file already exists
                var newname = prompt("File already exists. Please enter a new name.\nNote: This may overwrite existing files.", 
                                     name);
                if (newname == "" || newname == null) {
                    // prompt() returns "" if empty value, or null 
                    // if user clicked cancel, want to abort in either case
                    return;
                }
                download_nb_on_server(url, newname, true);
            } else if (xhr.status == 200) {
                window.open(url_path_split(Jupyter.notebook.notebook_path)[0] + encodeURIComponent(this.responseText));
            }
        };
        xhr.send(JSON.stringify(nb_info));
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
        console.log("loaded gist.js");
    };

    return {
        load_ipython_extension: load_ipython_extension
    };
});
