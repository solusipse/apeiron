# -*- encoding: utf-8 -*-

from flask import Flask, render_template, session, redirect, url_for, escape, request, send_from_directory
import generator as Generator
import json, sys

app = Flask('apeiron')

@app.route("/", methods=['GET', 'POST'])
def main():

    context = {}

    if 'login' in session:
        context['loggedin'] = True
        context['sections'] = manager.get_all_sections()
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
        context['sections'] = manager.get_all_sections()
        context['section_name'] = section_name
        context['section_pages'] = manager.create_pages_dictionary(section_name)

        return render_template('admin.html', **context)
    else:
        return redirect(url_for('main'))


@app.route('/section/<section_name>/page/new/', methods=['GET', 'POST'])
def new_page(section_name):
    if 'login' in session:

        context = {}

        if request.method == 'POST':
            page = request.form['page']
            if manager.check_if_page_exists(section_name, page):
                context['page_status'] = True
            else:
                manager.save_page_md(section_name, page, '')
                return redirect('/section/' + section_name + '/' + page)

        context['loggedin'] = True
        context['new_page'] = True
        context['sections'] = manager.get_all_sections()
        context['section_name'] = section_name

        return render_template('admin.html', **context)
    else:
        return redirect(url_for('main'))


@app.route('/section/<section_name>/<page>/', methods=['GET', 'POST'])
def edit_page(section_name, page):

    if 'login' in session:

        context = {}

        if request.method == 'POST':
            md_formatted_file = '---\n'
            md_formatted_file += 'Title: ' + request.form['title'] + '\n'
            md_formatted_file += 'Author: ' + request.form['author'] + '\n'
            md_formatted_file += 'Tags: ' + request.form['tags'] + '\n'
            md_formatted_file += 'Date: ' + request.form['date'] + '\n'
            md_formatted_file += 'ID: ' + request.form['id'] + '\n'
            md_formatted_file += '---\n'
            md_formatted_file += request.form['content']
            manager.save_page_md(section_name, page, md_formatted_file)
            context['save_success'] = True

            if request.form.has_key('generate'):
                return redirect(url_for('web_generate_pages'))

        contents = manager.get_file_contents(page + '.md', section_name).decode('utf-8')
        parsed_contents = manager.parse_file("file.md", contents)

        metadata = parsed_contents['metadata']

        context['loggedin'] = True
        context['edit_page'] = True
        context['output_directory'] = settings.get_output_directory()
        context['sections'] = manager.get_all_sections()
        context['section_name'] = section_name
        context['page'] = page

        id_list = []

        pages_dict = manager.create_pages_dictionary(section_name)

        for item in pages_dict:
            id_list.append(int(pages_dict[item]['ID']))

        context['highest_id'] = max(id_list) + 1

        try:
            context['contents'] = contents.split('---')[2]
        except(IndexError):
            context['contents'] = contents

        try:
            context['title'] = metadata['Title']
        except(KeyError):
            pass

        try:
            context['date'] = metadata['Date']
        except(KeyError):
            pass

        try:
            context['tags'] = metadata['Tags']
        except(KeyError):
            pass

        try:
            context['author'] = metadata['Author']
        except(KeyError):
            pass

        try:
            context['ID'] = metadata['ID']
        except(KeyError):
            pass

        return render_template('admin.html', **context)

    return redirect(url_for('main'))

@app.route('/generate/')
def web_generate_pages():
    if 'login' in session:

        context = {}
        context['sections'] = manager.get_all_sections()
        context['loggedin'] = True
        context['generator'] = True

        if 'force' in request.args:
            context['pages_feedback'], context['index_feedback'] = handler.generate_feedback(force=True)
        else:
            context['pages_feedback'], context['index_feedback'] = handler.generate_feedback(force=False)

        return render_template('admin.html', **context)

    return redirect(url_for('main'))

@app.route('/config/', methods=['GET', 'POST'])
def config_editor():
    if 'login' in session:

        context = {}

        if request.method == 'POST':
            settings.save_config(request.form['content'])
            context['save_success'] = True
            
        context['sections'] = manager.get_all_sections()
        context['loggedin'] = True
        context['config_editor'] = True
        context['config_contents'] = settings.get_contents()

        return render_template('admin.html', **context)

    return redirect(url_for('main'))

@app.route('/config/templates/', methods=['GET', 'POST'])
def templates_editor():
    if 'login' in session:

        context = {}

        if request.method == 'POST':
            manager.save_template(request.form['template'], request.form['content'])
            context['save_success'] = True

        
        context['sections'] = manager.get_all_sections()
        context['loggedin'] = True
        context['template_editor'] = True
        context['templates'] = manager.get_templates()

        if 'template' in request.args and request.args['template'] != '':
            context['selected_template'] = request.args['template']
            context['template_code'] = manager.get_template_code(request.args['template'])

        return render_template('admin.html', **context)

    return redirect(url_for('main'))

@app.route('/delete/section/<section_name>/', methods=['GET', 'POST'])
def web_delete_section(section_name):
    if 'login' in session:

        context = {}

        if request.method == 'POST':
            manager.delete_section(section_name)
            settings.remove_section(section_name)
            return redirect(url_for('main'))
        
        context['sections'] = manager.get_all_sections()
        context['loggedin'] = True
        context['section'] = section_name
        context['delete_section'] = True

        return render_template('admin.html', **context)

    return redirect(url_for('main'))

@app.route('/delete/page/', methods=['GET', 'POST'])
def web_delete_page():
    if 'login' in session:

        if request.method == 'POST':
            section = request.form['section']
            for page in request.form.getlist('page'):
                manager.delete_page(section, page)
            return redirect(url_for('main'))

    return redirect(url_for('main'))

@app.route('/section/', methods=['GET', 'POST'])
def add_new_section():
    if 'login' in session:

        context = {}

        if request.method == 'POST':
            section = request.form['section']
            if manager.create_directory('input/' + section):
                if Generator.Settings().add_new_section(section):
                    context['section_message'] = 'Created new section!'
                else:
                    context['section_message'] = 'Could not create new section!'
            else:
                context['section_message'] = 'Section already exists!'

        context['sections'] = manager.get_all_sections()
        context['loggedin'] = True
        context['section_creator'] = True

        return render_template('admin.html', **context)

    return redirect(url_for('main'))

@app.route('/lib/<path:filename>')
def lib_static(filename):
    if 'login' in session:
        return send_from_directory(app.root_path + '/lib/', filename)

    return redirect(url_for('main'))

@app.route('/logout/')
def logout():
    session.pop('login', None)
    return redirect(url_for('main'))

def valid_login(login, password):
    if login == settings.get_login() and password == settings.get_password():
        return True

settings = Generator.Settings()
handler = Generator.Generator()
manager = Generator.Manager()

app.secret_key = settings.get_secret_key()

if __name__ == "__main__":
    port = 5000
    if 'port' in sys.argv:
        try:
            port = int(sys.argv[ [i for i,x in enumerate(sys.argv) if x == 'port'][0] + 1 ])
        except(IndexError, ValueError):
            print 'You should provide valid port number! Using default port.'

    for arg in sys.argv:
        if arg == 'force':
            handler.generate_feedback(force=True)
        elif arg == 'gen':
            if not 'force' in sys.argv:
                handler.generate_feedback(force=False)
        elif arg == 'admin':
            if 'debug' in sys.argv:
                app.debug = True
            app.run(host='0.0.0.0', port=port)