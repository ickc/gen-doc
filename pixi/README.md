This rebuild pixi doc with single file targets.

# Notes

pixi doc uses mkdocs, which by default doesn't support single file target.

A few tricks are used here,

- add `mkdocs-print-site-plugin` which provide a `print-site` plugin to mkdocs. That's why we have our own `mkdocs.yml` here created by make.
    - Once the single page HTML is generated, it is used to create a GFM markdown version and a plain text version, via pandoc.
