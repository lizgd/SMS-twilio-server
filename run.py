#import all the libraries we will be using
from flask import Flask, request
from twilio import twiml
import wolframalpha
import wikipedia
import yweather

# set up Flask to connect this code to the local host, which will
# later be connected to the internet through Ngrok
app = Flask(__name__)

# Set up the Wolfram Alpha API and the yWeather API. You will need to get an app_id
# on https://products.wolframalpha.com/api/ 
wolfram_app_id = "MY_APP_ID_FOR_WOLFRAM_API"
wolf = wolframalpha.Client(wolfram_app_id)
weath = yweather.Client()
    
# Main method. When a POST request is sent to our local host through Ngrok (which creates 
# a tunnel to the web), this code will run. The Twilio service sends the POST request - we will
# set this up on the Twilio website. So when a message is sent over SMS to our Twilio number,
# this code will run
@app.route('/', methods=['POST'])
def sms():
    # Get the text in the message sent
    message_body = request.form['Body']
    
    # Create a Twilio response object to be able to send a reply back
    resp = twiml.Response()
    
    # Send the message body to the getReply message, where 
    # we will query the String and formulate a response
    replyText = getReply(message_body)
    resp.message('Hi\n\n' + replyText )
    return str(resp)

# Function for editing input text. Ex: If you send the message "wolfram calories in bread", 
# the program will recognize "wolfram" and call this function and will 
# change the text to "calories in bread", which will then be sent to wolfram.
def removeHead(fromThis, removeThis):
    if fromThis.endswith(removeThis):
        fromThis = fromThis[:-len(removeThis)].strip()
    elif fromThis.startswith(removeThis):
        fromThis = fromThis[len(removeThis):].strip()
    
    return fromThis

# Function to formulate a response based on message input.
def getReply(message):
    
    # Make the message lower case and without spaces on the end for easier handling
    message = message.lower().strip()
    # This is the variable where we will store our response
    answer = ""
    
    # is the keyword schedule in the message? Ex: "What is my A day schedule?" 
    # Will return class schedule
    if "schedule" in message:
        if "a day" in message:
            answer = "Your A day schedule:\n4. Study hall\n1. Chinese\n2. Lang\n8. CSP\n5. AT CS\n6. AS"
        elif "b day" in message:
            answer = "Your B day schedule:\n3. Calc\n4. Study Hall\n1. Chinese\n7. Health\n8. CSP\n5. AT CS"
        elif "c day" in message:
            answer = "Your C day schedule:\n2. Lang\n3. Calc\n4. Study Hall\n6. AS\n7. Health\n8. CSP"
        elif "d day" in message:
            answer = "Your D day schedule:\n1. Chinese\n2. Lang\n3. Health\n5.AT CS\n6. AS\n7.  Health"
            
    # is the keyword "wolfram" in the message? Ex: "wolfram integral of x + 1"
    elif "wolfram" in message:
        # remove the keyword "wolfram" from the message
        message = removeHead(message, "wolfram")
        
        # send the message to the wolfram service, get a response
        res = wolf.query(message)
        try:
            answer = next(res.results).text
        except:
            # Handle errors such as request not found error
            answer = "Request was not found using wolfram. Be more specific?"
    
    # is the keyword "wiki" in the message? Ex: "wiki donald trump"
    elif "wiki" in message:
        # remove the keyword "wiki" from the message
        message = removeHead(message, "wiki")
        
        # Get the wikipedia summary for the request
        try:
            answer = wikipedia.summary(message)
        except:
            # handle errors or non specificity errors (ex: there are many people named donald)
            answer = "Request was not found using wiki. Be more specific?"
    
    # is the keyword "westher" in the message? Ex: "weather for New York City, NY
    elif "weather" in message:
        
        # remove the keyword to just get the address/place
        message = removeHead(message, "weather").trim()
        message = removeHead(message, "for").trim()
        
        # using the yWeather API functions, get the weather data. Check out their docs for more info
        try:
            woeID = weath.fetch_woeid(message)
            lid = weath.fetch_lid(woeID)
            myWeather = weath.fetch_weather(lid)
            answer = "" + myWeather[title] + "\n" + myWeather[condition][temp] + "\n" + myWeather[condition][text] + "\n" + "Humidity: " + myWeather[atmosphere][humidity] + "\n" + "Wind: " + myWeather[wind][speed] + "\n" + "Wind chill: " + myWeather[wind][chill] + "\n"
        except:
            answer = "Something went wrong getting the weather :|"
    
    # the message contains no keyword. Display a help prompt to identify possible commands
    else:
        answer = "\n Welcome! These are the commands you may use: \nSCHEDULE + \"day\" + DAY\nWOLFRAM \"wolframalpha request\" \nWIKI \"wikipedia request\"\nWEATHER \"place\"\n"
    
    # Twilio can not send messages over 1600 characters in one message. Wikipedia summaries may have
    # way more than this. So shortening is required (1500 chars is a good bet):
    if len(answer) > 1500:
        answer = answer[0:1500] + "..."
    
    # return the formulated answer
    return answer

# when you run the code through terminal, this will allow Flask to work
if __name__ == '__main__':
    app.run()