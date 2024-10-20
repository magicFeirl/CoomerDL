import os
import json
from urllib.parse import urljoin

import requests
from lxml.html import fromstring
import requests.cookies


os.environ['HTTP_PROXY'] = os.environ['HTTPS_PROXY'] = 'http://localhost:10809'

CONFIG = {
    'cookie': '''your cookie here''',
    'csrf-token': 'csrf token here'
}


class FantiaDL(object):
    def __init__(self) -> None:
        self.session = s = requests.Session()
        s.headers.update(
            {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'})
        s.headers.setdefault('cookie', CONFIG['cookie'])

    def _parse_post_id(self, uid: int, page: int):
        url = f'https://fantia.jp/fanclubs/{uid}/posts'

        html = self.session.get(url, params={
            'page': page
        }).text

        selector = fromstring(html)
        ret = selector.xpath('//a[@class="link-block"]/@href')

        if not ret:
            if page == 1:
              raise ValueError(f'无法找到用户 {uid} 第 {page} 页 Post id')
            else:
                return None
            
        return [s[s.rfind('/')+1:] for s in ret]

    def get_user_posts_info(self, uid: int, begin: int = 1, end: int = 2):
        for page in range(begin, end):
            id_list = self._parse_post_id(uid, page)

            if not id_list:
                return 
            
            for id in id_list:
                print(f'Get post info: {id}')

                yield self.get_post_info(id)

    def get_post_info(self, post_id: int):
        url = f'https://fantia.jp/api/v1/posts/{post_id}'
        resp = self.session.get(url, headers={
            'referer': f'https://fantia.jp/posts/{post_id}',
            "x-requested-with": "XMLHttpRequest",
            'x-csrf-token': CONFIG['csrf-token']
        })

        try:
            return resp.json()
        except json.JSONDecodeError:
            print('Decode json error:', resp.text)


if __name__ == '__main__':
    content_key = ['title', 'id', 'download_uri', 'filename']
    for info in FantiaDL().get_user_posts_info(1111, 1, 20):
        post = info['post']
        content_info = {}

        for content in post['post_contents']:
            if 'download_uri' not in content:
                continue
            
            for k in content_key:
                try:
                  content_info[k] = content[k]
                except KeyError:
                    print(k, 'doesnt exists')
            content_info['download_uri'] = urljoin('https://fantia.jp', content_info['download_uri'])

        print(content_info)
