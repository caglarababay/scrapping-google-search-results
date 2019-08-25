#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
from urllib import parse

import requests
from bs4 import BeautifulSoup


import argparse
parser = argparse.ArgumentParser()

# -url GOOGLE_SEARCH_URL -m 1/0
parser.add_argument("-url", "--url", help="Google Search URL", required=True)
parser.add_argument("-m", "--is_mobile", help="Is mobile?", type=int, default=0)

def scrape(url=None, is_mobile=0):
    __results = []
    if url:
        __args_str = '-url {0} -m {1}'.format(url, is_mobile)
        args = parser.parse_args(__args_str.split())
        args.is_mobile = is_mobile
    else:
        args = parser.parse_args()

    if args.is_mobile == 1:
        USER_AGENT = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'}
    else:
        USER_AGENT = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

    r = requests.get(url=args.url, headers= USER_AGENT)
    html_text = BeautifulSoup(r.content, 'html.parser')

    def get_target_url(url_str):
        if '/aclk?' in url_str or '/search?' in url_str:
            __r = requests.get('https://www.google.com{0}'.format(url_str), headers= USER_AGENT)
            if len(__r.history) == 0:
                return None

            last_redirect_url = __r.history[-1].url
            parsed = parse.parse_qs(parse.urlparse(last_redirect_url).query)

            if not parsed.get('adurl') and 'https://ad.doubleclick.net' in last_redirect_url:
                url2 = urllib.parse.unquote(last_redirect_url)
                return url2.split(';')[-1].split('?')[1]

            return parsed['adurl'][0]

        return url_str

    if args.is_mobile == 1:
        groups = html_text.find('div', {'id': 'main'}).findAll('div', recursive=False)
        for g in groups:
            for _g in g.findAll('div', {'class': 'mnr-c'}):
                item = _g.find('a')
                if item and item.get('href'):
                    __url = get_target_url(item['href'])
                    if __url and item.get('data-rw'):
                        __results.append(['ad', __url])
                    else:
                        __results.append(['organic', __url])

    else:
        groups = html_text.find('div', {'id': 'center_col'}).findAll('div', recursive=False)
        for g in groups:
            if 'med' in g.get('class', []):
                for _g in g.findAll('div', {'class': 'g'}):
                    for _r in _g.findAll('div', {'class': 'r'}):
                        __url = get_target_url(_r.find('a')['href'])
                        if __url:
                            __results.append(['organic', __url])

            if g.get('id') in ['taw', 'bottomads']:
                if g.find('ol'):
                    for _g in g.find('ol').findAll('li', recursive=False):
                        __url = get_target_url(_g.find('div', {'class': 'ad_cclk'}).findAll('a', recursive=False)[1]['href'])
                        if __url:
                            __results.append(['ad', __url])

    return __results

if __name__ == '__main__':
    for rec in scrape():
        print('{0}, {1}'.format(rec[0], rec[1]))
