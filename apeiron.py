# -*- encoding: utf-8 -*-

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

@app.route('/section/<section_name>/<page>/', methods=['GET', 'POST'])
def edit_page(section_name, page):

    if 'login' in session:

        context = {}

        if request.method == 'POST':
            Generator.Manager().save_page_md(section_name, page, request.form['content'])
            context['save_success'] = True

        contents = Generator.Manager().get_file_contents(page + '.md', section_name).decode('utf-8')

        context['loggedin'] = True
        context['edit_page'] = True
        context['output_directory'] = settings.get_output_directory()
        context['sections'] = Generator.Manager().get_all_sections()
        context['section_name'] = section_name
        context['page'] = page
        context['contents'] = contents

        return render_template('admin.html', **context)

    return redirect(url_for('main'))

@app.route('/generate/')
def web_generate_pages():
    if 'login' in session:

        context = {}
        context['sections'] = Generator.Manager().get_all_sections()
        context['loggedin'] = True
        context['generator'] = True
        context['pages_feedback'], context['index_feedback'] = handler.generate_feedback()

        return render_template('admin.html', **context)

    return redirect(url_for('main'))

@app.route('/delete/section/<section_name>/', methods=['GET', 'POST'])
def web_delete_section(section_name):
    if 'login' in session:

        context = {}

        if request.method == 'POST':
            Generator.Manager().delete_section(section_name)
            context['success'] = True
        
        context['sections'] = Generator.Manager().get_all_sections()
        context['loggedin'] = True
        context['section'] = section_name
        context['delete_section'] = True

        return render_template('admin.html', **context)

    return redirect(url_for('main'))

@app.route('/section/', methods=['GET', 'POST'])
def add_new_section():
    if 'login' in session:

        context = {}

        if request.method == 'POST':
            section = request.form['section']
            if Generator.Manager().create_directory('input/' + section):
                if Generator.Settings().add_new_section(section):
                    context['section_message'] = 'Created new section!'
                else:
                    context['section_message'] = 'Could not create new section!'
            else:
                context['section_message'] = 'Section already exists!'

        context['sections'] = Generator.Manager().get_all_sections()
        context['loggedin'] = True
        context['section_creator'] = True

        return render_template('admin.html', **context)

    return redirect(url_for('main'))

@app.route('/lib/<path:filename>')
def lib_static(filename):
    if 'login' in session:
        return send_from_directory(app.root_path + '/lib/', filename)

    return redirect(url_for('main'))

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