This rebuild NERSC doc with single file targets.

# Notes

NERSC doc uses mkdocs, which by default doesn't support single file target.

A few tricks are used here,

- add `mkdocs-print-site-plugin` which provide a `print-site` plugin to mkdocs. That's why we have our own `mkdocs.yml` here created by make.
    - Once the single page HTML is generated, it is used to create a GFM markdown version and a plain text version, via pandoc.
- concat-based markdown output `index.md` by parsing `mkdocs.yml` and get all its input md files, and then concat with the permalink info to each page.

So far, the one with the best answer via ChatGPT seems to be the HTML output.
