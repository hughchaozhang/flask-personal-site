from flask import Flask, render_template
from apps.iss_guide.routes import iss_bp

app = Flask(__name__)

# Register the ISS Guide blueprint
app.register_blueprint(iss_bp)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/apps')
def apps():
    return render_template('apps.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)