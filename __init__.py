"""
أدوات المساعد الصوتي آدم
======================

هذا المجلد يحتوي على جميع أدوات المساعد:
- time.py: أداة معرفة الوقت والتاريخ
- web_search.py: أدوات البحث على الإنترنت
- system_control.py: أدوات التحكم في النظام

المطور: المساعد الصوتي آدم
"""

from .time import get_time
from .web_search import search_google, get_website_info, search_and_read, get_news
from .system_control import (
    play_music, open_app, show_system_info, list_processes, close_program,
    create_new_folder, list_files, shutdown_computer, restart_computer,
    find_files, open_website, set_volume
)

__version__ = "1.0.0"
__author__ = "المساعد الصوتي آدم"

# قائمة جميع الأدوات المتاحة
__all__ = [
    # أدوات الوقت
    'get_time',

    # أدوات البحث والإنترنت
    'search_google',
    'get_website_info',
    'search_and_read',
    'get_news',

    # أدوات التحكم في النظام
    'play_music',
    'open_app',
    'show_system_info',
    'list_processes',
    'close_program',
    'create_new_folder',
    'list_files',
    'shutdown_computer',
    'restart_computer',
    'find_files',
    'open_website',
    'set_volume'
]


def get_available_tools():
    """إرجاع قائمة بجميع الأدوات المتاحة"""
    return {
        'time_tools': ['get_time'],
        'web_tools': ['search_google', 'get_website_info', 'search_and_read', 'get_news'],
        'system_tools': [
            'play_music', 'open_app', 'show_system_info', 'list_processes',
            'close_program', 'create_new_folder', 'list_files', 'shutdown_computer',
            'restart_computer', 'find_files', 'open_website', 'set_volume'
        ]
    }