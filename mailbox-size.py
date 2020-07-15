#!/usr/bin/python

import MySQLdb

# Import local Configuration
from config import *

# Log function
def write_log(text):
	# Escribe el archivo log en la carpeta SFTP_LOG
	log = open(XRED_LOG + datetime.datetime.now().strftime("%Y-%m-%d") + "_mailbox-size.log","a")
	line = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + text + "\n"
	log.write(line)
	log.close()

def main():
    # Open database connection
    db = MySQLdb.connect(MYSQL_SERVER, MYSQL_USER, MYSQL_PWD, MYSQL_DB)

    print(MYSQL_DB)
    # Prepare a cursor object using cursor() method
    cursor = db.cursor()

    sql = "SELECT maildir FROM mailbox WHERE active ='1'"

    try:
       # Execute the SQL command
       cursor.execute(sql)
       # Fetch all the rows in a list of lists.
       results = cursor.fetchall()
       for row in results:
          maildir = row[0]

          # Now print fetched result
          print("/virtual/vmail/" + maildir)

          # Calculate the size of every mail folder

          # Update the usage table

          
    except:
       print "Error: unable to fecth data"

    # disconnect from server
    db.close()

# Main function
if __name__ == "__main__":
    main()
