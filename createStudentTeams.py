import json
import os
import sys
from dotenv import load_dotenv
import urllib
import logging

load_dotenv()

# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def createChannel(channel):
    isPrivate = False
    if "type" in channel:
        isPrivate = (channel["type"].upper() == "PRIVATE")

    print("Creating channel: {} private: {}".format(channel["name"],isPrivate))

    # WebClient insantiates a client that can call API methods
    # When using Bolt, you can use either `app.client` or the `client` passed to listeners.
    client = WebClient(token=os.getenv("SLACK_USER_OAUTH_TOKEN"))
    logger = logging.getLogger(__name__)
    try:
            # Call the conversations.create method using the WebClient
            # conversations_create requires the channels:manage bot scope
            result = client.conversations_create(
                # The name of the conversation
                name=channel["name"],
                is_private=isPrivate
            )
            # Log the result which includes information like the ID of the conversation
            logger.info(result)
            channel["slackChannelId"] = result["channel"]["id"]
            print("Successful creation, channel has id {}".format(result["channel"]["id"]))
            return channel
    except SlackApiError as e:
        raise Exception("Error creating conversation: {}".format(e))
    
def setChannelPurpose(channel):
    # WebClient insantiates a client that can call API methods
    # When using Bolt, you can use either `app.client` or the `client` passed to listeners.
    client = WebClient(token=os.getenv("SLACK_USER_OAUTH_TOKEN"))
    logger = logging.getLogger(__name__)
    try:
            # Call the conversations.create method using the WebClient
            # conversations_create requires the channels:manage bot scope
            result = client.conversations_setPurpose(
                # The name of the conversation
                channel=channel["slackChannelId"],
                purpose=channel["description"]
            )
            # Log the result which includes information like the ID of the conversation
            logger.info(result)
    except SlackApiError as e:
        raise Exception("Error creating conversation: {}".format(e))

def getAllUsers():
    # WebClient insantiates a client that can call API methods
    # When using Bolt, you can use either `app.client` or the `client` passed to listeners.
    client = WebClient(token=os.getenv("SLACK_USER_OAUTH_TOKEN"))
    logger = logging.getLogger(__name__)
    try:
            result = client.users_list()
            # Log the result which includes information like the ID of the conversation
            logger.info(result)
            return result["members"]
    except SlackApiError as e:
        raise Exception("Error creating conversation: {}".format(e))


def addMember(channel, member):
    # TODO check if member is self if so then we can't add it, or we can just ignore this error
    print("Adding {} ({}) to channel {}".format(member["name"], member["slackUserId"], channel["name"]))
    # WebClient insantiates a client that can call API methods
    # When using Bolt, you can use either `app.client` or the `client` passed to listeners.
    client = WebClient(token=os.getenv("SLACK_USER_OAUTH_TOKEN"))
    logger = logging.getLogger(__name__)
    try:
            # Call the conversations.create method using the WebClient
            # conversations_create requires the channels:manage bot scope
            result = client.conversations_invite(
                # The name of the conversation
                channel=channel["slackChannelId"],
                users=member["slackUserId"]
            )
            # Log the result which includes information like the ID of the conversation
            logger.info(result)
    except SlackApiError as e:
        raise Exception("Error creating conversation: {}".format(e))

def addMembers(team, admins=None):
    if admins:
        for admin in admins:
            addMember(team, admin)
    if "members" in team:
        for member in team["members"]:
            addMember(team, member)

class TeamBuilder:
    def __init__(self, teamsJsonFile, users):
        self.teamsJsonFile = teamsJsonFile
        self.data = None
        self.users = users

    def loadFile(self, fileName=None):
        if not fileName:
            fileName = self.teamsJsonFile
        with open(fileName) as inFile:
            self.data = json.load(inFile)

    def findUser(self, user):
        for u in self.users:
            if u["name"] == user:
                return u["id"]
        raise Exception("could not find {} in users".format(user))

    def build(self):
        if not self.data:
            self.loadFile()
        admins = self.data["admins"]
        for index, admin in enumerate(admins):
            slackUserId = self.findUser(admin)
            admins[index] = {
                "name": admin,
                "slackUserId": slackUserId
            }

        teams = self.data["teams"]
        for index, team in enumerate(teams):
            if "members" in team:
                for index, member in enumerate(team["members"]):
                    slackUserId = self.findUser(member)
                    team["members"][index] = {
                        "name": member,
                        "slackUserId": slackUserId
                    }

        for index, team in enumerate(teams):
            team = createChannel(team)
            setChannelPurpose(team)
            addMembers(team, self.data["admins"])


if __name__ == "__main__":
    teamsJsonFile = None
    argIndex = 1
    while argIndex < len(sys.argv):
        if argIndex == len(sys.argv)-1:
            teamsJsonFile = sys.argv[argIndex]
        argIndex += 1

    if not teamsJsonFile:
        raise Exception("no teams json file specified")
    
    users = getAllUsers()
    teams = TeamBuilder(teamsJsonFile, users)
    teams.build()
    
    