from flask import Flask, render_template, jsonify
from apps.iss_guide.routes import iss_bp
from apps.system_monitor import get_system_stats

app = Flask(__name__)

@app.after_request
def add_security_headers(response):
    csp = ("default-src 'self';"
           "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net;"
           "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com;"
           "font-src 'self' https://cdnjs.cloudflare.com;"
           "img-src 'self' data:;")
    response.headers['Content-Security-Policy'] = csp
    print("CSP Header:", response.headers['Content-Security-Policy'])
    return response

# Register the ISS Guide blueprint
app.register_blueprint(iss_bp)

@app.route('/')
def home():
    system_stats = get_system_stats()
    return render_template('home.html', system_stats=system_stats)

@app.route('/apps')
def apps():
    return render_template('apps.html')

@app.route('/get_system_stats')
def get_stats():
    return jsonify(get_system_stats())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)