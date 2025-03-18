import argparse
import json
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--apikey")
parser.add_argument("-t", "--token")
args = parser.parse_args()

pwd = os.getcwd()
collection_path = Path(f'{pwd}/out/postman/collection.json')

# setup default environment variables
env = [
        {
            "key": "baseUrl",
            "value": "http://localhost:80",
            "enabled": "true"
        },
        {
            "key": "account",
            "value": "dev",
            "enabled": "true"
        },
        {
            "key": "default-auth",
            "value": "authn",
            "enabled": "true"
        },
        {
            "key": "role",
            "value": "admin",
            "enabled": "true"
        },
        {
            "key": "api-key",
            "value": "",
            "enabled": "true"
        },
        {
            "key": "token",
            "value": "",
            "enabled": "true"
        },
        {
            "key": "formatted-token",
            "value": "Token token=\"{{token}}\"",
            "enabled": "true"
        }
    ]

def initial_setup(collection_json):
    """Add scripts to update access token collection variables before each
    request, and after requests to the default authenticate endpoint. Adds
    default, hard-coded collection variables."""
    collection_json["variable"] = env

    pre_event = [
        {
            "listen": "prerequest",
            "script": {
                "exec": [
                    "var baseUrl = pm.collectionVariables.get(\"baseUrl\");",
                    "var authenticator = pm.collectionVariables.get(\"default-auth\");",
                    "var account = pm.collectionVariables.get(\"account\");",
                    "var role = pm.collectionVariables.get(\"role\");",
                    "var api_key = pm.collectionVariables.get(\"api-key\");",
                    "var url = baseUrl + \"/\" + authenticator + \"/\" + account + \"/\" + role + \"/authenticate\"",
                    "",
                    "pm.sendRequest({",
                    "    url: url,",
                    "    method: 'POST',",
                    "    header: 'Accept-Encoding:base64',",
                    "    body: {",
                    "        mode: 'raw',",
                    "        raw: api_key",
                    "    }",
                    "}, (err, response) => {",
                    "    pm.collectionVariables.set(\"token\", response.text());",
                    "});",
                    ""
                ],
                "type": "text/javascript"
            }
        }
    ]
    collection_json["event"] = pre_event

    post_auth = [
        {
            "listen": "test",
            "script": {
                "exec": [
                    "if (responseBody[0] == '{') {",
                    "    pm.collectionVariables.set(\"token\", btoa(responseBody));",
                    "} else {",
                    "    pm.collectionVariables.set(\"token\", responseBody);",
                    "}"
                ],
                "type": "text/javascript"
            }
        }
    ]
    collection_json["item"][0]["item"][1]["event"] = post_auth

    return collection_json

def custom_auth_setup(collection_json):
    """Fill collection variables with auth credentials from command line args"""
    env[4]['value'] = args.apikey
    env[5]['value'] = args.token.replace('\r','')[28:-1]
    collection_json["variable"] = env
    return collection_json

with open(collection_path, 'r', encoding="utf-8") as content:
    collection_json = json.loads(content.read())

collection_json = initial_setup(collection_json)
if args.apikey or args.token:
    collection_json = custom_auth_setup(collection_json)

# write updated collection to collection file
with open(collection_path, 'w', encoding="utf-8") as content:
    content.write(json.dumps(collection_json, indent=4, sort_keys=False))
