Lesson 5 Ubuntu-server-project

Operating Instruction
1. Start project by visiting http://ec2-35-163-150-67.us-west-2.compute.amazonaws.com/
2. Without logging in, can view available categories, item list, item details and featured items,
3. Use Google Login to add ability to add, delete and modify items.

Available Public Endpoints from http://ec2-35-163-150-67.us-west-2.compute.amazonaws.com/
1. Home Page, list of available Categories and Featured Items / and /catalog
2. Items Listing /catalog/"catalog_name" and /catalog/"catalog_name"/item
3. Item Details c & /catalog/"catalog_name"/item/item_id
4. Login screen at /login
5. JSON available for all listed endpoints

Additional Private Endpoints from http://ec2-35-163-150-67.us-west-2.compute.amazonaws.com/
1. Add Item available at /catalog/"catalog_name"/item/add
2. Delete Item available at /catalog/"catalog_name"/item_id/delete
3. Edit Item available at /catalog/"catalog_name"/item_id/Edit
4. Logout available at /disconnect

Project running on AWS Lightsail located:
http://ec2-35-163-150-67.us-west-2.compute.amazonaws.com/
34.212.89.127 public ip
172.26.4.6 private IP

Software Installed
apache2
postgresql
pip
mod_wsgi
flask
sqlalchemy
oauth2client
psycopg2
httplib2

Configurations Made
Ubuntu software update
Add user grader
Added grader as root user
Create directory .ssh and file authorized_keys
Add local generated public key to authorized_keys
Modified grader .ssh and authorized_keys permissions
Removed password access through modificaiton of
Change SSH port to 2200
Set UFW restrictions
Create Database with user access
Disable root access

References Used
http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/
http://www.jakowicz.com/flask-apache-wsgi/
https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
http://docs.sqlalchemy.org/en/latest/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg2
https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps
https://github.com/harushimo/linux-server-configuration
https://help.github.com/articles/cloning-a-repository/
http://docs.python-requests.org/en/master/user/install/
https://oauth2client.readthedocs.io/en/latest/
http://pythoncentral.io/how-to-install-sqlalchemy/
https://discussions.udacity.com/c/nd004-p7-linux-based-server-configuration
