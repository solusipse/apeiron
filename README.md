apeiron
=======

Static websites generator with web admin panel based on flask and jinja2. Its main purpose is to provide
simple, lightweight platform for bloggers. There is still much to do, although it's usable even now.

Requirements
--------------
-   Python 2.7
-   Flask
-   Pygments

Installation and basic usage
-----
Your Python needs to meet the requirements, so we must install these packages:
```
pip install flask
```
```
pip install pygments
```
When you are done, you have to clone into apeiron's repository:
```
git clone git://github.com/solusipse/apeiron.git
```
Package should work out of box. To generate pages type:
```
python apeiron.py gen
```
For force generation (regenerating every page):
```
python apeiron.py force
```
For web panel:
```
python apeiron.py admin
```
For flask debbuger (use it only if something doesn't work):
```
python apeiron.py debug admin
```

To adjust apeiron to your needs, edit file called `settings.cfg`. It is generated when you run
program for the first time. To regenerate it, simply delete it and run program again.

File format
-----
Format for input files is markdown. There is live markdown editor provided in web panel.
There is also syntax colouring option. To colour some fragment of text you need to ident it
with at least four spaces or one tab and put language name in first line. When code is being highlighted it also
being put into table with line numbers.
```python
This will be coloured:
    
    python
    if __name__ == "__main__":
    for arg in sys.argv:
        if arg == 'force':
            Generator().generate_feedback(force=True)
            exit()

This will not:

    cat /etc/nginx/nginx.conf > nginx_backup.txt

```

Config file
------
Default contents of this file:
```
[main]
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
login = admin
password = iztazprdhs
secret_key = KUvyKAzaIhKZpS0KwuPyaVJb

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

[contact] 
per_page = 5 

[blog] 
per_page = 5 

[about] 
per_page = 5 
```

License
----
Apeiron is MIT licensed.
