16b Liability Calculator
==================

Note: Due to database and server dependencies, this app will not run locally without installing all requirements from the setup.py file and creating the MySQL database from the initializeDatabase.sql script.

Install the app and run it locally (Mac or Linux)
------------
> Running the app via Windows is complicated and not covered in this guide.

- Susbcribe to Carolina Cloudapps (https://cloudapps.unc.edu/subscribe)
- Install Ruby 
```sh
$ brew install ruby
```
- Install rhc
```sh
$ sudo gem install rhc
```
- Setup rhc
```sh
$ rhc setup --server=broker.apps.unc.edu
```
- Log in with your onyen
- Enter onyen password
- Type "Yes" to generate a token
- Type "yes" to upload the ssh key
- Create the app (replace APPNAME with the desired name for your app)
```sh
$ rhc create-app APPNAME python-2.7 --from-code=https://github.com/sixteen-b-liability-calculator/comp521-mirror.git
```
- Add the MySQL cartridge to your app
```sh
$ rhc cartridge add mysql-5.5 -a APPNAME
```
- SSH into app and initialize the database
```sh
$ rhc ssh APPNAME
$ mysql APPNAME < app-root/repo/initializeDatabase.sql
$ exit
```
- Your app is now available at http://APPNAME-ONYEN.apps.unc.edu

Testing the app
------------
- In terminal, cd into your project folder (the one created when you called "git clone")
```sh
$ rhc ssh APPNAME
```
- Navigate into the app's directory
```sh
$ cd app-root/repo
```
- Run the tests
```sh
$ python wsgi/myflaskapptests.py
```


