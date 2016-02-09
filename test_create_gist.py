import unittest
import tornado
from create_gist import *

import io
import os
from nbformat import write
from nbformat.v4 import (new_notebook, new_markdown_cell)
class TestError(unittest.TestCase):
	def test_error(self):

		try:
			raise_error("This is a test error")
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: This is a test error)")
		else:
			assert(False)

	def test_error_empty(self):

		try:
			raise_error("")
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: )")
		else:
			assert(False)

	def test_github_error(self):

		try:
			raise_github_error("This is a test error")
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Github returned the following: This is a test error)")
		else:
			assert(False)

	def test_github_error_empty(self):

		try:
			raise_github_error("")
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Github returned the following: )")
		else:
			assert(False)

#TODO: In the below tests, we call the function we want to test via a static function type call..
# but the way they were designed suggests we should instantiate the class, and then call it as a method.
# I cannot instantiate IPythonHandler as they need 2 parameters - application and request.
# So instead I called them like a static function, passing in None where self is supposed to be...
class TestBaseHandler(unittest.TestCase):
	authCodeError = "HTTP 500: Internal Server Error (ERROR: Couldn't extract github authentication code from response)"
	notebookPathError = "HTTP 500: Internal Server Error (ERROR: Couldn't extract notebook path from response)"
	notebookFileNameError = "HTTP 500: Internal Server Error (ERROR: Problem with notebook file name)"
	notebookExportError = "HTTP 500: Internal Server Error (ERROR: Couldn't export notebook contents)"
	accessTokenError = "HTTP 500: Internal Server Error (ERROR: Couldn't extract needed info from github access token response)"
	multipleGistsError = "HTTP 500: Internal Server Error (ERROR: You had multiple gists with the same name as this notebook. Aborting.)"
	invalidURLError = "HTTP 500: Internal Server Error (ERROR: Couldn't get the url for the gist that was just updated)"

	def _should_throw_error(self, func, args, error):

		try:
			func(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), error)
		else:
			assert(False)


	# extract_code_from args tests
	def test_extract_code_from_args_valid(self):

		expected_code = "some code"
		expected_code_bytes =  str.encode(expected_code)
		args = { "code" : [expected_code_bytes] }

		self.assertEqual(BaseHandler.extract_code_from_args(None, args), expected_code)

	def test_extract_code_from_args_none_in_list(self):

		args = { "code" : [None] }

		self._should_throw_error(BaseHandler.extract_code_from_args, args, 
			self.authCodeError)
	
	def test_extract_code_from_args_none(self):

		args = None

		self._should_throw_error(BaseHandler.extract_code_from_args, args, 
			self.authCodeError)

	def test_extract_code_from_args_code_is_none(self):

		args = { "code" : None}

		self._should_throw_error(BaseHandler.extract_code_from_args, args, 
			self.authCodeError)

	def test_extract_code_from_args_code_is_char(self):

		expected_code = "a"
		expected_code_bytes =  str.encode(expected_code)
		args = { "code" : [expected_code_bytes]}

		self.assertEqual(BaseHandler.extract_code_from_args(None, args), expected_code)

	def test_extract_code_from_args_code_is_empty_str(self):

		args = { "code" : [b""] }

		self._should_throw_error(BaseHandler.extract_code_from_args, args, 
			self.authCodeError)

	def test_extract_code_from_args_long_code_list(self):

		args = { "code" : [b"aa", b"aa"] }

		self._should_throw_error(BaseHandler.extract_code_from_args, args, 
			self.authCodeError)

	def test_extract_code_from_args_with_error(self):

		error = "This is an error!"

		args = { "error_description" : error}

		self._should_throw_error(BaseHandler.extract_code_from_args, args, 
			"HTTP 500: Internal Server Error (ERROR: Github returned the following: " + error + ")")


	def test_extract_code_from_args_with_empty_error(self):

		args = { "error_description" : ""}

		self._should_throw_error(BaseHandler.extract_code_from_args, args, 
			"HTTP 500: Internal Server Error (ERROR: Github returned the following: )")

	# This test succeeds the error description part, but fails the access code
	def test_extract_code_from_args_with_none_error(self):

		args = { "error_description" : None }

		self._should_throw_error(BaseHandler.extract_code_from_args, args, 
			self.authCodeError)

	############### end of extract_code_from_args tests #################

	#extract_notebook_path_from_args tests
	def test_extract_notebook_path_from_args_valid(self):

		# Make a string, encode it into bytes via encode, then convert to base 64 since
		# thats what github gives
		somePath = "somepath"
		somePath = somePath.encode('utf-8')
		somePath = base64.b64encode(somePath)
		
		args = { "nb_path" : [somePath] }		

		self.assertEqual(BaseHandler.extract_notebook_path_from_args(None, args), "somepath")

	def test_extract_notebook_path_from_args_none_in_list(self):

		args = { "nb_path" : [None] }

		self._should_throw_error(BaseHandler.extract_notebook_path_from_args, args, 
			self.notebookPathError)

	def test_extract_notebook_path_from_args_none(self):

		args = None

		self._should_throw_error(BaseHandler.extract_notebook_path_from_args, args, 
			self.notebookPathError)

	def test_extract_notebook_path_from_args_code_is_none(self):

		args = { "nb_path" : None}

		self._should_throw_error(BaseHandler.extract_notebook_path_from_args, args, 
			self.notebookPathError)

	def test_extract_notebook_path_from_args_code_is_char(self):

		# Make a string, encode it into bytes via encode, then convert to base 64 since
		# thats what github gives
		somePath = "a"
		somePath = somePath.encode('utf-8')
		somePath = base64.b64encode(somePath)
		
		args = { "nb_path" : [somePath] }

		self.assertEqual(BaseHandler.extract_notebook_path_from_args(None, args), "a")

	def test_extract_notebook_path_from_args_code_is_empty_str(self):

		args = { "nb_path" : [b""] }

		self._should_throw_error(BaseHandler.extract_notebook_path_from_args, args, 
			self.notebookPathError)

	def test_extract_notebook_path_from_args_long_code_list(self):

		somePathA = "a"
		somePathA = somePathA.encode('utf-8')
		somePathA = base64.b64encode(somePathA)

		somePathB = "b"
		somePathB = somePathB.encode('utf-8')
		somePathB = base64.b64encode(somePathB)

		args = { "code" : [somePathA, somePathB] }

		self._should_throw_error(BaseHandler.extract_notebook_path_from_args, args, 
			self.notebookPathError)

	def test_extract_notebook_path_from_args_with_error_(self):

		error = "This is an error!"
		args = { "error_description" : error}

		self._should_throw_error(BaseHandler.extract_notebook_path_from_args, args, 
			"HTTP 500: Internal Server Error (ERROR: Github returned the following: " + error + ")")

	def test_extract_notebook_path_from_args_with_empty_error_(self):

		args = { "error_description" : ""}

		self._should_throw_error(BaseHandler.extract_notebook_path_from_args, args, 
			"HTTP 500: Internal Server Error (ERROR: Github returned the following: )")

	# This test succeeds the error description part, but fails the extraction
	def test_extract_notebook_path_from_args_with_none_error_(self):

		args = { "error_description" : None }

		self._should_throw_error(BaseHandler.extract_notebook_path_from_args, args, 
			self.notebookPathError)

	################end of extract_notebook_path_from_args tests

	#request_access_token tests 

	#how should we approach testing posting?

	#def test_request_access_token
	################end of request_access_token tests

	#get_notebook_filename tests

	def test_get_notebook_filename_none(self):

		self._should_throw_error(BaseHandler.get_notebook_filename, None, 
			self.notebookFileNameError)

	def test_get_notebook_filename_empty(self):

		self._should_throw_error(BaseHandler.get_notebook_filename, "", 
			self.notebookFileNameError)

	def test_get_notebook_filename_no_extension(self):

		filename = "somefile"

		self.assertEqual(BaseHandler.get_notebook_filename(None, filename), (filename, filename))

	def test_get_notebook_filename_extension(self):

		filename_no_ext = "somefile"
		filename = filename_no_ext + ".abc"

		self.assertEqual(BaseHandler.get_notebook_filename(None, filename), (filename, filename_no_ext))
	
	def test_get_notebook_filename_path_no_extension(self):

		filename = "somefile"

		self.assertEqual(BaseHandler.get_notebook_filename(None, "/a/b/c/" + filename), (filename, filename))
	
	def test_get_notebook_filename_path_extension(self):

		filename_no_ext = "somefile"
		filename = filename_no_ext + ".abc"

		self.assertEqual(BaseHandler.get_notebook_filename(None, "/a/b/c/" + filename), (filename, filename_no_ext))

	def test_get_notebook_filename_double_dot(self):

		filename_no_ext = "some.file"
		filename = filename_no_ext + ".abc"

		self.assertEqual(BaseHandler.get_notebook_filename(None, filename), (filename, filename_no_ext))

	#####################end of get_notebook_filename tests

	# get_notebook_contents tests
	def test_get_notebook_contents_none(self):

		self._should_throw_error(BaseHandler.get_notebook_contents, None,
			self.notebookExportError)

	def test_get_notebook_contents_empty(self):

		self._should_throw_error(BaseHandler.get_notebook_contents, "",
			self.notebookExportError)

	def test_get_notebook_contents_non_existent_notebook(self):

		self._should_throw_error(BaseHandler.get_notebook_contents, "doesntExist.ipynb", 
			self.notebookExportError)


	def test_get_notebook_contents_notebook(self):

		filename = "test_get_notebook_contents_notebook.ipynb"

		# Create temporary test.ipynb file
		nbdir = os.getcwd()

		nb = new_notebook(
            cells=[
                new_markdown_cell(u'Testing')
            ] )
        

		with io.open(os.path.join(nbdir, filename), 'w', encoding='utf-8') as f:
			write(nb, f, version=4)

		nb_content, python_content = BaseHandler.get_notebook_contents(None, filename)
		self.assertTrue(len(nb_content) > 0)
		self.assertTrue(len(python_content) > 0)

		# Delete the temporary file
		os.remove(nbdir + "/" + filename);

	######################end of get_notebook_contents tests

	#_request_access_token tests
	def test__request_access_token_error(self):

		error = "This is an error!"
		args = { "error_description" : error }

		self._should_throw_error(BaseHandler._request_access_token, args, 
			"HTTP 500: Internal Server Error (ERROR: Github returned the following: " + error + ")")

	def test__request_access_token_blank_error(self):

		args = { "error_description" : "" }

		self._should_throw_error(BaseHandler._request_access_token, args, 
			"HTTP 500: Internal Server Error (ERROR: Github returned the following: )")

	def test__request_access_token_valid(self):

		args = { "access_token" : "Token", "token_type" : "not none", "scope" : "not none" }

		self.assertEqual(BaseHandler._request_access_token(None, args), "Token")

	def test__request_access_token_invalid(self):

		args = { "access_token" : None, "token_type" : "not none", "scope" : "not none" }

		self._should_throw_error(BaseHandler._request_access_token, args, 
			self.accessTokenError)

	####################end of _request_access_token tests

	#_find_existing_gist_by_name tests
	def test__find_existing_gist_by_name_none(self):

		filename = "somename"
		args = [ {"files" : None } ]

		self.assertEqual(BaseHandler._find_existing_gist_by_name(None, args, filename, filename), None)


	def test__find_existing_gist_by_name_none_files(self):

		filename = "somename"
		args = [ {"files" : [None] } ]

		self.assertEqual(BaseHandler._find_existing_gist_by_name(None, args, filename, filename), None)

	def test__find_existing_gist_by_name_two_match(self):

		filename = "somename"
		args = [ {"files" : filename }, {"files" : filename } ]
		
		try:
			file_id = BaseHandler._find_existing_gist_by_name(None, args, filename, filename)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), self.multipleGistsError)
		else:
			assert(False)

	def test__find_existing_gist_by_name_no_match_not_empty(self):

		filename = "somename"
		args = [ {"files" : "apples" } ]

		self.assertEqual(BaseHandler._find_existing_gist_by_name(None, args, filename, filename), None)

	def test__find_existing_gist_by_name_one_match(self):

		filename = "somename"
		file_id = "123"
		args = [ {"files" : filename, "id" : file_id } ]

		self.assertEqual(BaseHandler._find_existing_gist_by_name(None, args, filename, filename), file_id)

	def test__find_existing_gist_by_name_one_match_no_id(self):

		filename = "somename"
		args = [ {"files" : filename } ]

		self.assertEqual(BaseHandler._find_existing_gist_by_name(None, args, filename, filename), None)


	######end of _find_existing_gist_by_name tests

	#_verify_gist_response tests
	def test__verify_gist_response_error(self):

		error = "This is an error!"
		args = { "error_description" : error }

		self._should_throw_error(BaseHandler._verify_gist_response, args, 
			"HTTP 500: Internal Server Error (ERROR: Github returned the following: " + error + ")")

	def test__verify_gist_response_valid(self):

		args = { "html_url" : "some url" }

		self.assertEqual(BaseHandler._verify_gist_response(None, args), "some url")

	def test__verify_gist_response_no_url(self):

		args = { "html_url" : None }

		self._should_throw_error(BaseHandler._verify_gist_response, args, 
			self.invalidURLError)

	def test__verify_gist_response_none(self):

		args = None

		self._should_throw_error(BaseHandler._verify_gist_response, args, 
			self.invalidURLError)
	def test__verify_gist_response_none_error(self):

		args = { "error_description" : None }

		self._should_throw_error(BaseHandler._verify_gist_response, args, 
			self.invalidURLError)

	############end of _verify_gist_response tests

