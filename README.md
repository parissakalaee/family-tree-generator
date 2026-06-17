# Family Tree Generator

A Python tool that generates multilingual family tree PDFs from simple YAML files.

## Features

- Define your family in a readable YAML file — no coding needed
- Two-sided layout: maternal and paternal pages
- Bilingual output (any two languages you define in `translations.json`)
- Supports aliases, step-children, bridge nodes (couples spanning both pages), and cousin marriages
- RTL language support (Arabic, Persian, Hebrew, …)

## Quick start

```bash
pip install -e .
family-tree --tree sample --lang en
```

The PDF is written to `output/`.

## Supported languages

Pass `--lang` with any language code defined in `translations.json`. The sample data ships with `en` (English) and `nl` (Dutch).

## Defining your own family

1. Copy `src/family_tree/data/trees/sample.yaml` and edit it with your own names and structure.
2. Add name translations to `src/family_tree/data/translations.json`.
3. Run `family-tree --tree <your-file-slug> --lang en`.

See the comments at the top of `sample.yaml` for all available node options.

## Requirements

- Python 3.10+
- [reportlab](https://www.reportlab.com/) for PDF rendering
- [python-bidi](https://github.com/MeirKriheli/python-bidi) and [arabic-reshaper](https://github.com/mpcabd/python-arabic-reshaper) for RTL support

## License

MIT
