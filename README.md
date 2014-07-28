opine-server
============

Backend server for the 2014.1 Software Entrepreneurship class project/product

The following environment vars are necessary:

* SECRET_KEY
* * If running locally, generate this envvar using Python's `os.urandom(24)`
* PARSE_APPLICATION_ID \*
* PARSE_REST_API_KEY \*

\* Use valid Parse envvars so that Push notifications triggering is enabled
