from . import create_app

# WSGI expects `application` to be defined for communication with the webserver
application = create_app()
