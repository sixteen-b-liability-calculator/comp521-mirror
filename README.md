16b Liability Calculator
==================


Running on local computer
----------------------------

Note: not all of the features will work on local machines. Go to http://16b.law.unc.edu/ to see the finished product.

To clone the repo:

    git clone https://github.com/sixteen-b-liability-calculator/comp521-mirror.git

After the repo is cloned, you will need to set up a virtual environment (instructions are for Mac and Linux only):

If you have never used a virtual environment before:

    sudo pip install virtualenv
or 
    '''sudo easy_instal virtualenv'''
    git remote add upstream -m master https://github.com/openshift/flask-example.git
    git pull -s recursive -X theirs upstream master
    
Then push the repo upstream

    git push

That's it, you can now checkout your application at:

    http://flask-$yournamespace.rhcloud.com

------------------------------

To get more log messages in your OpenShift logs please add the following line to your code

    app.config['PROPAGATE_EXCEPTIONS'] = True

To read more about logging in Flask please see this email

http://librelist.com/browser//flask/2012/1/27/catching-exceptions-from-flask/
