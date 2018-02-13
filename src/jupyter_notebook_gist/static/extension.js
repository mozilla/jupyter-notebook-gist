/*
Run to enable this:

jupyter serverextension enable --py jupyter_notebook_gist
jupyter nbextension install --py jupyter_notebook_gist
jupyter nbextension enable --py jupyter_notebook_gist
*/
//
// Regular Expression for URL validation
//
// Author: Diego Perini
// Updated: 2010/12/05
// License: MIT
//
// Copyright (c) 2010-2013 Diego Perini (http://www.iport.it)
//
// Permission is hereby granted, free of charge, to any person
// obtaining a copy of this software and associated documentation
// files (the "Software"), to deal in the Software without
// restriction, including without limitation the rights to use,
// copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the
// Software is furnished to do so, subject to the following
// conditions:
//
// The above copyright notice and this permission notice shall be
// included in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
// EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
// OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
// NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
// HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
// WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
// OTHER DEALINGS IN THE SOFTWARE.
//
// the regular expression composed & commented
// could be easily tweaked for RFC compliance,
// it was expressly modified to fit & satisfy
// these test for an URL shortener:
//
//   http://mathiasbynens.be/demo/url-regex
//
// Notes on possible differences from a standard/generic validation:
//
// - utf-8 char class take in consideration the full Unicode range
// - TLDs have been made mandatory so single names like "localhost" fails
// - protocols have been restricted to ftp, http and https only as requested
//
// Changes:
//
// - IP address dotted notation validation, range: 1.0.0.0 - 223.255.255.255
//   first and last IP address of each class is considered invalid
//   (since they are broadcast/network addresses)
//
// - Added exclusion of private, reserved and/or local networks ranges
//
// - Made starting path slash optional (http://example.com?foo=bar)
//
// - Allow a dot (.) at the end of hostnames (http://example.com.)
//
// Compressed one-line versions:
//
// Javascript version
//
// /^(?:(?:https?|ftp):\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,}))\.?)(?::\d{2,5})?(?:[/?#]\S*)?$/i
//
// PHP version
//
// _^(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\x{00a1}-\x{ffff}0-9]-*)*[a-z\x{00a1}-\x{ffff}0-9]+)(?:\.(?:[a-z\x{00a1}-\x{ffff}0-9]-*)*[a-z\x{00a1}-\x{ffff}0-9]+)*(?:\.(?:[a-z\x{00a1}-\x{ffff}]{2,}))\.?)(?::\d{2,5})?(?:[/?#]\S*)?$_iuS
//
var re_weburl = new RegExp(
    "^" +
    // protocol identifier
    "(?:(?:https?|ftp)://)" +
    // user:pass authentication
    "(?:\\S+(?::\\S*)?@)?" +
    "(?:" +
      // IP address exclusion
      // private & local networks
      "(?!(?:10|127)(?:\\.\\d{1,3}){3})" +
      "(?!(?:169\\.254|192\\.168)(?:\\.\\d{1,3}){2})" +
      "(?!172\\.(?:1[6-9]|2\\d|3[0-1])(?:\\.\\d{1,3}){2})" +
      // IP address dotted notation octets
      // excludes loopback network 0.0.0.0
      // excludes reserved space >= 224.0.0.0
      // excludes network & broacast addresses
      // (first & last IP address of each class)
      "(?:[1-9]\\d?|1\\d\\d|2[01]\\d|22[0-3])" +
      "(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5])){2}" +
      "(?:\\.(?:[1-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-4]))" +
    "|" +
      // host name
      "(?:(?:[a-z\\u00a1-\\uffff0-9]-*)*[a-z\\u00a1-\\uffff0-9]+)" +
      // domain name
      "(?:\\.(?:[a-z\\u00a1-\\uffff0-9]-*)*[a-z\\u00a1-\\uffff0-9]+)*" +
      // TLD identifier
      "(?:\\.(?:[a-z\\u00a1-\\uffff]{2,}))" +
      // TLD may end with dot
      "\\.?" +
    ")" +
    // port number
    "(?::\\d{2,5})?" +
    // resource path
    "(?:[/?#]\\S*)?" +
  "$", "i"
);

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

function is_url_valid(url) {
    return re_weburl.test(url);
}

define([
    'base/js/namespace',
    'base/js/utils',
    'moment'
], function (Jupyter, utils, moment) {
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
        var url = prompt("Enter the URL to a Gist or a .ipynb.");
        if (url == "" || url == null) {
            // prompt() returns "" if empty value, or null
            // if user clicked cancel, want to abort in either case
            return;
        }
        if (!is_url_valid(url)) {
            alert('Invalid URL.');
            return;
        }
        var parser = document.createElement('a');
        parser.href = url;
        if (parser.hostname.indexOf('gist.github.com') > -1) {
            // this is a gist URL, extract the raw_url for the .ipynb file
            load_from_gist_url(url);
        } else if (url.indexOf('.ipynb', url.length - '.ipynb'.length) !== -1) {
            // URL is a raw .ipynb file
            var nb_pathname_parts = parser.pathname.split('/');
            var filename = decodeURIComponent(nb_pathname_parts[nb_pathname_parts.length - 1]);
            download_nb_on_server(url, filename, false);
        }
    }

    var load_from_gist_url = function(url) {
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
    }

    var download_nb_on_server = function(url, name, force_download) {
        var nb_info = {
            nb_url: url,
            nb_name: window.btoa(name),
            force_download: force_download
        }
        utils.ajax({
            url: "/download_notebook",
            type: "POST",
            dataType: "json",
            data: JSON.stringify(nb_info)
        }).fail(function(xhr, textStatus) {
            if (xhr.status == 409) {
                // 409 Conflict
                // used if file already exists
                var newname = prompt(
                    "File already exists. Please enter a new name.\n" +
                    "Note: This may overwrite existing files.",
                    name);
                if (newname == "" || newname == null) {
                    // prompt() returns "" if empty value, or null
                    // if user clicked cancel, want to abort in either case
                    return;
                }
                download_nb_on_server(url, newname, true);
            } else if (xhr.status == 200) {
                window.open(url_path_split(Jupyter.notebook.notebook_path)[0] + encodeURIComponent(this.responseText));
            } else if (xhr.status == 400) {
                alert("File did not download");
            }
        });
    }

    var load_public_user_gists = function() {
        // TODO: Figure out how to deal with page redirect when obtaining GitHub access code
        // For now, prompt user for their GitHub username to load their public gists
        var github_username = prompt("Please enter your GitHub username in order to retrieve your public gists.");
        if (github_username == "" || github_username == null) {
            // Do not send a request if user did not input anything
            return;
        }

        var gist_api_url = "https://api.github.com/users/" + github_username + "/gists";

        if (!is_url_valid(gist_api_url)) {
            alert('GitHub username is invalid.');
        }

        var xhr = new XMLHttpRequest();
        xhr.open("GET", gist_api_url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onload = function(){
            Jupyter.dialog.modal({
                title: "Gists",
                body: format_user_gists(xhr.responseText),
                buttons: {
                    "OK": {}
                }
            });
        };
        xhr.send(null);
    };

    // Listen for the response message containing the user's gists
    // that is sent from the LoadGistHandler
    var auth_window;
    window.addEventListener('message', function(event) {
        if (event.origin != get_base_path()) return;
        auth_window.close();
        Jupyter.dialog.modal({
            title: "All User Gists",
            body: format_user_gists(window.atob(event.data)),
            buttons: {
                "OK": {}
            }
        })
    });

    var load_all_user_gists = function () {
        var redirect_uri = get_base_path() + "/load_user_gists"

        var github_client_id = Jupyter.notebook.config.data.oauth_client_id;
        var nb_path = window.btoa(Jupyter.notebook.base_url + Jupyter.notebook.notebook_path);

        auth_window = window.open("https://github.com/login/oauth/authorize?client_id=" + github_client_id +
                                  "&scope=gist&redirect_uri=" + redirect_uri, "", "width=550, height=500");
    };


    var format_user_gists = function(responseText) {
        var body = $('<table/>').attr({class: "table", id: "my_table"});
        var head = $('<thead/>');
        var header = $('<tr/>').addClass("row list_header");
        header.append("<th>Filename</th>");
        header.append("<th>Description</th>");
        header.append("<th>Last Updated</th>");
        header.append("<th>Open Notebook</th>");
        head.append(header);
        body.append(head);
        var row, button, files, last_updated, pretty_date;
        var json_response = JSON.parse(responseText);
        // create flag to check if a notebook has been loaded
        var notebook_loaded = false;

        for (var i = 0; i < json_response.length; i++) {
            files = json_response[i].files;
            // Only load notebook gists
            if (!files[Object.keys(files)[0]].filename.endsWith('.ipynb')) continue;
            notebook_loaded = true;

            // Use same date formatting as SaveWidget's _render_checkpoint
            last_updated = moment(json_response[i].updated_at);
            var tdelta = Math.ceil(new Date() - last_updated);
            if (tdelta < utils.time.milliseconds.d) {
                // less than 24 hours old, use relative date
                pretty_date = last_updated.fromNow();
            } else {
                // otherwise show calendar
                // <Today | yesterday|...> at hh,mm,ss
                pretty_date = last_updated.calendar();
            }

            // Create row containing gist information
            row = $('<tr/>').addClass("list_item row");
            row.append("<td>" + files[Object.keys(files)[0]].filename + "</td>");
            row.append("<td>" + json_response[i].description + "</td>");
            row.append("<td>" + pretty_date + "</td>");
            // Create button to load notebook
            button_td = $('<td/>');
            button = $('<button>Open</button>').addClass("btn btn-default btn-sm");
            button.click({url: json_response[i].html_url}, load_gist_from_click);
            button.appendTo(button_td);
            row.append(button_td);
            body.append(row);
        }

        // Inform user if no public notebooks were found
        if (!notebook_loaded) {
            row = $('<tr/>').addClass("list_item row");
            row_message = $('<td/>').attr("colspan", "4");
            row_message.text('No public notebooks found.');
            row.append(row_message);
            body.append(row);
        }

        return body;
    };

    var load_gist_from_click = function(event) {
        var url = event.data.url;
        load_from_gist_url(url);
    };

    var setup_info = function() {
        Jupyter.dialog.modal({
            title: "Configuration Incomplete",
            body: "You haven't configured your GitHub Client ID in your jupyter_notebook_config.py file. Please set the Client ID and Secret before using this plugin. See <a href=\"https://github.com/mozilla/jupyter-notebook-gist/blob/master/README.md\">the README</a> for more info.",
            buttons: {
                "OK": {}
            },
            sanitize: false
        });
    }

    var is_valid_client_id = function(client_id) {
        if (client_id === "my_client_id" || client_id === null || client_id === undefined) {
            return false;
        }
        return true;
    }

    var gist_button = function () {
        if (!Jupyter.toolbar) {
            $([Jupyter.events]).on("app_initialized.NotebookApp", gist_button);
            return;
        }

        if (!is_valid_client_id(Jupyter.notebook.config.data.oauth_client_id)) {
            Jupyter.toolbar.add_buttons_group([{
                'label':    'jupyter-notebook-gist setup',
                'icon':     'fa-github',
                'callback': setup_info,
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
                    'callback': load_from_url,
                    'id'      : 'load_notebook_from_url'
                }, {
                    'label'   : 'load public user gists',
                    'icon'    : 'fa-list-alt',
                    'callback': load_public_user_gists,
                    'id'      : 'load_public_user_gists',
                }, {
                    'label'   : 'load all user gists',
                    'icon'    : 'fa-list',
                    'callback': load_all_user_gists,
                    'id'      : 'load_all_user_gists',
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
});
