Bibliography: A Plugin for Pelican
====================================================

[![Build Status](https://img.shields.io/github/workflow/status/pelican-plugins/research-page/build)](https://github.com/micahjsmith/pelican-bibliography/actions)
[![PyPI Version](https://img.shields.io/pypi/v/pelican-bibliography)](https://pypi.org/project/pelican-bibliography/)
![License](https://img.shields.io/pypi/l/pelican-bibliography?color=blue)

Generated bibliography items that can be rendered in a research page

Installation
------------

This plugin can be installed via:

    python -m pip install pelican-bibliography

Usage
-----

This plugin provides a new generator, `BibliographyGenerator`. When this generator is run, it first detects a bibliography file from the `BIBLIOGRAPHY_PATHS` setting. Any filetype that can be consumed by `citeproc-py` may be supported, but for now only BibTeX (`.bib`) files are supported. The references are read from this file and loaded into `pelican.plugins.bibliography.Reference` objects, which provide attributes `fields` (the computed fields in CSL) and `metadata` (additional metadata about this reference). The set of all references is made available in the global context as `context.bibliography` as a `List[Reference]`. Now, you can use `bibliography` in your templates.

### Configuration

The following variables can be configured in your `pelicanconf.py`:

```
# A directory that contains the bibliography-related templates
BIBLIOGRAPHY_RESEARCH_TEMPLATES: Union[str, os.PathLike]

# A list of directories and files to look at for bibliographies, relative to PATH.
BIBLIOGRAPHY_PATHS: List[str]

# A list of directories to exclude when looking for pages
BIBLIOGRAPHY_EXCLUDES: List[str]

# list of file extensions (without leading period) that are bibliography files
BIBLIOGRAPHY_EXTENSIONS: List[str]

# list of file extensions (without leading period) that are metadata files
BIBLIOGRAPHY_METADATA_EXTENSIONS: List[str]
```

### Research page

A main application of this is to create a research page that displays some collection of published research. For example, you could create a new template in your theme, `research.html` that renders your research:

```
Here are the titles of my papers:
<ul>
    {% for ref in bibliography %}
    <li>{{ ref.fields.title }}</li>
    {% endfor %}
</ul>
```

You can't just create your bibliography in your site's `content/`, because the context that includes the articles, pages, bibliography, etc. is not available when your content is read. What you can do is create a new template that extends `page.html` or `article.html`, and use that template to render some text in your content tree.

### Extra metadata

You can also provide additional metadata in a YAML file with the following structure:
```yaml
- key: someCitationKey2020
  metadata:
    key1: value1
    key2: value2
```

Now the keys and values in the metadata hash associated with the citation key will be available in the corresponding `ref.metadata` dictionary in the `bibliography`.

### Styling

The `research.html` default template that is included with the package has its own styling for jump links and highlighting. You can customize additional elements. For example, to style specific authors:

```css
.ref-author[data-family="Micah J."][data-family="Smith"] {
    text-weight: bold;
}
```

You can use multiple selectors to apply styles to the `ref-author` span with data attributes matching a certain name.


Contributing
------------

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.

[existing issues]: https://github.com/micahjsmith/pelican-bibliography/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html

License
-------

This project is licensed under the MIT license.
