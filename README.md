dandl
=====
*A simple Danbooru/Gelbooru/Shimmie scraper tool*

# Setup

Install Python 3 with pip, then install the dependencies:

```bash
pip install -r requirements.txt --target lib
```

If your default system Python is version 2, try `python3` and `pip3` instead.

If the `pip install ...` doesn't work, this might work on Ubuntu:

```bash
python3 -m pip install -r requirements.txt --target lib
```

# Usage

Just run the script~!

```bash
./dandl.py <provider> <search-tag> [search-tag ...]
```

Provider can be a hostname or short code. A list of all supported providers is in the help menu, accessible via the `-h` flag.

If desired, you can copy `example-config.conf` to your configuration directory to specify default options (see file for instructions).
