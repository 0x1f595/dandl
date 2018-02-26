dandl
=====
*A simple Danbooru/Gelbooru/Shimmie scraper tool*

Install Python 3, the dependencies, and run the script~!

```bash
pip install -r requirements.txt
python dandl.py <provider> <search>
```

If your default system Python is version 2, try `python3` and `pip3` instead.

If the `install -r` doesn't work, this might work on Ubuntu:

```bash
sudo -H python3 -m pip install -r requirements.txt
```

Provider can be a hostname or short code. A list of all supported providers is in the help menu, accessible via the `-h` flag.

If desired, you can copy `example-config.conf` to your configuration directory to specify default options (see file for instructions).
