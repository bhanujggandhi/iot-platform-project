from flask import Flask, render_template, request, Response
import os
import subprocess
import json

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run():
    if request.method == "POST":
        command = request.form["command"]
        file_path = request.form["file_path"]
        full_path = (
            os.path.abspath(os.path.join(os.getcwd(), file_path)) + "/" + command
        )
        print(full_path)
        process = subprocess.check_output(["python3", full_path])
        # output = run_command(process)
        return process


@app.route("/create_json", methods=["POST"])
def create_json():
    if request.method == "POST":
        data = {
            "command": request.form["command"],
            "file_path": request.form["file_path"],
        }
        with open("data.json", "w") as f:
            json.dump(data, f)
        return Response(status=201)


# def run_command(process):
#     while True:
#         output = process.stdout.readline().decode()
#         if output == '' and process.poll() is not None:
#             break
#         elif output:
#             yield output
#     stderr = process.stderr.read().decode()
#     if stderr:
#         yield stderr

if __name__ == "__main__":
    app.run(debug=True, port=8070)
