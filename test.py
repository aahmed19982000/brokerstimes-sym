import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404
from tasks.models import Task


def get_h1_words(url,):


    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.content, "html.parser")
        h1 = soup.find("h1")
        if h1:
            return h1.text.split()
        return []
    except Exception as e:
        print(f"❌ خطأ في تحميل {url}: {e}")
        return []

def search_sitemap_by_keywords(sitemap_url, query, min_slug_matches=1, min_h1_matches=0):
    response = requests.get(sitemap_url, timeout=10)
    if response.status_code != 200:
        print("❌ لا يمكن تحميل الـ sitemap")
        return []

    root = ET.fromstring(response.content)
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

    keywords = query.split()
    results = []

    for loc in root.iter(f"{namespace}loc"):
        url = loc.text.strip()
        decoded_url = unquote(url)

        # تقسيم الـ slug لكلمات منفصلة
        slug_words = decoded_url.split("/")[-1].split("-")

        slug_match_count = sum(1 for word in keywords if word in slug_words)

        if slug_match_count >= min_slug_matches:
            h1_words = get_h1_words(url)
            h1_match_count = sum(1 for word in keywords if word in h1_words)
            if h1_match_count >= min_h1_matches:
                results.append((decoded_url, slug_match_count, h1_match_count))

    # ترتيب النتائج حسب أعلى تطابق في H1 أولًا ثم في slug
    results.sort(key=lambda x: (x[2], x[1]), reverse=True)
    return results

# مثال استخدام
sitemap = "https://tdqiq.com/xml/article-sitemap.xml"
query = Task.objects.first().article_title

matches = search_sitemap_by_keywords(sitemap, query, min_slug_matches=1, min_h1_matches=1)

for url, slug_score, h1_score in matches:
    print(f"{url}  ➤ تطابق slug: {slug_score}/{len(query.split())}, تطابق H1: {h1_score}/{len(query.split())}")
import os
import django
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from bs4 import BeautifulSoup

# تهيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # عدل الاسم هنا
django.setup()

from tasks.models import Task


def get_h1_words(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.content, "html.parser")
        h1 = soup.find("h1")
        if h1:
            return h1.text.split()
        return []
    except Exception as e:
        print(f"❌ خطأ في تحميل {url}: {e}")
        return []


def search_sitemap_by_keywords(sitemap_url, query, min_slug_matches=1, min_h1_matches=0):
    response = requests.get(sitemap_url, timeout=10)
    if response.status_code != 200:
        print("❌ لا يمكن تحميل الـ sitemap")
        return []

    root = ET.fromstring(response.content)
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

    keywords = query.split()
    results = []

    for loc in root.iter(f"{namespace}loc"):
        url = loc.text.strip()
        decoded_url = unquote(url)

        # تقسيم الـ slug لكلمات منفصلة
        slug_words = decoded_url.split("/")[-1].split("-")

        slug_match_count = sum(1 for word in keywords if word in slug_words)

        if slug_match_count >= min_slug_matches:
            h1_words = get_h1_words(url)
            h1_match_count = sum(1 for word in keywords if word in h1_words)
            if h1_match_count >= min_h1_matches:
                results.append((decoded_url, slug_match_count, h1_match_count))

    # ترتيب النتائج حسب أعلى تطابق في H1 أولًا ثم في slug
    results.sort(key=lambda x: (x[2], x[1]), reverse=True)
    return results


# مثال استخدام
sitemap = "https://tdqiq.com/xml/article-sitemap.xml"
query = Task.objects.first().article_title

matches = search_sitemap_by_keywords(sitemap, query, min_slug_matches=1, min_h1_matches=1)

for url, slug_score, h1_score in matches:
    print(f"{url}  ➤ تطابق slug: {slug_score}/{len(query.split())}, تطابق H1: {h1_score}/{len(query.split())}")
