import json
import mysql.connector
import boto3
import uuid
import datetime
import time
import os
import ast
import urllib3
http = urllib3.PoolManager()


REPLICATE_OFF = 0

TOKEN = 'r8_fSwG4EeM42yJOgtOAAMXUcBmAYUUNqA428QLS'

bucket = 'soulscribebucket'

def lambda_handler(event, context):
    print("lam")
    # get the type of request and call handler
    req = event["routeKey"][:event["routeKey"].find("/")-1]
    
    # extract caller information
    caller_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    print("before get")
    if req == "GET":
        print("get request")
        return handle_get(event, caller_id)
        # return main("")
        
    

def handle_get(event, caller_id):
    response = {}
    try:
        journal_id_int = event["rawQueryString"].split('=')[1]
        journal_id = journal_id_int.split('&')[0]
        # print("stage test", str(event["rawQueryString"].split('=')[2]))
        # ml_req_stage = str(event["rawQueryString"].split('=')[2])
        print("journal id in try", journal_id )
        ret_schema = ['JournalID', 'Title', 'Category', 'Mood', 'JournalType', 'CatharticStage', 'createdTimestamp', 'JournalStage1', 'JournalStage2', 'JournalStage3', 'JournalStage4', 'JournalStage5', 'HarmfulIntentStage1'
        ,'HarmfulIntentStage2','HarmfulIntentStage3','HarmfulIntentStage4','HarmfulIntentStage5', 'LastModifiedTimestamp']
        
        cnx = create_sql_connection()
        cursor = cnx.cursor()
        create_db_insertion_query = f"select JournalID, Title, Category, Mood, JournalType, CatharticStage, createdTimestamp, S3JIDStage1, S3JIDStage2, S3JIDStage3, S3JIDStage4, S3JIDStage5, HarmfulIntentStage1,HarmfulIntentStage2,HarmfulIntentStage3,HarmfulIntentStage4,HarmfulIntentStage5, LastModifiedTimestamp from Journals where JournalID = '{journal_id}' and UserID = '{caller_id}' ;"
        cursor.execute(create_db_insertion_query)
        journal_entry = json.loads(json.dumps(cursor.fetchall(),default=str))
   
        cnx.commit()
        cursor.close()
        cnx.close()
        
        
        
     
        s3 = boto3.client('s3')
       

        je = {}
        for list_elem in range(len(journal_entry[0])):
            je[ret_schema[list_elem]] = journal_entry[0][list_elem]
        
        response["journal_entry"] = je
        for i in range(5):
            try:
                S3JEid = je[f"JournalStage{i+1}"]
                ret_bytes = s3.get_object(Bucket=bucket, Key=S3JEid)
                
                journal_entry = ret_bytes["Body"].read()
                
                journal_entry_str = journal_entry.decode('utf-8')
                
                journal_list = ast.literal_eval(journal_entry_str)
                
                je[f"JournalStage{i+1}"] = journal_list
            except:
                je[f"JournalStage{i+1}"] = []
                
        response["success"] = "true"
            
    except:
        response["success"] = "false"
        res = {
            'statusCode': '400',
            'body': 'error while journal extraction!',
            'headers': {
                'Content-Type': 'application/json',
            }
        };
        print(res)
        return response
        
    ml_req_stage = int(event["rawQueryString"].split('=')[2])
    # print(ml_req_stage)
    data = response
    model_output = main(data, ml_req_stage)
    return model_output


def create_sql_connection():
    return mysql.connector.connect( 
        host='soulscribe-db.c7k0qn3qv7uc.us-east-1.rds.amazonaws.com', 
        user='admin', 
        password='SoulScribe69AiMl777',
        database= 'soulscribe'
    )
    
    

def casual_system_prompt(previous_entries):
    system_prompt = """
You are a therapist and help the user process their emotions. Do not try to provide solutions and instead provide empathy.
Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.
If you think the prompt is lacking information, provide possible follow-up questions in a kind, therapeutic manner while being conscious of the user's feelings. 
The context of the conversation is given below. You are the "therapist", and the user is the "patient". Keep your response as short as possible.If the overall sentiment in the patients entry is positive then try to keep your repsonse positive.Your response should be responding to the patient as the therapist \n"""
    for index, entry in enumerate(previous_entries):
        system_prompt += f"Therapist: {entry['modelResponse']}\n"
        
        if index != len(previous_entries)-1:
            system_prompt += f"Patient: {entry['userEntry']}\n"
        
    
    system_prompt += "The patients repsonse is in the prompt."
    
    return system_prompt
    
def cathartic_system_prompt(stage, journalEntries):
    system_prompt = f"""
You are a therapist and help the user process their emotions. Do not try to provide solutions and instead provide empathy.
Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.
If you think the prompt is lacking information, provide possible follow-up questions in a kind, therapeutic manner while being conscious of the user's feelings. 
You should build a response based on cathartic style of reflection, which is explained in stages below: 
Stage 1: Describing the event. 
Stage 2: Coping Mechanisms.
Stage 3: Backstage scene.
Stage 4: Effects of behavior on the patient as well as people around them. 
Stage 5: Changing patient's perspective: Here, the goal is to identify negative thinking patterns and try to reform them into positive thoughts. 

Currently, the patient is in stage {stage}. Use the context of cathartic style of reflection defined above to help the patient. 
The  conversation is given below. You are the "therapist", and the user is the "patient". Keep your response as short as possible. 
If the overall sentiment in the patients entry is positive then try to keep your repsonse positive. Your response should be responding to the patient as the therapist. \\n"""
    for stage, stageEntry in enumerate(journalEntries):
        system_prompt += f"This is the entry for stage {stage + 1}: \n"
        for index, entry in enumerate(stageEntry):
            system_prompt += f"Therapist: {entry['modelResponse']}\n"

            if index != len(journalEntries)-1:
                system_prompt += f"Patient: {entry['userEntry']}\n"
        
    
    system_prompt += "The patients repsonse is in the prompt."
    
    return system_prompt
    
    
    

def generate_text(text, sys_prompt):
    # a = 1
    # if a:
    #     return "sample response"
        
    headers = {
        'Authorization': 'Token ' + TOKEN,
    }
    
    
    json_data = {
        'version': '2d19859030ff705a87c746f7e96eea03aefb71f166725aee39692f1476566d48',
        'input': {
            'prompt': text,
            'system_prompt': sys_prompt
        },
    }
    
    # Convert the json_data dictionary to a JSON-formatted string
    json_string = json.dumps(json_data)
    
    # Make the POST request
    url = 'https://api.replicate.com/v1/predictions'
    response = http.request('POST', url, headers=headers, body=json_string)
    
    # Parse the response data
    response_data = json.loads(response.data)
    
    replicate_req_id = response_data['id']
    
    time.sleep(5)
    
    replicate_status = 'processing'
    
    while replicate_status != 'succeeded':
        if replicate_status not in ('processing', 'starting') :
            # TODO: return error//error handling
            # print(response)
            # print(response_data)
            print("ERRORRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
            break
    
        # Make the GET request
        url = 'https://api.replicate.com/v1/predictions/' + replicate_req_id
        response = http.request('GET', url, headers=headers)
    
        # Parse the response data
        response_data = json.loads(response.data)
        replicate_status = response_data['status']
        time.sleep(1)
        # break
        # return response_data
        # print(response_data)
    
           
        
    result = "".join(response_data["output"])  
    result = result.strip()
    if "therapist" in result[0:11].lower():
        return result[11:]
        
    return result


def checkHarmfulIntent(user_entry):
    # API_URL = "https://api-inference.huggingface.co/models/vibhorag101/roberta-base-suicide-prediction-phr"
    API_URL = "https://api-inference.huggingface.co/models/mrm8488/distilroberta-base-finetuned-suicide-depression"
    headers = {"Authorization": "Bearer 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"}
    
    # testing hamr intent:
    # user_entry = "I want to die"
    # print("User Entry : ", user_entry)
    def query(payload):
        json_string = json.dumps(payload)
        response = http.request('POST', API_URL, headers=headers, body=json_string)
        return json.loads(response.data)
    
    
    counter = 0
    while counter < 5:
        try:
            output = query({
                "inputs": user_entry,
            })
            break
        except:
            print("error")
            counter ++ 1
        
    if counter == 5:
        return False
    
    # delete after integrating try catch blocks
    print("out classification values:", output)

    # if output[0][0]['label'] == 'suicide':
    #     harmful_score = output[0][0]['score']
    # else:
    #     harmful_score = output[0][1]['score']
    
    if output[0][0]['label'] == 'LABEL_1':
        harmful_score = output[0][0]['score']
    else:
        harmful_score = output[0][1]['score']
        
        
    print(harmful_score)
        
    threshold = 0.97
    
    print("Harm Intent output",output)
    if harmful_score >= threshold:
        print("True")
        return True 
    print("False")
    return False 

def buildHarmresponse():
    # make generative later 
    response = "As an AI language model, I don't have feelings or emotions, but I am designed to provide helpful and supportive responses to you. However, it seems like you are going through a challenging time and dealing with issues that may benefit from professional help, I would recommend that you consider speaking with a licensed therapist or counselor."
    return response

def generateCatharticResponse(user_entry, stage, journalEntries):
    if REPLICATE_OFF:
        return "dummy response, testing mode"
    system_prompt = cathartic_system_prompt(stage, journalEntries)
    prompt = user_entry
    
    # print(system_prompt)
    # print(f"Prompt: {prompt}")

    response = generate_text(prompt, system_prompt)
    return response

def generateCasualResponse(user_entry, journalEntries):
    if REPLICATE_OFF:
        return "dummy response, testing mode"
    prompt = user_entry
    system_prompt = casual_system_prompt(journalEntries[0])
    # print(system_prompt)
    
    # print(f"Prompt: {prompt}")
    response = generate_text(prompt, system_prompt)
    return response

def promptSafetyDetector(model_repsonse):
    print("entering prompt satfety")
    
    API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
    headers = {"Authorization": "Bearer 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"}
    
    def query(payload):
        json_string = json.dumps(payload)
        response = http.request('POST', API_URL, headers=headers, body=json_string)
        return json.loads(response.data)
        
    output = query({
        "inputs": model_repsonse,
    })
    
    print(output)
    # print(f"OUTPUT: {output}")
    for op in output[0]:
        # print(f"{op['label']}")
        if op['label'] == 'negative':
            # print("in neg", op['score'])
            if op['score'] > 0.80:
                # print("HARMMM DETEXCTED")
                return False
    

    
    return True

def generatePrompt(journal_type, user_entry, stage, journalEntries):
    safety_counter = 0
    safety_threshold = 2
    
    while(safety_counter<safety_threshold):
        
        if journal_type == 1:
            response = generateCatharticResponse(user_entry, stage, journalEntries)
        else:
            response = generateCasualResponse(user_entry, journalEntries)
        # check safe
        try:
            safe = promptSafetyDetector(response)
        except:
            #response = "Prompt safety detector model is down, please try again."
            safe = True
        if safe:
            # return safe model response
            print(response)
            return response
        safety_counter += 1
        
    
    # if unsafe response:
    
    response = "Thank you for sharing your feelings with me. Can you please tell me more about what you said?"
    
    # print(f"RESPONSE: {response}")
    
    return response
    

    
def main(response, stage):
    # stage = response["journal_entry"]["CatharticStage"]
    # stage =5
    # print(f"Stage:{stage}")
    # print(f"Response:{response}")
    # print(f"current entry raw",response["journal_entry"][f"JournalStage{stage}"])
    currentEntry = response["journal_entry"][f"JournalStage{stage}"][-1]
    print(currentEntry)
    previousEntries = response["journal_entry"][f"JournalStage{stage}"]
    journalEntries = []
    for i in range(1, stage+1):
        journalEntries.append(response["journal_entry"][f"JournalStage{i}"])
    print(journalEntries)
    # change later 
    if currentEntry["userEntry"].strip() == "":
        return {"modelResponse":  "Please enter something"}
        
    try:
        harmIntent = checkHarmfulIntent(currentEntry["userEntry"])
    except:
        harmIntent = False
    # test harm intent
    # harmIntent = checkHarmfulIntent("I want to die")
    # harmIntent = False
    print("in main")
    print(f"harm intent: {harmIntent}")
    if harmIntent: 
        modelResponse = buildHarmresponse() 
        
        response["journal_entry"][f"HarmfulIntentStage{stage}"] = 1
        response["journal_entry"][f"JournalStage{stage}"].append({"modelResponse": modelResponse, "userEntry": ""})
        
        return {"modelResponse":  modelResponse}
    
    modelResponse = generatePrompt(response["journal_entry"]["JournalType"], currentEntry["userEntry"], stage, journalEntries)
    
    response["journal_entry"][f"HarmfulIntentStage{stage}"] = 0
    response["journal_entry"][f"JournalStage{stage}"].append({"modelResponse": modelResponse, "userEntry": ""})

    # return response
    # At the moment santino only wants the response generated
    print("final model response sent: ",  modelResponse)
    return {"modelResponse":  modelResponse}