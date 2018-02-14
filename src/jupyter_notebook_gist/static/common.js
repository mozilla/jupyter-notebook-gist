define([
    'base/js/namespace',
    'base/js/utils',
    'moment',
    'services/config'
], function(Jupyter, utils, moment, config) {
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

    function is_url_valid(url) {
        return /^(https?|s?ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(url);
    }

    var github_redirect_uri = (
        get_base_path() +
        utils.get_body_data("baseUrl") +
        "create_gist");

    // Get the server side path to download to.
    var get_download_path = function() {
        if (Jupyter.hasOwnProperty('notebook')) {
            // On a notebook page
            return utils.url_path_split(Jupyter.notebook.notebook_path)[0];
        } else if (Jupyter.hasOwnProperty('notebook_list')) {
            return Jupyter.notebook_list.notebook_path;
        } else {
            return '';
        }
    }

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
            nb_name: window.btoa(
                utils.url_path_join(get_download_path(), name)),
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
                window.open(
                    utils.url_path_join(
                        utils.get_body_data("baseUrl"),
                        'notebooks',
                        encodeURIComponent(xhr.responseText)));
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
        };

        var gist_api_url = "https://api.github.com/users/" + github_username + "/gists";

        if (!is_url_valid(gist_api_url)) {
            alert('GitHub username is invalid.');
        };

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
        if (auth_window === undefined) return;
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
        var redirect_uri = (
            get_base_path() +
                utils.get_body_data("baseUrl") +
                "load_user_gists");
        get_client_id(function(client_id) {
            auth_window = window.open(
                "https://github.com/login/oauth/authorize?client_id=" + client_id +
                    "&scope=gist&redirect_uri=" + redirect_uri, "", "width=550, height=500");
        });
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
        };

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

    var get_client_id = function(callback) {
        var common_options = {
            base_url: utils.get_body_data("baseUrl"),
            notebook_path: utils.get_body_data("notebookPath"),
        };
        var cfg = new config.ConfigSection('notebook', common_options);
        cfg.loaded.then(function() {
            callback(cfg.data.oauth_client_id);
        });
        cfg.load();
    }

    var is_valid_client_id = function(client_id) {
        if (client_id === "my_client_id" || client_id === null || client_id === undefined) {
            return false;
        }
        return true;
    }

    return {
        github_redirect_uri: github_redirect_uri,
        load_from_url: load_from_url,
        load_public_user_gists: load_public_user_gists,
        load_all_user_gists: load_all_user_gists,
        get_client_id: get_client_id,
        is_valid_client_id: is_valid_client_id,
        setup_info: setup_info
    };
});
