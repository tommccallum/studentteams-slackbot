# Student Teams

Create channels and add students and teachers to it.

## Getting started

```
python -m venv venv
source venv/bin/activate
pip install slack_bot
pip install python-dotenv
git clone https://github.com/slackapi/python-slack-sdk slack-sdk
cp .env .env.template
```

Modify the .env file with your Slack credentials for your new bot.

To run the script you then need to do the following:

```
source venv/bin/activate
export PYTHONPATH=slack-sdk
python createStudentTeams.py <team json description>
```

## Example teams file

Here is an example teams file.  The list of admins will be added to ALL channels specified under the **teams** key.

**name** is the name of the channel

**description** gives you slightly longer string to give more information.  This is mapped to what Slack called the conversation *purpose*.

**type** parameter can be set to **private** or **public**.

**members** parameter is a list of *name* values for each member you want to add.  You may need to query the users.list API call first to know what to put here.

```
{
    "admins": [ "USER1", "USER2" ],
    "teams": [
        {
            "name": "newprivatechannel",
            "description": "description of new private channel",
            "members": [
                "USER3",
                "USER4",
                "USER5",
                "USER6",
                "USER7"
            ],
            "type": "private"
        }
    ]
}
```
