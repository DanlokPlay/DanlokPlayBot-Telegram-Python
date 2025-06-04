from flask import Flask, send_file, abort
import os

app = Flask(__name__)

@app.route('/')
def index():
    return 'Server is running!'

@app.route('/code')
def get_code():
    return send_file('codes.json.gz', mimetype='application/gzip')

@app.route('/content/<path:filename>')
def get_image(filename):
    full_path = os.path.abspath(os.path.join('content', filename))

    if 'check' in full_path or not full_path.startswith(os.path.abspath('content')):
        return abort(403)

    if not os.path.isfile(full_path) or not filename.lower().endswith('.png'):
        return abort(404)

    return send_file(full_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(port=49152, host='0.0.0.0')