import json
import os
import re
import shutil

import requests
from bs4 import BeautifulSoup


class Scraper(object):
    pages = 1000
    stop_if_existed = True

    existing_data = None
    data = {}

    def __init__(self, incremental=True):
        self.incremental = incremental
        self.post_images_dir = self.get_post_images_dir()

    def scrape(self):
        if self.incremental and self.existing_data is None:
            self.load_existing_data()
        self.data = self.existing_data or {}

        base_url = 'https://warhammer-community.com'
        for i in range(self.pages):
            url = '{base_url}?pg={i}'.format(base_url=base_url, i=i)
            print('Fetching {}'.format(url))
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                posts = soup.findAll('a', {'class': 'post-feed__post'})
                print('  Found {} posts'.format(len(posts)))
                if not posts:
                    print('  No posts on page. Stopping')
                    break
                any_existed = False
                for post in posts:
                    existed = self.handle_post(post)
                    if existed:
                        any_existed = True
                        break
                if any_existed and self.stop_if_existed:
                    print('  Stopping')
                    break
            else:
                print('  Failed lookup. Stopping')
                break
        self.dump_data()

    def handle_post(self, post):
        href = post.attrs.get('href')
        if self.data.get(href):
            print('      Post {} already found'.format(href))
            return True
        print('    Storing post {}'.format(href))
        image_url = post.find('img').attrs.get('src')
        image_filename = image_url.split('uploads/')[1]
        self.data[href] = {
            'title': post.attrs.get('title'),
            'date': re.search(r'\d{4}/\d{2}/\d{2}', href).group(),
            'image': image_filename,
        }
        print('    Fetching image {}'.format(image_url))
        image_response = requests.get(image_url, stream=True)
        image_path = os.path.join(self.post_images_dir, image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, 'wb') as f:
            shutil.copyfileobj(image_response.raw, f)
        del image_response
        print('      Saved as {}'.format(image_filename))
    
    def load_existing_data(self):
        posts_path = self.get_data_file_path()
        if not os.path.exists(posts_path):
            return
        with open(posts_path, 'r') as f:
            try:
                data = f.read()
                self.existing_data = json.loads(data)
            except json.JSONDecodeError:
                self.existing_data = {}
        print('Loaded {} posts from disk'.format(len(self.existing_data.keys())))
    
    def dump_data(self):
        print('Writing {} posts to disk'.format(len(self.data.keys())))
        posts_path = self.get_data_file_path()
        with open(posts_path, 'w') as f:
            f.write(json.dumps(self.data))
        print('Success')

    @staticmethod
    def get_data_file_path():
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        return os.path.join(data_dir, 'posts.json')

    @staticmethod
    def get_post_images_dir():
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'post_images')

if __name__ == '__main__':
    scraper = Scraper()
    scraper.scrape()
