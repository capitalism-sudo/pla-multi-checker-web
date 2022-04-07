import signal
import json
from flask import Flask, render_template, request
import pla

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')


@app.route("/seeds")
def seed():
   return render_template('pages/seeds.html', title='MMO Checker')

@app.route("/spawns")
def alpha():
   return render_template('pages/spawns.html', title='Spawn Checker')

@app.route("/settings")
def settings():
   return render_template('pages/settings.html', title='Settings')

@app.route('/check-mmoseed', methods=['POST'])
def get_from_seed():
   results = pla.check_from_seed(request.json['seed'],
                                 request.json['rolls'],
                                 request.json['frencounter'],
                                 request.json['brencounter'],
                                 request.json['isbonus'],
                                 request.json['frspawns'],
                                 request.json['brspawns'])
   return { "mmo_spawns": results }

@app.route('/check-alphaseed', methods=['POST'])
def get_alpha_from_seed():
   results = pla.check_alpha_from_seed(request.json['seed'], request.json['rolls'],
                                       request.json['isalpha'], request.json['setgender'],
                                       request.json['filter'])
   return { "alpha_spawns": results }

if __name__ == '__main__':
    app.run(host="localhost", port=8200, debug=True)
