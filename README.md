16b Liability Calculator
==================


Running/Testing locally
----------------------------

Note: not all of the features will work on local machines. Go to http://16b.law.unc.edu/ to see the finished product.

To clone the repo:

    git clone https://github.com/sixteen-b-liability-calculator/comp521-mirror.git

After the repo is cloned, you will need to set up a virtual environment (instructions are for Mac and Linux only):

If you have never used a virtual environment before:

    sudo pip install virtualenv
    
Navigate to the folder (repo) where the project is stored locally (not the wsgi folder but the parent directory)

    virtualenv env
    source env/bin/activate
    pip install flask
    python setup.py install
    python wsgi/myflaskapp.py

The last line is how to run the website. For testing, you do the same except:

    python wsgi/myflaskapptests.py

Note: testing may not work in the virtual environment, it may have to be run directly from the app itself.

------------------------------

