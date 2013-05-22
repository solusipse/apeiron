from jinja2 import Template, Environment, FileSystemLoader
import os, shutil, markdown, time, ConfigParser

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

        for section in Generator().get_all_sections():
            config += '['+section+'] \n'
            config += 'per_page = 5 \n\n'

        with open('settings.cfg', 'wb') as configfile:
            configfile.write(config)

    def get_value(self, section, value):
        parser=ConfigParser.SafeConfigParser()
        parser.read(['settings.cfg'])
        return parser.get(section, value)

    def get_default_section(self, section):
        default_section = self.get_value('main', 'default_section')
        if default_section != 'disabled':
            return default_section
        else:
            return False

    def get_template(self, section):
        try:
            template = self.get_value(section, 'template')
        except:
            template = self.get_value('main', 'default_template')
        return template

    def check_if_ascending(self, section):
        try:
            ascending = self.get_value(section, 'ascending')
            if ascending == 'True':
                return True
        except:
            return False

class Generator:

    def __init__(self):
        self.sections = self.get_all_sections()

    def generate_pages(self):
        for section in self.sections:
            section_pages = self._get_sections_pages(section)
            template = Settings().get_template(section)
            for page in section_pages:
                page_slug = self.get_slug(page)
                parsed_contents = self.parse_file(page, self._get_file_contents(page, section))
                if parsed_contents == False:
                    continue

                parsed_metadata = parsed_contents['metadata']
                parsed_contents = parsed_contents['contents']

                # Arguments for template generator
                context = {}
                context['Section'] = section
                context['Page'] = page_slug
                context['Contents'] = parsed_contents
                context['Title'] = parsed_metadata.get('Title', '')
                context['Date'] = parsed_metadata.get('Date', '')
                context['Author'] = parsed_metadata.get('Author', '')
                context['Tags'] = parsed_metadata.get('Tags', '')
                context['ID'] = parsed_metadata.get('ID', '')

                contents = self._generate_static_html(template, **context)

                # If there is only one page in section, generate it in
                # root section directory
                if len(section_pages) == 1:
                    page_slug = '.'

                self._save_static_html(section, page_slug, contents)

    def _get_sections_pages(self, section):
        return os.walk('input/'+section).next()[2]

    def _get_file_contents(self, filename, section):
        with open('input/' + section + '/' + filename, 'r') as input_file:
            return input_file.read()

    def generate_index_pages(self):
        index_dict = {}

        for section in self.sections:
            section_pages = self._get_sections_pages(section)

            if len(section_pages) > 1:
                for page in section_pages:
                    parsed_contents = self.parse_file(page, self._get_file_contents(page, section))
                    if parsed_contents == False:
                        continue

                    page_slug = self.get_slug(page)
                    page_id = int(parsed_contents['metadata'].get('ID'))
                    contents = parsed_contents['contents']
                    data = parsed_contents['metadata']

                    data['Contents'] = contents
                    data['Slug'] = '../' + page_slug + '/'
                    index_dict[page_id] = data

                self._generate_single_index_page(section, index_dict)

    def _generate_single_index_page(self, section, dictionary):
        per_page = int(Settings().get_value(section, 'per_page'))
        i = 0

        template = Settings().get_template(section)
        ascending = Settings().check_if_ascending(section)
        count_dict = len(dictionary)

        while(i < count_dict):
            page_slug = str(i+1) + '-' + str(i+per_page)

            buffer_dict = {}

            if ascending:
                for j in dictionary:
                    if j > i and j <= i + per_page:
                        buffer_dict[j] = dictionary[j]
            else:
                for j in dictionary:
                    if j > i and j <= i + per_page:
                        buffer_dict[count_dict - j] = dictionary[count_dict - j + 1]

            context = {}
            context['Index_page'] = True
            context['Dictionary'] = buffer_dict

            if i < count_dict - per_page:
                context['next_page_url'] = '../' + str(i+1+per_page) + '-' + str(i+per_page*2) + '/'
            if i != 0:
                context['previous_page_url'] = '../' + str(i+1-per_page) + '-' + str(i) + '/'

            contents = self._generate_static_html(template, **context)
            self._save_static_html(section, page_slug, contents)

            if Settings().get_default_section(section) == section:
                if i == 0:

                    for j in buffer_dict:
                        page_slug_single = str(buffer_dict[j]['Slug']).split('../')[1]
                        buffer_dict[j]['Slug'] = page_slug_single

                    context['next_page_url'] = str(i+1+per_page) + '-' + str(i+per_page*2) + '/'
                    contents = self._generate_static_html(template, **context)

                    for j in buffer_dict:
                        buffer_dict[j]['Slug'] = section + '/' + page_slug_single

                    self._save_static_html(section, '.', contents)
                    context['next_page_url'] = section + '/' + str(i+1+per_page) + '-' + str(i+per_page*2) + '/'
                    contents = self._generate_static_html(template, **context)
                    self._save_static_html(section, '..', contents)

            i += per_page

    def clean_output_directory(self):
        output_directory = Settings().get_value('main', 'output_directory')
        shutil.rmtree(output_directory)

    def get_slug(self, filename):
        return os.path.splitext(filename)[0]

    def get_modification_date(self, filename, section):
        return time.ctime(os.path.getctime('input/' + section + '/' + filename))

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

    def _generate_static_html(self, template, **context):
        template = env.get_template(template)
        return template.render(context)

    def create_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def _save_static_html(self, section, page, contents):
        output_directory = Settings().get_value('main', 'output_directory')
        self.create_directory(output_directory+'/'+section+'/'+page)
        with open(output_directory+'/'+section+'/'+page+'/index.html', 'w+') as html_file:
            html_file.write(contents)

    def get_all_sections(self):
        return os.walk('input').next()[1]