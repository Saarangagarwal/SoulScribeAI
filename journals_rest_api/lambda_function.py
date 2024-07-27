import json
import mysql.connector
import boto3
import uuid

# bucket = 'soulscribebucket'

def lambda_handler(event, context):

    # get the type of request and call handler
    req = event["routeKey"][:event["routeKey"].find("/")-1]
    
    # extract caller information
    caller_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    
    # if req == "POST":
        # return handle_post(event, caller_id)
    if req == "GET":
        return handle_get(event, caller_id)
    # elif req == "PUT":
        # return handle_put(event, caller_id)
    # elif req == "PATCH":
        # return handle_patch()
    # elif req == "DELETE":
        # return handle_delete(event, caller_id)
        

def handle_get(event, caller_id):
    cnx = create_sql_connection()
    cursor = cnx.cursor()

    # create_db_query = f"select JournalID, Title, J.CatID, Mood, JournalType, CatharticStage, LastModifiedTimestamp, createdTimestamp, CatName from Journals J left join Category C on J.CatID = C.CatID where J.UserID = '{caller_id}';"
    create_db_query = f"select JournalID, Title, Category, Mood, JournalType, CatharticStage, LastModifiedTimestamp, createdTimestamp, Description from Journals where UserID = '{caller_id}';"
    
    cursor.execute(create_db_query)
    journal_entries = json.loads(json.dumps(cursor.fetchall(), default=str))
    cnx.commit()
    cursor.close()
    cnx.close()
    res = []

    res_entry_keys = ["journalId", "title", "category", "mood", "journalType", "catharticStage", "lastModifiedTimestamp", "createdTimestamp", "Description"]
    res_entry = {}
    
    for i in range(9):
        res_entry[res_entry_keys[i]] = ""
    
    for entry in journal_entries:
        for i in range(9):
            res_entry[res_entry_keys[i]] = entry[i]
        res.append(res_entry.copy())

    return {"journalEntries": res}


def create_sql_connection():
    return mysql.connector.connect( 
        host='soulscribe-db.c7k0qn3qv7uc.us-east-1.rds.amazonaws.com', 
        user='admin', 
        password='SoulScribe69AiMl777',
        database= 'soulscribe'
    )