from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    menu_choices = {
        "/report": "View Time Report"
        # Add more links as your app grows
    }
    return render_template("index.html", menu_choices=menu_choices)

if __name__ == "__main__":
    app.run(debug=True)
