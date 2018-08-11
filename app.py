from os import walk
import argparse

from flask import Flask, redirect, url_for, request
from flask import render_template
from flask import send_file


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/tagger')
def tagger():
    if (app.config["HEAD"] == len(app.config["FILES"])):
        return redirect(url_for('bye'))
    directory = app.config['IMAGES']
    image = app.config["FILES"][app.config["HEAD"]]
    labels = app.config["LABELS"]
    not_end = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
    print(not_end)
    return render_template(
        'tagger.html', not_end=not_end, directory=directory, image=image, labels=labels,
        head=app.config["HEAD"] + 1, len=len(app.config["FILES"])
    )


@app.route('/next')
def next():
    image = app.config["FILES"][app.config["HEAD"]]
    app.config["HEAD"] = app.config["HEAD"] + 1
    with open(app.config["OUT"], 'a') as f:
        for label in app.config["LABELS"]:
            f.write(
                (image + "," + label["id"] + "," + label["name"] + "," + str(round(float(label["xMin"]))) + "," +
                 str(round(float(label["xMax"]))) + "," + str(round(float(label["yMin"]))) + "," +
                 str(round(float(label["yMax"]))) + "\n")
            )
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
    app.config["LABELS"].append({"id": id, "name": "", "xMin": xMin, "xMax": xMax, "yMin": yMin, "yMax": yMax})
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

# @app.route('/prev')
# def prev():
#     app.config["HEAD"] = app.config["HEAD"] - 1
#     return redirect(url_for('tagger'))


@app.route('/image/<f>')
def images(f):
    images = app.config['IMAGES']
    return send_file(images + f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=str, help='specify the images directory')
    parser.add_argument("--out")
    parser.add_argument(
        "-s",
        "--separator",
        help="The character which separates the string and integer portions of the files names",
        default="_"
    )
    parser.add_argument(
        "--no_sort",
        help="Toggle between sorting and not sorting the order in which the images are displayed",
        default=False
    )
    args = parser.parse_args()
    directory = args.dir
    separator_character = str(args.separator)
    if directory[len(directory) - 1] != "/":
        directory += "/"
    app.config["IMAGES"] = directory
    app.config["LABELS"] = []
    files = None
    for (dirpath, dirnames, filenames) in walk(app.config["IMAGES"]):
        if args.no_sort:
            files = filenames
        else:
            files = sorted(filenames, key=lambda a: int(a.split(separator_character)[1][:-len(".png")]))
        break
    if files is None:
        print("No files")
        exit()
    app.config["FILES"] = files
    app.config["HEAD"] = 0
    if args.out is None:
        app.config["OUT"] = "out.csv"
    else:
        app.config["OUT"] = args.out
    print(files)
    with open("out.csv", 'w') as f:
        f.write("image,id,name,xMin,xMax,yMin,yMax\n")
    app.run(debug="True")
