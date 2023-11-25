from flask import Flask, render_template

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)


@app.route('/')
def home():
    # return 'Hello, World!'
    return render_template("index.html")

@app.route('/about')
def about():
    return 'About'


if __name__ == "__main__":
    app.run(debug=True, port=5001)
