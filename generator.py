# -*- encoding: utf-8 -*-

from jinja2 import Template, Environment, FileSystemLoader
import os, shutil, time, ConfigParser, HTMLParser, hashlib
import string, random, codecs, sys

import lib.markdown as markdown

# Pygments imports
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

env = Environment(loader=FileSystemLoader('templates'))

class Settings:

    def __init__(self):
        if not os.path.isfile('settings.cfg'):
            self.generate_default_config()

    def generate_default_config(self):
        config = '''[main]
# default_section:
# change 'disabled' to name of one of your sections
# to make it default (its index page will be generated
# on the top of other directories)
default_section = disabled

# default_template:
# this template will be used for all sections in case you won't
# specify templates for individual section
default_template = default.html

# output directory: (this may be relative and absolute as well)
# remember not to add slash at the end of key
# default: ./output e.g.: /home/www/my_site 
output_directory = ./output

# static_directory:
# this is directory where you can put all your static files:
# images, csses, javascripts, relative link to that directory
# will be provided on all pages - {{ Static }}
static_directory = ./static

# These are your login informations and secret key. Both key and
# password were randomly generated and don't need to be changed.
#login_data

# always regenerate everything:
# if you want to regenerate every file when running generator,
# uncomment line below
# regenerate_everything = True

# example section's configuration:
# [section_name]
# template = template_name.html
# ascending = True

# template:
# if template is specified, section will use it instead of default
# template = template_name.html

# ascending:
# if you want to have oldest post before newer, you should add
# key 'ascending = True', remember that you need also to edit
# template (more in documentation)
# ascending = True

# Automaticaly generated sections
# to regenerate, simply delete settings.cfg

'''

        for section in Manager().get_all_sections():
            config += '['+section+'] \n'
            config += 'per_page = 5 \n\n'

        config = config.replace('#login_data', 'login = admin\n' + 'password = ' \
            + self.generate_password() + '\nsecret_key = ' + self.generate_secret_key())

        with open('settings.cfg', 'wb') as configfile:
            configfile.write(config)

    def get_value(self, section, value):
        parser = ConfigParser.SafeConfigParser()
        parser.read(['settings.cfg'])
        return parser.get(section, value)

    def compare_default_section(self, section):
        default_section = self.get_value('main', 'default_section')
        if default_section != 'disabled':
            return default_section
        else:
            return False

    def get_default_section(self):
        return self.get_value('main', 'default_section')

    def get_output_directory(self):
        return Settings().get_value('main', 'output_directory')

    def get_static_directory(self):
        return Settings().get_value('main', 'static_directory')

    def get_template(self, section):
        try:
            template = self.get_value(section, 'template')
        except:
            template = self.get_value('main', 'default_template')
        return template

    def get_default_template(self):
        return self.get_value('main', 'default_template')

    def get_contents(self):
        with open('settings.cfg') as settings_file:
            return settings_file.read()

    def check_if_ascending(self, section):
        try:
            ascending = self.get_value(section, 'ascending')
            if ascending == 'True':
                return True
        except:
            return False

    def check_regen_policy(self):
        try:
            if self.get_value('main', 'regenerate_everything') == 'True':
                return True
        except:
            return False

    def generate_password(self):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(10))

    def generate_secret_key(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(24))

    def get_login(self):
        return self.get_value('main', 'login')

    def get_password(self):
        return self.get_value('main', 'password')

    def get_secret_key(self):
        return self.get_value('main', 'secret_key')

    def add_new_section(self, section):
        Config = ConfigParser.ConfigParser()
        config_file = open("settings.cfg",'a')

        try:
            Config.add_section(section)
            Config.set(section, 'per_page', '5')

            Config.write(config_file)
            config_file.close()

            return True
        except:
            return False

    def remove_section(self, section):
        config = ConfigParser.RawConfigParser()
        config.read('settings.cfg')
        config.remove_section(section)
        config.write(open('settings.cfg', 'w'))

    def save_config(self, contents):
        with open('settings.cfg', 'w') as config_file:
            config_file.write(contents)


class Syntax(HTMLParser.HTMLParser):

    def highlight(self, html):
        self.tag_stack = []
        self.inputhtml = html.replace('&', 'ampersand___').replace(';', '')
        self.feed(self.inputhtml)
        return self.inputhtml

    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag.lower())

    def handle_endtag(self, tag):
        self.tag_stack.pop()

    def handle_data(self, data):
        if len(self.tag_stack) and self.tag_stack[-1] == 'code':
            try:
                lexer = get_lexer_by_name(data.splitlines()[0], stripall=True)
                formatter = HtmlFormatter(linenos=True, cssclass="highlight")
                output_html = highlight(data.replace(data.splitlines()[0], '', 1), lexer, formatter)
                self.inputhtml = self.inputhtml.replace(data, output_html).replace('ampersand___', '&')
            except:
                self.inputhtml = self.inputhtml.replace('ampersand___', '&')


class Manager:

    def create_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
            return True
        return False

    def set_static_directory(self):
        static_directory = Settings().get_static_directory()
        output_directory = Settings().get_output_directory()
        self.create_directory(output_directory + '/' + static_directory)

    def parse_url(self, data, source):
        static_directory = Settings().get_static_directory()
        if source == 0:
            return data.replace('{{ Static }}', '../../' + static_directory)
        return data.replace('{{ Static }}', '../' + static_directory)

    def get_sections_pages(self, section):
        filelist = os.walk('input/'+section).next()[2]
        filelist = [item for item in filelist if item.endswith('.md')]

        return filelist

    def get_file_contents(self, filename, section):
        with open('input/' + section + '/' + filename) as input_file:
            return input_file.read()

    def clean_output_directory(self):
        output_directory = Settings().get_output_directory()
        shutil.rmtree(output_directory)

    def delete_section(self, section):
        output_directory = Settings().get_output_directory()
        shutil.rmtree('input/' + section)
        try:
            shutil.rmtree(output_directory+'/'+section)
        except(OSError):
            pass

    def rename_section(self, section, new_name):
        Settings().add_new_section(new_name)
        try:
            Settings().remove_section(section)
        except(NoSectionError):
            pass

        output_directory = Settings().get_output_directory()
        shutil.copytree('input/'+section, 'input/'+new_name)
        self.delete_section(section)

    def delete_page(self, section, page):
        output_directory = Settings().get_output_directory()
        os.remove('input/' + section + '/' + page + '.md')
        try:
            os.remove('input/' + section + '/' + page + '.md.md5')
        except(OSError):
            pass
        try:
            shutil.rmtree(output_directory+'/'+section+'/'+page)
        except(OSError):
            pass

    def get_syntax_css_url(self, source):
        static_directory = Settings().get_static_directory()
        if source == 1:
            return '../../' + static_directory + '/Syntax.css'
        return '../' + static_directory + '/Syntax.css'

    def get_all_sections(self):
        return os.walk('input').next()[1]

    def get_slug(self, filename):
        return os.path.splitext(filename)[0]

    def get_file_hash(self, section, page):
        return hashlib.md5(self.get_file_contents(page, section)).hexdigest()

    def get_saved_hash(self, section, page):
        if not os.path.isfile('input/' + section + '/' + '.' + page + '.md5'):
            return False
        with open('input/' + section + '/' + '.' + page + '.md5', 'r') as input_file:
            return input_file.read()

    def save_file_hash(self, section, page, hash_info):
        with open('input/' + section + '/' + '.' + page + '.md5', 'w+') as input_file:
            input_file.write(hash_info)

    def parse_file(self, filename, contents):
        filetype = os.path.splitext(filename)[1]

        if filetype == '.md':
            contents = self.parse_markdown(contents)
            metadata = contents.metadata
        
            return {'contents': contents, 'metadata': metadata}
        else:
            return False

    def parse_markdown(self, contents):
        return markdown.markdown(contents, extras=["metadata"])

    def create_pages_dictionary(self, section):
        pages_list = self.get_sections_pages(section)
        pages_dictionary = {}
        
        for page in pages_list:
            parsed_contents = self.parse_file(page, self.get_file_contents(page, section))
            pages_dictionary[page[:-3]] = parsed_contents['metadata']

        return pages_dictionary

    def save_page_md(self, section, page, content):
        output_directory = Settings().get_output_directory()
        file_location = './input/' + section + '/' + page + '.md'

        with codecs.open(file_location, 'w+', 'utf-8') as output_file:
            output_file.write(content)

    def check_if_page_exists(self, section, page):
        output_directory = Settings().get_output_directory()
        if os.path.isfile(output_directory+'/'+section+'/'+page+'/index.html'):
            return True

    def get_templates(self):
        return os.walk('templates/').next()[2]

    def get_template_code(self, template):
        with open('templates/'+template) as template_file:
            return template_file.read()

    def save_template(self, template, contents):
        with open('templates/' + template, 'w') as template_file:
            template_file.write(contents)


class Generator:

    def __init__(self):
        Manager().set_static_directory()
        self.generate_syntax_css()

    def generate_feedback(self, force):
        return self.generate_pages(force), self.generate_index_pages()

    def generate_pages(self, force):
        self.sections = Manager().get_all_sections()
        feedback = []

        for section in self.sections:
            section_pages = Manager().get_sections_pages(section)
            template = Settings().get_template(section)

            for page in section_pages:
                page_slug = Manager().get_slug(page)

                parsed_contents = Manager().parse_file(page, Manager().get_file_contents(page, section))

                # If file has other extension than markdown
                if parsed_contents == False:
                    continue

                # If there is only one file in section, generate
                # there only one index file without page directory
                if len(section_pages) == 1:
                    page_slug = '.'

                output_directory = Settings().get_output_directory()

                # If not specified, generated are only those files
                # which have no previous generations
                if not Settings().check_regen_policy() and not force:
                    if Manager().check_if_page_exists(section, page_slug):
                        if Manager().get_saved_hash(section, page) == Manager().get_file_hash(section, page):
                            print output_directory+'/'+section+'/'+page_slug+'/index.html' + '\033[94m PASS\033[0m'
                            feedback.append(output_directory+'/'+section+'/'+page_slug+'/index.html' + ' PASS')
                            continue
                        else:
                            Manager().save_file_hash(section, page, Manager().get_file_hash(section, page))

                parsed_metadata = parsed_contents['metadata']
                parsed_contents = parsed_contents['contents']

                # Highlight syntax
                parsed_contents = Syntax().highlight(parsed_contents)

                context = {}

                # Add static url
                if len(section_pages) == 1:
                    parsed_contents = Manager().parse_url(parsed_contents, 1)
                    context['SyntaxCSS'] = Manager().get_syntax_css_url(0)
                else:
                    parsed_contents = Manager().parse_url(parsed_contents, 0)
                    context['SyntaxCSS'] = Manager().get_syntax_css_url(1)

                # Arguments for template generator
                context['Section'] = section
                context['Page'] = page_slug
                context['Contents'] = parsed_contents
                context['Title'] = parsed_metadata.get('Title', '')
                context['Date'] = parsed_metadata.get('Date', '')
                context['Author'] = parsed_metadata.get('Author', '')
                context['Tags'] = parsed_metadata.get('Tags', '')
                context['ID'] = parsed_metadata.get('ID', '')
                context['Menu'] = self.sections

                if page_slug == '.':
                    context['Page'] = section

                # Generate template
                contents = self._generate_static_html(template, **context)

                # and save it to file
                self._save_static_html(section, page_slug, contents)

                if len(section_pages) == 1 and Settings().compare_default_section(section) == section:
                    self._save_static_html(section, '..', contents)
                    feedback.append(output_directory+'/index.html' + ' OK')

                feedback.append(output_directory+'/'+section+'/'+page_slug+'/index.html' + ' OK')

        return feedback

    def generate_index_pages(self):
        index_dict = {}
        feedback = []

        for section in self.sections:
            section_pages = Manager().get_sections_pages(section)

            if len(section_pages) > 1:
                for page in section_pages:
                    parsed_contents = Manager().parse_file(page, Manager().get_file_contents(page, section))
                    if parsed_contents == False:
                        continue

                    # Highlight syntax
                    parsed_contents['contents'] = Syntax().highlight(parsed_contents['contents'])

                    # Add static url
                    parsed_contents['contents'] = Manager().parse_url(parsed_contents['contents'], 1)

                    page_slug = Manager().get_slug(page)
                    page_id = int(parsed_contents['metadata'].get('ID'))
                    contents = parsed_contents['contents']
                    data = parsed_contents['metadata']

                    data['Contents'] = contents
                    data['Slug'] = '../' + page_slug + '/'
                    index_dict[page_id] = data

                feedback.append(self._generate_single_index_page(section, index_dict))

        return feedback

    def _generate_single_index_page(self, section, dictionary):

        feedback = []

        per_page = int(Settings().get_value(section, 'per_page'))
        i = 0

        template = Settings().get_template(section)
        ascending = Settings().check_if_ascending(section)
        count_dict = len(dictionary)

        # This loop is used for split list of all section's
        # contents to pages
        while(i < count_dict):
            page_slug = str(i+1) + '-' + str(i+per_page)

            buffer_dict = {}

            # If there exists key called ascending in config,
            # pages on index page will be generated from
            # oldest to newest. In that case remember to change
            # in your template line with for loop to:
            # {% for page in Dictionary|sort %}
            if ascending:
                for j in dictionary:
                    if j > i and j <= i + per_page:
                        buffer_dict[j] = dictionary[j]
            else:
                for j in dictionary:
                    if j > i and j <= i + per_page:
                        try:
                            buffer_dict[count_dict - j] = dictionary[count_dict - j + 1]
                        except(KeyError):
                            feedback.append('ERROR! Check pages order!')
                            print 'ERROR! Check pages order!'

            context = {}
            context['Index_page'] = True
            context['Dictionary'] = buffer_dict
            context['Menu'] = self.sections
            context['Section'] = section
            context['SyntaxCSS'] = Manager().get_syntax_css_url(0)

            if i < count_dict - per_page:
                context['next_page_url'] = '../' + str(i+1+per_page) + '-' + str(i+per_page*2) + '/'
            if i != 0:
                context['previous_page_url'] = '../' + str(i+1-per_page) + '-' + str(i) + '/'

            contents = self._generate_static_html(template, **context)
            self._save_static_html(section, page_slug, contents)

            output_directory = Settings().get_output_directory()

            # If section was marked as default in config file
            # its index page will be generated in top of other
            # sections. To make urls compatibile with the rest
            # of files, there is need to modify the dictionary
            if i == 0:

                for j in buffer_dict:
                    page_slug_single = str(buffer_dict[j]['Slug']).split('../')[1]
                    buffer_dict[j]['Slug'] = page_slug_single

                if i < count_dict - per_page:
                    context['next_page_url'] = str(i+1+per_page) + '-' + str(i+per_page*2) + '/'
                contents = self._generate_static_html(template, **context)
                self._save_static_html(section, '.', contents)

                if Settings().compare_default_section(section) == section:

                    for j in buffer_dict:
                        buffer_dict[j]['Slug'] = section + '/' + buffer_dict[j]['Slug']

                    if i < count_dict - per_page:
                        context['next_page_url'] = section + '/' + str(i+1+per_page) + '-' + str(i+per_page*2) + '/'
                    contents = self._generate_static_html(template, **context)
                    self._save_static_html(section, '..', contents)

                    feedback.append(output_directory+'/index.html' + ' OK')

            feedback.append(output_directory+'/'+section+'/'+page_slug+'/index.html' + ' OK')
            i += per_page

        return feedback

    def generate_syntax_css(self):
        css_code = HtmlFormatter().get_style_defs('.highlight')
        output_directory = Settings().get_output_directory()
        static_directory = Settings().get_static_directory()
        if not os.path.isfile(output_directory + '/' + static_directory + '/Syntax.css'):
            with open(output_directory + '/' + static_directory + '/Syntax.css', 'w+') as css_file:
                css_file.write(css_code)

    def _generate_static_html(self, template, **context):
        template = env.get_template(template)
        return template.render(context)

    def _save_static_html(self, section, page, contents):
        output_directory = Settings().get_output_directory()
        Manager().create_directory(output_directory+'/'+section+'/'+page)
        try:
            with codecs.open(output_directory+'/'+section+'/'+page+'/index.html', 'w+', 'utf-8') as html_file:
                html_file.write(contents)
            print output_directory+'/'+section+'/'+page+'/index.html' + '\033[92m OK\033[0m'
        except EnvironmentError:
            print output_directory+'/'+section+'/'+page+'/index.html' + '\033[91m ERROR\033[0m'



# Creating settings file
Settings()

if __name__ == "__main__":
    for arg in sys.argv:
        if arg == 'force':
            Generator().generate_feedback(force=True)
            exit()

    Generator().generate_feedback(force=False)