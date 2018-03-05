import sys
import os.path
from os import walk
import imghdr
import csv
import argparse
import re

from flask import Flask, redirect, url_for, request
from flask import render_template
from flask import send_file

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['CURFIL'] = ""

def writeLabels():
    image = app.config["FILES"][app.config["HEAD"]]
    with open(app.config["OUTDIR"]+re.sub('\.(jpg|jpeg|png|tif)','.txt',image),'w') as f:
        for label in app.config["LABELS"]:
            if label["name"] == "":continue
            trunc = "0.0"
            if "-trunc-" in label["name"]:
                trunc = re.sub('.*-','',label["name"])
                label["name"] = re.sub('-.*','',label["name"])
            f.write(label["name"] + " " +
            trunc + " "
            "0 0.0 " +
            str(round(float(label["xMin"]))) + " " +
            str(round(float(label["yMin"]))) + " " +
            str(round(float(label["xMax"]))) + " " +
            str(round(float(label["yMax"]))) + " " +
            "0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    f.close()

@app.route('/tagger')
def tagger():
    if (app.config["HEAD"] == len(app.config["FILES"])):
        return redirect(url_for('bye'))
    if (app.config["HEAD"] < 0):
        app.config["HEAD"] = 0
        return redirect(url_for('tagger'))
    directory = app.config['IMAGES']
    image = app.config["FILES"][app.config["HEAD"]]
    labels = app.config["LABELS"]
    if not image == app.config["CURFIL"]:
        app.config["CURFIL"] = image
        current_file = app.config["OUTDIR"]+re.sub('\.(jpg|jpeg|png|tif)','.txt',app.config["CURFIL"])
        if os.path.isfile(current_file):
            for idx,line in enumerate(open(current_file,'r').readlines()):
                larr = line.strip().split(" ")
                lname = larr[0]
                if not larr[1] == "0.0":
                    lname = lname + "-trunc-" + larr[1]
                app.config["LABELS"].append({"id":idx+1, "name":lname, "xMin":float(larr[4]), "yMin":float(larr[5]), "xMax":float(larr[6]), "yMax":float(larr[7])})
    not_end = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
    not_begin = app.config["HEAD"] > 0
    return render_template('tagger.html', not_end=not_end, not_begin=not_begin, directory=directory, image=image, labels=labels, head=app.config["HEAD"] + 1, len=len(app.config["FILES"]))

@app.route('/next')
def next():
    writeLabels()
    app.config["HEAD"] = app.config["HEAD"] + 1
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
    app.config["LABELS"].append({"id":id, "name":"", "xMin":xMin, "xMax":xMax, "yMin":yMin, "yMax":yMax})
    return redirect(url_for('tagger'))

@app.route('/remove/<id>')
def remove(id):
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]:
        label["id"] = str(int(label["id"]) - 1)
    return redirect(url_for('tagger'))

@app.route('/label/<id>')
def label(id):
    name = request.args.get("name")
    app.config["LABELS"][int(id) - 1]["name"] = name
    return redirect(url_for('tagger'))

@app.route('/prev')
def prev():
    writeLabels()
    app.config["HEAD"] = app.config["HEAD"] - 1
    app.config["LABELS"] = []
    return redirect(url_for('tagger'))

@app.route('/image/<f>')
def images(f):
    images = app.config['IMAGES']
    return send_file(images + f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=str, help='specify the images directory')
    parser.add_argument("--out", help='specify labels director')
    parser.add_argument("--port", help='specify port to run on')
    args = parser.parse_args()
    directory = args.dir
    if directory[len(directory) - 1] != "/":
         directory += "/"
    app.config["IMAGES"] = directory
    app.config["LABELS"] = []
    files = None
    for (dirpath, dirnames, filenames) in walk(app.config["IMAGES"]):
        files = filenames
        break
    if files == None:
        print("No files")
        exit()
    app.config["FILES"] = files
    app.config["HEAD"] = 0
    if args.out == None:
        app.config["OUTDIR"] = args.dir
    else:
        app.config["OUTDIR"] = args.out
    if not app.config["OUTDIR"].endswith("/"):
        app.config["OUTDIR"] += "/"
    if args.port == None:
        app.config["PORT"] = 5555
    else:
        app.config["PORT"] = args.port
    print(files)
    with open("out.csv",'w') as f:
        f.write("image,id,name,xMin,xMax,yMin,yMax\n")
    app.run(host='0.0.0.0',debug="True",port=int(app.config["PORT"]))
