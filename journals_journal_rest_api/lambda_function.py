import json
import mysql.connector
import boto3
import uuid
import datetime
import ast
from dateutil import tz
# import rsa
# (publickey, privatekey) = (rsa.PublicKey(141246519868846003894338361868741299369130313524150308064755185766676668067369935421832072725632182491899274551030791672706990550804301704846871213345332325684004685074332536906320944501500312732925524875692434783890974488992210016296297984550019764335417519537159900313663598589710621359297809855424352771259, 65537), rsa.PrivateKey(141246519868846003894338361868741299369130313524150308064755185766676668067369935421832072725632182491899274551030791672706990550804301704846871213345332325684004685074332536906320944501500312732925524875692434783890974488992210016296297984550019764335417519537159900313663598589710621359297809855424352771259, 65537, 32448961703241610611305955052806338454638234896617285475730565587425178363707855832752547216947955194745494570095054693139393773485352800222385710100291913238287438848248881702157270014359619380896241144637878173696957997823893220512782617522688588864685355489208300116591415167771631052927548679152767380353, 46844081587247657453060832288526791259960908901410719199267217402208343339367712584320952886093842253632884160747958596636420547931456274281893596733190086226528079, 3015247926374064686869823187666135858293375894566144238714306691981691297490828353136736532798232638425639857725060492039232191993390521779550421))

bucket = 'soulscribebucket'
CATHARTIC_TYPE = 0
CASUAL_TYPE = 1

def lambda_handler(event, context):
    
    
    # get the type of request and call handler
    req = event["routeKey"][:event["routeKey"].find("/")-1]
    
    # extract caller information
    caller_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    
    if req == "POST":
        return handle_post(event, caller_id)
    elif req == "GET":
        return handle_get(event, caller_id)
    # elif req == "PUT":
    #     return handle_put(event, caller_id)
    elif req == "PATCH":
        return handle_patch(event,caller_id)
    elif req == "DELETE":
        return handle_delete(event, caller_id)
        
    
def handle_post(event, caller_id):
    # save information to the database
    try:
        body = json.loads(event["body"])
        journal_id = str(uuid.uuid4())
        journal_title = body["Title"]
        journal_category = body["Category"]
        journal_mood = body["Mood"]
        journal_type = body["JournalType"]
        cathartic_stage= body["CatharticStage"]
        created_date = body["createdDate"]
        journal_image = body["JournalImageString"] if "JournalImageString" in body else ''
        
        last_modified_timestamp = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('America/New_York')
        last_modified_timestamp = last_modified_timestamp.astimezone(to_zone)
        
        
        # process date appropiately
        created_datetime = created_date + ' ' + last_modified_timestamp.strftime('%H:%M:%S')
        
        created_datetime_format = '%d/%m/%Y %H:%M:%S'
        created_timestamp = datetime.datetime.strptime(created_datetime, created_datetime_format)
        
        last_modified_date = last_modified_timestamp.strftime('%d/%m/%Y')
        last_modified_datetime = last_modified_date + ' ' + last_modified_timestamp.strftime('%H:%M:%S')
        last_modified_timestamp = datetime.datetime.strptime(last_modified_datetime, created_datetime_format)

        
        journal_stage_1 = []
        journal_stage_2 = []
        journal_stage_3 = []
        journal_stage_4 = []
        journal_stage_5 = []
        
        stage1_data = {
            "userEntry": "",
            "modelResponse": """Describe the event: Here are some questions to think about while you write about this: What was the event like? What happened during that time? How did the situation affect you personally? What did it mean to you?"""
        }
        
        casual_data = {
            "userEntry": "", 
            "modelResponse": """What do you want to talk about today?"""
        }
        
        if journal_image:
            lambda_client = boto3.client('lambda')
            data_patch = event.copy()
            function_name = 'journal-upload-client'
            data_patch["requestContext"]['http']['method'] = "POST"
            
            response = lambda_client.invoke(FunctionName=function_name,
                                    Payload=json.dumps(data_patch))
           
                                    
            user_entry = json.loads(response['Payload'].read().decode())['journal_entry']
        
            stage1_data['userEntry'] = user_entry
            casual_data['userEntry'] = user_entry
            
        stage2_data = {
            "userEntry": "",
            "modelResponse": """Let's talk about coping mechanisms: How did this make you feel? What did you do to cope with these feelings?"""
        }
        
        stage3_data = {
            "userEntry": "",
            "modelResponse": """Backstage Scene: Does this remind you of other incidents from the past?"""
        }
        
        stage4_data = {
            "userEntry": "",
            "modelResponse": """Effects: How did you react to this situation? What were the effects of your behavior?"""
        }
        
        stage5_data = {
            "userEntry": "",
            "modelResponse": """Change perspective: Is this thought based on facts or feelings? Is this black and white or more complicated? Am I making assumptions? How would someone else interpret this situation? Is there another way of looking at the situation?"""
        }
    
        
        if(int(journal_type) == 0 ):
            journal_stage_1.append(stage1_data)
            journal_stage_2.append(stage2_data)
            journal_stage_3.append(stage3_data)
            journal_stage_4.append(stage4_data)
            journal_stage_5.append(stage5_data)
            
            journal_stage_1 = str(journal_stage_1)
            journal_stage_2 = str(journal_stage_2)
            journal_stage_3 = str(journal_stage_3)
            journal_stage_4 = str(journal_stage_4)
            journal_stage_5 = str(journal_stage_5)
            
            # encryption
            # print("encryyyyyyyyyyy")
            # journal_stage_1 = journal_stage_1.encode('utf8')
            # journal_stage_1 = rsa.encrypt(journal_stage_1, publickey)
            # print("refnbjkr5bghrb")
            # message2 = rsa.decrypt(journal_stage_1, privatekey).decode('ascii')
            # print("jdhfbhjrgvhuvfr")
            # print(message2)
            
        else:
            journal_stage_1.append(casual_data)
            journal_stage_2.append(casual_data)
            journal_stage_3.append(casual_data)
            journal_stage_4.append(casual_data)
            journal_stage_5.append(casual_data)
            
            journal_stage_1 = str(journal_stage_1)
            journal_stage_2 = str(journal_stage_2)
            journal_stage_3 = str(journal_stage_3)
            journal_stage_4 = str(journal_stage_4)
            journal_stage_5 = str(journal_stage_5)
        

        # create S3 entry and extract s3journalID
        s3_file_title_1 = str(uuid.uuid4())
        s3_file_title_2 = str(uuid.uuid4())
        s3_file_title_3 = str(uuid.uuid4())
        s3_file_title_4 = str(uuid.uuid4())
        s3_file_title_5 = str(uuid.uuid4())
        
        uploadByteStream1 = bytes(journal_stage_1.encode('UTF-8'))
        uploadByteStream2 = bytes(journal_stage_2.encode('UTF-8'))
        uploadByteStream3 = bytes(journal_stage_3.encode('UTF-8'))
        uploadByteStream4 = bytes(journal_stage_4.encode('UTF-8'))
        uploadByteStream5 = bytes(journal_stage_5.encode('UTF-8'))
        
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket, Key=s3_file_title_1, Body=uploadByteStream1)
        s3.put_object(Bucket=bucket, Key=s3_file_title_2, Body=uploadByteStream2)
        s3.put_object(Bucket=bucket, Key=s3_file_title_3, Body=uploadByteStream3)
        s3.put_object(Bucket=bucket, Key=s3_file_title_4, Body=uploadByteStream4)
        s3.put_object(Bucket=bucket, Key=s3_file_title_5, Body=uploadByteStream5)
        
        
        cnx = create_sql_connection()
        cursor = cnx.cursor()
    
        create_db_insertion_query = f"insert into Journals (JournalID, UserID, Title, Category, Mood, JournalType, CatharticStage, S3JIDStage1, S3JIDStage2, S3JIDStage3, S3JIDStage4, S3JIDStage5, LastModifiedTimestamp, createdTimestamp) values ('{journal_id}', '{caller_id}', '{journal_title}', '{journal_category}', '{journal_mood}', '{journal_type}', '{cathartic_stage}', '{s3_file_title_1}', '{s3_file_title_2}', '{s3_file_title_3}', '{s3_file_title_4}', '{s3_file_title_5}','{last_modified_timestamp}','{created_timestamp}');"
        cursor.execute(create_db_insertion_query)
        
    
        cnx.commit()
        cursor.close()
        cnx.close()
    
        response = {}
        response["journal_id"] = journal_id
        response["success"] = "true"

        return response
        
    except Exception as e:
        print("In the exception block... Error in textract!")
        response = {}
        response["success"] = "false"
        print(e)
        return response
        
        
def handle_get(event, caller_id):
    try:
        received_parameters = event["rawQueryString"].split('&')
        journal_id = received_parameters[0].split('=')[1]
        required_stage = received_parameters[1].split('=')[1]
        
        cnx = create_sql_connection()
        cursor = cnx.cursor()
        create_db_insertion_query = f"select JournalID, Title, Category, Mood, JournalType, CatharticStage, createdTimestamp, S3JIDStage1, S3JIDStage2, S3JIDStage3, S3JIDStage4, S3JIDStage5, HarmfulIntentStage1,HarmfulIntentStage2,HarmfulIntentStage3,HarmfulIntentStage4,HarmfulIntentStage5, LastModifiedTimestamp from Journals where JournalID = '{journal_id}' and UserID = '{caller_id}' ;"
        cursor.execute(create_db_insertion_query)
        journal_entry = json.loads(json.dumps(cursor.fetchall(),default=str))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        
        je = {
            "JournalID": "",
            "Title": "",
            "Category": "",
            "Mood": "",
            "JournalType": CATHARTIC_TYPE,
            "CatharticStage": 1,
            "createdTimestamp": "",
            "currentStage": [],
            "LastModifiedTimestamp": ""
        }
        
        je['JournalID'] = journal_entry[0][0]
        je['Title'] = journal_entry[0][1]
        je['Category'] = journal_entry[0][2]
        je['Mood'] = journal_entry[0][3]
        je['JournalType'] = journal_entry[0][4]
        # je['CatharticStage'] = journal_entry[0][5]
        je['CatharticStage'] = int(required_stage)
        je['createdTimestamp'] = journal_entry[0][6]
        je['LastModifiedTimestamp'] = journal_entry[0][17]
        
        ################### feedback changes ############################
        je['feedback'] = -1
         # check if feedback for the journal_id for a user already exists
        cnx = create_sql_connection()
        cursor = cnx.cursor()
        journal_feedback_existance_check = f"select Feedback from JournalFeedback where JournalID = '{journal_id}' and UserID = '{caller_id}' ;"
        cursor.execute(journal_feedback_existance_check)
        journal_feedback_existance_check = json.loads(json.dumps(cursor.fetchall(),default=str))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        
        if len(journal_feedback_existance_check) != 0:
            if journal_feedback_existance_check[0][0] == "0":
                je['feedback'] = 0
            else:
                je['feedback'] = 1
        #################################################################
        
        
        
        
        response = {}
        response["journal_entry"] = je
        
        # s3 stuff
        s3 = boto3.client('s3')
        i = int(required_stage) - 1
        try:
            S3JEid = journal_entry[0][7+i]
            ret_bytes = s3.get_object(Bucket=bucket, Key=S3JEid)
            journal_entry = ret_bytes["Body"].read()
            journal_entry_str = journal_entry.decode('utf-8')
            journal_list = ast.literal_eval(journal_entry_str)
            je["currentStage"] = journal_list
        except:
            je["currentStage"] = []
            response["success"] = "false"
            return response
            
        response["success"] = "true"
        return response
    except:
        response = {}
        response["success"] = "false"
        return response
        
# def handle_get(event, caller_id):
#     try:
#         # body = json.loads(event["body"])
        
#         # get a specefic journal from S3
        
            
#         # journal_id = body["JournalID"]
#         journal_id = event["rawQueryString"].split('=')[1]
        
#         ret_schema = ['JournalID', 'Title', 'CatID', 'Mood', 'JournalType', 'CatharticStage', 'createdTimestamp', 'JournalStage1', 'JournalStage2', 'JournalStage3', 'JournalStage4', 'JournalStage5', 'HarmfulIntentStage1'
#         ,'HarmfulIntentStage2','HarmfulIntentStage3','HarmfulIntentStage4','HarmfulIntentStage5', 'LastModifiedTimestamp']
        
#         cnx = create_sql_connection()
#         cursor = cnx.cursor()
#         create_db_insertion_query = f"select JournalID, Title, CatID, Mood, JournalType, CatharticStage, createdTimestamp, S3JIDStage1, S3JIDStage2, S3JIDStage3, S3JIDStage4, S3JIDStage5, HarmfulIntentStage1,HarmfulIntentStage2,HarmfulIntentStage3,HarmfulIntentStage4,HarmfulIntentStage5, LastModifiedTimestamp from Journals where JournalID = '{journal_id}' and UserID = '{caller_id}' ;"
#         cursor.execute(create_db_insertion_query)
#         journal_entry = json.loads(json.dumps(cursor.fetchall(),default=str))
        
#         cnx.commit()
#         cursor.close()
#         cnx.close()
        
#         response = {}
        
#         s3 = boto3.client('s3')
       
#         print("Journal Entry::", journal_entry)
#         je = {}
#         for list_elem in range(len(journal_entry[0])):
#             je[ret_schema[list_elem]] = journal_entry[0][list_elem]
        
#         response["journal_entry"] = je

#         for i in range(5):
#             entry_dict = {}
#             user_entry_list = []
#             model_entry_list = []
            
#             try:
            
#                 S3JEid = je[f"JournalStage{i+1}"]
#                 ret_bytes = s3.get_object(Bucket=bucket, Key=S3JEid)
#                 journal_entry = ret_bytes["Body"].read()
                
#                 journal_entry_str = journal_entry.decode('utf-8')
                
#                 journal_list = ast.literal_eval(journal_entry_str)
            
#                 # for elem in journal_list:
#                 #     user_entry_list.append(elem["userEntry"])
#                 #     model_entry_list.append(elem["modelResponse"])
#                 #     entry_dict["userEntry"] = user_entry_list
#                 #     entry_dict["modelResponse"] = model_entry_list
                
#                 je[f"JournalStage{i+1}"] = journal_list
#             except:
#                 # entry_dict["userEntry"] = []
#                 # entry_dict["modelResponse"] = []
#                 # je[f"JournalStage{i+1}"] = entry_dict
#                 je[f"JournalStage{i+1}"] = []
            
#         response["success"] = "true"
            
#     except:
#         response["success"] = "false"
            
#     # for i in range(5):
      
#     #     S3JEid = je[f"JournalStage{i+1}"]
#     #     ret_bytes = s3.get_object(Bucket=bucket, Key=S3JEid)
#     #     journal_entry = ret_bytes["Body"].read()
        
#     #     if(len(journal_entry) > 0):
#     #         JEStage_dict = {}
#     #         JEStage_dict["StageID"] = S3JEid
#     #         JEStage_dict["Entry"] = journal_entry
#     #         response["journal_entry"][f"JournalStage{i+1}"] = JEStage_dict
#     #     else:
#     #         JEStage_dict = {}
#     #         JEStage_dict["StageID"] = S3JEid
#     #         JEStage_dict["Entry"] = ""
#     #         response["journal_entry"][f"JournalStage{i+1}"] = JEStage_dict
    
#     return response
    
def handle_patch(event, caller_id):
    try:
        body = json.loads(event["body"])
        journal_id = body["JournalID"]
        stage = int(body["CurrentStageNumber"])
        
        last_modified_timestamp = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('America/New_York')
        last_modified_timestamp = last_modified_timestamp.astimezone(to_zone)
        
        journal_stage_entry = str(body["CurrentStageData"])
        
        cnx = create_sql_connection()
        cursor = cnx.cursor()
        
        if stage == 1:
            description = body["CurrentStageData"][0]['userEntry']
            if len(description) > 50:
                description = description[:51]
            create_db_insertion_query = f"update Journals set Description = '{description}', LastModifiedTimestamp = '{last_modified_timestamp}' where JournalID = '{journal_id}' and UserID = '{caller_id}';"
            cursor.execute(create_db_insertion_query)
            cnx.commit()
        else:
            create_db_insertion_query = f"update Journals set LastModifiedTimestamp = '{last_modified_timestamp}' where JournalID = '{journal_id}' and UserID = '{caller_id}';"
            cursor.execute(create_db_insertion_query)
            cnx.commit()
        
        create_db_select_query = f"select S3JIDStage1, S3JIDStage2, S3JIDStage3, S3JIDStage4, S3JIDStage5 from Journals where JournalID = '{journal_id}' and UserID = '{caller_id}' ;"
        cursor.execute(create_db_select_query)
        journal_entry = json.loads(json.dumps(cursor.fetchall(), default=str))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        
        uploadByteStream = bytes(journal_stage_entry.encode('UTF-8'))
        
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket, Key=journal_entry[0][stage - 1], Body=uploadByteStream)
        
        response = {}
        response["journal_id"] = journal_id
        response["success"] = "true"
        return response 
    except:
        journal_id = body["JournalID"]
        response = {}
        response["journal_id"] = journal_id
        response["success"] = "false"
        return response
    

# def handle_patch(event, caller_id):
#     # loop through the number of elements in the body and update these in the database
#     # and the s3 bucket if something in the journal changed
#     try:
#         body = json.loads(event["body"])
        
#         print("BODY is ", body)
        
#         journal_id = body["JournalID"]
#         # journal_title = body["Title"]
#         # journal_cat_id = body["CatID"]
#         # journal_mood = body["Mood"]
#         # journal_type = body["JournalType"]
#         cathartic_stage= body["CatharticStage"]
#         # harmful_intent_stage1 = body["HarmfulIntentStage1"]
#         # harmful_intent_stage2 = body["HarmfulIntentStage2"]
#         # harmful_intent_stage3 = body["HarmfulIntentStage3"]
#         # harmful_intent_stage4 = body["HarmfulIntentStage4"]
#         # harmful_intent_stage5 = body["HarmfulIntentStage5"]
#         last_modified_timestamp = datetime.datetime.now()
        
#         journal_stage_1 = str(body["JournalStage1"])
#         journal_stage_2 = str(body["JournalStage2"])
#         journal_stage_3 = str(body["JournalStage3"])
#         journal_stage_4 = str(body["JournalStage4"])
#         journal_stage_5 = str(body["JournalStage5"])
        
        
#         ret_schema = ["S3JIDStage1","S3JIDStage2", "S3JIDStage3," "S3JIDStage4", "S3JIDStage5"]
        
#         cnx = create_sql_connection()
#         cursor = cnx.cursor()
        
#         print("GOOD TILL NOW 1")
    
#         # create_db_insertion_query = f"update Journals set Title = '{journal_title}', CatID = '{journal_cat_id}', Mood = '{journal_mood}', JournalType = '{journal_type}', CatharticStage = '{cathartic_stage}', LastModifiedTimestamp = '{last_modified_timestamp}', HarmfulIntentStage1 = '{harmful_intent_stage1}', HarmfulIntentStage2 = '{harmful_intent_stage2}',HarmfulIntentStage3 = '{harmful_intent_stage3}',HarmfulIntentStage4 = '{harmful_intent_stage4}',HarmfulIntentStage5 = '{harmful_intent_stage5}';"
#         create_db_insertion_query = f"update Journals set CatharticStage = '{cathartic_stage}', LastModifiedTimestamp = '{last_modified_timestamp}' where JournalID = '{journal_id}' and UserID = '{caller_id}';"
#         cursor.execute(create_db_insertion_query)
        
#         cnx.commit()
#         print("GOOD TILL NOW 2")
#         create_db_insertion_query = f"select S3JIDStage1, S3JIDStage2, S3JIDStage3, S3JIDStage4, S3JIDStage5 from Journals where JournalID = '{journal_id}' and UserID = '{caller_id}' ;"
#         cursor.execute(create_db_insertion_query)
#         journal_entry = json.loads(json.dumps(cursor.fetchall(),default=str))
#         print("GOOD TILL NOW 3")
#         cnx.commit()
        
#         cursor.close()
#         cnx.close()
        
#         print("GOOD TILL NOW 4")
#         uploadByteStream1 = bytes(journal_stage_1.encode('UTF-8'))
#         uploadByteStream2 = bytes(journal_stage_2.encode('UTF-8'))
#         uploadByteStream3 = bytes(journal_stage_3.encode('UTF-8'))
#         uploadByteStream4 = bytes(journal_stage_4.encode('UTF-8'))
#         uploadByteStream5 = bytes(journal_stage_5.encode('UTF-8'))
        
#         s3 = boto3.client('s3')
#         s3.put_object(Bucket=bucket, Key=journal_entry[0][0], Body=uploadByteStream1)
#         s3.put_object(Bucket=bucket, Key=journal_entry[0][1], Body=uploadByteStream2)
#         s3.put_object(Bucket=bucket, Key=journal_entry[0][2], Body=uploadByteStream3)
#         s3.put_object(Bucket=bucket, Key=journal_entry[0][3], Body=uploadByteStream4)
#         s3.put_object(Bucket=bucket, Key=journal_entry[0][4], Body=uploadByteStream5)
        
#         print("GOOD TILL NOW 5")
#         response = {}
#         response["journal_id"] = journal_id
#         response["success"] = "true"
#         return response
        
#     except:
#         journal_id = body["JournalID"]
#         response = {}
#         response["journal_id"] = journal_id
#         response["success"] = "false"
#         return response


# def handle_put(event, caller_id):

#     try:
#         body = json.loads(event["body"])
            
#         journal_id = body["JournalID"]
#         journal_title = body["Title"]
#         journal_cat_id = body["CatID"]
#         journal_mood = body["Mood"]
#         journal_type = body["JournalType"]
#         cathartic_stage = body["CatharticStage"]
        
#         s3_file_title_1 = body["JournalStage1"]
#         s3_file_title_2 = body["JournalStage2"]
#         s3_file_title_3 = body["JournalStage3"]
#         s3_file_title_4 = body["JournalStage4"]
#         s3_file_title_5 = body["JournalStage5"]
        
#         cnx = create_sql_connection()
#         cursor = cnx.cursor()
    
#         create_db_insertion_query = f"select * from Journals where JournalID = '{journal_id}';"
#         cursor.execute(create_db_insertion_query)
#         journal_record = cursor.fetchall()
#         return str(journal_record)
    
#         # update S3 entry and extract s3journalID
#         s3_file_1 = journal_record[0][8]
#         s3_file_1 = journal_record[0][9]
#         s3_file_1 = journal_record[0][10]
#         s3_file_1 = journal_record[0][11]
#         s3_file_1 = journal_record[0][12]
        
#         uploadByteStream1 = bytes(s3_file_title_1.encode('UTF-8'))
#         uploadByteStream2 = bytes(s3_file_title_2.encode('UTF-8'))
#         uploadByteStream3 = bytes(s3_file_title_3.encode('UTF-8'))
#         uploadByteStream4 = bytes(s3_file_title_4.encode('UTF-8'))
#         uploadByteStream5 = bytes(s3_file_title_5.encode('UTF-8'))
        
#         s3 = boto3.client('s3')
#         s3.put_object(Bucket=bucket, Key=s3_file_1, Body=uploadByteStream1)
#         s3.put_object(Bucket=bucket, Key=s3_file_2, Body=uploadByteStream2)
#         s3.put_object(Bucket=bucket, Key=s3_file_3, Body=uploadByteStream3)
#         s3.put_object(Bucket=bucket, Key=s3_file_4, Body=uploadByteStream4)
#         s3.put_object(Bucket=bucket, Key=s3_file_5, Body=uploadByteStream5)
        
#         create_db_insertion_query = f"update Journals set UserID = '{caller_id}', \
#         Title = '{journal_title}', CatID = '{journal_cat_id}', Mood = '{journal_mood}', \
#         JournalType = '{journal_type}', CatharticStage = '{cathartic_stage}', LastModifiedTimestamp =  where JournalID = '{journal_id}'\
#         ;";
#         cursor.execute(create_db_insertion_query)
        
        
#         cnx.commit()
#         cursor.close()
#         cnx.close()
        
#         response = {}
#         response["journal_id"] = journal_id
#         response["success"] = "true"
#         return response
        
#     except:
#         response = {}
#         response["journal_id"] = journal_id
#         response["success"] = "false"
#         return response

def handle_delete(event, caller_id):
    
    try:
        received_parameters = event["rawQueryString"]
        journal_id = received_parameters.split('=')[1]
        
        # check if feedback for the journal_id for a user already exists
        cnx = create_sql_connection()
        cursor = cnx.cursor()
        journal_feedback_existance_check = f"select JournalID from JournalFeedback where JournalID = '{journal_id}' and UserID = '{caller_id}' ;"
        cursor.execute(journal_feedback_existance_check)
        journal_feedback_existance_check = json.loads(json.dumps(cursor.fetchall(),default=str))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        
        if len(journal_feedback_existance_check) != 0:
            cnx = create_sql_connection()
            cursor = cnx.cursor()
            journal_feedback_existance_check = f"delete from JournalFeedback where JournalID = '{journal_id}' and UserID = '{caller_id}';"
            cursor.execute(journal_feedback_existance_check)
            journal_feedback_existance_check = json.loads(json.dumps(cursor.fetchall(),default=str))
            
            cnx.commit()
            cursor.close()
            cnx.close()
        
        cnx = create_sql_connection()
        cursor = cnx.cursor()
        
        create_db_insertion_query = f"select * from Journals where JournalID = '{journal_id}' and UserID = '{caller_id}';"
        cursor.execute(create_db_insertion_query)
        journal_record = cursor.fetchall()
    
        # update S3 entry and extract s3journalID
        s3_file_1 = journal_record[0][8]
        s3_file_2 = journal_record[0][9]
        s3_file_3 = journal_record[0][10]
        s3_file_4 = journal_record[0][11]
        s3_file_5 = journal_record[0][12]
        
        s3 = boto3.client('s3')
        s3.delete_object(Bucket=bucket, Key=s3_file_1)
        s3.delete_object(Bucket=bucket, Key=s3_file_2)
        s3.delete_object(Bucket=bucket, Key=s3_file_3)
        s3.delete_object(Bucket=bucket, Key=s3_file_4)
        s3.delete_object(Bucket=bucket, Key=s3_file_5)
        
        create_db_insertion_query = f"delete from Journals where JournalID = '{journal_id}' and UserID = '{caller_id}';";
        cursor.execute(create_db_insertion_query)
        
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