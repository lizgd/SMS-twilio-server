from twilio.rest import TwilioRestClient

account_sid = "AC05bed0fc7c8006ca723e7dc69946ed58" # Your Account SID from www.twilio.com/console
auth_token  = "9db110c7e933fae38ba724bbe902ee2a"  # Your Auth Token from www.twilio.com/console

client = TwilioRestClient(account_sid, auth_token)

message = client.messages.create(body="Hello from Python",
    to="+16092739725",    # Replace with your phone number
    from_="+16093373487") # Replace with your Twilio number

print(message.sid)
