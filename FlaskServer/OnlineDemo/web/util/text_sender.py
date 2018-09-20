from twilio.rest import Client

# the following line needs your Twilio Account SID and Auth Token
client = Client("AC81c3ecea6bee236ac20aae9f12f3ef93", "160da42a5b96af1fff29eee3887b726d")

# change the "from_" number to your Twilio number and the "to" number
# to the phone number you signed up for Twilio with, or upgrade your
# account to send SMS to any phone number
client.messages.create(to="+13108014729",
                       from_="+16263176399",
                       body="Hello from Python!")
