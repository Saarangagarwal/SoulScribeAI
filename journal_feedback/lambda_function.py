import json
import mysql.connector
import boto3
import uuid
import datetime
import ast
from dateutil import tz

bucket = 'soulscribebucket'

def lambda_handler(event, context):
    # get the type of request and call handler
    req = event["routeKey"][:event["routeKey"].find("/")-1]
    
    # extract caller information
    caller_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    
    if req == "POST":
        return handle_post(event, caller_id)

        
def handle_post(event, caller_id):
    try:
        body = json.loads(event["body"])
        journal_id = body["journalId"]
        feedbackId = str(uuid.uuid4())
        feedback = str(body["feedback"])
        
        last_modified_timestamp = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('America/New_York')
        last_modified_timestamp = last_modified_timestamp.astimezone(to_zone)
        created_timestamp = last_modified_timestamp
    
        # check if feedback for the journal_id for a user already exists
        cnx = create_sql_connection()
        cursor = cnx.cursor()
        journal_feedback_existance_check = f"select JournalID from JournalFeedback where JournalID = '{journal_id}' and UserID = '{caller_id}' ;"
        cursor.execute(journal_feedback_existance_check)
        journal_feedback_existance_check = json.loads(json.dumps(cursor.fetchall(),default=str))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        
        if len(journal_feedback_existance_check) == 0:
            cnx = create_sql_connection()
            cursor = cnx.cursor()
            create_db_insertion_query = f"insert into JournalFeedback (JournalID, UserID, Feedback, LastModifiedTimestamp, createdTimestamp, FeedbackID) values ('{journal_id}', '{caller_id}', '{feedback}','{last_modified_timestamp}','{created_timestamp}','{feedbackId}');"
            cursor.execute(create_db_insertion_query)
            cnx.commit()
            cursor.close()
            cnx.close()
        else:
            cnx = create_sql_connection()
            cursor = cnx.cursor()
        
            create_db_insertion_query = f"update JournalFeedback set Feedback = '{feedback}', LastModifiedTimestamp = '{last_modified_timestamp}' where JournalID = '{journal_id}' and UserID = '{caller_id}';"
            cursor.execute(create_db_insertion_query)
            
            cnx.commit()
            cursor.close()
            cnx.close()
    
        response = {}
        response["journal_id"] = journal_id
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