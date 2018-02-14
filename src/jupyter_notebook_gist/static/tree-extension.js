define([
    'nbextensions/jupyter-notebook-gist/common'
], function (common) {
    function add_toolbar_button(group, label, icon, callback, id) {
        group.append(
            $('<button/>')
                .attr('class', 'btn btn-default')
                .attr('title', label)
                .attr('id', id)
                .on('click', callback)
                .append(
                    $('<i/>')
                        .attr('class', icon + ' fa'))
                .append(
                    $('<span/>')
                        .attr('class', 'toolbar-btn-label')
                        .text(label)
                )
        )
    }

    function add_gist_buttons() {
        var group = $('<div/>')
            .attr('class', 'btn-group')
            .appendTo('#notebook_toolbar');

        common.get_client_id(function(client_id) {
            if (!common.is_valid_client_id(client_id)) {
                add_toolbar_button(
                    group,
                    "jupyter-notebook-gist setup",
                    "fa-github",
                    common.setup_info,
                    "setup_info");
            } else {
                add_toolbar_button(
                    group,
                    "load notebook from URL",
                    "fa-link",
                    common.load_from_url,
                    "load_notebook_from_url");

                add_toolbar_button(
                    group,
                    "load public user gists",
                    "fa-list-alt",
                    common.load_public_user_gists,
                    "load_public_user_gists");

                add_toolbar_button(
                    group,
                    "load all user gists",
                    "fa-list",
                    common.load_all_user_gists,
                    "load_add_user_gists");
            }
        });
    }

    var load_ipython_extension = function () {
        add_gist_buttons();
    };

    return {
        load_ipython_extension: load_ipython_extension
    };
});
