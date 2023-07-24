import discord
from discord.ext import commands
from flask import Flask, request, url_for, redirect, session, render_template
import rethinkdb as r
import requests
import asyncio
import copy
import ast

conn = r.connect(db="appbot")
db = r.table("guilds")

async def tcp_echo_client(message, loop):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888,
                                                   loop=loop)

    print('Send: %r' % message)
    writer.write(message.encode())

    data = await reader.read()
    print('Received: %r' % data.decode())

    print('Close the socket')
    writer.close()

    return data.decode()

app = Flask(__name__)
app.secret_key = "423374132873527297"
loop = asyncio.get_event_loop()

LOGIN_URL = "https://discordapp.com/oauth2/authorize?client_id=424817451293736961&redirect_uri=https%3A%2F%2Fwww.appbot.site%2F&response_type=code&scope=identify%20guilds"
API_ENDPOINT = 'https://discordapp.com/api/v6'
CLIENT_ID = YOUR_CLIENT_ID
CLIENT_SECRET = YOUR_CLIENT_SECRET
REDIRECT_URI = 'https://www.appbot.site/'

def exchange_code(code):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': 'identify guilds'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data, headers)
    r.raise_for_status()
    return r.json()

@app.route("/")
def home():
    code = request.args.get("code", default=None)
    if code is not None:
        access_token = exchange_code(code)['access_token']
        session["token"] = access_token
        user = requests.get("https://discordapp.com/api/users/@me",headers={"Authorization":f"Bearer {session['token']}"}).json()
        return redirect("/dash/")
    else:
        if 'token' in session:
            user = requests.get("https://discordapp.com/api/users/@me",headers={"Authorization":f"Bearer {session['token']}"}).json()
        return render_template('home.html', **locals())

@app.route('/docs/')
@app.route('/documentation/')
@app.route('/commands/')
def docs():
    code = request.args.get("code", default=None)
    if code is not None:
        access_token = exchange_code(code)['access_token']
        session["token"] = access_token
        user = requests.get("https://discordapp.com/api/users/@me",headers={"Authorization":f"Bearer {session['token']}"}).json()
        return redirect("/dash/")
    else:
        if 'token' in session:
            user = requests.get("https://discordapp.com/api/users/@me",headers={"Authorization":f"Bearer {session['token']}"}).json()
        return render_template('docs.html', **locals())

@app.route('/faq/')
@app.route('/FAQ/')
def faq():
    code = request.args.get("code", default=None)
    if code is not None:
        access_token = exchange_code(code)['access_token']
        session["token"] = access_token
        user = requests.get("https://discordapp.com/api/users/@me",headers={"Authorization":f"Bearer {session['token']}"}).json()
        return redirect("/dash/")
    else:
        if 'token' in session:
            user = requests.get("https://discordapp.com/api/users/@me",headers={"Authorization":f"Bearer {session['token']}"}).json()
        return render_template('faq.html', **locals())

@app.route('/support/')
def support():
    return redirect("https://discord.gg/u5xGqzh")

@app.route('/donate/')
def donate():
    return redirect("https://www.patreon.com/AppBot")

@app.route('/upvote/')
def upvote():
    return redirect("https://discordbots.org/bot/appbot")

@app.route("/dash/")
@app.route("/dash/<string:guild_id>/")
@app.route("/dash/<string:guild_id>/<string:menu>")
def dashboard(guild_id=None, menu=None):
    return redirect(url_for('home'))
    if "token" in session:
        app = request.args.get("app", default=None)

        if menu != None: # If a menu was added...
            if menu not in ["app-settings","create","delete","edit","channels-perms","settings","apps","review","questions","apply","register","report"]:
                return redirect(url_for('dashboard',guild_id=guild_id))

        # Get user guilds
        r = requests.get("https://discordapp.com/api/users/@me/guilds",headers={"Authorization":f"Bearer {session['token']}"})
        
        def perms(userperms, requiredperms): # Used for checking if user can manage server
            if userperms & requiredperms != 0:
                return True
            else: return False
        
        def bot_run(text):
            print(text)
            resp = loop.run_until_complete(tcp_echo_client(text, loop))
            print(resp)
            return resp

        def listify(text):
            return ast.literal_eval(text)

        def get_apps():
            return db.get(guild_id)["apps"].keys().run(conn)

        if guild_id is not None:
            data = db.get(guild_id).run(conn)

        user = requests.get("https://discordapp.com/api/users/@me",headers={"Authorization":f"Bearer {session['token']}"}).json()
        
        return render_template('dash.html', **locals())
    
    else: return redirect(LOGIN_URL)

@app.route('/dash/', methods=['POST'])
def dashboard_form():
    def bot_run(text):
        print(text)
        resp = loop.run_until_complete(tcp_echo_client(text, loop))
        print(resp)
        return resp
    guild_id = request.args.get("guild_id", default=None)
    menu = request.args.get("menu", default=None)
    app = request.form.to_dict()
    if menu in ["create","edit"]:
        newapp = copy.deepcopy(app)
        qns = []
        for k,v in app.items():
            if k.startswith('q'):
                qns.append(v)
                del newapp[k]
        newapp["open"] = True
        newapp["app"] = qns

        name = newapp["name"]
        del newapp["name"]
        if newapp["requiredrole"] != "none":
            newapp["requiredrole"] = bot_run(guild_id + " ROLEID " + newapp["requiredrole"])
        else:
            del newapp["requiredrole"]

        if newapp["acceptrole"] != "none":
            newapp["acceptrole"] = bot_run(guild_id + " ROLEID " + newapp["acceptrole"])
        else:
            del newapp["acceptrole"]

        print(newapp)
        db.get(str(guild_id)).update({"apps":{name:newapp}}).run(conn)
    elif menu == 'delete':
        appname = request.args.get("app", default=None)
        db.get(str(guild_id)).replace(r.row.without({"apps":{appname:True}})).run(conn)
    return redirect(url_for('dashboard', guild_id=guild_id))


@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect(url_for('home'))

@app.route('/dbl/<int:guild_id>/<string:webhook_token>', methods=['POST']) 
def dbl(guild_id, webhook_token):
    if not request.json:
        abort(400)
    dictdata = request.json
    print(dictdata)
    ty = "Thank you <@{0}> for upvoting!".format(dictdata['user'])
    requests.post(
        "https://discordapp.com/api/webhooks/{0}/{1}".format(guild_id,webhook_token), 
        json={
            "embeds":[
                {
                    "title":"Thanks for Upvoting!",
                    "description":ty,
                    "color":2733814
                }
            ]
        },
        headers={'Content-Type': 'application/json'}
    )
    return json.dumps(request.json)

@app.errorhandler(RuntimeError)
def fixeventloop(error):
    loop.stop()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
