from flask import Flask, request, render_template, jsonify
from rule.model import GeoTranslator
from rule.tables import initTables

app = Flask(__name__)
tableData = initTables()
translator = GeoTranslator(tableData)


def translate(text1):
    src = [text1]
    trans_out = translator.run(src)[0]
    tgt = []
    for i in range(len(trans_out)):
        tgt.append("翻译 {}: {}\n原因：{}".format(i + 1, trans_out[i][0], trans_out[i][1]))
    return "\n\n".join(tgt)


@app.route("/")
def home():
    return render_template("present_page.html")


@app.route("/join", methods=["GET", "POST"])
def my_form_post():
    text1 = request.form["text1"]
    tgt = translate(text1)
    result = {"output": tgt}
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


if __name__ == "__main__":
    app.run(host="localhost", port=5000)
