import subprocess

subprocess.Popen(["open", "-a", "Terminal.app", "python", "main.py"])

subprocess.run(["python", "main-prod.py"])
