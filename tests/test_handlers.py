import base64
import io
import os
import unittest

import tornado
from jupyter_notebook_gist.handlers import (extract_code_from_args,
                                            extract_notebook_path_from_args,
                                            get_notebook_contents,
                                            get_notebook_filename,
                                            helper_find_existing_gist_by_name,
                                            helper_request_access_token,
                                            raise_error, raise_github_error,
                                            verify_gist_response)
from nbformat import write
from nbformat.v4 import new_markdown_cell, new_notebook


class TestError(unittest.TestCase):
    normal_error = "HTTP 500: Internal Server Error (ERROR: "
    github_error = normal_error + "Github returned the following: "
    error = "This is a test error"

    def test_error(self):
        try:
            raise_error(self.error)
        except tornado.web.HTTPError as exc:
            assert (self.normal_error + self.error) in str(exc)
        else:
            assert False

    def test_error_empty(self):
        try:
            raise_error("")
        except tornado.web.HTTPError as exc:
            assert self.normal_error in str(exc)
        else:
            assert False

    def test_github_error(self):
        try:
            raise_github_error("This is a test error")
        except tornado.web.HTTPError as exc:
            assert self.github_error + self.error in str(exc)
        else:
            assert False

    def test_github_error_empty(self):
        try:
            raise_github_error("")
        except tornado.web.HTTPError as exc:
            assert self.github_error in str(exc)
        else:
            assert False


class TestBaseHandler(unittest.TestCase):
    auth_code_error = ("Couldn't extract GitHub authentication code "
                       "from response")
    notebook_path_error = "Couldn't extract notebook path from response"
    notebook_filemame_error = "Problem with notebook file name"
    notebook_export_error = "Couldn't export notebook contents"
    access_token_error = ("Couldn't extract needed info from GitHub "
                          "access token response")
    multiple_gists_error = ("You had multiple gists with the same name as "
                            "this notebook. Aborting.")
    invalid_url_error = ("Couldn't get the URL for the gist that was just "
                         "updated")
    github_error = "Github returned the following: "

    def assert_throws_error(self, func, args, error):
        try:
            func(args)
        except tornado.web.HTTPError as exc:
            assert error in str(exc)
        else:
            assert False

    # extract_code_from args tests
    def test_extract_code_from_args_valid(self):

        expected_code = "some code"
        expected_code_bytes = str.encode(expected_code)
        args = {"code": [expected_code_bytes]}

        assert extract_code_from_args(args) == expected_code

    def test_extract_code_from_args_none_in_list(self):

        args = {"code": [None]}

        self.assert_throws_error(extract_code_from_args, args,
                                 self.auth_code_error)

    def test_extract_code_from_args_none(self):

        args = None

        self.assert_throws_error(extract_code_from_args, args,
                                 self.auth_code_error)

    def test_extract_code_from_args_code_is_none(self):

        args = {"code": None}

        self.assert_throws_error(extract_code_from_args, args,
                                 self.auth_code_error)

    def test_extract_code_from_args_code_is_char(self):

        expected_code = "a"
        expected_code_bytes = str.encode(expected_code)
        args = {"code": [expected_code_bytes]}

        assert extract_code_from_args(args) == expected_code

    def test_extract_code_from_args_code_is_empty_str(self):

        args = {"code": [b""]}

        self.assert_throws_error(extract_code_from_args, args,
                                 self.auth_code_error)

    def test_extract_code_from_args_long_code_list(self):

        args = {"code": [b"aa", b"aa"]}

        self.assert_throws_error(extract_code_from_args, args,
                                 self.auth_code_error)

    def test_extract_code_from_args_with_error(self):

        error = "This is an error!"

        args = {"error_description": error}

        self.assert_throws_error(extract_code_from_args, args,
                                 self.github_error + error)

    def test_extract_code_from_args_with_empty_error(self):

        args = {"error_description": ""}

        self.assert_throws_error(extract_code_from_args, args,
                                 self.github_error)

    # This test succeeds the error description part, but fails the access code
    def test_extract_code_from_args_with_none_error(self):

        args = {"error_description": None}

        self.assert_throws_error(extract_code_from_args, args,
                                 self.auth_code_error)

    # ############## end of extract_code_from_args tests #################

    # extract_notebook_path_from_args tests
    def test_extract_notebook_path_from_args_valid(self):

        # Make a string, encode it into bytes via encode, then convert
        # to base 64 since thats what github gives
        somePath = "somepath"
        encodedPath = somePath.encode('utf-8')
        encodedPath = base64.b64encode(encodedPath)

        args = {"nb_path": [encodedPath]}

        assert extract_notebook_path_from_args(args) == somePath

    def test_extract_notebook_path_from_args_none_in_list(self):

        args = {"nb_path": [None]}

        self.assert_throws_error(extract_notebook_path_from_args,
                                 args, self.notebook_path_error)

    def test_extract_notebook_path_from_args_none(self):

        args = None

        self.assert_throws_error(extract_notebook_path_from_args,
                                 args, self.notebook_path_error)

    def test_extract_notebook_path_from_args_code_is_none(self):

        args = {"nb_path": None}

        self.assert_throws_error(extract_notebook_path_from_args,
                                 args, self.notebook_path_error)

    def test_extract_notebook_path_from_args_code_is_char(self):

        # Make a string, encode it into bytes via encode, then convert to
        # base 64 since thats what github gives
        somePath = "a"
        encodedPath = somePath.encode('utf-8')
        encodedPath = base64.b64encode(encodedPath)

        args = {"nb_path": [encodedPath]}

        assert extract_notebook_path_from_args(args) == somePath

    def test_extract_notebook_path_from_args_code_is_empty_str(self):

        args = {"nb_path": [b""]}

        self.assert_throws_error(extract_notebook_path_from_args,
                                 args, self.notebook_path_error)

    def test_extract_notebook_path_from_args_long_code_list(self):

        somePathA = "a"
        encodedPathA = somePathA.encode('utf-8')
        encodedPathA = base64.b64encode(encodedPathA)

        somePathB = "b"
        encodedPathB = somePathB.encode('utf-8')
        encodedPathB = base64.b64encode(encodedPathB)

        args = {"code": [encodedPathA, encodedPathB]}

        self.assert_throws_error(extract_notebook_path_from_args,
                                 args, self.notebook_path_error)

    def test_extract_notebook_path_from_args_with_error_(self):

        error = "This is an error!"
        args = {"error_description": error}

        self.assert_throws_error(extract_notebook_path_from_args,
                                 args, self.github_error + error)

    def test_extract_notebook_path_from_args_with_empty_error_(self):

        args = {"error_description": ""}

        self.assert_throws_error(extract_notebook_path_from_args,
                                 args, self.github_error)

    # This test succeeds the error description part, but fails the extraction
    def test_extract_notebook_path_from_args_with_none_error_(self):

        args = {"error_description": None}

        self.assert_throws_error(extract_notebook_path_from_args,
                                 args, self.notebook_path_error)

    # ###############end of extract_notebook_path_from_args tests

    # request_access_token tests

    # how should we approach testing posting?

    # def test_request_access_token
    # ###############end of request_access_token tests

    # get_notebook_filename tests

    def test_get_notebook_filename_none(self):

        self.assert_throws_error(get_notebook_filename, None,
                                 self.notebook_filemame_error)

    def test_get_notebook_filename_empty(self):

        self.assert_throws_error(get_notebook_filename, "",
                                 self.notebook_filemame_error)

    def test_get_notebook_filename_no_extension(self):

        filename = "somefile"

        assert get_notebook_filename(filename), (filename == filename)

    def test_get_notebook_filename_extension(self):

        filename_no_ext = "somefile"
        filename = filename_no_ext + ".abc"

        assert get_notebook_filename(filename) == (filename, filename_no_ext)

    def test_get_notebook_filename_path_no_extension(self):

        filename = "somefile"

        assert get_notebook_filename("/a/b/c/" + filename) == (filename, filename)

    def test_get_notebook_filename_path_extension(self):

        filename_no_ext = "somefile"
        filename = filename_no_ext + ".abc"

        assert get_notebook_filename("/a/b/c/" + filename) == (filename, filename_no_ext)

    def test_get_notebook_filename_double_dot(self):

        filename_no_ext = "some.file"
        filename = filename_no_ext + ".abc"

        assert get_notebook_filename(filename) == (filename, filename_no_ext)

    # ####################end of get_notebook_filename tests

    # get_notebook_contents tests
    def test_get_notebook_contents_none(self):

        self.assert_throws_error(get_notebook_contents, None,
                                 self.notebook_export_error)

    def test_get_notebook_contents_empty(self):

        self.assert_throws_error(get_notebook_contents, "",
                                 self.notebook_export_error)

    def test_get_notebook_contents_non_existent_notebook(self):

        self.assert_throws_error(get_notebook_contents,
                                 "doesntExist.ipynb",
                                 self.notebook_export_error)

    def test_get_notebook_contents_notebook(self):

        fname = "test_get_notebook_contents_notebook.ipynb"

        # Create temporary test.ipynb file
        nbdir = os.getcwd()

        nb = new_notebook(
            cells=[
                new_markdown_cell(u'Testing')
            ])

        with io.open(os.path.join(nbdir, fname), 'w',
                     encoding='utf-8') as f:
            write(nb, f, version=4)

        nb_content, python_content = get_notebook_contents(fname)
        self.assertTrue(len(nb_content) > 0)
        self.assertTrue(len(python_content) > 0)

        # Delete the temporary file
        os.remove(nbdir + "/" + fname)

    # #####################end of get_notebook_contents tests

    # _request_access_token tests
    def test_helper_request_access_token_error(self):

        error = "This is an error!"
        args = {"error_description": error}

        self.assert_throws_error(helper_request_access_token, args,
                                 self.github_error + error)

    def test_helper_request_access_token_blank_error(self):

        args = {"error_description": ""}

        self.assert_throws_error(helper_request_access_token, args,
                                 self.github_error)

    def test_helper_request_access_token_valid(self):

        args = {"access_token": "Token", "token_type": "not none",
                "scope": "not none"}

        assert helper_request_access_token(args) == "Token"

    def test_helper_request_access_token_invalid(self):

        args = {"access_token": None, "token_type": "not none",
                "scope": "not none"}

        self.assert_throws_error(helper_request_access_token, args,
                                 self.access_token_error)

    # ###################end of _request_access_token tests

    # helper_find_existing_gist_by_name tests
    def test_helper_find_existing_gist_by_name_none(self):

        filename = "somename"
        args = [{"files": None}]

        assert helper_find_existing_gist_by_name(args, filename, filename) is None

    def test_helper_find_existing_gist_by_name_none_files(self):

        filename = "somename"
        args = [{"files": [None]}]

        assert helper_find_existing_gist_by_name(args, filename, filename) is None

    def test_helper_find_existing_gist_by_name_two_match(self):

        filename = "somename"
        args = [{"files": filename}, {"files": filename}]

        try:
            helper_find_existing_gist_by_name(args, filename, filename)
        except tornado.web.HTTPError as exc:
            assert self.multiple_gists_error in str(exc)
        else:
            assert False

    def test_helper_find_existing_gist_by_name_no_match_not_empty(self):

        filename = "somename"
        args = [{"files": "apples"}]

        assert helper_find_existing_gist_by_name(args, filename, filename) is None

    def test_helper_find_existing_gist_by_name_one_match(self):

        filename = "somename"
        file_id = "123"
        args = [{"files": filename, "id": file_id}]

        assert helper_find_existing_gist_by_name(args, filename, filename) == file_id

    def test_helper_find_existing_gist_by_name_one_match_no_id(self):

        filename = "somename"
        args = [{"files": filename}]

        assert helper_find_existing_gist_by_name(args, filename, filename) is None

    # #####end of _find_existing_gist_by_name tests

    # _verify_gist_response tests
    def test_verify_gist_response_error(self):

        error = "This is an error!"
        args = {"error_description": error}

        self.assert_throws_error(verify_gist_response, args,
                                 self.github_error + error)

    def test_verify_gist_response_valid(self):
        url = "some url"
        args = {"html_url": url}

        try:
            verify_gist_response(args)
        except tornado.web.HTTPError:
            assert False

    def test_verify_gist_response_no_url(self):
        args = {"html_url": None}
        self.assert_throws_error(verify_gist_response, args,
                                 self.invalid_url_error)

    def test_verify_gist_response_none(self):
        args = None

        self.assert_throws_error(verify_gist_response, args,
                                 self.invalid_url_error)

    def test_verify_gist_response_none_error(self):
        args = {"error_description": None}

        self.assert_throws_error(verify_gist_response,
                                 args, self.invalid_url_error)
# ###########end of _verify_gist_response tests
