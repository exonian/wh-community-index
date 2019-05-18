import json
import os

from jinja2 import Environment

template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Warhammer Community Index</title>
    <link rel="stylesheet" href="css/style.css">
</head>

<body id="home">

    <h1>News and Features</h1>
    {% for url, post in posts %}
        <a href="{{ url }}" title="{{ post.title }}">
            <h2>{{ post.title }}</h2>
            <p>{{ post.date }}</p>
            <img src="{{ post.image }}" title="{{ post.title }}">
        </a>
    {% endfor %}

</body>
</html>
"""

def build():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    data_path = os.path.join(data_dir, 'posts.json')
    with open(data_path, 'r') as f:
        data = f.read()
        posts = json.loads(data)
        posts = sorted(posts.items(), key=lambda x: x[1]['date'], reverse=True)

    html = Environment().from_string(template).render(posts=posts)
    print(html)

if __name__ == '__main__':
    build()
