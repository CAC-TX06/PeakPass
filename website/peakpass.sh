# For production, this is the file that is run, make sure that you have installed gunicorn
# and all other dependencies for the project.
gunicorn -b 0.0.0.0:5000 wsgi:app