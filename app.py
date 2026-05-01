from flask import Flask, render_template, request

from utils.analyzer import analyze_distraction, validate_inputs


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    errors = {}
    form_data = {
        "screen_time": "",
        "social_media": "",
        "productive_hours": "",
        "app_switches": "",
    }

    if request.method == "POST":
        form_data = {
            "screen_time": request.form.get("screen_time", "").strip(),
            "social_media": request.form.get("social_media", "").strip(),
            "productive_hours": request.form.get("productive_hours", "").strip(),
            "app_switches": request.form.get("app_switches", "").strip(),
        }
        cleaned_data, errors = validate_inputs(form_data)
        if not errors:
            result = analyze_distraction(cleaned_data)

    return render_template(
        "index.html",
        result=result,
        errors=errors,
        form_data=form_data,
    )


if __name__ == "__main__":
    app.run(debug=True)
