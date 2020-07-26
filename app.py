from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from detector import  Detector
import cfg
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

application = Flask(__name__)

application.config['UPLOAD_FOLDER'] = cfg.UPLOAD_FOLDER 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@application.route("/")
def index():

  return render_template("index.html")

@application.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
  """Upload image for detection"""
  
  if request.method == 'POST':
    
    # check if the post request has the file part
    if 'file' not in request.files:
        return redirect(url_for('index'))
    f = request.files['file']

    # if user does not select file, browser will submit an empty part without filename
    if f.filename == '':
      return redirect(url_for('index'))
    
    if f and allowed_file(f.filename):
    
      filename = secure_filename(f.filename) # create a secure filename
      print(filename)
      filepath = os.path.join(application.config['UPLOAD_FOLDER'], filename)  # save file to /static/uploads
      print(filepath)
      f.save(filepath)
      detector = Detector(filepath,filename)
      if detector.detect():
        return render_template("detected.html", display_detection = filename, fname = filename)
      else:
        return render_template("not_detected.html", display_detection = filename, fname = filename)
    else:
      return redirect(url_for('index'))
