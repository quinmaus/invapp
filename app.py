from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

app = Flask(__name__)

# Sample inventory items
items = []
for line in open("items.txt"):
    item, count = line.strip().split(",")
    items.append({"name": item, "count": int(count)})

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        idx = int(request.form["idx"])
        action = request.form["action"]
        if action == "up":
            items[idx]["count"] += 1
        elif action == "down" and items[idx]["count"] > 0:
            items[idx]["count"] -= 1
        # Update the items.txt file
        with open("items.txt", "w") as f:
            for item in items:
                f.write(f"{item['name']},{item['count']}\n")
        return redirect(url_for("index"))
    return render_template("index.html", items=items)

@app.route("/additem", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        new_item = request.form["item"]
        items.append({"name": new_item, "count": 0})
        with open("items.txt", "a") as f:
            f.write(f"{new_item},0\n")
        return redirect(url_for("add_item"))
    else:
        return render_template("additem.html")
@app.route("/deleteitem", methods=["GET", "POST"])
def delete_item():
    if request.method == "GET":
        return redirect(url_for("add_item"))
    if request.method == "POST":
        item_name = request.form["item_name"]
        global items
        items = [item for item in items if item["name"] != item_name]
        with open("items.txt", "w") as f:
            for item in items:
                f.write(f"{item['name']},{item['count']}\n")
        return redirect(url_for("index"))
@app.route("/export", methods=["POST"])
def export():
    email = request.form["gmail"]
    sheet = client.open_by_key("1bSiAFSInmpWg8jk8MNn9mUBK677X_yfXQsNySh9PExk")
    sheet.share("inventory-sheet-account@miscandtesting.iam.gserviceaccount.com", perm_type="user", role="writer")
    sheet.share(email, perm_type="user", role="writer")
    worksheet = sheet.sheet1
    worksheet.clear()
    worksheet.append_row(["Item", "Count"])
    for item in items:
        worksheet.append_row([item["name"], item["count"]])
    worksheet.append_row(["Exported on", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    return redirect(url_for("clear_data"))
@app.route("/clear_data")
def clear_data():
    with open("items.txt", "w") as f:
        f.write("")
    return redirect(url_for("index"))
@app.route("/sheet")
def sheet():
    return redirect("https://docs.google.com/spreadsheets/d/1bSiAFSInmpWg8jk8MNn9mUBK677X_yfXQsNySh9PExk/edit?gid=0#gid=0")
if __name__ == "__main__":
    app.run(debug=True)