# Vercel WSGI handler for Flask
from app import app as application

# For local development
if __name__ == '__main__':
    application.run()
