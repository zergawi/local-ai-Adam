# tools/web_search.py

import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
import urllib.parse
import json
import time


class WebSearcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def google_search(self, query, num_results=5, lang='ar'):
        """البحث في Google وإرجاع النتائج"""
        try:
            # تشفير الاستعلام
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://www.google.com/search?q={encoded_query}&hl={lang}&num={num_results}"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            results = []

            # البحث عن نتائج البحث
            search_results = soup.find_all('div', class_='g')

            for result in search_results[:num_results]:
                title_elem = result.find('h3')
                link_elem = result.find('a')
                snippet_elem = result.find('span', class_=['aCOpRe', 'st'])

                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    if link.startswith('/url?q='):
                        link = urllib.parse.unquote(link.split('/url?q=')[1].split('&')[0])

                    if link.startswith('http'):
                        results.append({
                            'title': title,
                            'link': link,
                            'snippet': snippet
                        })

            return results

        except Exception as e:
            print(f"خطأ في البحث في Google: {e}")
            return []

    def get_website_content(self, url, max_chars=2000):
        """استخراج محتوى موقع ويب"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # إزالة العناصر غير المرغوب فيها
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()

            # البحث عن المحتوى الرئيسي
            main_content = soup.find('main') or soup.find('article') or soup.find('div',
                                                                                  class_=['content', 'main-content',
                                                                                          'post-content'])

            if main_content:
                text = main_content.get_text(strip=True, separator=' ')
            else:
                text = soup.get_text(strip=True, separator=' ')

            # تنظيف النص وتحديد الطول
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            clean_text = ' '.join(lines)

            if len(clean_text) > max_chars:
                clean_text = clean_text[:max_chars] + "..."

            return clean_text

        except Exception as e:
            print(f"خطأ في استخراج محتوى الموقع {url}: {e}")
            return f"لم أتمكن من الوصول إلى محتوى الموقع: {str(e)}"


# إنشاء مثيل من فئة البحث
web_searcher = WebSearcher()


@tool
def search_google(query: str, num_results: int = 3) -> str:
    """البحث في Google عن المعلومات. استخدم هذه الأداة للبحث عن أي معلومات على الإنترنت."""
    try:
        results = web_searcher.google_search(query, num_results)

        if not results:
            return f"لم أجد نتائج للبحث عن: {query}"

        response = f"نتائج البحث عن '{query}':\n\n"

        for i, result in enumerate(results, 1):
            response += f"{i}. {result['title']}\n"
            if result['snippet']:
                response += f"   {result['snippet']}\n"
            response += f"   الرابط: {result['link']}\n\n"

        return response

    except Exception as e:
        return f"خطأ في البحث: {str(e)}"


@tool
def get_website_info(url: str) -> str:
    """قراءة محتوى موقع ويب معين. استخدم هذه الأداة لقراءة محتوى صفحة ويب محددة."""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        content = web_searcher.get_website_content(url)
        return f"محتوى الموقع {url}:\n\n{content}"

    except Exception as e:
        return f"خطأ في قراءة الموقع: {str(e)}"


@tool
def search_and_read(query: str, read_first: bool = True) -> str:
    """البحث في Google وقراءة أول نتيجة تلقائياً. مفيد للحصول على معلومات مفصلة حول موضوع معين."""
    try:
        # البحث أولاً
        results = web_searcher.google_search(query, 3)

        if not results:
            return f"لم أجد نتائج للبحث عن: {query}"

        response = f"بحثت عن '{query}' ووجدت:\n\n"

        if read_first and results:
            # قراءة أول نتيجة
            first_result = results[0]
            response += f"العنوان: {first_result['title']}\n"
            response += f"الرابط: {first_result['link']}\n\n"

            content = web_searcher.get_website_content(first_result['link'])
            response += f"المحتوى:\n{content}\n\n"

            # عرض باقي النتائج
            if len(results) > 1:
                response += "نتائج أخرى:\n"
                for i, result in enumerate(results[1:], 2):
                    response += f"{i}. {result['title']}\n"
                    response += f"   {result['link']}\n"
        else:
            # عرض النتائج فقط
            for i, result in enumerate(results, 1):
                response += f"{i}. {result['title']}\n"
                if result['snippet']:
                    response += f"   {result['snippet']}\n"
                response += f"   {result['link']}\n\n"

        return response

    except Exception as e:
        return f"خطأ في البحث والقراءة: {str(e)}"


@tool
def get_news(topic: str = "أخبار اليوم", language: str = "ar") -> str:
    """البحث عن آخر الأخبار حول موضوع معين."""
    try:
        if language == "ar":
            search_query = f"{topic} أخبار اليوم"
        else:
            search_query = f"{topic} news today"

        results = web_searcher.google_search(search_query, 5)

        if not results:
            return f"لم أجد أخباراً حول: {topic}"

        response = f"آخر الأخبار حول '{topic}':\n\n"

        for i, result in enumerate(results, 1):
            response += f"📰 {result['title']}\n"
            if result['snippet']:
                response += f"   {result['snippet']}\n"
            response += f"   المصدر: {result['link']}\n\n"

        return response

    except Exception as e:
        return f"خطأ في جلب الأخبار: {str(e)}"