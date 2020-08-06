from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import detector
import logging
import cfg
import os

# Logging Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/app.log")
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

application = Flask(__name__)
application.config["UPLOAD_FOLDER"] = cfg.UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@application.route("/")
def index():

    return render_template("index.html")


@application.route("/uploader", methods=["GET", "POST"])
def upload_file():
    """Upload image for detection"""

    if request.method == "POST":

        # check if the post request has the file part
        if "file" not in request.files:
            logger.info("No file part in request.files")
            return redirect(url_for("index"))

        f = request.files["file"]

        # if user does not select file, browser will submit an empty part without filename
        if f.filename == "":
            logger.info("No file selected")
            return redirect(url_for("index"))

        if allowed_file(f.filename):

            filename = secure_filename(f.filename)  # create a secure filename
            logger.info(f"File name : {filename}")
            filepath = os.path.join(
                application.config["UPLOAD_FOLDER"], filename
            )  # save file to /static/uploads
            f.save(filepath)
            logger.info(f"File saved to : {filepath}")

            _detector = detector.Detector(filepath, filename)

            if _detector.detect():
                return render_template(
                    "detected.html", display_detection=filename, fname=filename
                )
            else:
                return render_template(
                    "not_detected.html", display_detection=filename, fname=filename
                )
        else:
            logger.info("Unsupported file format")
            return redirect(url_for("index"))
