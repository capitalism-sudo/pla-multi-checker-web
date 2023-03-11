import json
import mimetypes

from flask import Flask, render_template, request
from .pla import *
from .pla.core import get_sprite
from .pla.data import hisuidex
from .pla.saves import read_research, rolls_from_research
from .pla.data.data_utils import *
from .pla.filters import *
from .bdsp.data.data_utils import flatten_ug, flatten_bdsp_stationary
from .swsh import *
from .bdsp import *
from .pla.rng import Filter
from .gen3 import *

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/javascript', '.mjs')

app = Flask(__name__)

# Set max size for uploads
app.config['MAX_CONTENT_LENGTH'] = 2 * 1000 * 1000

config = json.load(open("/home/pla-multi-checker-web/config.json"))

if config["SeedCheckOnly"]:
    print("Seed Check only mode! Note: You will not be able to use MMO checker or Distiortion Checker!")

@app.route("/")
def home():
    return render_template('index.html', home='true')

@app.route("/mmos")
@app.route("/seeds")
def seed():
    return render_template('pages/seeds.html', title='MMO Checker')

@app.route("/spawns")
def alpha():
    return render_template('pages/spawns.html', title='Spawn Checker')

@app.route("/multis")
@app.route("/multiseed")
def multiseed():
    return render_template('pages/multiseed.html', title='Multi Spawn Seed Checker')

@app.route("/settings")
def settings():
    return render_template('pages/settings.html', title='Settings')

@app.route("/cram")
def cram():
    return render_template('pages/cram.html', title='Fun Tools', swsh="true")

@app.route("/underground")
def ug():
    return render_template('pages/underground.html', title='Underground Checker', bdsp="true")

@app.route("/bdspstationary")
def bdsp_stationary():
    return render_template('pages/b_stationary.html', title='Stationary Checker', bdsp="true")

@app.route("/bdspwild")
def bwild():
    return render_template('pages/b_wild.html', title='Wild Checker', bdsp="true")

@app.route("/bdsproamer")
def broamer():
    return render_template('pages/b_roamer.html', title='Roamer Checker', bdsp="true")

@app.route("/bdspegg")
def begg():
    return render_template('pages/b_egg.html', title='Egg Checker', bdsp="true")

@app.route("/bdsptid")
def btid():
    return render_template('pages/b_tid.html', title='TID Checker', bdsp="true")

@app.route("/overworld")
def owrng():
    return render_template('pages/overworld.html', title='Overworld Checker', swsh="true")

@app.route("/g3static")
def g3static():
    return render_template('pages/rse_static.html', title='RSE Static Checker', g3="true") 

@app.route("/g3wild")
def g3wild():
    return render_template('pages/rse_wild.html', title='RSE Static Checker', g3="true")


# API ROUTES

@app.route('/api/check-gen3-static', methods=['POST'])
def check_gen3_static():

    filter_command = filter_commands.get(request.json['command'], is_shiny)

    results = gen3.check_statics(request.json['tid'],
                                 request.json['sid'],
                                 request.json['filter'],
                                 request.json['delay'],
                                 request.json['method'],
                                 request.json['seed'])
    
    return { "results": flatten_bdsp_stationary(results, config.get('FILTER_ON_SERVER', False), filter_command) }

@app.route('/api/g3-check-wilds', methods=['POST'])
def check_g3_wilds():

    filter_command = filter_commands.get(request.json['command'], is_shiny)

    results = gen3.check_wilds(request.json['tid'],
                               request.json['sid'],
                               request.json['filter'],
                               request.json['delay'],
                               request.json['method'],
                               request.json['info'],
                               request.json['syncnature'],
                               request.json['seed'])
    
    return { "results": flatten_bdsp_stationary(results, config.get('FILTER_ON_SERVER', False), filter_command) }

@app.route('/api/g3-pop-location', methods=['POST'])
def g3_pop_location():

    results = gen3.populate_routes(request.json['version'])

    return { "results": results}

@app.route('/api/g3-pop-species', methods=['POST'])
def g3_pop_species():

    results = gen3.populate_species(request.json['version'],request.json['type'],request.json['location'])

    return { "results": results}

@app.route('/api/g3-autofill', methods=['POST'])
def g3_autofill():

    results = gen3.autofill(request.json['version'],request.json['type'],request.json['location'],request.json['species'])

    return { "results": results}


@app.route('/api/read-distortion-map-info', methods=['POST'])
def get_map_info():
    locations = pla.get_distortion_locations(request.json['map_name'])
    spawns = pla.get_distortion_spawns(request.json['map_name'])
    return { "locations": locations, "spawns": spawns }

@app.route('/api/check-mmoseed', methods=['POST'])
def get_from_seed():
    try:
        group_seed = int(request.json['seed'])
    except ValueError:
        return { "error": "You need to input a number for the seed" }
    
    filter_command = filter_commands.get(request.json['filter'], is_shiny)
    
    results = pla.check_mmo_from_seed(group_seed,
                                  request.json['research'],
                                  request.json['frencounter'],
                                  request.json['brencounter'],
                                  request.json['isbonus'],
                                  request.json['frspawns'],
                                  request.json['brspawns'],
                                  request.json['isnormal'])
    print(request.json['research'])
    return { "results": flatten_map_mmo_results(results, config.get('FILTER_ON_SERVER', False), filter_command) }

@app.route('/api/check-alphaseed', methods=['POST'])
def get_alpha_from_seed():
    try:
        group_seed = int(request.json['seed'])
    except ValueError:
        return { "error": "You need to input a number for the seed" }
    
    results = pla.check_alpha_from_seed(group_seed,
                                        request.json['rolls'],
                                        request.json['isalpha'],
                                        request.json['setgender'],
                                        request.json['filter'])
    return { "results": results }

@app.route('/api/check-multi-seed', methods=['POST'])
def check_multiseed():
    try:
        group_seed = int(request.json['seed'])
    except ValueError:
        return { "error": "You need to input a number for the seed" }

    filter_command = filter_commands.get(request.json['filter'], is_shiny)

    results = pla.check_multi_spawner_seed(group_seed,
                                           request.json['research'],
                                           request.json['group_id'],
                                           request.json['maxalive'],
                                           request.json['maxdepth'],
                                           request.json['isnight'])
    return { "results": flatten_multi(results, config.get('FILTER_ON_SERVER', False), filter_command) }

@app.route('/api/hisuidex')
def pokemon():
    return { "hisuidex": [
                {
                    "id": p.id,
                    "species": p.species,
                    "sprite": get_sprite(p),
                    "number": p.dex_number('hisui')
                } for p in hisuidex
            ]
        }

@app.route('/api/read-research', methods=['POST'])
def read_savefile():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'save' not in request.files:
            return { 'error': 'There was no save file selected' }
        save = request.files['save']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if save.filename == '':
            return { 'error': 'There was no save file selected' }

        if save:
            savedata = bytearray(save.read());
            results = read_research(savedata)
            if 'error' in results:
                return { 'error': results['error'] }

            rolls = { pkm.species : rolls_from_research(results['research_entries'], pkm.dex_number()) for pkm in hisuidex }
            
            return {
                'shinycharm': results['shinycharm'],
                'rolls': rolls
            }
    
    return { 'error': 'There was a problem reading your save' }

@app.route('/api/check-cramomatic', methods=['POST'])
def check_cram_o_matic():

    results = []

    result = swsh.predict_cram(request.json['s0'],
                                request.json['s1'],
                                request.json['npc_count'],
                                request.json['filter'])

    results.append(result)

    return { "results": results }

@app.route('/api/check-lotto', methods=['POST'])
def check_lottery():

    results = []

    result = swsh.check_lotto(request.json['s0'],
                                request.json['s1'],
                                request.json['npc_count'],
                                request.json['ids'])

    results.append(result)

    return { "results": results }

@app.route('/api/find-swsh-seed', methods=['POST'])
def find_swsh_seed():

    results = swsh.find_swsh_seed(request.json['motions'])

    return { "results": results }

@app.route('/api/update-swsh-seed', methods=['POST'])
def update_swsh_seed():

    results = swsh.update_swsh_seed(request.json['s0'],
                                        request.json['s1'],
                                        request.json['motions'],
                                        request.json['min'],
                                        request.json['max'])

    return { "results": results }

@app.route('/api/check-underground', methods=['POST'])
def check_ug_seed():

    filter_command = filter_commands.get(request.json['filter'], is_shiny)

    results = bdsp.check_ug_advance(request.json['s0'],
                                    request.json['s1'],
                                    request.json['s2'],
                                    request.json['s3'],
                                    request.json['story'],
                                    request.json['room'],
                                    request.json['version'],
                                    request.json['advances'],
                                    request.json['minadv'],
                                    request.json['diglett'],
                                    request.json['ivs'],
                                    request.json['delay'])

    return { "results": flatten_ug(results, config.get('FILTER_ON_SERVER', False), filter_command) }

@app.route('/api/check-bdsp-stationary', methods=['POST'])
def check_bdsp_stationary():

    filter_command = filter_commands.get(request.json['command'], is_shiny)

    states = [request.json['s0'], request.json['s1'], request.json['s2'], request.json['s3']]

    results = bdsp.read_stationary_seed(states,
                                        request.json['filter'],
                                        request.json['fixed_ivs'],
                                        request.json['set_gender'],
                                        request.json['species'],
                                        request.json['delay'])
    
    return { "results": flatten_bdsp_stationary(results, config.get('FILTER_ON_SERVER', False), filter_command) }

@app.route('/api/check-bdsp-wild', methods=['POST'])
def check_bdsp_wild():

    filter_command = filter_commands.get(request.json['command'], is_shiny)

    states = [request.json['s0'], request.json['s1'], request.json['s2'], request.json['s3']]

    results = bdsp.read_wild_seed(states,
                                request.json['filter'],
                                request.json['set_gender'],
                                request.json['delay'])
    
    return { "results": flatten_bdsp_stationary(results, config.get('FILTER_ON_SERVER', False), filter_command) }

@app.route('/api/check-bdsp-roamer', methods=['POST'])
def check_bdsp_roamer():

    filter_command = filter_commands.get(request.json['command'], is_shiny)

    states = [request.json['s0'], request.json['s1'], request.json['s2'], request.json['s3']]

    results = bdsp.read_roamer_seed(states,
                                    request.json['filter'],
                                    request.json['fixed_ivs'],
                                    request.json['set_gender'],
                                    request.json['delay'])
    
    return { "results": flatten_bdsp_stationary(results, config.get('FILTER_ON_SERVER', False), filter_command) }

@app.route('/api/check-bdsp-egg', methods=['POST'])
def check_bdsp_egg():

    filter_command = filter_commands.get(request.json['command'], is_shiny)

    states = [request.json['s0'], request.json['s1'], request.json['s2'], request.json['s3']]

    results = bdsp.read_egg_seed(states,
                            request.json['filter'],
                            request.json['daycare'],
                            request.json['delay'])
    
    return { "results": flatten_bdsp_stationary(results, config.get('FILTER_ON_SERVER', False), filter_command) }

@app.route('/api/check-bdsp-tid', methods=['POST'])
def check_bdsp_tid():

    states = [request.json['s0'], request.json['s1'], request.json['s2'], request.json['s3']]

    results = bdsp.read_tid_seed(states,
                                request.json['filter'],
                                request.json['ids'])
    
    return { "results": flatten_bdsp_stationary(results, False) }

@app.route('/api/pop-location', methods=['POST'])
def pop_location():

    results = swsh.populate_location(request.json['type'], request.json['version'])

    return { "results": results}

@app.route('/api/pop-weather', methods=['POST'])
def pop_weather():

    results = swsh.populate_weather(request.json['loc'], request.json['type'], request.json['version'])

    return { "results": results}

@app.route('/api/pop-species', methods=['POST'])
def pop_species():

    results = swsh.populate_species(request.json['weather'], request.json['loc'], request.json['type'], request.json['version'])

    return { "results": results}

@app.route('/api/pop-options', methods=['POST'])
def pop_options():

    results = swsh.autofill(request.json['weather'], request.json['loc'], request.json['type'], request.json['version'], request.json['species'])

    return { "results": results}

@app.route('/api/check-overworld', methods=['POST'])
def check_ow():

    states = [request.json['s0'], request.json['s1']]

    #filters = Filter(None, None, None, "Star/Square", request.json['filter']['slot_min'], request.json['filter']['slot_max'], None, None, None, None, None, None, None, None)

    filters = Filter(request.json['filter']['minivs'], request.json['filter']['maxivs'], None, request.json['filter']['shiny_filter'] if request.json['filter']['shiny_filter'] != "None" else None,
                    request.json['filter']['slot_min'], request.json['filter']['slot_max'], None, None, request.json['filter']['brilliant'], None,
                    None, None, None, None)

    results = swsh.check_overworld_seed(states, filters, request.json['options'], request.json['initadv'], request.json['maxadv'], request.json['info'])

    #return { "results":  [results] }
    return { "results": flatten_overworld(results, False)}

"""
# Legacy routes used by bots
from .app.legacy import *
app.add_url_rule('/check-mmoseed', view_func=legacy.legacy_get_from_seed)
app.add_url_rule('/check-alphaseed', view_func=legacy.legacy_get_alpha_from_seed)
app.add_url_rule('/check-multi-seed', view_func=legacy.legacy_check_multiseed)

if __name__ == '__main__':
    app.run(host="localhost", port=8100, debug=True)
"""