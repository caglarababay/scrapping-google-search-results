#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
from urllib import parse

import requests
from bs4 import BeautifulSoup


class ContentNotScrapedException(Exception):
    pass


class GoogleCrawler:
    def __init__(self, url, is_mobile=0):
        self._url = url
        self._is_mobile = is_mobile
        self.user_agent = self._get_user_agent()
        self.__results = []

    def _get_html_content(self):
        """
        getting google search result page's html content via bs4
        :return:
        html context or exception
        """
        try:
            r = requests.get(url=self._url, headers=self.user_agent)
            if r.ok:
                return BeautifulSoup(r.content, 'html.parser')
        except:
            raise ContentNotScrapedException("could not load html content !")

    def _get_user_agent(self):
        """
        getting user agent for web or mobile response
        :return:
        user agent as like that mobile or desktop
        """
        if self._is_mobile == 1:
            return {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'}
        else:
            return {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

    def _parse_mobile_content(self, html_text):
        """
        getting parsed html content for mobile devices
        :param html_text: google search result (bs4 context)
        :return: list as type (ad or organic) and url
        """
        groups = html_text.find('div', {'id': 'main'}).findAll('div', recursive=False)
        for g in groups:
            for _g in g.findAll('div', {'class': 'mnr-c'}):
                item = _g.find('a')
                if item and item.get('href'):
                    __url = self._get_target_url(item['href'])
                    if __url is None:
                        continue

                    if item.get('data-rw'):
                        self.__results.append(['ad', self._get_target_url(__url)])
                    else:
                        self.__results.append(['organic', __url])

    def _parse_web_content(self, html_text):
        """
        getting parsed html content for desktop devices
        :param html_text: google search result (bs4 context)
        :return: list as type (ad or organic) and url
        """
        groups = html_text.find('div', {'id': 'center_col'}).findAll('div', recursive=False)
        for g in groups:
            if 'med' in g.get('class', []):
                for _g in g.findAll('div', {'class': 'g'}):
                    for _r in _g.findAll('div', {'class': 'r'}):
                        __url = self._get_target_url(_r.find('a')['href'])
                        if __url:
                            self.__results.append(['organic', __url])

            if g.get('id') in ['taw', 'bottomads']:
                if g.find('ol'):
                    for _g in g.find('ol').findAll('li', recursive=False):
                        __url = self._get_target_url(
                            _g.find('div', {'class': 'ad_cclk'}).findAll('a', recursive=False)[1]['href'])
                        if __url:
                            self.__results.append(['ad', __url])

    def _get_target_url(self, url_str):
        """
        getting redirected loop url
        :param url_str: url
        :return: redirected loop url
        """
        if '/aclk?' in url_str or '/search?' in url_str:
            __r = requests.get('https://www.google.com{0}'.format(url_str), headers=self._get_user_agent())
            if len(__r.history) == 0:
                return None

            last_redirect_url = __r.history[-1].url
            parsed = parse.parse_qs(parse.urlparse(last_redirect_url).query)

            if parsed.get('adurl'):
                return parsed['adurl'][0]

            if 'https://ad.doubleclick.net' in last_redirect_url:
                url2 = urllib.parse.unquote(last_redirect_url)
                return url2.split(';')[-1].split('?')[1]

            if '/aclk?' in last_redirect_url:
                return None

            return last_redirect_url

        return url_str

    def run(self):
        """
        runner.
        :return:
        """

        html_text = self._get_html_content()

        try:
            if self._is_mobile == 1:
                self._parse_mobile_content(html_text)
            else:
                self._parse_web_content(html_text)
        except Exception as e:
            print("content not parsed -> ", e)

        return self.__results


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    # -url GOOGLE_SEARCH_URL -m 1/0
    parser.add_argument("-url", "--url", help="Google Search URL", required=True)
    parser.add_argument("-m", "--is_mobile", help="Is mobile?", type=int, default=0)

    args = parser.parse_args()

    google_crawler = GoogleCrawler(args.url, args.is_mobile)
    for rec in google_crawler.run():
        print('{0}, {1}'.format(rec[0], rec[1]))
