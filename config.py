# X-Red.Com - Configuration file

SERVER_NAME = "servidor.x-red.com"

VIRTUAL_ROOT = "/virtual/vweb/" # Must unclude the / at the end
XRED_LOG  = "/var/log/x-red.com/"
MYSQL_SERVER = "localhost"
MYSQL_USER = "root"
MYSQL_PWD = "Use config_local.py to store the password"
MYSQL_DB = "mysql"

# Load the local configuration
try:
	from config_local import *
except Exception, e:
	print e
