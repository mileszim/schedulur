#!/usr/bin/env python

"""
Run script for Schedulur web app
"""

import os
from dotenv import load_dotenv
load_dotenv()


from schedulur.web_app import app

# if HOST is not set, use default
HOST = os.getenv("HOST", "0.0.0.0")

if __name__ == "__main__":
    print("Starting Schedulur web app on http://127.0.0.1:5000")
    app.run(debug=True,host=HOST,port=5000)

