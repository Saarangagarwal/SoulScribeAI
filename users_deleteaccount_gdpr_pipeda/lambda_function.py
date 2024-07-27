import json
import mysql.connector
import boto3
import uuid

bucket = 'soulscribebucket'

def lambda_handler(event, context):
    
    # get the type of request and call handler
    req = event["routeKey"][:event["routeKey"].find("/")-1]
    
    # extract caller information
    caller_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    
    # if req == "POST":
    #     return handle_post(event, caller_id)
    # elif req == "GET":
    #     return handle_get()
    # elif req == "PUT":
    #     return handle_put(event, caller_id)
    # elif req == "PATCH":
    #     return handle_patch()
    if req == "DELETE":
        return handle_delete(event, caller_id)
        

def handle_delete(event, caller_id):
    
    try:

        cnx = create_sql_connection()
        cursor = cnx.cursor()
        
        # delete all journals that the user has
        create_db_query = f"select * from Journals where userID = '{caller_id}';"
        cursor.execute(create_db_query)
        journal_record = cursor.fetchall()
        return journal_record
    
        # delete records from s3 bucket first
        # # update S3 entry and extract s3journalID
        # s3_file_title = journal_record[0][5]
        
        # s3 = boto3.client('s3')
        # s3.delete_object(Bucket=bucket, Key=s3_file_title)
        
        # delete the records from the Journals table
        # create_db_insertion_query = f"delete from Journals where JournalID = '{journal_id}';";
        # cursor.execute(create_db_insertion_query)
        
        # delete all the categories that the user has
        
        
        # delete the user from the users table

        # delete the user from aws
        
        
        cnx.commit()
        cursor.close()
        cnx.close()
        response = {}
        response["success"] = "true"
        return response
        
    except:
        response = {}
        response["success"] = "false"
        return response
        

def create_sql_connection():
    return mysql.connector.connect( 
        host='soulscribe-db.c7k0qn3qv7uc.us-east-1.rds.amazonaws.com', 
        user='admin', 
        password='SoulScribe69AiMl777',
        database= 'soulscribe'
    )