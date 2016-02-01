import unittest
import tornado
from create_gist import *

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

	# extract_code_from args tests
	def test_extract_code_from_args_valid(self):

		args = { "code" : [b"some code"] }

		self.assertEqual(BaseHandler.extract_code_from_args(None, args), "some code")

	def test_extract_code_from_args_none_in_list(self):

		args = { "code" : [None] }

		try:
			BaseHandler.extract_code_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Couldn't extract github authentication code from response)")
		else:
			assert(False)

	def test_extract_code_from_args_none(self):

		args = None

		try:
			BaseHandler.extract_code_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Couldn't extract github authentication code from response)")
		else:
			assert(False)

	def test_extract_code_from_args_code_is_none(self):

		args = { "code" : None}

		try:
			BaseHandler.extract_code_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Couldn't extract github authentication code from response)")
		else:
			assert(False)

	def test_extract_code_from_args_code_is_char(self):

		args = { "code" : [b"a"]}

		self.assertEqual(BaseHandler.extract_code_from_args(None, args), "a")

	def test_extract_code_from_args_code_is_empty_str(self):

		args = { "code" : [b""] }

		try:
			BaseHandler.extract_code_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Couldn't extract github authentication code from response)")
		else:
			assert(False)

	def test_extract_code_from_args_long_code_list(self):

		args = { "code" : [b"aa", b"aa"] }

		try:
			BaseHandler.extract_code_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Couldn't extract github authentication code from response)")
		else:
			assert(False)

	def test_extract_code_from_args_with_error_(self):

		args = { "error_description" : "This is an error!"}

		try:
			BaseHandler.extract_code_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Github returned the following: This is an error!)")
		else:
			assert(False)

	def test_extract_code_from_args_with_empty_error_(self):

		args = { "error_description" : ""}

		try:
			BaseHandler.extract_code_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Github returned the following: )")
		else:
			assert(False)

	# This test succeeds the error description part, but fails the access code
	def test_extract_code_from_args_with_none_error_(self):

		args = { "error_description" : None }

		try:
			BaseHandler.extract_code_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Couldn't extract github authentication code from response)")
		else:
			assert(False)

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

		try:
			BaseHandler.extract_notebook_path_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Couldn't extract notebook path from response)")
		else:
			assert(False)

	def test_extract_notebook_path_from_args_none(self):

		args = None

		try:
			BaseHandler.extract_notebook_path_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Couldn't extract notebook path from response)")
		else:
			assert(False)

	def test_extract_notebook_path_from_args_code_is_none(self):

		args = { "nb_path" : None}

		try:
			BaseHandler.extract_notebook_path_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Couldn't extract notebook path from response)")
		else:
			assert(False)

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

		try:
			BaseHandler.extract_notebook_path_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Couldn't extract notebook path from response)")
		else:
			assert(False)

	def test_extract_notebook_path_from_args_long_code_list(self):

		somePathA = "a"
		somePathA = somePathA.encode('utf-8')
		somePathA = base64.b64encode(somePathA)

		somePathB = "b"
		somePathB = somePathB.encode('utf-8')
		somePathB = base64.b64encode(somePathB)

		args = { "code" : [somePathA, somePathB] }

		try:
			BaseHandler.extract_notebook_path_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Couldn't extract notebook path from response)")
		else:
			assert(False)

	def test_extract_notebook_path_from_args_with_error_(self):

		args = { "error_description" : "This is an error!"}

		try:
			BaseHandler.extract_notebook_path_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Github returned the following: This is an error!)")
		else:
			assert(False)

	def test_extract_notebook_path_from_args_with_empty_error_(self):

		args = { "error_description" : ""}

		try:
			BaseHandler.extract_notebook_path_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Github returned the following: )")
		else:
			assert(False)

	# This test succeeds the error description part, but fails the extraction
	def test_extract_notebook_path_from_args_with_none_error_(self):

		args = { "error_description" : None }

		try:
			BaseHandler.extract_notebook_path_from_args(None, args)
		except tornado.web.HTTPError as e:
			self.assertEqual(str(e), 
				"HTTP 500: Internal Server Error (ERROR: Couldn't extract notebook path from response)")
		else:
			assert(False)

	################end of extract_notebook_path_from_args tests

	#request_access_token tests

	#def test_request_access_token
	################end of request_access_token tests

	#get_notebook_filename tests

	def test_get_notebook_filename_none(self):

		self.assertEqual(BaseHandler.get_notebook_filename(None, None), (None, None))

	def test_get_notebook_filename_empty(self):

		self.assertEqual(BaseHandler.get_notebook_filename(None, ""), (None, None))

	def test_get_notebook_filename_no_extension(self):

		self.assertEqual(BaseHandler.get_notebook_filename(None, "somefile"), ("somefile", "somefile"))

	def test_get_notebook_filename_extension(self):

		self.assertEqual(BaseHandler.get_notebook_filename(None, "somefile.abc"), ("somefile.abc", "somefile"))
	
	def test_get_notebook_filename_path_no_extension(self):

		self.assertEqual(BaseHandler.get_notebook_filename(None, "/a/b/c/somefile"), ("somefile", "somefile"))
	
	def test_get_notebook_filename_path_extension(self):

		self.assertEqual(BaseHandler.get_notebook_filename(None, "/a/b/c/somefile.abc"), ("somefile.abc", "somefile"))

	def test_get_notebook_filename_double_dot(self):

		self.assertEqual(BaseHandler.get_notebook_filename(None, "some.file.abc"), ("some.file.abc", "some.file"))

# TODO: Tests for:

# request_access_token
# get_notebook_contents
# find_existing_gist_by_name
# create_new_gist
# edit_existing_gist
# verify_gist_response
# GistHandler functions
# How to test redirects?