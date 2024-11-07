import os
import json
from urllib.parse import urljoin

import requests
from lxml.html import fromstring
import requests.cookies
import time
import random


os.environ['HTTP_PROXY'] = os.environ['HTTPS_PROXY'] = 'http://localhost:10809'

CONFIG = {
    'cookie': '''jp_chatplus_vtoken=gfr9v2pw4s9524kbmo6sab404376; _gid=GA1.2.1958437104.1730469177; languageModalShowed=true; AMP_MKTG_b991fc5cce=JTdCJTdE; i18n_redirected=zh-cn; _f_v_k_1=a30405cfece3aa478b07671a364288dc0cde1bf0f508e61fe1d6fb6c85b11e2e; _session_id=2794a784b610c440daa0aaf645ad26fa0592e8903fa13c257773834e986ebf88; _im_vid=01JBM00JPRM3GYWKEDXTR2YFA4; _im_uid.3929=h.ebae80fbf04e2b2e; _ga_M9CHW7TDWC=GS1.1.1730469185.2.0.1730469187.0.0.0; _ga_5D88MN5EKL=GS1.1.1730469176.2.1.1730469479.53.0.0; _ga=GA1.2.1819708646.1728973226; _gat_UA-76513494-1=1; _ga_FVSMH3KV9Z=GS1.2.1730469176.2.1.1730469479.0.0.0; AMP_b991fc5cce=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjJjYzQ1ZWIyOS0xNGM1LTQ5NGUtYTUxZC0yM2M4YmFlOWQzYmYlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzMwNDY5MTc3NTczJTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTczMDQ2OTQ4MDE0NCUyQyUyMmxhc3RFdmVudElkJTIyJTNBMTglMkMlMjJwYWdlQ291bnRlciUyMiUzQTE0JTdE''',
    'csrf-token': 'Ual4GsGUfvDwQcmMzGnL7aEAptSgLhl55taTav3OkG_HsSDOFHyo0wclrlEv6pRb681XUEmZ0q9Q21h94knYrg'
}


class FantiaDL(object):
    def __init__(self, delay: int = 2) -> None:
        self.session = s = requests.Session()
        s.headers.update(
            {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'})
        s.headers.setdefault('cookie', CONFIG['cookie'])

        self.delay = delay

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

                time.sleep(random.randint(1, self.delay))

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


# 只保留 mp4
with open('1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

    with open('1.txt', 'w') as f:
        f.write('\r\n'.join([item['download_uri'] for item in data if item['filename'].endswith('.mp4')]))


if __name__ == '__main__':
    content_key = ['title', 'id', 'download_uri', 'filename']
    content_list = []

    for info in FantiaDL().get_user_posts_info(1, 1, 200):
        post = info['post']
        content_info = {}

        for content in post['post_contents']:
            if not content.get('download_uri', ''):
                continue
            
            for k in content_key:
                content_info[k] = content[k]

            content_info['download_uri'] = urljoin('https://fantia.jp', content_info['download_uri'])

        if content_info:
            content_list.append(content_info)
            print(content_info)

    
    with open('1.json', 'w') as f:
        json.dump(content_list, f)

    with open('1.txt', 'w') as f:
        f.write('\r\n'.join([item['download_uri'] for item in content_list]))