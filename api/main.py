from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    # return 'Hello, World!'
    return render_template("/templates/index.html")

@app.route('/about')
def about():
    return 'About'


if __name__ == "__main__":
    app.run(debug=True, port=5001)
