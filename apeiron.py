from flask import Flask, render_template, request
import generator as Generator

app = Flask('apeiron')

@app.route("/")
def main():
    return render_template('default.html')

Generator.Settings()
handler = Generator.Generator()
handler.generate_pages()
handler.generate_index_pages()

if __name__ == "__main__":
    app.debug = True
    app.run()