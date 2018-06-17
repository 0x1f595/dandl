#!/usr/bin/env python
"""
dandl - Danbooro/Gelbooru/Shimmie downloader
"""

# Allow local package installs
import sys
import os
sys.path.append(os.getcwd() + os.sep + 'lib')

import configparser
import argparse
import xml.etree.ElementTree as ET
import json
import time
import textwrap
from urllib import parse, request
from sys import stderr
from appdirs import user_config_dir

images = []

def main():
    """
    Run the scraper
    """

    # Read configuration
    config_file = user_config_dir() + os.sep + 'dandl.conf'
    config = configparser.ConfigParser()
    if os.path.isfile(config_file):
        config.read(config_file)

    supported_sites = ['danbooru.donmai.us', 'safebooru.org', 'rule34.paheal.net',
                       'rule34.xxx', 'shimmie.katawa-shoujo.com']
    max_filename_len = 240

    # Read arguments
    parser = argparse.ArgumentParser(
        description='Bulk download images from a Danbooru/Gelbooru/Shimmie site',
        epilog='supported providers: ' + ' '.join(supported_sites))
    parser.add_argument('--dir', help='Directory to save images to')
    parser.add_argument('--limit', type=int, help='Max number of images to download')
    parser.add_argument('--nd', action='store_true',
                        help='Skip downloading images, only displaying URLs')
    parser.add_argument('provider', help='Provider to download from')
    parser.add_argument('tag', nargs='+', help='Tags to search for')
    args = parser.parse_args()

    # Prepare output directory
    imgdir = config['DEFAULT'].get('savedir')
    if imgdir:
        imgdir = os.path.expanduser(imgdir)
        if not args.nd:
            os.makedirs(imgdir, exist_ok=True)
    else:
        imgdir = os.curdir

    # Find images by provider
    if args.provider == 'danbooru.donmai.us' or args.provider == 'danbooru':
        print_err('Searching for images...')
        url = 'https://danbooru.donmai.us/post/index.json?tags='
        query = parse.quote_plus(' '.join(args.tag))
        headers = {'User-Agent': 'dandl/1.0'} # Danbooru blocks non-UA'd reqs
        req = request.Request(url + query, None, headers)
        res = request.urlopen(req)
        root = json.loads(res.read().decode("utf-8"))

        limit = args.limit
        if not limit and config['DEFAULT'].get('limit'):
            limit = int(config['DEFAULT'].get('limit'))
        if not limit:
            limit = 1e7
        page = 1
        while len(images) < int(limit):
            count = add_danbooru_posts(root, url)
            if not count:
                break
            page += 1
            req = request.Request(url + query + '&page=' + str(page), None, headers)
            res = request.urlopen(req)
            root = json.loads(res.read().decode("utf-8"))
            if not root:
                break
            time.sleep(0.5)

    elif args.provider == 'safebooru.org' or args.provider == 'safebooru':
        print_err('Searching for images...')
        url = 'https://safebooru.org/index.php?page=dapi&s=post&q=index&'
        query = parse.quote_plus(' '.join(args.tag))
        req = request.urlopen(url + query)
        root = ET.fromstring(req.read())

        limit = args.limit
        if not limit and config['DEFAULT'].get('limit'):
            limit = int(config['DEFAULT'].get('limit'))
        if not limit:
            limit = root.get('count')
        while len(images) < int(limit):
            count = add_gelbooru_posts(root, url)
            if not count:
                break
            req = request.urlopen(url + query + '&offset=' + str(len(images)))
            root = ET.fromstring(req.read())
            time.sleep(0.5)

    elif args.provider == 'rule34.paheal.net' or args.provider == 'r34':
        print_err('Searching for images...')
        xmlns = {'media': 'http://search.yahoo.com/mrss',
                 'atom': 'http://www.w3.org/2005/Atom'}

        url = 'https://rule34.paheal.net/rss/images/'
        tags = parse.quote(' '.join(args.tag))
        req = request.urlopen(url + tags + '/1')
        root = ET.fromstring(req.read())

        limit = args.limit
        if not limit and config['DEFAULT'].get('limit'):
            limit = int(config['DEFAULT'].get('limit'))
        if not limit:
            limit = 1e7

        while len(images) < int(limit):
            next_pg = None
            channel = root.find('channel')
            count = add_shimmie_posts(channel, url, xmlns)
            if not count:
                break
            for link in channel.findall('atom:link', xmlns):
                if link.get('rel') == 'next':
                    next_pg = parse.urljoin(url, link.get('href'))
                    time.sleep(0.5)
                    req = request.urlopen(next_pg)
                    root = ET.fromstring(req.read())
                    break
            if not next_pg:
                break

    elif args.provider == 'rule34.xxx' or args.provider == 'r34x':
        print_err('Searching for images...')
        url = 'https://rule34.xxx/index.php?page=dapi&s=post&q=index&'
        query = parse.quote_plus(' '.join(args.tag))
        req = request.urlopen(url + query)
        root = ET.fromstring(req.read())

        limit = args.limit
        if not limit and config['DEFAULT'].get('limit'):
            limit = int(config['DEFAULT'].get('limit'))
        if not limit:
            limit = root.get('count')
        while len(images) < int(limit):
            count = add_gelbooru_posts(root, url)
            if not count:
                break
            req = request.urlopen(url + query + '&offset=' + str(len(images)))
            root = ET.fromstring(req.read())
            time.sleep(0.5)

    elif args.provider == 'shimmie.katawa-shoujo.com' or args.provider == 'ks':
        print_err('Searching for images...')
        xmlns = {'media': 'http://search.yahoo.com/mrss/',
                 'atom': 'http://www.w3.org/2005/Atom'}

        url = 'https://shimmie.katawa-shoujo.com/rss/images/'
        tags = parse.quote(' '.join(args.tag))
        req = request.urlopen(url + tags + '/1')
        root = ET.fromstring(req.read())

        limit = args.limit
        if not limit and config['DEFAULT'].get('limit'):
            limit = int(config['DEFAULT'].get('limit'))
        if not limit:
            limit = 1e7

        while len(images) < int(limit):
            next_pg = None
            channel = root.find('channel')
            count = add_shimmie_posts(channel, url, xmlns)
            if not count:
                break
            for link in channel.findall('atom:link', xmlns):
                if link.get('rel') == 'next':
                    next_pg = parse.urljoin(url, link.get('href'))
                    time.sleep(0.5)
                    req = request.urlopen(next_pg)
                    root = ET.fromstring(req.read())
                    break
            if not next_pg:
                break

    else:
        print_err('The specified provider is not supported.')

    # Download images
    print_err('%u images found' % len(images))
    for image in images:
        print(image['url'])
        if not args.nd:
            ireq = request.urlopen(image['url'])
            basename = image['name']
            if len(basename) > max_filename_len:
                _, ext = os.path.splitext(basename)
                basename = textwrap.shorten(basename, width=max_filename_len, placeholder=ext)
            filename = imgdir.rstrip(os.sep) + os.sep + basename
            if not os.path.isfile(filename):
                with open(filename, 'xb') as file:
                    file.write(ireq.read())
            time.sleep(0.5)

def add_danbooru_posts(response, url):
    """
    Add images from a Danbooru JSON response
    """
    count = 0
    for entry in response:
        if not 'file_url' in entry:
            return
        file_url = entry['file_url']
        file_url = parse.urljoin(url, file_url)
        images.append({
            'id': entry['id'],
            'url': file_url,
            'name': parse.unquote(file_url.split('/')[-1])
        })
        count = count + 1
    return count

def add_gelbooru_posts(root, url):
    """
    Add images from a Gelbooru XML feed
    """
    count = 0
    for post in root.findall('post'):
        file_url = parse.urljoin(url, post.get('file_url'))
        images.append({
            'id': post.get('id'),
            'url': file_url,
            'name': parse.unquote(file_url.split('/')[-1])
        })
        count = count + 1
    return count

def add_shimmie_posts(channel, url, xmlns):
    """
    Add images from a Shimmie RSS 2.0 feed
    """
    count = 0
    for image in channel.findall('item'):
        file_url = image.find('media:content', xmlns).get('url')
        file_url = parse.urljoin(url, file_url)
        images.append({
            'id': image.find('guid').text.split('/')[-1],
            'url': file_url,
            'name': parse.unquote(file_url.split('/')[-1])
        })
        count = count + 1
    return count

def print_err(*args, **kwargs):
    """
    Print a string to stderr
    """
    print(*args, file=stderr, **kwargs)

# Run application
if __name__ == '__main__':
    main()
