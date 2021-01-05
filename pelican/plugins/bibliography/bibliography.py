import logging
import os.path
from collections import defaultdict
from copy import deepcopy
from functools import total_ordering
from typing import List

from pelican import signals
from pelican.generators import Generator

from .bibtex.models import BibtexEntry
from .bibtex.parser import parser

try:
    import citeproc
    import yaml
except ImportError:
    citeproc = None
    yaml = None

logger = logging.getLogger(__name__)

_template_path = os.path.join(
    os.path.realpath(os.path.dirname(__file__)),
    'data', 'templates')


DEFAULT_SETTINGS = {
    'BIBLIOGRAPHY_RESEARCH_TEMPLATES': _template_path,
    'BIBLIOGRAPHY_PATHS': ['bibliography'],
    'BIBLIOGRAPHY_EXCLUDES': [],
    'BIBLIOGRAPHY_EXTENSIONS': ['bib'],
    'BIBLIOGRAPHY_METADATA_EXTENSIONS': ['yml', 'yaml'],
    # 'BIBLIOGRAPHY_ORDER_BY': lambda ref: -ref.issued.year,  # TODO
    'BIBLIOGRAPHY_WRITE_REFENTRIES': True,
    'BIBLIOGRAPHY_REFENTRY_TEMPLATE_NAME': 'bibentry.html',
    'BIBLIOGRAPHY_REFENTRY_PATH': 'files/bib/'
}


@total_ordering
class AlwaysLessThan:
    def __lt__(self, other):
        return True


_lt = AlwaysLessThan()


class Reference:

    def __init__(self, ref: citeproc.source.Reference, metadata: dict = None):
        self.fields = dict(ref)
        self.metadata = {
            'key': ref.key,
            'type': ref.type,
        }
        if metadata is not None:
            self.metadata.update(metadata)

    @property
    def sortkey(self):
        if 'issued' in self.fields:
            return self.fields['issued'].sort_key()
        else:
            return _lt


def format_bibtex(entry: BibtexEntry):
    entry_template = '@{type}{{{key},\n{fields}\n}}'
    field_template = '  {key} = {value},'
    fields = '\n'.join(
        field_template.format(key=key, value=value)
        for key, value in entry.fields.items()
    )
    return entry_template.format(type=entry.type, key=entry.key, fields=fields)


def read_references(base_path, path, context):
    """Parse content and metadata of csl files"""
    source_path = os.path.join(base_path, path)

    if not source_path.endswith('bib'):
        raise NotImplementedError

    references = []

    refsource = citeproc.source.bibtex.BibTeX(source_path, encoding='ascii')

    # process metadata
    metadata = {}
    _head, _tail = os.path.split(source_path)
    name, _ext = os.path.splitext(_tail)
    metadata['collection'] = name

    for key in refsource:
        ref = Reference(refsource[key], deepcopy(metadata))
        references.append(ref)

    # separately, parse the .bib file preserving the original markup, and
    # reformat the bib entry
    with open(source_path, 'r') as f:
        entries: List[BibtexEntry] = parser.parse(f.read())
    # lazy O(n^2)
    for entry in entries:
        key = entry.key
        for ref in references:
            if ref.metadata['key'] == key:
                ref.metadata['bibtex'] = format_bibtex(entry)

    return references


def read_metadata(base_path, path):
    source_path = os.path.join(base_path, path)
    if source_path.endswith('yml') or source_path.endswith('yaml'):
        with open(source_path, 'r') as f:
            return yaml.safe_load(f)  # List[Dict]


class BibliographyGenerator(Generator):

    def generate_context(self):
        bibliography: List[Reference] = []
        for file in self.get_files(
            self.settings['BIBLIOGRAPHY_PATHS'],
            exclude=self.settings['BIBLIOGRAPHY_EXCLUDES'],
            extensions=self.settings['BIBLIOGRAPHY_EXTENSIONS'],
        ):
            logger.debug(f'Reading references from {file}')
            try:
                new_references = read_references(
                    base_path=self.path, path=file, context=self.context)
            except Exception as e:
                logger.error(
                    'Could not process %s\n%s', file, e,
                    exc_info=self.settings.get('DEBUG', False))
                self._add_failed_source_path(file)
                continue

            logger.debug(f'Read {len(new_references)} references from {file}')
            bibliography.extend(new_references)

        # add extra key-value pairs for matching citation keys
        extra_metadata = []
        for file in self.get_files(
            self.settings['BIBLIOGRAPHY_PATHS'],
            exclude=self.settings['BIBLIOGRAPHY_EXCLUDES'],
            extensions=self.settings['BIBLIOGRAPHY_METADATA_EXTENSIONS'],
        ):
            logger.debug(f'Reading extra metadata from {file}')
            try:
                new_metadata = read_metadata(
                    base_path=self.path, path=file)
            except Exception as e:
                logger.error(
                    'Could not process %s\n%s', file, e,
                    exc_info=self.settings.get('DEBUG', False))
                continue

            logger.debug(
                f'Read {len(new_metadata)} extra metadata entries from {file}')
            extra_metadata.extend(new_metadata)

        # lazy O(n^2)
        for item in extra_metadata:
            key = item['key']
            for ref in bibliography:
                if ref.metadata['key'] == key:
                    ref.metadata.update(item['metadata'])

        # add ref_href and ref_saveas
        refdir = self.settings['BIBLIOGRAPHY_REFENTRY_PATH']
        for ref in bibliography:
            key = ref.metadata['key']
            ref.metadata['ref_href'] = os.path.join(refdir, key + '.bib')
            ref.metadata['ref_saveas'] = os.path.join(refdir, key + '.bib', 'index.html')

        self.bibliography = bibliography

        # organize into collections
        self.bibliography_collections = defaultdict(list)
        for ref in self.bibliography:
            collection = ref.metadata.get('collection', 'Other')
            self.bibliography_collections[collection].append(ref)

        self._update_context(('bibliography', 'bibliography_collections', ))

    def generate_output(self, writer):
        if self.settings['BIBLIOGRAPHY_WRITE_REFENTRIES']:
            template = self.env.get_template(
                self.settings['BIBLIOGRAPHY_REFENTRY_TEMPLATE_NAME'])
            for ref in self.bibliography:
                dest= ref.metadata['ref_saveas']
                writer.write_file(
                    dest, template, self.context, override_output=True, url='', ref=ref)


def update_settings(pelican):
    for key in DEFAULT_SETTINGS:
        pelican.settings.setdefault(key, DEFAULT_SETTINGS[key])
    if pelican.settings['BIBLIOGRAPHY_RESEARCH_TEMPLATES']:
        pelican.settings['THEME_TEMPLATES_OVERRIDES'].append(
            pelican.settings['BIBLIOGRAPHY_RESEARCH_TEMPLATES'])


def get_generators(pelican_object):
    return BibliographyGenerator


def register():
    signals.initialized.connect(update_settings)
    signals.get_generators.connect(get_generators)
