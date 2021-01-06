# simple

This is an example Pelican site showing the usage and configuration of pelican-bibliography.

The "bibliography.html" template from pelican-bibliography extends your theme's "page.html" template and assumes there exists a block called "after_content" in which it places the rendered bibliography. In this site, we are using the stock *notmyidea* theme which has a different structure for its page template. So we have to design our own bibliography template. Thus we create [templates/simplebibliography.html](./templates/simplebibliography.html) and add our [templates](./templates]) subdirectory to the `THEME_TEMPLATES_OVERRIDE` setting in `pelicanconf.py`. If you look at the new template we created, you can see that we import the `bibentry` macro and the `bibcss` variable from the plugin's `bibentry.html` template, which exists just to provide these macros for your use.

## Install

```
pip install --upgrade pip
pip install -r requirements.txt
```

## Build the site

```
invoke clean build serve
```

## View the bibliography

Navigate to `http://localhost:8000/bibliography`
