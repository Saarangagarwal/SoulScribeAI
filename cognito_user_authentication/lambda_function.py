import json
import mysql.connector
import boto3
import rsa
(publickey, privatekey) = (rsa.PublicKey(141246519868846003894338361868741299369130313524150308064755185766676668067369935421832072725632182491899274551030791672706990550804301704846871213345332325684004685074332536906320944501500312732925524875692434783890974488992210016296297984550019764335417519537159900313663598589710621359297809855424352771259, 65537), rsa.PrivateKey(141246519868846003894338361868741299369130313524150308064755185766676668067369935421832072725632182491899274551030791672706990550804301704846871213345332325684004685074332536906320944501500312732925524875692434783890974488992210016296297984550019764335417519537159900313663598589710621359297809855424352771259, 65537, 32448961703241610611305955052806338454638234896617285475730565587425178363707855832752547216947955194745494570095054693139393773485352800222385710100291913238287438848248881702157270014359619380896241144637878173696957997823893220512782617522688588864685355489208300116591415167771631052927548679152767380353, 46844081587247657453060832288526791259960908901410719199267217402208343339367712584320952886093842253632884160747958596636420547931456274281893596733190086226528079, 3015247926374064686869823187666135858293375894566144238714306691981691297490828353136736532798232638425639857725060492039232191993390521779550421))


def lambda_handler(event, context):
    

    # check the type of trigger
    if event["triggerSource"] == "PostConfirmation_ConfirmSignUp":
        return handle_PostConfirmation_ConfirmSignUp(event)

    return event

def handle_PostConfirmation_ConfirmSignUp(event):
    # extract data from the request
    user_id = event["userName"]
    user_email = event["request"]["userAttributes"]["email"]
    user_name = event["request"]["userAttributes"]["name"]
    
    # encrypt user email:
    user_email = user_email.encode('ascii')
    user_email = rsa.encrypt(user_email, publickey)
    xyz = ''

    for char in user_email:
        xyz += str(int(char))
        
    user_email = xyz
    
    user_name = user_name.encode('ascii')
    user_name = rsa.encrypt(user_name, publickey)
    xyz = ''

    for char in user_name:
        xyz += str(int(char))
    
    user_name = xyz
    
    user_email_verified = 0
    if event["request"]["userAttributes"]["email_verified"] == "true":
        user_email_verified = 1
    
    
    # save information to the database
    cnx = mysql.connector.connect( 
        host='soulscribe-db.c7k0qn3qv7uc.us-east-1.rds.amazonaws.com', 
        user='admin', 
        password='SoulScribe69AiMl777',
        database= 'soulscribe'
    )
    
    cursor = cnx.cursor()
    

    create_db_insertion_query = f"insert into Users (UserID, UserEmail, UserName, UserEmailVerified) values ('{user_id}', '{user_email}', '{user_name}', {user_email_verified});"
    print(create_db_insertion_query)
    cursor.execute(create_db_insertion_query)

    cnx.commit()
    cursor.close()
    cnx.close()
    
    return event