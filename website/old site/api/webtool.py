from flask import Flask, abort, render_template, request
import json
import requests
 
app = Flask(__name__)
 
@app.route("/<string:guild>/<string:applier>/<string:job>/<string:gist_id>")
def answers(guild, applier, job, gist_id):

    return """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1">
  <link rel="shortcut icon" href="/assets/images/appbotcircle.gif" type="image/x-icon">
  <meta name="description" content="The answer provided by the user was too long. A URL was generated to replace it.">
  <title>""" + guild + """</title>
  <link rel="stylesheet" href="assets/web/assets/mobirise-icons-bold/mobirise-icons-bold.css">
  <link rel="stylesheet" href="/assets/web/assets/mobirise-icons/mobirise-icons.css">
  <link rel="stylesheet" href="/assets/tether/tether.min.css">
  <link rel="stylesheet" href="/assets/bootstrap/css/bootstrap.min.css">
  <link rel="stylesheet" href="/assets/bootstrap/css/bootstrap-grid.min.css">
  <link rel="stylesheet" href="/assets/bootstrap/css/bootstrap-reboot.min.css">
  <link rel="stylesheet" href="/assets/dropdown/css/style.css">
  <link rel="stylesheet" href="/assets/socicon/css/styles.css">
  <link rel="stylesheet" href="/assets/animatecss/animate.min.css">
  <link rel="stylesheet" href="/assets/theme/css/style.css">
  <link rel="stylesheet" href="/assets/mobirise/css/mbr-additional.css" type="text/css">
  
  
  
</head>
<body>
  <section class="menu cid-qTkzRZLJNu" once="menu" id="menu1-9">
    <nav class="navbar navbar-expand beta-menu navbar-dropdown align-items-center navbar-fixed-top navbar-toggleable-sm">
        <button class="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <div class="hamburger">
                <span></span>
                <span></span>
                <span></span>
                <span></span>
            </div>
        </button>
        <div class="menu-logo">
            <div class="navbar-brand">
                <span class="navbar-logo">
                    <a href="index">
                         <img src="/assets/images/appbotcircle.gif" alt="AppBot" title="" style="height: 3.8rem;">
                    </a>
                </span>
                <span class="navbar-caption-wrap"><a class="navbar-caption text-white display-4" href="/home">
                        AppBot</a></span>
            </div>
        </div>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav nav-dropdown" data-app-modern-menu="true"><li class="nav-item">
                    <a class="nav-link link text-white display-4" href="/home">
                        <span class="mbri-home mbr-iconfont mbr-iconfont-btn"></span>Home</a>
                </li><li class="nav-item"><a class="nav-link link text-white display-4" href="/Documentation"><span class="mbri-pages mbr-iconfont mbr-iconfont-btn"></span>
                        Documentation</a></li>
                <li class="nav-item"><a class="nav-link link text-white display-4" href="/FAQ"><span class="mbri-question mbr-iconfont mbr-iconfont-btn"></span>FAQ</a></li></ul>
            <div class="navbar-buttons mbr-section-btn"><a class="btn btn-sm btn-primary display-4" href="http://www.nooooooooooooooo.com/"><span class="mbrib-key mbr-iconfont mbr-iconfont-btn"></span>
                    Login</a></div>
        </div>
    </nav>
</section>

<section class="mbr-section content5 cid-qWtlioKByz mbr-parallax-background" id="content5-a">
    <div class="container">
        <div class="media-container-row">
            <div class="title col-12 col-md-8">
                <h2 class="align-center mbr-bold mbr-white pb-3 mbr-fonts-style display-1"><br>""" + guild + """</h2>
                <h3 class="mbr-section-subtitle align-center mbr-light mbr-white pb-3 mbr-fonts-style display-5">
                    """ + job + ": " + applier + """
                </h3>
            </div>
        </div>
    </div>
</section>


<section class="mbr-section article content1 cid-qWuZN9tJpK" id="content1-f">
    <div class="container">
        <div class="media-container-row">
            <div class="mbr-text col-12 col-md-8 mbr-fonts-style display-7">
              <script src="https://gist.github.com/Discord-AppBot/""" + gist_id + """.js"></script> 
            </div>
        </div>
    </div>
</section>

<section class="cid-qWv1aE73XL mbr-reveal" id="footer1-g">
    <div class="container">
        <div class="media-container-row content text-white">
            <div class="col-12 col-md-3">
                <div class="media-wrap">
                    <a href="index">
                        <img src="/assets/images/appbotcircle.gif" alt="AppBot" title="">
                    </a>
                </div>
            </div>
            <div class="col-12 col-md-3 mbr-fonts-style display-7">
                <h5 class="pb-3">
                    Support Us</h5>
                <p class="mbr-text"><a href="https://patreon.com/AppBot">Donate to me</a><br><a href="https://bit.ly/appbot-upvote">Upvote the bot</a><br><a href="https://bit.ly/appbot-help">Say "I like your bot"</a></p>
            </div>
            <div class="col-12 col-md-3 mbr-fonts-style display-7">
                <h5 class="pb-3">
                    Get Help</h5>
                <p class="mbr-text"><a href="https://bit.ly/appbot-help">Join Support Server</a><br><a href="/FAQ">See the FAQ</a><br><a href="/Documentation">Read the Docs</a><br><br></p>
            </div>
            <div class="col-12 col-md-3 mbr-fonts-style display-7">
                <h5 class="pb-3">Useful Links</h5>
                <p class="mbr-text"><a href="/Documentation">Documentation</a><br><a href="https://discordapp.com/api/oauth2/authorize?client_id=424817451293736961&permissions=8&scope=bot">Invite the Bot</a><br><a href="https://bit.ly/appbot-help">Join Support Server</a></p>
            </div>
        </div>
        <div class="footer-lower">
            <div class="media-container-row">
                <div class="col-sm-12">
                    <hr>
                </div>
            </div>
            <div class="media-container-row mbr-white">
                <div class="col-sm-6 copyright">
                    <p class="mbr-text mbr-fonts-style display-7">
                        Copyright 2018-2019 Joshuliu</p>
                </div>
                <div class="col-md-6">
                    
                </div>
            </div>
        </div>
    </div>
</section>


  <script src="/assets/web/assets/jquery/jquery.min.js"></script>
  <script src="/assets/popper/popper.min.js"></script>
  <script src="/assets/tether/tether.min.js"></script>
  <script src="/assets/bootstrap/js/bootstrap.min.js"></script>
  <script src="/assets/dropdown/js/script.min.js"></script>
  <script src="/assets/viewportchecker/jquery.viewportchecker.js"></script>
  <script src="/assets/parallax/jarallax.min.js"></script>
  <script src="/assets/mbr-switch-arrow/mbr-switch-arrow.js"></script>
  <script src="/assets/smoothscroll/smooth-scroll.js"></script>
  <script src="/assets/touchswipe/jquery.touch-swipe.min.js"></script>
  <script src="/assets/theme/js/script.js"></script>
  
  
  <input name="animation" type="hidden">
  </body>
</html>
    """

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

@app.route('/test')
def test():
    return "works."
if __name__ == "__main__":
    app.run()