# X-Red.Com - Configuration file
SERVER_NAME = "servidor.x-red.com"

VIRTUAL_ROOT = "/virtual/vweb/" # Must unclude the / at the end
XRED_LOG  = "/var/log/x-red.com/"
MYSQL_HOST = "127.0.0.1"
MYSQL_USER = "root"
# MYSQL_PWD = "Create this variable in config_local.py file and fill this part with your password. If config_local.py does not exist, create one."
MYSQL_DB = "vmail"

# This query is the default query to be used in select_user_paths() function
SELECT_QUERY = "SELECT username, maildir FROM mailbox WHERE active ='1'"

# Please specify the table details for creating new a table and/or inserting obtained sizes.
# If edited, you should change the values on the right hand side with column names (table
# name for the first one) you desire.
USAGE_TABLE = {
	'name':'usage_size', # This should be the name of the table
	'pk_column':'UsageId', # You may not want to touch this if you already have a table. It is the primary key of the table and it is auto incremented.
	'relational_column':'username', # Foreign key column fthat should take a unique identifier for each user (i.e. username, userid, email etc.)
	'size_column':'UsageSize', # Finally column for recording total usage size.
	'timestamp_column': 'TimeDetected', # Column for recording the time detected
}

TEST_TABLE = "test_table" # This variable is used for unit testing. If you already have a table with the name "test_table" in database, change this variable.

# If you will create a table in order to store the data obtained upon initial use, you may customize the specifications below.
TABLE_DESCRIPTION = (
    "CREATE TABLE " + USAGE_TABLE['name']  + "("
	"  " + USAGE_TABLE['pk_column'] +" int NOT NULL AUTO_INCREMENT,"
    "  " + USAGE_TABLE['relational_column'] + " varchar(255) NOT NULL,"
    "  " + USAGE_TABLE['size_column'] + " double,"
	"  " + USAGE_TABLE['timestamp_column'] + " timestamp,"
    "  PRIMARY KEY (" + USAGE_TABLE['pk_column'] + ")"
    ")"
	)

#ROOT_DIR = '/virtual/vmail/'

# Load the local configuration
try:
	from config_local import *
except:
	print("config_local.py is not imported. Please check if the file exists.")
