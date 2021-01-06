#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = 'Micah Smith'
SITENAME = 'My Bibliography'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'America/New_York'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'https://getpelican.com/'),
         ('Python.org', 'https://www.python.org/'),
         ('Jinja2', 'https://palletsprojects.com/p/jinja/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# pelican-bibliograpy config
PLUGINS = ['pelican.plugins.bibliography']
BIBLIOGRAPHY_PATHS = 'bibliography'  # this is the default already
BIBLIOGRAPHY_EXTENSIONS = ["bib"]  # this is the default already
BIBLIOGRAPHY_METADATA_EXTENSIONS = ["yml", "yaml"]  # this is the default already
BIBLIOGRAPHY_WRITE_CITATIONS = True  # this is the default already
THEME_TEMPLATES_OVERRIDES = ['templates']
