# Note:
# On Brunch days there are no Entrees, but rather the category is called BRUNCH
# For Breakfast there are Breakfast Meats, Breakfast Entrees, Breakfast Bakery. But who the fuck eats breakfast anyways.

import requests
from bs4 import BeautifulSoup
import datetime

def lambda_handler(event, context):
    
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event, context)
    elif event['request']['type'] == "IntentRequest":
        return intent_router(event, context)
        
def on_launch(event, context):
    return statement("This is the title", "This is the body")
    
def statement(title, body):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
    speechlet['shouldEndSession'] = True
    return build_response(speechlet)
    
def build_PlainSpeech(body):
    speech = {}
    speech['type'] = 'PlainText'
    speech['text'] = body
    return speech

def build_SimpleCard(title, body):
    card = {}
    card['type'] = 'Simple'
    card['title'] = title
    card['content'] = body
    return card

def build_response(message, session_attributes={}):
    response = {}
    response['version'] = '1.0'
    response['sessionAttributes'] = session_attributes
    response['response'] = message
    return response

def intent_router(event, context):
    intent = event['request']['intent']['name']
    # Custom Intents
    if intent == "FindTheEntrees":
        return get_entrees_intent(event, context)
    # Required Intents
    if intent == "AMAZON.CancelIntent":
        return cancel_intent()
    if intent == "AMAZON.HelpIntent":
        return help_intent()
    if intent == "AMAZON.StopIntent":
        return stop_intent()

def get_entrees_intent(event, context):
    meal = event['request']['intent']['slots']['Meal']['value']
    entreeStatement = format_response(get_menu_items(meal))
    return statement("What's Cookin?", entreeStatement)

            
def get_menu_items(meal):
    """ input is lunch or dinner (case insensitive) and the output is a list of foods. """

    # Remove all spaces in the meal
    meal = meal.replace(" ","")
    print(meal)
    url = "http://www.foodpro.huds.harvard.edu/foodpro/menu_items.asp?type=05&"

    # If it is a saturday, then we need to change the url input.
    now = datetime.datetime.now()
    # Subtract 5 hours from the system time to get EST.
    now = now - datetime.timedelta(hours=5, minutes=0)
    print(now.weekday())
    if int(now.weekday()) == 6:
        if meal.lower() == 'lunch':
            url = url + "meal=0"
        elif meal.lower() == 'dinner':
            url = url + "meal=1"
    else:
        if meal.lower() == 'lunch':
            url = url + "meal=1"
        elif meal.lower() == 'dinner':
            url = url + "meal=2"

    s = requests.session()
    r=s.get(url)
    soup=BeautifulSoup(r.content,'html.parser')
    menuList = soup.findAll(True, {"class":["category", "item_wrap"]})

    textList = []
    for menuItem in menuList:
        textm = menuItem.text.replace("\t","").replace("\n","").replace("\r","").replace("\xa0",""). replace("| ","").replace("|","")
        textList.append(textm)

    #print(textList)

    outputList = []

    isEntree = False
    for text in textList:
        if text == 'Poutine':
            # FUCKING POUTINE!!!
            outputList.append(text)
            print('There is fucking poutine.')

        # Otherwise output the elements in Entrees and Vegetarian Entree (AKA stop once you read STARCH & POTATOES)

        if text == 'ENTREES':
            isEntree = True
        elif text == 'VEGETARIAN ENTREE':
            continue
        elif text == 'STARCH & POTATOES':
            isEntree = False
        elif isEntree:
            outputList.append(text)
            print(text)
        elif text == 'BRUNCH':
            outputList.append("brunch food")

    return outputList

def format_response(foodList):
    """ When given a list of foods, it takes it and formats it into a sentence. """

    statement = "The entrees today are "

    if len(foodList) > 1:
        counter = 1
        for food in foodList:
            if counter == len(foodList):
                statement = statement + "and " + food + "."
            else:
                statement = statement + food + ", "
            counter += 1
    else:
        for food in foodList:
            statement = "The entree today is " + food + "."

    print(statement)
    return statement