import logging
import time
import json
import asyncio
import edge_tts
import os
import tempfile
import uuid
from dotenv import load_dotenv
import speech_recognition as sr
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
import pygame
import re

# استيراد الأدوات مباشرة - النسخة المحسنة
from tools.time import get_time
from tools.web_search import search_google, get_website_info, search_and_read, get_news
from tools.system_control import (
    play_music, open_app, show_system_info, list_processes, close_program,
    create_new_folder, list_files, shutdown_computer, restart_computer,
    find_files, open_website, set_volume
)

load_dotenv()


# إعدادات الميكروفون المحسنة
def load_mic_config():
    """تحميل إعدادات الميكروفون من الملف أو استخدام الافتراضية"""
    try:
        if os.path.exists('mic_config.json'):
            with open('mic_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                print("✅ تم تحميل إعدادات الميكروفون من mic_config.json")
                return config
    except Exception as e:
        print(f"⚠️ خطأ في تحميل إعدادات الميكروفون: {e}")

    # الإعدادات الافتراضية
    return {
        "microphone_index": 1,  # جرب الميكروفون الثاني
        "energy_threshold": 300,
        "dynamic_energy_threshold": True,
        "pause_threshold": 0.8,
        "timeout": 8,
        "phrase_time_limit": 4
    }


# تحميل إعدادات الميكروفون
MIC_CONFIG = load_mic_config()
MIC_INDEX = MIC_CONFIG.get("microphone_index", 1)
TRIGGER_WORD = "ادم"
CONVERSATION_TIMEOUT = 30

logging.basicConfig(level=logging.INFO)

# إعداد speech recognizer مع الإعدادات المحسنة
recognizer = sr.Recognizer()
recognizer.energy_threshold = MIC_CONFIG.get("energy_threshold", 300)
recognizer.dynamic_energy_threshold = MIC_CONFIG.get("dynamic_energy_threshold", True)
recognizer.pause_threshold = MIC_CONFIG.get("pause_threshold", 0.8)

# إنشاء مجلد للملفات الصوتية
AUDIO_DIR = "audio_files"
if not os.path.exists(AUDIO_DIR):
    try:
        os.makedirs(AUDIO_DIR)
        print(f"✅ تم إنشاء مجلد الملفات الصوتية: {AUDIO_DIR}")
    except Exception as e:
        print(f"⚠️ لم يتم إنشاء مجلد الملفات الصوتية: {e}")
        AUDIO_DIR = tempfile.gettempdir()

# تهيئة pygame mixer
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    print("✅ تم تهيئة pygame mixer بنجاح")
except Exception as e:
    print(f"❌ خطأ في تهيئة pygame mixer: {e}")


# إعداد الميكروفون مع معالجة أفضل للأخطاء
def setup_microphone():
    """إعداد الميكروفون مع معالجة محسنة"""
    global mic

    try:
        print(f"🎤 محاولة إعداد الميكروفون {MIC_INDEX}...")

        # عرض الميكروفونات المتاحة
        microphones = sr.Microphone.list_microphone_names()
        print(f"🎙️ الميكروفونات المتاحة: {len(microphones)}")

        if MIC_INDEX < len(microphones):
            print(f"🎯 الميكروفون المختار: {MIC_INDEX} - {microphones[MIC_INDEX]}")

        mic = sr.Microphone(device_index=MIC_INDEX)

        with mic as source:
            print("🔧 جاري ضبط الميكروفون للضوضاء المحيطة...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print(f"✅ تم ضبط الميكروفون - مستوى الطاقة: {recognizer.energy_threshold}")

        return True

    except Exception as e:
        print(f"❌ خطأ في إعداد الميكروفون {MIC_INDEX}: {e}")

        # محاولة الميكروفون الافتراضي
        try:
            print("🔄 محاولة الميكروفون الافتراضي...")
            mic = sr.Microphone()

            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"✅ تم إعداد الميكروفون الافتراضي - مستوى الطاقة: {recognizer.energy_threshold}")

            return True

        except Exception as e2:
            print(f"❌ فشل في إعداد الميكروفون الافتراضي: {e2}")
            print("💡 سيتم المتابعة بدون ميكروفون - يمكنك استخدام الكتابة")
            mic = None
            return False


# إعداد الميكروفون
mic_available = setup_microphone()

# تكوين النموذج
llm = ChatOllama(
    model="command-r7b-arabic",
    reasoning=False,
    temperature=0.1
)


class AdamAssistant:
    """نظام المساعد الذكي آدم مع تنفيذ مباشر للأدوات"""

    def __init__(self):
        # قاموس الأدوات المتاحة
        self.tools = {
            'play_music': play_music,
            'open_app': open_app,
            'show_system_info': show_system_info,
            'list_processes': list_processes,
            'close_program': close_program,
            'create_new_folder': create_new_folder,
            'list_files': list_files,
            'shutdown_computer': shutdown_computer,
            'restart_computer': restart_computer,
            'find_files': find_files,
            'open_website': open_website,
            'set_volume': set_volume,
            'get_time': get_time,
            'search_google': search_google,
            'get_website_info': get_website_info,
            'search_and_read': search_and_read,
            'get_news': get_news
        }

        # خريطة الكلمات المفتاحية للأدوات
        self.keyword_to_tool = {
            # كلمات الموسيقى
            'شغل': self._handle_music_or_app,
            'تشغيل': self._handle_music_or_app,
            'موسيقى': lambda query: self.tools['play_music'](query),
            'أغنية': lambda query: self.tools['play_music'](query),

            # كلمات التطبيقات
            'افتح': self._handle_open_command,
            'فتح': self._handle_open_command,

            # كلمات البحث والإنترنت
            'ابحث': lambda query: self.tools['search_google'](query),
            'بحث': lambda query: self.tools['search_google'](query),
            'أخبار': lambda query="أخبار اليوم": self.tools['get_news'](query),
            'معلومات': self._handle_info_request,

            # كلمات الطقس والحرارة
            'درجة الحرارة': self._handle_weather_request,
            'درجه الحراره': self._handle_weather_request,
            'الحرارة': self._handle_weather_request,
            'الحراره': self._handle_weather_request,
            'الطقس': self._handle_weather_request,
            'طقس': self._handle_weather_request,
            'حرارة': self._handle_weather_request,
            'حراره': self._handle_weather_request,
            'كم درجة': self._handle_weather_request,
            'كم درجه': self._handle_weather_request,

            # كلمات النظام
            'معلومات النظام': lambda: self.tools['show_system_info'](),
            'العمليات': lambda: self.tools['list_processes'](),
            'الوقت': lambda city="بغداد": self.tools['get_time'](city),

            # كلمات الإدارة
            'اطفئ': lambda delay=1: self.tools['shutdown_computer'](delay),
            'اعد تشغيل': lambda delay=1: self.tools['restart_computer'](delay),
            'انشئ مجلد': lambda name, location=".": self.tools['create_new_folder'](name, location),
        }

    def _handle_music_or_app(self, command):
        """معالجة أوامر الموسيقى أو التطبيقات"""
        if any(word in command.lower() for word in ['موسيقى', 'أغنية', 'نغمة']):
            # استخراج اسم الأغنية أو الفنان
            music_query = self._extract_music_query(command)
            return self.tools['play_music'].invoke({"query": music_query})
        else:
            # تطبيق
            app_name = self._extract_app_name(command)
            return self.tools['open_app'].invoke({"app_name": app_name})

    def _handle_open_command(self, command):
        """معالجة أوامر الفتح"""
        if 'موقع' in command.lower():
            url = self._extract_url(command)
            return self.tools['open_website'].invoke({"url": url})
        else:
            app_name = self._extract_app_name(command)
            return self.tools['open_app'].invoke({"app_name": app_name})

    def _handle_weather_request(self, command):
        """معالجة طلبات الطقس ودرجة الحرارة"""
        try:
            # استخراج اسم المدينة من الأمر
            city = self._extract_city_from_command(command)

            # البحث عن معلومات الطقس
            if city:
                weather_query = f"طقس {city} اليوم درجة الحرارة"
            else:
                weather_query = "طقس بغداد اليوم درجة الحرارة"

            print(f"🌤️ البحث عن معلومات الطقس: {weather_query}")
            return self.tools['search_google'](weather_query)

        except Exception as e:
            return f"عذراً، حدث خطأ في البحث عن معلومات الطقس: {str(e)}"

    def _handle_info_request(self, command):
        """معالجة طلبات المعلومات العامة"""
        try:
            # استخراج موضوع البحث
            search_query = command.replace('معلومات', '').replace('عن', '').strip()

            if not search_query:
                search_query = "معلومات عامة"

            print(f"🔍 البحث عن معلومات: {search_query}")
            return self.tools['search_google'](search_query)

        except Exception as e:
            return f"عذراً، حدث خطأ في البحث عن المعلومات: {str(e)}"

    def _extract_city_from_command(self, command):
        """استخراج اسم المدينة من أمر الطقس"""
        cities = {
            'بغداد': 'بغداد',
            'القاهرة': 'القاهرة',
            'الرياض': 'الرياض',
            'دبي': 'دبي',
            'الكويت': 'الكويت',
            'بيروت': 'بيروت',
            'عمان': 'عمان',
            'الدوحة': 'الدوحة',
            'أبوظبي': 'أبوظبي',
            'مكة': 'مكة',
            'المدينة': 'المدينة المنورة',
            'جدة': 'جدة',
            'الإسكندرية': 'الإسكندرية',
            'دمشق': 'دمشق',
            'حلب': 'حلب'
        }

        command_lower = command.lower()
        for city_key, city_name in cities.items():
            if city_key.lower() in command_lower:
                return city_name

        # إذا لم نجد مدينة محددة، استخدم بغداد كافتراضي
        return 'بغداد'

    def _extract_music_query(self, command):
        """استخراج استعلام الموسيقى من الأمر"""
        # البحث عن أسماء فنانين أو أنواع موسيقية
        artists = ['باخ', 'بيتهوفن', 'موتسارت', 'عمرو دياب', 'فيروز', 'أم كلثوم']
        genres = ['كلاسيك', 'جاز', 'روك', 'بوب', 'حزين', 'سعيد', 'هادئ']

        command_lower = command.lower()

        for artist in artists:
            if artist in command_lower:
                return artist

        for genre in genres:
            if genre in command_lower:
                return genre

        return ""  # بحث عام

    def _extract_app_name(self, command):
        """استخراج اسم التطبيق من الأمر مع معالجة محسنة"""
        app_mapping = {
            'حاسبة': 'calculator',
            'حاسب': 'calculator',
            'حاس': 'calculator',
            'مفكرة': 'notepad',
            'مفكره': 'notepad',
            'رسام': 'paint',
            'الرسام': 'paint',
            'متصفح': 'chrome',
            'كروم': 'chrome',
            'فايرفوكس': 'firefox',
            'اكسبلورر': 'explorer',
            'مستكشف': 'explorer',
            'مدير المهام': 'task manager'
        }

        command_lower = command.lower().strip()

        # البحث المباشر
        for arabic_name, english_name in app_mapping.items():
            if arabic_name in command_lower:
                print(f"🎯 تم تحديد التطبيق: {arabic_name} → {english_name}")
                return english_name

        # البحث الجزئي
        for arabic_name, english_name in app_mapping.items():
            if any(part in command_lower for part in arabic_name.split()):
                print(f"🎯 تطابق جزئي: {arabic_name} → {english_name}")
                return english_name

        # استخراج الكلمة بعد "افتح" أو "شغل"
        words = command.split()
        for i, word in enumerate(words):
            if word in ['افتح', 'شغل', 'فتح']:
                if i + 1 < len(words):
                    extracted_name = words[i + 1]
                    # البحث في الخريطة مرة أخرى
                    for arabic_name, english_name in app_mapping.items():
                        if arabic_name in extracted_name.lower():
                            return english_name
                    return extracted_name

        return command  # إرجاع الأمر كاملاً كاسم التطبيق

    def _extract_url(self, command):
        """استخراج الرابط من الأمر"""
        sites = {
            'جوجل': 'google.com',
            'يوتيوب': 'youtube.com',
            'فيسبوك': 'facebook.com',
            'تويتر': 'twitter.com',
            'انستقرام': 'instagram.com'
        }

        command_lower = command.lower()
        for site_name, url in sites.items():
            if site_name in command_lower:
                return url

        return "google.com"  # افتراضي

    def process_command(self, command):
        """معالجة الأمر وتنفيذ الأداة المناسبة مباشرة"""
        try:
            print(f"🔍 تحليل الأمر: {command}")

            command_lower = command.lower()

            # فحص خاص للطقس ودرجة الحرارة
            weather_keywords = ['درجة الحرارة', 'درجه الحراره', 'الحرارة', 'الحراره', 'الطقس', 'طقس', 'حرارة', 'حراره']
            if any(keyword in command_lower for keyword in weather_keywords):
                print("🌤️ تم تحديد طلب طقس ودرجة حرارة")
                return self._handle_weather_request(command)

            # فحص خاص للأسئلة التي تبدأ بـ "كم"
            if command_lower.startswith('كم') or 'كم درجة' in command_lower or 'كم درجه' in command_lower:
                print("❓ تم تحديد سؤال كمي - البحث في الإنترنت")
                search_query = command.replace('كم', '').strip()
                return self.tools['search_google'](search_query)

            # البحث عن الكلمة المفتاحية المناسبة
            for keyword, handler in self.keyword_to_tool.items():
                if keyword in command_lower:
                    print(f"🎯 تم تحديد الإجراء: {keyword}")

                    # تنفيذ الأداة مباشرة
                    if callable(handler):
                        try:
                            if keyword in ['موسيقى', 'أغنية']:
                                query = self._extract_music_query(command)
                                result = handler(query)
                            elif keyword in ['شغل', 'تشغيل']:
                                result = handler(command)
                            elif keyword in ['افتح', 'فتح']:
                                result = handler(command)
                            elif keyword in ['ابحث', 'بحث']:
                                # استخراج كلمات البحث
                                search_words = command_lower.replace('ابحث', '').replace('عن', '').strip()
                                result = handler(search_words)
                            elif keyword == 'أخبار':
                                result = handler()
                            elif keyword == 'معلومات':
                                result = handler(command)
                            elif keyword in weather_keywords:
                                result = handler(command)
                            elif keyword in ['معلومات النظام', 'العمليات', 'الوقت']:
                                result = handler()
                            else:
                                result = handler(command)

                            print(f"✅ تم تنفيذ الأداة بنجاح")
                            return result

                        except Exception as e:
                            error_msg = f"❌ خطأ في تنفيذ الأداة: {str(e)}"
                            print(error_msg)
                            return error_msg

            # إذا لم نجد أداة مطابقة، فحص إضافي للاستفسارات العامة
            if any(word in command_lower for word in ['ما', 'متى', 'أين', 'لماذا', 'كيف', 'هل']):
                print("❓ تم تحديد سؤال عام - البحث في الإنترنت")
                return self.tools['search_google'](command)

            # استخدام النموذج للرد العام كخيار أخير
            try:
                response = llm.invoke([HumanMessage(content=command)])
                return response.content
            except Exception as e:
                return f"عذراً، لم أتمكن من فهم طلبك: {command}"

        except Exception as e:
            error_msg = f"خطأ في معالجة الأمر: {str(e)}"
            print(error_msg)
            return error_msg


# إنشاء مثيل المساعد
adam = AdamAssistant()


def play_audio_with_pygame(audio_file_path):
    """تشغيل الملف الصوتي باستخدام pygame"""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        pygame.mixer.music.load(audio_file_path)
        pygame.mixer.music.play()

        print("🎵 بدء تشغيل الصوت باستخدام pygame...")

        start_time = time.time()
        timeout = 30

        while pygame.mixer.music.get_busy():
            if time.time() - start_time > timeout:
                print("⏰ انتهت مهلة التشغيل، إيقاف الصوت")
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)

        print("✅ انتهى تشغيل الصوت بنجاح")
        return True

    except Exception as e:
        print(f"❌ خطأ في تشغيل الصوت: {e}")
        return False


async def speak_arabic(text: str):
    """نظام النطق"""
    try:
        # تنظيف النص من markdown أو رموز غريبة
        clean_text = text.replace('`', '').replace('```', '').replace('play_music', '')
        clean_text = re.sub(r'\([^)]*\)', '', clean_text)  # إزالة النص داخل الأقواس
        clean_text = clean_text.strip()

        if not clean_text:
            clean_text = "تم تنفيذ المهمة"

        unique_filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
        audio_file_path = os.path.join(AUDIO_DIR, unique_filename)

        print(f"🔊 جاري إنشاء الملف الصوتي للنص: {clean_text[:50]}...")

        communicate = edge_tts.Communicate(text=clean_text, voice="ar-IQ-BasselNeural")
        await communicate.save(audio_file_path)

        if os.path.exists(audio_file_path):
            print(f"✅ تم إنشاء الملف الصوتي بنجاح")

            if play_audio_with_pygame(audio_file_path):
                print("🎵 تم تشغيل الصوت بنجاح باستخدام pygame")

            # حذف الملف
            try:
                time.sleep(1)
                pygame.mixer.music.unload()
                time.sleep(0.5)

                if os.path.exists(audio_file_path):
                    os.remove(audio_file_path)
                    print("🗑️ تم حذف الملف الصوتي المؤقت")
            except Exception as delete_error:
                print(f"⚠️ لم يتم حذف الملف المؤقت: {delete_error}")

    except Exception as e:
        print(f"❌ خطأ في نطق النص: {e}")


def speak_text(text: str):
    """تشغيل النطق"""
    try:
        print(f"🔊 النطق: {text}")
        asyncio.run(speak_arabic(text))
    except Exception as e:
        print(f"❌ خطأ في النطق: {e}")


def listen_for_audio(timeout=5, phrase_timeout=1):
    """الاستماع للصوت مع معالجة محسنة للأخطاء"""
    if not mic_available or mic is None:
        print("❌ الميكروفون غير متاح")
        return None

    try:
        timeout = MIC_CONFIG.get("timeout", 8)
        phrase_timeout = MIC_CONFIG.get("phrase_time_limit", 4)

        with mic as source:
            print("🎤 جاري الاستماع...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_timeout)
            return audio
    except sr.WaitTimeoutError:
        print("⌛ انتهت مهلة الانتظار")
        return None
    except Exception as e:
        print(f"❌ خطأ في الاستماع: {e}")
        return None


def recognize_speech(audio, language="ar-SA"):
    """التعرف على الكلام مع محاولات متعددة"""
    languages_to_try = ["ar-IQ", "ar-SA", "ar-EG"]
    for lang in languages_to_try:
        try:
            text = recognizer.recognize_google(audio, language=lang)
            print(f"✅ تم التعرف على النص ({lang}): {text}")
            return text
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"❌ خطأ في طلب التعرف على الكلام: {e}")
            continue
    print("❌ لم يتم التعرف على أي نص")
    return None


def save_conversation(input_text: str, response_text: str):
    """حفظ المحادثة"""
    try:
        if not os.path.exists("logs"):
            os.makedirs("logs")

        history_file = os.path.join("logs", "history.jsonl")

        with open(history_file, "a", encoding="utf-8") as f:
            json_line = {
                "input": input_text,
                "response": response_text,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            f.write(json.dumps(json_line, ensure_ascii=False) + "\n")
        print(f"💾 تم حفظ المحادثة في: {history_file}")
    except Exception as e:
        print(f"❌ فشل في حفظ المحادثة: {e}")


def display_capabilities():
    """عرض قدرات المساعد"""
    print("""
🚀 المساعد الذكي آدم - النظام المُحسن بالتنفيذ المباشر

🎯 القدرات المتاحة:
┌─────────────────────────────────────────┐
│ 🎵 تشغيل الموسيقى                      │
│ • "شغل موسيقى باخ"                     │
│ • "شغل أغنية حزينة"                    │
├─────────────────────────────────────────┤
│ 💻 فتح التطبيقات                       │
│ • "افتح الحاسبة"                       │
│ • "افتح كروم"                          │
├─────────────────────────────────────────┤
│ 🌐 البحث والأخبار                      │
│ • "كم درجة الحرارة اليوم؟"              │
│ • "ما أخبار التكنولوجيا؟"              │
├─────────────────────────────────────────┤
│ ⚙️ معلومات النظام                      │
│ • "اعرض معلومات النظام"                │
│ • "ما الوقت الآن؟"                      │
└─────────────────────────────────────────┘

🔥 النظام الجديد ينفذ الأدوات مباشرة!
🎤 إعدادات الميكروفون محسنة ومُخصصة!
""")


def get_text_input():
    """دالة للحصول على إدخال نصي كبديل للصوت"""
    try:
        text = input("💬 اكتب أمرك (أو 'خروج' للإنهاء): ").strip()
        return text if text.lower() not in ['خروج', 'exit', 'quit'] else None
    except KeyboardInterrupt:
        return None
    except Exception as e:
        print(f"❌ خطأ في قراءة النص: {e}")
        return None


def main():
    conversation_mode = False
    last_interaction_time = None

    print("🚀 تم بدء تشغيل المساعد الصوتي آدم - النظام المُحسن")
    print(f"🎯 كلمة التفعيل: '{TRIGGER_WORD}'")

    if not mic_available:
        print("⚠️ الميكروفون غير متاح - سيتم استخدام الإدخال النصي")
        print("💡 لإصلاح الميكروفون، شغل: python mic_fix.py")

    display_capabilities()

    try:
        while True:
            try:
                if not conversation_mode:
                    if mic_available:
                        print(f"\n🔍 في انتظار كلمة التفعيل '{TRIGGER_WORD}'...")
                        audio = listen_for_audio(timeout=10, phrase_timeout=3)
                        if audio is None:
                            continue
                        transcript = recognize_speech(audio, "ar-IQ")
                        if transcript is None:
                            continue
                        if transcript and TRIGGER_WORD.lower() in transcript.lower():
                            print(f"🎉 تم تفعيل المساعد بواسطة: {transcript}")
                            speak_text("نعم، كيف يمكنني مساعدتك؟")
                            conversation_mode = True
                            last_interaction_time = time.time()
                        else:
                            print(f"🔄 لم يتم العثور على كلمة التفعيل. سمعت: '{transcript}'")
                    else:
                        # وضع نصي
                        print(f"\n💬 اكتب '{TRIGGER_WORD}' لتفعيل المساعد:")
                        text_input = get_text_input()
                        if text_input is None:
                            break
                        if TRIGGER_WORD.lower() in text_input.lower():
                            print(f"🎉 تم تفعيل المساعد")
                            speak_text("نعم، كيف يمكنني مساعدتك؟")
                            conversation_mode = True
                            last_interaction_time = time.time()
                else:
                    if mic_available:
                        print("\n💬 جاري الاستماع لأمرك...")
                        audio = listen_for_audio(timeout=8, phrase_timeout=4)
                        if audio is None:
                            if time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                                print("⌛ انتهت الجلسة، العودة لوضع الانتظار")
                                conversation_mode = False
                            continue
                        command = recognize_speech(audio, "ar-SA")
                        if command is None:
                            speak_text("عذراً، لم أفهم ما قلت. يرجى الإعادة.")
                            continue
                    else:
                        # وضع نصي
                        command = get_text_input()
                        if command is None:
                            break

                    print(f"📥 الأمر المستلم: {command}")
                    print("🤖 جاري معالجة الطلب...")

                    try:
                        # استخدام النظام الجديد للمعالجة المباشرة
                        response = adam.process_command(command)

                        print(f"✅ رد المساعد: {response}")
                        speak_text(response)
                        save_conversation(command, response)
                        last_interaction_time = time.time()

                    except Exception as e:
                        error_msg = "عذراً، حدث خطأ في معالجة طلبك"
                        print(f"❌ خطأ في المعالجة: {e}")
                        speak_text(error_msg)

                    if time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                        print("⌛ انتهت مهلة المحادثة")
                        speak_text("تم انتهاء الجلسة. قل كلمة التفعيل للبدء من جديد.")
                        conversation_mode = False

            except KeyboardInterrupt:
                print("\n👋 تم إيقاف المساعد بواسطة المستخدم")
                speak_text("وداعاً!")
                break
            except Exception as e:
                print(f"❌ خطأ غير متوقع: {e}")
                time.sleep(1)
    except Exception as e:
        print(f"❌ خطأ حرج في البرنامج: {e}")
    finally:
        try:
            pygame.mixer.quit()
            print("🧹 تم تنظيف pygame mixer")
        except:
            pass


if __name__ == "__main__":
    main()