#!/usr/bin/python

from config import *
from config_local import *
from mailboxsize import *
import os
import subprocess
import shutil
import random

ROOT_DIR = f'{os.getcwd()}/test' # For testing

TEST_TABLE = {
	'name':'test_table', # This should be the name of the table
	'pk_column':'UsageId', # You may not want to touch this if you already have a table. It is the primary key of the table and it is auto incremented.
	'relational_column':'username', # Foreign key column fthat should take a unique identifier for each user (i.e. username, userid, email etc.)
	'size_column':'UsageSize', # Finally column for recording total usage size.
	'timestamp_column': 'TimeDetected', # Column for recording the time detected
}

TEST_DESCRIPTION = (
    "CREATE TABLE " + TEST_TABLE['name']  + "("
	"  " + TEST_TABLE['pk_column'] +" int NOT NULL AUTO_INCREMENT,"
    "  " + TEST_TABLE['relational_column'] + " varchar(255) NOT NULL,"
    "  " + TEST_TABLE['size_column'] + " double,"
	"  " + TEST_TABLE['timestamp_column'] + " timestamp,"
    "  PRIMARY KEY (" + TEST_TABLE['pk_column'] + ")"
    ")"
	)



USAGE_SIZES = {}
def init():

    if not table_exists(TEST_TABLE['name']):
        create_table(TABLE_DESCRIPTION=TEST_DESCRIPTION)

    if not os.path.isdir('./test'):
        #test_dir = os.path.join(os.getcwd(), 'test')
        os.mkdir(ROOT_DIR)

    paths = select_user_paths()
    users = [tup[0].split("@")[1] for tup in paths]
    users = dict.fromkeys(users, False)

    for path in paths:
        try:
            account, user = path[0].split("@")
            if not users[user]:
                user_dir = os.path.join(ROOT_DIR, user)
                os.mkdir(user_dir)
                users[user] = True
            
            account_dir = os.path.join(ROOT_DIR, path[1])
            os.mkdir(account_dir)
            
            
            test_paths = ['/test_one', '/test_two']
            for test_path in test_paths:
                test_dir = account_dir + test_path
                os.mkdir(test_dir)
                p = test_dir + '/bin_file'
                rand = random.randint(1, 10)
                size = 1024*1024*rand
                with open(p, 'wb') as fout:
                    fout.write(os.urandom(size))
            
            rand = random.randint(1, 10)
            size = 1024*1024*rand
            f = account_dir + 'bin_file'
            with open(f, 'wb') as fout:
                fout.write(os.urandom(size))
            USAGE_SIZES[path[0]] = size

        except OSError as e:
            print (e) 


def clean():
    shutil.rmtree(ROOT_DIR)
    cnx = create_connection()
    cursor = cnx.cursor()
    query = f"DROP TABLE {TEST_TABLE['name']}"
    try:
        cursor.execute(query)
    except mysql.connector.errors.ProgrammingError as e:
        cursor.close()
        cnx.close()
        print(e)
        return

    cursor.close()
    cnx.close()
    

def test_database_records():
    init()
    print("Testing for correct database records.... ", end="")   
    PASSED = True

    try:
        update_usage_sizes(USAGE_TABLE=TEST_TABLE, ROOT_DIR=ROOT_DIR)

        user_paths = select_user_paths()
        for x in user_paths:
            curr_dir = os.path.join(ROOT_DIR, x[1])
            USAGE_SIZES[str(x[0])] = round(get_directory_size_in_megabytes(curr_dir), 6)

        cnx = create_connection()
        cursor = cnx.cursor()
        query = f"SELECT {TEST_TABLE['relational_column']}, {TEST_TABLE['size_column']}, {TEST_TABLE['timestamp_column']} FROM {TEST_TABLE['name']}"
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

        for result in query_result:
            if USAGE_SIZES[result[0]] != result[1]:
                print("Failed!")
                PASSED = False
                break

    except Exception as e:
        print("Error! \n", e)
    finally:
        clean()

    if PASSED:
        print("Passed!")
    else:
        print("Failed!")
    
    return PASSED

def test_size_function():
    init()
    print("Testing size calculation.... ", end="")
    PASSED = True

    try:
        user_paths = select_user_paths()
        user_sizes = {}
        for x in user_paths:
            curr_dir = os.path.join(ROOT_DIR, x[1])
            user_sizes[str(x[0])] = round(get_directory_size_in_megabytes(curr_dir), 6)

        for path in user_paths:
            command_path = f'./test/{path[1]}'
            out = subprocess.run(["du", "-sb", "-s" , command_path], capture_output=True)
            sys_size = out.stdout.decode('ascii')
            size = sys_size.split(".")[0]
            size = float(size)
            size = (size-4)/(1024*1024)
            size = round(size, 6)
            
            if size != user_sizes[path[0]]:
                print("Failed!")
                PASSED = False
                break
            
    except Exception as e:
        print("Error! \n", e)
    finally:
        clean()

    if PASSED:
        print("Passed!")
    else:
        print("Failed!")

    return PASSED
   
def main():
    test_size_function()
    test_database_records()

# Main function
if __name__ == "__main__":
    main()