from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import paramiko, json, os, time
from config import USER, PASS, SUDO_PASS

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_FILE = "db.json"
LOG_FILE = "logs.json"

# helper load/save
def load_db(): return json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else []
def save_db(data): json.dump(data, open(DB_FILE,"w"), indent=2)
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_logs(data): json.dump(data, open(LOG_FILE,"w"), indent=2)

def log_command(user, ssh_host, command, output):
    logs = load_logs()
    logs.append({"time": time.strftime("%Y-%m-%d %H:%M:%S"), "user": user, "host": ssh_host, "command": command, "output": output})
    save_logs(logs)

# login
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username==USER and password==PASS:
            session["logged_in"] = True
            session["username"] = username
            log_command(username, "-", "LOGIN SUCCESS", "")
            return redirect(url_for("dashboard"))
        else:
            log_command(username, "-", "LOGIN FAILED", "")
            flash("Login Failed")
    return render_template("login.html")

# dashboard
@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"): return redirect(url_for("login"))
    ssh_list = load_db()
    return render_template("dashboard.html", ssh_list=ssh_list)

# add ssh
@app.route("/add_ssh", methods=["POST"])
def add_ssh():
    if not session.get("logged_in"): return redirect(url_for("login"))
    host = request.form.get("host")
    port = int(request.form.get("port"))
    user = request.form.get("user")
    password = request.form.get("password")
    note = request.form.get("note","")
    ssh_list = load_db()
    ssh_list.append({"host":host,"port":port,"user":user,"password":password,"note":note})
    save_db(ssh_list)
    return redirect(url_for("dashboard"))

# delete ssh
@app.route("/delete_ssh/<int:ssh_index>")
def delete_ssh(ssh_index):
    if not session.get("logged_in"): return redirect(url_for("login"))
    ssh_list = load_db()
    if ssh_index >= len(ssh_list): flash("SSH Not Found"); return redirect(url_for("dashboard"))
    removed = ssh_list.pop(ssh_index)
    save_db(ssh_list)
    flash(f"Deleted SSH {removed['host']}")
    return redirect(url_for("dashboard"))

# edit ssh
@app.route("/edit_ssh/<int:ssh_index>", methods=["GET","POST"])
def edit_ssh(ssh_index):
    if not session.get("logged_in"): return redirect(url_for("login"))
    ssh_list = load_db()
    if ssh_index >= len(ssh_list): flash("SSH Not Found"); return redirect(url_for("dashboard"))
    ssh_info = ssh_list[ssh_index]
    if request.method=="POST":
        ssh_info["host"] = request.form.get("host")
        ssh_info["port"] = int(request.form.get("port"))
        ssh_info["user"] = request.form.get("user")
        ssh_info["password"] = request.form.get("password")
        ssh_info["note"] = request.form.get("note","")
        save_db(ssh_list)
        flash(f"Updated SSH {ssh_info['host']}")
        return redirect(url_for("dashboard"))
    return render_template("edit_ssh.html", ssh_info=ssh_info, ssh_index=ssh_index)

# summon (GET render page, POST AJAX)
@app.route("/summon/<int:ssh_index>", methods=["GET","POST"])
def summon(ssh_index):
    if not session.get("logged_in"): return redirect(url_for("login"))
    ssh_list = load_db()
    if ssh_index >= len(ssh_list): flash("SSH Not Found"); return redirect(url_for("dashboard"))
    ssh_info = ssh_list[ssh_index]

    if request.method=="GET":
        return render_template("summon.html", ssh_info=ssh_info, ssh_index=ssh_index, SUDO_PASS=SUDO_PASS)

    # POST: AJAX
    command = request.form.get("command")
    output=""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ssh_info["host"], port=ssh_info["port"], username=ssh_info["user"], password=ssh_info["password"], timeout=5)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode() + stderr.read().decode()
        client.close()
        log_command(session["username"], ssh_info["host"], command, output)
    except Exception as e:
        output = str(e)
    return jsonify({"output": output})

# health
@app.route("/health_page/<int:ssh_index>")
def health_page(ssh_index):
    if not session.get("logged_in"): return redirect(url_for("login"))
    ssh_list = load_db()
    if ssh_index >= len(ssh_list): flash("SSH Not Found"); return redirect(url_for("dashboard"))
    ssh_info = ssh_list[ssh_index]
    output={}
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ssh_info["host"], port=ssh_info["port"], username=ssh_info["user"], password=ssh_info["password"], timeout=5)
        cmds = {"uptime":"uptime","disk":"df -h /","memory":"free -h","cpu":"top -bn1 | grep 'Cpu(s)'"}
        for k,v in cmds.items():
            stdin, stdout, stderr = client.exec_command(v)
            output[k] = stdout.read().decode() + stderr.read().decode()
        client.close()
    except Exception as e:
        output["error"] = str(e)
    return render_template("health.html", ssh_info=ssh_info, output=output)

# sudo reboot
@app.route("/sudo_reboot/<int:ssh_index>")
def sudo_reboot(ssh_index):
    if not session.get("logged_in"): return redirect(url_for("login"))
    ssh_list = load_db()
    if ssh_index >= len(ssh_list): flash("SSH Not Found"); return redirect(url_for("dashboard"))
    ssh_info = ssh_list[ssh_index]
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ssh_info["host"], port=ssh_info["port"], username=ssh_info["user"], password=ssh_info["password"], timeout=5)
        stdin, stdout, stderr = client.exec_command(f"echo {SUDO_PASS} | sudo -S reboot")
        stdout.read(); stderr.read(); client.close()
        flash(f"Reboot command sent to {ssh_info['host']}")
    except Exception as e:
        flash(str(e))
    return redirect(url_for("dashboard"))

# reboot all
@app.route("/reboot_all", methods=["POST"])
def reboot_all():
    if not session.get("logged_in"): return redirect(url_for("login"))
    ssh_indices = request.form.getlist("ssh_index")
    ssh_list = load_db()
    results = {}
    for idx in ssh_indices:
        ssh_info = ssh_list[int(idx)]
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ssh_info["host"], port=ssh_info["port"], username=ssh_info["user"], password=ssh_info["password"], timeout=5)
            stdin, stdout, stderr = client.exec_command(f"echo {SUDO_PASS} | sudo -S reboot")
            stdout.read(); stderr.read(); client.close()
            results[ssh_info["host"]] = "Reboot command sent"
            log_command(session["username"], ssh_info["host"], "sudo reboot", "Reboot command sent")
        except Exception as e:
            results[ssh_info["host"]] = str(e)
    return jsonify(results)

# export logs
@app.route("/export_logs")
def export_logs():
    if not session.get("logged_in"): return redirect(url_for("login"))
    logs = load_logs()
    return jsonify(logs)

# logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=65512)
