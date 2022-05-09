import json
import boto3

dynamo_client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')
tableName = 'CSCVT_Clients'
    
    
#intent request reach in for slots property and placeses them in a list

def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']

#looks for a specific slot in the list of slots after confirming the list isn't empty and the slot isn't none

def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None:
        return slots[slotName]['value']['interpretedValue']
    else:
        return None  
        
def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']


#fufills intent and sends message and closes Dialog State

def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }
    
def check_State(intent_request):
    
    resolvedSlots = intent_request['transcriptions'][0]['resolvedSlots']
    attributes2 = get_session_attributes(intent_request)
    
    if (len(resolvedSlots) > 0 ):
        
        print(resolvedSlots)
        
        if ('CustomerEmail'  in resolvedSlots ):
        
            ##session_attributes = get_sess_state(intent_request)
            #slots = get_slots(intent_request)
            #acquire items for DB
            CustomerEmail = intent_request['interpretations'][0]['intent']['slots']['CustomerEmail']['value']['originalValue']
            CustomerFirstName = intent_request['interpretations'][0]['intent']['slots']['CustomerFirstName']['value']['originalValue']
            CustomerLastName = intent_request['interpretations'][0]['intent']['slots']['CustomerLastName']['value']['originalValue']
            CustomerNumber = intent_request['interpretations'][0]['intent']['slots']['CustomerNumber']['value']['originalValue']
            
            attributes2 = get_session_attributes(intent_request)
        
            return(DBQueryandUpdate(CustomerEmail,CustomerFirstName,CustomerLastName,CustomerNumber,attributes2,intent_request))
           
        
        else:
            
            session_attributes = get_session_attributes(intent_request)
            slots = get_slots(intent_request)
            
            text = "......"
            message =  {
                'contentType': 'PlainText',
                'content': text
            }
            
            print("proceeding")
            print('innner else')
            
            sessionState = intent_request['interpretations'][0]['intent']['state']
            
            return proceed(intent_request, session_attributes, sessionState, message)
    
    else:
        
        session_attributes = get_session_attributes(intent_request)
        slots = get_slots(intent_request)
        
        text = "......"
        message =  {
            'contentType': 'PlainText',
            'content': text
        }
            
        print("proceeding")
        print('outer else')
        
        fullfillment_state = intent_request['interpretations'][0]['intent']['state']
        return proceed(intent_request, session_attributes, fullfillment_state, message)
    
    return(null)
    

#attempt to proceed with intent

def proceed(intent_request,session_attributes,fullfillment_state,message):
    
    CustomerEmail = intent_request['sessionState']['intent']['slots']
    
    
    #intent_request['interpretations'][0]['intent']['state'] = fullfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction' : {
            #checkhere
                'type' : 'Delegate',
                #'slots': {
                    #'CustomerFirstName': CustomerFirstName,
                    #'CustomerNumber': CustomerNumber,
                    #'CustomerEmail': CustomerEmail,
                    #'CustomerLastName':CustomerLastName
                },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }
    
    
def DBQueryandUpdate(Email,First,Last,Number,event_attributes,event):
    
    table = dynamodb.Table(tableName)
    
    #query
    response_items = table.get_item(Key={
                                'Email': Email
                                })
        
        
    print(response_items)
    
    if 'Item' in response_items:
            print("User found by email!")
            
            query_name = response_items['Item']['FirstName']
            query_lastname= response_items['Item']['LastName']
            query_number = response_items['Item']['phoneNumber']
            query_email = response_items['Item']['Email']
            
            
            
            #####let user know we found his deets in database
            text = "User found as: "+query_name+" "+query_lastname+" with number: "+query_number+". And email;"+query_email
            message =  {
            'contentType': 'PlainText',
            'content': text
        }
            
            
            return {
                'sessionState': {
                'sessionAttributes': event_attributes,
                'dialogAction' : {
                 
                    'type' : 'Close'
                },
            'intent': event['sessionState']['intent']
            },
            'messages': [message],
            'sessionId': event['sessionId'],
            'requestAttributes': event['requestAttributes'] if 'requestAttributes' in event else None
    }
    
            
            
    else:
        response = dynamo_client.put_item(
        TableName = tableName, 
        Item = { 
            'Email': {
                'S':Email
            },
            'FirstName': {
                'S':First
            },
            'LastName': {
                'S':Last
            },
            'phoneNumber': {
                'S':Number
            }
            
            })
        
        print("Customer added to DB")
        
        text = "User added as: "+First+" "+Last+" with number: "+Number+". And email ;"+Email
        message =  {
            'contentType': 'PlainText',
            'content': text
        }
        #return to lex-bot
        return {
            'sessionState': {
            'sessionAttributes': event_attributes,
            'dialogAction' : {
             
                'type' : 'Close'
            },
            'intent': event['sessionState']['intent']
            },
            'messages': [message],
            'sessionId': event['sessionId'],
            'requestAttributes': event['requestAttributes'] if 'requestAttributes' in event else None
        }
        
        
##########################  MAIN MAGIC DOWN HERE  ######################################        

def dispatch(intent_request):
    intent_name = intent_request['sessionState']['intent']['name']
    response = None
    
    # Dispatch to your bot's intent handlers
    if intent_name == 'Greeting':
        return check_State(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

#handler function handling request

def lambda_handler(event, context):
    response = dispatch(event)
    return response