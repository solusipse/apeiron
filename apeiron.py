from flask import Flask, render_template, session, redirect, url_for, escape, request
import generator as Generator

app = Flask('apeiron')

@app.route("/", methods=['GET', 'POST'])
def main():

    context = {}

    if 'login' in session:
        context['loggedin'] = True
        return render_template('admin.html', **context)

    context['notloggedin'] = True

    if request.method == 'POST':
        if valid_login(request.form['login'], request.form['password']):
            session['login'] = request.form['login']
            return redirect(url_for('main'))
        else:
            context['invalid'] = True

    return render_template('admin.html', **context)

@app.errorhandler(404)
def page_not_found(error):
    return 'Error 404', 404

@app.route('/logout')
def logout():
    session.pop('login', None)
    return redirect(url_for('main'))

def valid_login(login, password):
    if login == settings.get_login() and password == settings.get_password():
        return True

settings = Generator.Settings()
handler = Generator.Generator()
handler.generate_pages()
handler.generate_index_pages()

app.secret_key = settings.get_secret_key()

if __name__ == "__main__":
    app.debug = True
    app.run()