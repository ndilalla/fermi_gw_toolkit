import os 
import requests
from fermi_gw_toolkit.tools.config import slack_token

def send_chat(message, channel='ligofup', icon_emoji=":crystal_ball:", username="GWFUP"):

	# Slack API endpoint for chat.postMessage
	url = "https://slack.com/api/chat.postMessage"

	# Create a dictionary with the required parameters
	payload = {
	    "token": slack_token,
	    "channel": channel,
	    "text": message,
	    "icon_emoji": icon_emoji,
		"username": username
	}

	# Make the request to send the message
	response = requests.post(url, data=payload)

	# Check if the request was successful
	if response.json()['ok'] == True:
	    print("Message sent successfully!")
	else:
	    print("Error sending message. Error code:", response.json()['error'])

if __name__ == '__main__':
	send_chat("Test. Please ignore.", channel='bot-testing')