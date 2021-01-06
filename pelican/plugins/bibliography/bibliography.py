import logging
import os.path
from collections import defaultdict
from functools import wraps, total_ordering
from typing import Dict
from urllib.parse import urljoin

from pelican import signals
from pelican.contents import Content
from pelican.generators import Generator

try:
    import pybtex
    import pybtex.database
    import yaml
except ImportError:
    pybtex = None
    yaml = None
    fy = None


enabled = bool(pybtex) and bool(yaml)
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
    'BIBLIOGRAPHY_ORDER_BY': 'sortkey',
    'BIBLIOGRAPHY_WRITE_REFENTRIES': True,
    'BIBLIOGRAPHY_REFENTRY_TEMPLATE_NAME': 'reference.html',
    'BIBLIOGRAPHY_REFENTRY_PATH': 'files/bib/'
}


@total_ordering
class AlwaysLessThan:
    def __lt__(self, other):
        return True


_lt = AlwaysLessThan()


def memoize(func):
    memory = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = args + tuple(sorted(kwargs.items())) if kwargs else args
        if key not in memory:
            memory[key] = func(*args, **kwargs)
        return memory[key]

    return wrapper


@memoize
def collection_from_path(source_path: str):
    # process metadata
    _, tail = os.path.split(source_path)
    collection, _ = os.path.splitext(tail)
    return collection


class Reference(Content):
    mandatory_properties = ('key', 'type',)
    default_template = 'reference'  # this is the default, but ignored

    @classmethod
    def from_entry(
        cls,
        entry: pybtex.database.Entry,
        source_path: str,
        metadata: dict,
        settings: dict,
    ):
        content = entry.to_string('bibtex')
        collection = collection_from_path(source_path)
        fields = {
            key.lower(): entry.fields[key]
            for key in entry.fields
        }
        metadata = {
            'key': entry.key,
            'type': entry.type,
            'sortkey': cls.sortkey(fields),
            'collection': collection,
            **fields,
            **metadata,
        }

        # add url and save_as
        refdir = settings['BIBLIOGRAPHY_REFENTRY_PATH']
        key = metadata['key']
        metadata['url'] = urljoin(
            settings['SITEURL'], f'{refdir}/{key}.bib')
        metadata['save_as'] = os.path.join(
            refdir, key + '.bib', 'index.html')

        return cls(content, metadata=metadata, source_path=source_path)

    @staticmethod
    def sortkey(fields):
        if 'issued' in fields:
            return fields['issued'].sort_key()
        else:
            return _lt


def read_references(source_path) -> 'pybtex.database.BibliographicData':
    """Parse content and metadata of bibtex files"""
    if not source_path.endswith('bib'):
        raise NotImplementedError
    return pybtex.database.parse_file(source_path, bib_format='bibtex').lower()


def read_metadata(source_path):
    if source_path.endswith('yml') or source_path.endswith('yaml'):
        with open(source_path, 'r') as f:
            return yaml.safe_load(f)  # List[Dict]


class BibliographyGenerator(Generator):

    def _read_bibdata(self) -> Dict[str, 'pybtex.database.BibliographyData']:
        all_bibdata = {}
        for file in self.get_files(
            self.settings['BIBLIOGRAPHY_PATHS'],
            exclude=self.settings['BIBLIOGRAPHY_EXCLUDES'],
            extensions=self.settings['BIBLIOGRAPHY_EXTENSIONS'],
        ):
            logger.debug(f'Reading references from {file}')
            try:
                source_path = os.path.join(self.path, file)
                new_bibdata = read_references(source_path)
                all_bibdata[source_path] = new_bibdata
            except Exception as e:
                logger.error(
                    'Could not process %s\n%s', file, e,
                    exc_info=self.settings.get('DEBUG', False))
                self._add_failed_source_path(file)
                continue

            logger.debug(
                f'Read {len(new_bibdata.entries)} references from {file}')

        return all_bibdata

    def _read_extra_metadata(self) -> Dict[str, dict]:
        # add extra key-value pairs for matching citation keys
        extra_metadata = {}
        for file in self.get_files(
            self.settings['BIBLIOGRAPHY_PATHS'],
            exclude=self.settings['BIBLIOGRAPHY_EXCLUDES'],
            extensions=self.settings['BIBLIOGRAPHY_METADATA_EXTENSIONS'],
        ):
            logger.debug(f'Reading extra metadata from {file}')
            try:
                source_path = os.path.join(self.path, file)
                new_metadata = read_metadata(source_path)
            except Exception as e:
                logger.error(
                    'Could not process %s\n%s', file, e,
                    exc_info=self.settings.get('DEBUG', False))
                continue

            logger.debug(
                f'Read {len(new_metadata)} extra metadata entries from {file}')
            for item in new_metadata:
                extra_metadata[item['key']] = item['metadata']

        return extra_metadata

    def generate_context(self):
        all_bibdata = self._read_bibdata()
        extra_metadata = self._read_extra_metadata()

        # convert to Reference, subclass of Content
        bibliography = []
        for source_path in all_bibdata:
            bibdata = all_bibdata[source_path]
            for key in bibdata.entries:
                entry = bibdata.entries[key]
                metadata = extra_metadata[key]
                ref = Reference.from_entry(
                    entry, source_path, metadata, self.settings)
                bibliography.append(ref)

        # organize into collections
        bibliography_collections = defaultdict(list)
        for ref in bibliography:
            collection = ref.metadata['collection']
            bibliography_collections[collection].append(ref)

        sortkey = self.settings['BIBLIOGRAPHY_ORDER_BY']

        def sort(ref):
            return ref.metadata.get(sortkey)

        self.bibliography = sorted(bibliography, key=sort, reverse=True)
        self.bibliography_collections = bibliography_collections
        self._update_context(('bibliography', 'bibliography_collections', ))

    def generate_output(self, writer):
        if self.settings['BIBLIOGRAPHY_WRITE_REFENTRIES']:
            template = self.env.get_template(
                self.settings['BIBLIOGRAPHY_REFENTRY_TEMPLATE_NAME'])
            for ref in self.bibliography:
                dest = ref.metadata['save_as']
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
    if enabled:
        signals.initialized.connect(update_settings)
        signals.get_generators.connect(get_generators)
    else:
        logger.warn(
            'pelican-bibliography disabled due to missing dependencies')
