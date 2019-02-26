import requests
import json
import time
import getkeys

favourites = {}

def sendmessage(webex_token, message_room, message):
    HTTPHeaders = {"Authorization": webex_token,
                   "Content-Type": "application/json"}
    data_json = {"roomId": message_room,
                 "text": message}
    requests.post("https://api.ciscospark.com/v1/messages",
                  data=json.dumps(data_json),
                  headers=HTTPHeaders)


def getnextmessage(webex_token, message_room, last_message):
    while True:
        getParams = {"roomId": listening_room, "max": 1}
        webex_res = requests.get("https://api.ciscospark.com/v1/messages",
                                 params=getParams,
                                 headers={"Authorization": webex_token})
        if not webex_res.status_code == 200:
            raise Exception("Incorrect reply from Webex Teams API.\n"
                            "Status code: {}.\n"
                            "Text: {}".format(webex_res.status_code,
                                              webex_res.text))
        message_json = webex_res.json()
        message = message_json["items"][0]["text"]
        if message != last_message:
            break
        time.sleep(1)
    return message


def displayhelp(webex_token, message_room):
    webex_msg = "\nCommand help:\n\n" +\
                "help - display help information\n" +\
                "listrepos - show all your repositories\n" +\
                "searchrepos - search repositories for a string\n" +\
                "listcollabs - show collaborators on each repository\n" +\
                "makerooms - make webex rooms for your repositories\n" +\
                "deleterooms - delete webex rooms for your repositories"
    sendmessage(webex_token, message_room, webex_msg)


def listrepos(github_token, webex_token, message_room):
    repos_res = requests.get("https://api.github.com/user/repos",
                             headers={"Authorization": github_token})

    github_json = repos_res.json()
    webex_msg = ""

    for repo in github_json:
        webex_msg += repo["name"] + ": https://www.github.com/" +\
            repo["full_name"] + "\n"
    sendmessage(webex_token, message_room, webex_msg)


def listcollaborators(github_token, webex_token, message_room):
    repos_res = requests.get("https://api.github.com/user/repos",
                             headers={"Authorization": github_token})
    repos_json = repos_res.json()
    webex_msg = ""

    for repo in repos_json:
        collab_res = requests.get("https://api.github.com/repos/" +
                                  repo["full_name"] +
                                  "/collaborators",
                                  headers={"Authorization": github_token})
        print("Collaborators on " + repo["full_name"] + ": ")
        webex_msg += "Collaborators on " + repo["name"] + ":\n"
        collab_json = collab_res.json()
        for collab in collab_json:
            print("    https://github.com/" + collab["login"] + "\n")
            webex_msg += "    https://github.com/" + collab["login"] + "\n"

    sendmessage(webex_token, message_room, webex_msg)


def searchrepos(github_token, webex_token, message_room):
    querytext = "What do you want to search for?"
    HTTPHeaders = {"Authorization": webex_token,
                   "Content-Type": "application/json"}
    data_json = {"roomId": message_room,
                 "text": querytext}
    requests.post("https://api.ciscospark.com/v1/messages",
                  data=json.dumps(data_json),
                  headers=HTTPHeaders)
    query = getnextmessage(webex_token, message_room, querytext)
    query_res = requests.get("https://api.github.com/search/repositories",
                             params={"q": query},
                             headers={"Authorization": github_token})
    query_data = query_res.json()

    webex_msg = ""
    for result in query_data["items"]:
        print(result["full_name"])
        webex_msg += "http://www.github.com/" + result["full_name"] + "\n"

    sendmessage(webex_token, message_room, webex_msg)

def bookmarkRepos(github_token, webex_token, message_room):
    starred_res = requests.get("https://api.github.com/user/starred", 
                    headers={"Authorization": github_token})
    github_json = starred_res.json()

    webex_msg = ""
    for starred in github_json:
        name = starred["name"]
        url = [starred["owner"]["starred_url"], starred["updated_at"]]
        favourites.update({name: url})
        webex_msg += name + "\n"
    sendmessage(webex_token, message_room, webex_msg)
    

def makerooms(github_token, webex_token, message_room):
    repos_res = requests.get("https://api.github.com/user/repos",
                             headers={"Authorization": github_token})
    repos_json = repos_res.json()
    webex_msg = ""

    for repo in repos_json:
        confirmtext = "Do you want to make room " + repo["full_name"] +\
                      "? (y/n)"
        sendmessage(webex_token, message_room, confirmtext)

        confirm = getnextmessage(webex_token, message_room, confirmtext)

        if confirm == "Y" or confirm == "y":
            webex_msg += "Made room: " + repo["full_name"] + "\n"
        
            HTTPHeaders = {"Authorization": webex_token,
                           "Content-Type": "application/json"}
            data_json = {"title": repo["full_name"]}
            make_res = requests.post("https://api.ciscospark.com/v1/rooms",
                                     data=json.dumps(data_json),
                                     headers=HTTPHeaders)
            if not make_res.status_code == 200:
                webex_msg += "Could not make room " + repo["full_name"] + "\n"

    webex_msg += "Finished makerooms.\n"
    sendmessage(webex_token, message_room, webex_msg)


def deleterooms(github_token, webex_token, message_room):
    repos_res = requests.get("https://api.github.com/user/repos",
                             headers={"Authorization": github_token})
    repos_json = repos_res.json()
    webex_msg = ""

    webex_res = requests.get("https://api.ciscospark.com/v1/rooms",
                             headers={"Authorization": webex_token})
    rooms = webex_res.json()["items"]
    for repo in repos_json:
        for room in rooms:
            if room["title"] == repo["full_name"]:
                confirmtext = "Do you want to delete room " + room["title"] +\
                      "? (y/n)"
                sendmessage(webex_token, message_room, confirmtext)
                
                confirm = getnextmessage(webex_token, message_room, confirmtext)

                if confirm == "Y" or confirm == "y":
                    HTTPHeaders = {"Authorization": webex_token,
                                   "Content-Type": "application/json"}
                    requests.delete("https://api.ciscospark.com/v1/rooms/" +
                                    room["id"],
                                    headers=HTTPHeaders)
                    webex_msg += "Deleted room: " + repo["full_name"] + "\n"
    webex_msg += "Finished deleterooms.\n"
    sendmessage(webex_token, message_room, webex_msg)

github_token = "Bearer "  # + input("Enter your github token")
# REMOVE BEFORE PRODUCTION developer's github token
github_token = "Bearer " + getkeys.github

webex_token = "Bearer "  # + input("Enter your webex teams token:")
# REMOVE BEFORE PRODUCTION developer's webex token
webex_token = "Bearer " + getkeys.teams

webex_res = requests.get("https://api.ciscospark.com/v1/rooms",
                         headers={"Authorization": webex_token})
if not webex_res.status_code == 200:
    raise Exception("Incorrect reply from Webex Teams API.\n"
                    "Status code: {}\n"
                    "Text: {}\n".format(webex_res.status_code,
                                        webex_res.text))
# give the user a rooms list
print("Select a room where the program will listen for commands:")
rooms = webex_res.json()["items"]
for room in rooms:
    print(room["title"])

listening_room = None
# user select which room to use
while listening_room is None:
    home_room = ""  # input("Type your desired room: ")
    # REMOVE BEFORE PRODUCTION developer's room name
    home_room = "Github Bot"

    for room in rooms:
        if room["title"] == home_room:
            listening_room = room["id"]
            print("Found room : " + room["title"])
            break
    if listening_room is None:
        print("Sorry, I didn't find any room called " + home_room + ".\n"
              "Please try again.")
displayhelp(webex_token, listening_room)
last_message_id = ""
# main infinite loop
while True:
    getParams = {"roomId": listening_room, "max": 1}
    webex_res = requests.get("https://api.ciscospark.com/v1/messages",
                             params=getParams,
                             headers={"Authorization": webex_token})
    if not webex_res.status_code == 200:
        raise Exception("Incorrect reply from Webex Teams API.\n"
                        "Status code: {}.\n"
                        "Text: {}".format(webex_res.status_code,
                                          webex_res.text))
    message_json = webex_res.json()
    # check for a new command
    if len(message_json["items"]) > 0:
        message_id = message_json["items"][0]["id"]
        message_text = message_json["items"][0]["text"]
        if message_id != last_message_id:
            print("\n\nReceived message: " + message_text)
            last_message_id = message_id

            # read and execute command
            if message_text == "listrepos":
                listrepos(github_token, webex_token, listening_room)
            if message_text == "makerooms":
                makerooms(github_token, webex_token, listening_room)
            if message_text == "deleterooms":
                deleterooms(github_token, webex_token, listening_room)
            if message_text == "help":
                displayhelp(webex_token, listening_room)
            if message_text == "listcollabs":
                listcollaborators(github_token, webex_token, listening_room)
            if message_text == "searchrepos":
                searchrepos(github_token, webex_token, listening_room)
            if message_text == "bookmarkrepos":
                bookmarkRepos(github_token, webex_token, listening_room)

    time.sleep(1)
