import requests
import json
import time
import getkeys
#to call GitHub https://api.github.com/

favourites = {}
github_token = "Bearer " + getkeys.github

'''
Looks through user's starred 
adds the found repository to the watch lists
'''
def bookmarkRepo(github_token, webex_token, message_room):
    starred_res = requests.get("https://api.github.com/user/starred", 
                    headers={"Authorization": github_token})
    github_json = starred_res.json()

    for starred in github_json:
        name = starred["name"]
        url = [starred["owner"][0]["starred_url"], starred["updated_at"]]
        favourites.update({name: url})

'''
Looks through the dict for the URL
If the repo has been updated the date & time are updated
if not then a message is returned about no updates found
'''
def checkRepoStatus():
    status_call = requests.get("https://api.github.com/user/starred", 
                    headers={"Authorization": github_token})    
    if status_call["updated_at"] != favourites.values([1]):
        request = requests.get("https://api.github.com/user/starred")
        github_json = request.json()
        for starred in github_json:
            url = [starred["owner"][0]["starred_url"], starred["updated_at"]]
            favourites.update({url})
    
    webex_res = requests.get("https://api.ciscospark.com/v1/rooms",
                             headers={"Authorization": webex_token})
        
        
