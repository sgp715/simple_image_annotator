# Simple Image Annotator

## Description
All image annotators I found either didn't work or were really hard to setup. So, I tried to make this  one simple to run and simple to use.

## Install
* Install Flask
```
$ pip install Flask
```

## Getting started
* cd into this directory after cloning the repo
* start the app
```
$ python app.py /images/directory
```
* open http://127.0.0.1:5000/tagger in your browser

## HOWTOs
* draw a bounding box
  * click on the image in the location of the first corner of the the bounding box you would like to add
  * click again for the second corner and the box will be drawn
* add a label for a box
  * for the box you would like to give a label, find its id (noted in the top left corner of the box)
  * find the label with the corresponding number
  * enter the name you want in the input field
  * press enter
* move to next image
  * click the blue arrow button at the bottom of the page (depending on the size of the image you may have to scroll down)
* check generated data
  * at the top level of the directory where the program was run, there shoud be a file called out.csv that contains the generate data
* GIFs coming soon..
