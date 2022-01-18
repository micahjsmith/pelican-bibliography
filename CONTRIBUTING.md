# Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.

[existing issues]: https://github.com/micahjsmith/pelican-bibliography/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html

## Note to self

A note to maintainers on how to publish a new version:

```
poetry version <bumptype>
git add -u
git commit -m "Bump version to <version>
poetry build
git push
# wait for tests to pass
poetry publish
```

Note that the deploy step on Actions only publishes a version if you follow the autopub workflow which requires a pull request to be merged that has a RELEASE.md file.
