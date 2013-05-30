from flask import Flask, render_template, session, redirect, url_for, escape, request, send_from_directory
import generator as Generator
import json

app = Flask('apeiron')

@app.route("/", methods=['GET', 'POST'])
def main():

    context = {}

    if 'login' in session:
        context['loggedin'] = True
        context['sections'] = Generator.Manager().get_all_sections()
        context['default_section'] = settings.get_default_section()
        context['dashboard'] = True
        context['default_template'] = settings.get_default_template()
        context['output_directory'] = settings.get_output_directory()
        context['static_directory'] = settings.get_static_directory()
        context['admin_login'] = settings.get_login()
        return render_template('admin.html', **context)

    context['notloggedin'] = True

    if request.method == 'POST':
        if valid_login(request.form['login'], request.form['password']):
            session['login'] = request.form['login']
            return redirect(url_for('main'))
        else:
            context['invalid'] = True

    return render_template('admin.html', **context)

@app.route('/section/<section_name>/')
def edit_section(section_name):
    if 'login' in session:

        context = {}
        context['loggedin'] = True
        context['edit_section'] = True
        context['sections'] = Generator.Manager().get_all_sections()
        context['section_name'] = section_name
        context['section_pages'] = Generator.Manager().create_pages_dictionary(section_name)

        return render_template('admin.html', **context)
    else:
        return redirect(url_for('main'))

@app.route('/section/<section_name>/<page>/')
def edit_page(section_name, page):

    if 'login' in session:

        context = {}
        context['loggedin'] = True
        context['edit_page'] = True
        context['output_directory'] = settings.get_output_directory()
        context['sections'] = Generator.Manager().get_all_sections()
        context['section_name'] = section_name
        context['page'] = page
        context['contents'] = json.dumps(Generator.Manager().get_file_contents(page + '.md', section_name))[1:][:-1]

        return render_template('admin.html', **context)
    else:
        return redirect(url_for('main'))

@app.route('/save/', methods=['GET', 'POST'])
def save_page():
    if request.method == 'POST':
        return request.form['content']

    return redirect(url_for('main'))


@app.route('/section/')
def add_new_section():
    return 'Not available yet.'

@app.route('/editor.js')
def show_editor():
    try:
        f = open('lib/epiceditor.min.js')
    except IOError, e:
        flask.abort(404)
        return
    return f.read()

@app.route('/lib/<path:filename>')
def lib_static(filename):
    return send_from_directory(app.root_path + '/lib/', filename)

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
    app.run(host='0.0.0.0')