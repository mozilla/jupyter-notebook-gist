import six
from traitlets.config import LoggingConfigurable
from traitlets.traitlets import Unicode


class NotebookGist(LoggingConfigurable):

    oauth_client_id = Unicode(
        '',
        help='The GitHub application OAUTH client ID',
    ).tag(config=True)

    oauth_client_secret = Unicode(
        '',
        help='The GitHub application OAUTH client secret',
    ).tag(config=True)

    def __init__(self, *args, **kwargs):
        self.config_manager = kwargs.pop('config_manager')
        super(NotebookGist, self).__init__(*args, **kwargs)
        # update the frontend settings with the currently passed
        # OAUTH client id
        client_id = self.config.NotebookGist.oauth_client_id
        if not isinstance(client_id, six.string_types):
            client_id = None
        self.config_manager.update('notebook', {
            'oauth_client_id': client_id,
        })
