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
    
    if req == "POST":
        return handle_post(event, caller_id)
    elif req == "GET":
        return handle_get(event, caller_id)
    elif req == "PUT":
        return handle_put(event, caller_id)
    elif req == "DELETE":
        return handle_delete(event, caller_id)
        
    
def handle_post(event, caller_id):
    # save information to the database
    try:
        body = json.loads(event["body"])
        
        category_id = str(uuid.uuid4())
        category_name = body["CategoryName"]
        
        cnx = create_sql_connection()
        cursor = cnx.cursor()
    
        create_db_insertion_query = f"insert into Category (CatID, UserID, CatName) values ('{category_id}', '{caller_id}', '{category_name}');"
        cursor.execute(create_db_insertion_query)
    
        cnx.commit()
        cursor.close()
        cnx.close()
    
        response = {}
        response["category_id"] = category_id
        response["success"] = "true"
        return response
        
    except:
        response = {}
        response["success"] = "false"
        return response
        

def handle_get(event, caller_id):

    cnx = create_sql_connection()
    cursor = cnx.cursor()

    create_db_query = f"select CatID, CatName from Category where UserID = '{caller_id}';"
    cursor.execute(create_db_query)
    categories = cursor.fetchall()

    cnx.commit()
    cursor.close()
    cnx.close()
    
    return categories


def handle_put(event, caller_id):

    try:
        body = json.loads(event["body"])
        category_id = body["CategoryID"]
        category_name = body["CategoryName"]

        
        cnx = create_sql_connection()
        cursor = cnx.cursor()
        
        create_db_query = f"update Category set UserID = '{caller_id}', CatName = '{category_name}', CatID = '{category_id}' where CatID = '{category_id}';"
        cursor.execute(create_db_query)
        
     
        cnx.commit()
        cursor.close()
        cnx.close()
        
        response = {}
        response["category_id"] = category_id
        response["success"] = "true"
        return response

    except:
        response = {}
        response["success"] = "false"
        return response


def handle_delete(event, caller_id):
    
    try:
        body = json.loads(event["body"])
        category_id = body["CategoryID"]
        
        cnx = create_sql_connection()
        cursor = cnx.cursor()
        
        create_db_query = f"delete from Category where CatID = '{category_id}' and UserID = '{caller_id}';"
        cursor.execute(create_db_query)
        
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