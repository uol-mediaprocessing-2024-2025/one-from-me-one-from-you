"""
Module to create a webapp using flask. To be updated with incoming changes.
"""

from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def collage():
    return render_template('collage.html')


if __name__ == '__main__':
    app.run(debug=True)
