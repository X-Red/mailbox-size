#!/usr/bin/python

import mysql.connector
from mysql.connector import errorcode
import os

# Import local Configuration
from config import *

def get_file_size_in_megabytes(file_path):
   """ Finds the size of a file in the given file_path in megabytes. """
   try:
      return os.path.getsize(file_path)*(10**-6)
   except FileNotFoundError:
      print("No file found in path: ", file_path)
      return 0 #Return 0 if file specified does not exist or path given is mistaken

def get_total_size_in_megabytes(files):
    """ Accepts a sequence of file paths and returns the total size of these files in megabytes. """
    return sum([get_file_size_in_megabytes(x) for x in files])

def get_directory_size_in_megabytes(directory_path):
    """ This function returns the total size of files in a given directory. """
    files = [directory_path + x for x in os.listdir(directory_path)]
    return get_total_size_in_megabytes(files)

def create_connection():
   """ Creates a database connection with the details specified in config.py file

   IMPORTANT Note: The connection returned from this function should be closed in
   the outer function when done being used. For example, if you make a function
   call such as cnx = create_connection(), you should not forget calling cnx.close()
   when you are done with the connection.
   """
   try:
      return mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PWD, host=MYSQL_HOST, database=MYSQL_DB)
   except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
         print("Something is wrong with your user name or password")
         return
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
         print("Database does not exist")
         return
      else:
         print(err)
         return

def create_table():
   """ Creates a table with the given specifications in config.py file """

   cnx = create_connection()
   cursor = cnx.cursor()

   print(TABLE_DESCRIPTION)
   try:
      print("Creating table...")
      cursor.execute(TABLE_DESCRIPTION)
      print("Table created!")
   except mysql.connector.Error as err:
      if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
         print("already exists.")
         cnx.close()
         cursor.close()
         return
      else:
         print(err.msg)
         cnx.close()
         cursor.close()
         return
   else:
      print("OK")

   cnx.close()
   cursor.close()

def table_exists(table_name):
   """ Checks if a table exists with the given name. """
   cnx = create_connection()
   cursor = cnx.cursor()
   try:
      cursor.execute("SHOW TABLES LIKE '" + table_name + "'")
   except:
      cnx.close()
      cursor.close()
      print("Show Tables query didn't execute.")
      return

   rows = cursor.fetchall()
   cnx.close()
   cursor.close()

   if len(rows):
      return True
   else:
      return False



def insert_usage(user_size):
   """ Inserts a new row to the table specified in USAGE_TABLE dictionary in config.py.

   It accepts a tuple of form (username, size used).
   Note: This function is to create new rows for cases when user specified in username not yet having a record in usage table.
   For updating usage sizes for users with existing records, see update_usage() function.
   """
   cnx = create_connection()
   cursor = cnx.cursor()

   insert_query = (
      "INSERT INTO " + USAGE_TABLE['name'] + " "
      "(" + USAGE_TABLE['relational_column'] + ", " + USAGE_TABLE['size_column'] + ")"
      " VALUES ('" + user_size[0] + "', " + str(user_size[1]) + ")"
   )

   try:
      cursor.execute(insert_query)
   except mysql.connector.Error as e:
      cursor.close()
      cnx.close()
      print(e)
      return

   cnx.commit()

   cursor.close()
   cnx.close()

def record_exists(user):
   """ Checks if a record exists for the user specified in the usage table. """
   cnx = create_connection()
   cursor = cnx.cursor()

   query = "SELECT * FROM " + USAGE_TABLE['name'] + " WHERE " + USAGE_TABLE['relational_column'] + " = '" + user + "'"

   try:
      cursor.execute(query)
   except mysql.connector.Error as e:
      cursor.close()
      cnx.close()
      if e.errno == errorcode.ER_BAD_TABLE_ERROR:
         print("Table doesn't exist!")
      else:
         print(e)
      return

   rows = cursor.fetchall()
   cnx.close()
   cursor.close()

   if len(rows):
      return True
   else:
      return False

def update_usage(user_size):
   """ Updates the usage table with the values specified in user_size of form (username, size used)"""

   cnx = create_connection()
   cursor = cnx.cursor()

   update_query = (
      "UPDATE " + USAGE_TABLE['name'] + " "
      " SET " + USAGE_TABLE['size_column'] + "=" + str(user_size[1]) + " "
      " WHERE " + USAGE_TABLE['relational_column'] + "='" + user_size[0] + "'"
   )

   try:
      cursor.execute(update_query)
   except mysql.connector.Error as e:
      cursor.close()
      cnx.close()
      print(e)
      return

   cursor.close()
   cnx.close()


def select_user_paths(query=SELECT_QUERY):
   """ Selects and returns a list of tuples of form (username, maildir path) for currently active users.

   The default value for the query is the SELECT_QUERY defined in config.py file. This default might be
   changed or other queries can be passed as an argument. However, if this is done, please make sure that
   the result of the query passed returns exactly 2 columns with information username/userid etc. in first
   column and path to usage directory in the other column.
   """

   if query[:6] != 'SELECT':
      print("The query specified is not a SELECT query. Aborting!")
      return

   cnx = create_connection()
   cursor = cnx.cursor()

   try:
      cursor.execute(query)
   except mysql.connector.errors.ProgrammingError as e:
      cursor.close()
      cnx.close()
      print(e)
      return

   query_result = [rows for rows in cursor]
   cursor.close()
   cnx.close()

   return query_result

def update_usage_sizes():
   """ Pseudo-main function that finds the sizes for all active users and updates/creates them accordingly in the database.

   Note: This function could've been defined as the main function. But I am leaving the main for the timing, testing and
   other purposes.
   Note: If no table with the specified table name in USAGE_TABLE dictionary is found, the script will
   create one using the information outlined in TABLE_DESCRIPTION variable. Also, The default values
   specified in USAGE_TABLE dictionary in config.py file can be changed/customized.
   """

   if not table_exists(USAGE_TABLE['name']):
      create_table()

   user_paths = select_user_paths()
   user_sizes = []
   for x in user_paths:
      curr_dir = os.path.join(ROOT_DIR, x[1])
      user_sizes.append((x[0], round(get_directory_size_in_megabytes(curr_dir), 8)))

   for tup in user_sizes:
      if not record_exists(tup[0]):
         insert_usage(tup)
      else:
         update_usage(tup)

def main():
   update_usage_sizes()

# Log function
def write_log(text):
	# Open and write the log file
	log = open(XRED_LOG + datetime.datetime.now().strftime("%Y-%m-%d") + "_mailbox-size.log","a")
	line = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + text + "\n"
	log.write(line)
	log.close()

# Main function
if __name__ == "__main__":
    main()
