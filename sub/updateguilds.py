import datetime
import requests
import json

now = datetime.datetime.utcnow()
with open('/home/joshuliu/AppBot/sub/guilds.json') as file:
    data = json.load(file)

data['dates'].append(f'{now.hour}:00')

appbot = requests.get('https://discordbots.org/api/bots/424817451293736961').json()['server_count']
applicationbot = requests.get('https://discordbots.org/api/bots/418842777720193037').json()['server_count']

data['appbot'].append(appbot)
data['applicationbot'].append(applicationbot)

print(data)
with open('/home/joshuliu/AppBot/sub/guilds.json','w') as file:
    json.dump(data, file, indent=4)