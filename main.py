import os
import re
from enum import Enum
from typing import Callable
from urllib.parse import urlparse, urljoin
from collections import defaultdict
import json


import requests



os.environ['HTTP_PROXY'] = os.environ['HTTPS_PROXY'] = 'http://localhost:1081'


class APIType(str, Enum):
    coomer = 'coomer'
    kemono = 'kemono'


class CoomerDL(object):
    def __init__(self, api_type: APIType) -> None:
        base_url = {
            APIType.coomer: ('https://coomer.su/api/v1', 'https://n3.coomer.su/data/'),
            APIType.kemono: ('https://kemono.su/api/v1', 'https://n4.kemono.su/data/')
        }

        self.api_base_url, self.file_base_url = base_url[api_type]


    def get_creator_posts(self, service: str, creator_id: str, begin: int=0, end: int=1):

        for page in range(begin, end):
            api = f'{self.api_base_url}/{service}/user/{creator_id}'
            
            result = requests.get(api, params={
                'o': page * 50
            }).json()

            
            if not result:
                return
            
            yield result

    def _iter_item(self, page_cb: Callable, **kwargs):

        for page, data in enumerate(self.get_creator_posts(**kwargs)):
            page_cb(page, data)

            for item in data:
                yield item

    def get_file_urls(self,  **kwargs):
        mp4list = []

        for item in self._iter_item(lambda p, d: print(p), **kwargs):
            for att in item['attachments']:
                if att['path'].endswith('.mp4'):
                    mp4list.append(urljoin(self.file_base_url, att['path']))

        return mp4list
    
    def get_links(self, **kwargs):
        def _sort(url: str):
            if 'drive.google' in url:
                return -1
            elif 'mega.gz' in url:
                return 0
            else:
                return 1
            
        posts = defaultdict(list)

        for item in self._iter_item(lambda p, d: print(p), **kwargs):
            content, id = item['content'], item['id']
            
            for url in re.findall(r'href="(.+?)"', content):
                posts[id].append(url)

            posts[id].sort(key=_sort)

        return posts




# example code
# You can download file with aria2 lately
dl = CoomerDL(APIType.kemono)
# links = dl.get_links(service='fanbox', creator_id='7011890', end=10000)
urls = dl.get_file_urls(service='fanbox', creator_id='7011390', end=10000)

with open('kusorucg.txt', 'w') as f:
    f.write(os.linesep.join(urls))


# dl = CoomerDL(APIType.coomer)
# # urls = dl.get_file_urls(service='fansly', creator_id='114514', end=10000)

# with open('henkawa.json', 'w') as f:
#     json.dump(posts, f)

