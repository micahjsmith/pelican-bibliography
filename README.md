# Bibliography: A Plugin for Pelican

[![Build Status](https://img.shields.io/github/workflow/status/micahjsmith/pelican-bibliography/build)](https://github.com/micahjsmith/pelican-bibliography/actions)
[![PyPI Version](https://img.shields.io/pypi/v/pelican-bibliography)](https://pypi.org/project/pelican-bibliography/)
![License](https://img.shields.io/pypi/l/pelican-bibliography?color=blue)

Generated bibliography in Pelican that can be rendered in references and citations

This plugin provides a new generator, `BibliographyGenerator`. This generator adds `bibliography` to the Pelican context and can write an output file for each reference using a `citation.html` template. Additionally, the entire bibliography can be written using a `bibliography.html` template or otherwise.

## Installation

This plugin can be installed via:

```shell
pip install pelican-bibliography
```

Now, add it to your `pelicanconf.py`:

```python
PLUGINS = ['pelican.plugins.bibliography']
```

That's it, thanks to the [namespace plugins](https://docs.getpelican.com/en/latest/plugins.html#how-to-use-plugins) in Pelican 4.5+.

## Usage

When this generator is run, it first reads bibliography files from the `BIBLIOGRAPHY_PATHS` setting. For now, only BibTeX (`.bib`) files are supported, but more may be added in the future. Each reference contained in the bibliography is instantiated as a `Reference` object. The content of the reference is its citation in bibtex, while most of the useful information is in the metadata, such as the citation key, the title, the authors, the publication venue. Extra metadata key-value pairs can be read from YAML files in the same bibliography path. Now, you can use `bibliography` in your templates.

Next, the citations can be written to separate files. If desired, for each reference, the citation will be rendered according to the `citation.html` template and written to a configured path. Ideally, your bibliography will link to the citation page so that interested readers can easily cite your work.

### Configuration

The following variables can be configured in your `pelicanconf.py`:

```python
# A directory that contains the bibliography-related templates
# type: Union[str, os.PathLike]
BIBLIOGRAPHY_TEMPLATES = '.../pelican/plugins/bibliography/data/templates'

# A list of directories and files to look at for bibliographies, relative
# to PATH.
# type: List[str]
BIBLIOGRAPHY_PATHS = ["bibliography"]

# A list of directories to exclude when looking for references
# type: List[str]
BIBLIOGRAPHY_EXCLUDES = []

# list of file extensions (without leading period) that are bibliography
# files
# type: List[str]
BIBLIOGRAPHY_EXTENSIONS = ["bib"]

# list of file extensions (without leading period) that are metadata files
# type: List[str]
BIBLIOGRAPHY_METADATA_EXTENSIONS = ["yml", "yaml"]

# attribute of the Reference object to order the bibliography by (in
# reverse order)
# type: str
BIBLIOGRAPHY_ORDER_BY = "sortkey"

# whether to write citations to files
# type: bool
BIBLIOGRAPHY_WRITE_CITATIONS = True

# template to use for citations
# type: str
BIBLIOGRAPHY_CITATION_TEMPLATE_NAME = "citation.html"

# format string to link to citation
# type: str
BIBLIOGRAPHY_CITATION_URL = "files/citation/{key}"

# format string to save citations as in generated site
# type: str
BIBLIOGRAPHY_CITATION_SAVE_AS = "files/citation/{key}/index.html"
```

### Bibliography page

A main application of this is to create a research page that displays some collection of published research. For example, you could create a new template in your theme, `bibliography.html` that renders your research:

```html
Here are the titles of my papers:
<ul>
    {% for ref in bibliography %}
    <li>{{ ref.title }}</li>
    {% endfor %}
</ul>
```

You can't just create your bibliography in your site's `content/`, because the context that includes the articles, pages, bibliography, etc. is not available when your content is read. What you can do is create a new template that extends `page.html` or `article.html`, and use that template to render some text in your content tree.

A basic bibliography template is included with the plugin that tries to extend your theme's page template. Thus you could render your bibliography by adding this page to your content:

```markdown
Title: My Bibliography
Template: bibliography

Here is my bibliography
```

View an [example bibliography](https://www.micahsmith.com/research/) using the provided
template.

### Extra metadata

You can also provide additional metadata in a YAML file with the following structure:
```yaml
- key: someCitationKey2020
  metadata:
    key1: value1
    key2: value2
```

Now the keys and values in the metadata hash associated with the citation key will be available in the corresponding `ref.metadata` dictionary in the `bibliography`.

### Bibliography template

The `bibliography.html` default template that is included with the package has its own styling for jump links and highlighting. You can customize additional elements. For example, to style specific authors:

```css
.ref-author[data-given="Micah J."][data-family="Smith"] {
    text-weight: bold;
}
```

You can use multiple selectors to apply styles to the `ref-author` span with data attributes matching a certain name.

The template also has support for rendering *links* for each item. Add to your metadata file a key `links` that is a list of hashes with keys `href` and `icon`, i.e.

```yaml
- key: someCitationKey2020
  metadata:
    links:
      - href: https://www.example.com
        icon: link
```

Now an icon will be included that links to the given site. The exact icon is determined by `fa-{link.icon}`, so `fa-link` is a link, `icon: file-pdf` would lead to `fa-file-pdf`, etc.

## Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues](https://github.com/micahjsmith/pelican-bibliography/issues).

To start contributing to this plugin, review the [Contributing to Pelican](https://docs.getpelican.com/en/latest/contribute.html) documentation, beginning with the **Contributing Code** section.

## License

This project is licensed under the MIT license.
