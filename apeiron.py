from flask import Flask, render_template, request
import generator as Generator

app = Flask('apeiron')


@app.route("/")
def main():
    return render_template('default.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error_code = error, request_path = request.path), 404

Generator.Settings()
handler = Generator.Generator()
handler.generate_pages()
handler.generate_index_pages()

if __name__ == "__main__":
    app.debug = False
    app.run()