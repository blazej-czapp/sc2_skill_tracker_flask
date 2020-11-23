import os
import sys
import base64

from io import BytesIO
from flask import Flask, render_template, flash, request, redirect, url_for

sys.path.insert(0, os.path.abspath('./sc2_skill_tracker')) # git submodule with the tracker library
from sc2_skill_tracker import skill_tracker

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/upload_replay', methods=['POST'])
    def upload():
        if 'replay_file' not in request.files:
            flash('Replay file missing!')
            return redirect(url_for('index'))

        replay_file = request.files['replay_file']

        if not replay_file.filename:
            flash('Missing replay file')
            return redirect(url_for('index'))

        if not replay_file.filename.endswith('.SC2Replay'):
            flash('This is not a *.SC2Replay file')
            return redirect(url_for('index'))

        try:
            figs = skill_tracker.generate_plots(replay_file)
        except Exception as e:
            flash(str(e))
            return redirect(url_for('index'))

        response = ""
        for fig in figs:
            # Save it to a temporary buffer.
            buf = BytesIO()
            fig.savefig(buf, format="svg")
            data = base64.b64encode(buf.getbuffer()).decode("ascii")
            response += f"<img src='data:image/svg+xml;base64,{data}'/><br>"

        return response

    return app