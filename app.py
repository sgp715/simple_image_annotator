import sys
from os import walk
import csv

from flask import Flask, redirect, url_for, request
from flask import render_template
from flask import send_file


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/tagger')
def tagger():
    if (app.config["HEAD"] == len(app.config["FILES"])):
        exit()
    directory = app.config['IMAGES']
    image = app.config["FILES"][app.config["HEAD"]]
    labels = app.config["LABELS"]
    # [{"id":"1", "name":None, "ymin":0, "ymax":2, "xmin":0, "ymax":5},
        # {"id":"2", "name":"image", "ymin":0, "ymax":20, "xmin":6, "ymax":50}]
    not_end = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
    print(not_end)
    return render_template('tagger.html', not_end=not_end, directory=directory, image=image, labels=labels)

@app.route('/next')
def next():
    image = app.config["FILES"][app.config["HEAD"]]
    app.config["HEAD"] = app.config["HEAD"] + 1
    with open("out.csv",'a+') as f:
        for label in app.config["LABELS"]:
            f.write(image + "," +
            label["id"] + "," +
            label["name"] + "," +
            label["xMin"] + "," +
            label["xMax"] + "," +
            label["yMin"] + "," +
            label["yMax"] + "\n")
    app.config["LABELS"] = []
    return redirect(url_for('tagger'))

@app.route("/bye")
def bye():
    return send_file("taf.gif", mimetype='image/gif')

@app.route('/add/<id>')
def add(id):
    xMin = request.args.get("xMin")
    xMax = request.args.get("xMax")
    yMin = request.args.get("yMin")
    yMax = request.args.get("yMax")
    app.config["LABELS"].append({"id":id, "name":None, "xMin":xMin, "xMax":xMax, "yMin":yMin, "yMax":yMax})
    return redirect(url_for('tagger'))

@app.route('/label/<id>')
def label(id):
    name = request.args.get("name")
    app.config["LABELS"][int(id) - 1]["name"] = name
    return redirect(url_for('tagger'))

# @app.route('/prev')
# def prev():
#     app.config["HEAD"] = app.config["HEAD"] - 1
#     return redirect(url_for('tagger'))

@app.route('/image/<f>')
def images(f):
    images = app.config['IMAGES']
    return send_file(images + f)


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        print("app.py [images_dir]")
        exit()
    app.config["IMAGES"] = args[1]
    app.config["LABELS"] = []
    files = None
    for (dirpath, dirnames, filenames) in walk(app.config["IMAGES"]):
        files = filenames
    if len(files) == 0:
        print("No files")
        exit()
    app.config["HEAD"] = 0
    app.config["FILES"] = files
    print(files)
    with open("out.csv",'w') as f:
        f.write("image,id,name,xMin,xMax,yMin,yMax\n")
    app.run(debug="True")
