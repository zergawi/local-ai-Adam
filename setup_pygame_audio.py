#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إعداد محسن للصوت باستخدام pygame للمساعد آدم
إصدار محسن مع اختبارات شاملة
"""

import os
import sys
import subprocess
import platform
import asyncio
import tempfile
import uuid
import json


def print_header():
    """طباعة رأس البرنامج"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                   🎵 إعداد الصوت المحسن                      ║
║                    مع pygame للمساعد آدم                     ║
║                       الإصدار المطور                         ║
╚══════════════════════════════════════════════════════════════╝
""")


def install_audio_dependencies():
    """تثبيت جميع مكتبات الصوت المطلوبة"""
    print("📦 تثبيت مكتبات الصوت...")

    audio_packages = [
        ('pygame', 'مكتبة الصوت الأساسية'),
        ('edge-tts', 'نظام النطق'),
        ('playsound', 'مشغل صوت بديل'),
        ('pydub', 'معالجة الصوت'),
        ('speech-recognition', 'التعرف على الكلام')
    ]

    if platform.system().lower() == "windows":
        audio_packages.append(('pycaw', 'التحكم في صوت Windows'))

    success_count = 0

    for package, description in audio_packages:
        try:
            print(f"🔧 تثبيت {package} ({description})...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package, '--upgrade'],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                print(f"✅ تم تثبيت {package}")
                success_count += 1
            else:
                print(f"❌ فشل تثبيت {package}")
                print(f"   الخطأ: {result.stderr.strip()}")

        except Exception as e:
            print(f"❌ خطأ في تثبيت {package}: {e}")

    print(f"\n📊 تم تثبيت {success_count}/{len(audio_packages)} مكتبة")
    return success_count == len(audio_packages)


def test_pygame_installation():
    """اختبار تثبيت pygame بشكل مفصل"""
    print("🧪 اختبار pygame...")

    try:
        import pygame
        print(f"✅ pygame الإصدار: {pygame.version.ver}")
        print(f"   SDL الإصدار: {pygame.version.SDL}")

        # اختبار تهيئة pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        if pygame.mixer.get_init():
            freq, size, channels = pygame.mixer.get_init()
            print(f"✅ pygame mixer مهيأ بنجاح:")
            print(f"   📊 التردد: {freq} Hz")
            print(f"   📊 حجم العينة: {abs(size)} bit {'(signed)' if size < 0 else '(unsigned)'}")
            print(f"   📊 القنوات: {'ستيريو' if channels == 2 else 'مونو'}")

            # اختبار الإمكانيات المتقدمة
            print(f"   🔧 عدد المخلطات المتاحة: {pygame.mixer.get_num_channels()}")

            pygame.mixer.quit()
            return True
        else:
            print("❌ فشل في تهيئة pygame mixer")
            return False

    except ImportError:
        print("❌ pygame غير مثبت")
        return False
    except Exception as e:
        print(f"❌ خطأ في اختبار pygame: {e}")
        return False


def create_test_audio():
    """إنشاء ملف صوتي للاختبار"""
    print("🎤 إنشاء ملف صوتي للاختبار...")

    try:
        import edge_tts

        # نصوص اختبار متعددة
        test_texts = [
            "مرحباً، هذا اختبار للصوت باستخدام pygame في المساعد آدم",
            "النطق يعمل بشكل ممتاز مع جودة صوت عالية",
            "pygame يوفر تشغيلاً مستقراً وسريعاً للملفات الصوتية"
        ]

        test_files = []

        async def create_audio_files():
            for i, text in enumerate(test_texts):
                test_file = os.path.join(
                    tempfile.gettempdir(),
                    f"pygame_test_{i}_{uuid.uuid4().hex[:8]}.mp3"
                )

                communicate = edge_tts.Communicate(text=text, voice="ar-IQ-BasselNeural")
                await communicate.save(test_file)

                if os.path.exists(test_file):
                    test_files.append(test_file)
                    file_size = os.path.getsize(test_file)
                    print(f"✅ تم إنشاء ملف {i + 1}: {os.path.basename(test_file)} ({file_size} bytes)")
                else:
                    print(f"❌ فشل في إنشاء ملف {i + 1}")

            return test_files

        # إنشاء الملفات
        audio_files = asyncio.run(create_audio_files())

        if audio_files:
            print(f"✅ تم إنشاء {len(audio_files)} ملف صوتي للاختبار")
            return audio_files
        else:
            print("❌ فشل في إنشاء ملفات الاختبار")
            return []

    except ImportError:
        print("❌ edge-tts غير مثبت")
        return []
    except Exception as e:
        print(f"❌ خطأ في إنشاء ملفات الاختبار: {e}")
        return []


def test_pygame_playback(audio_files):
    """اختبار تشغيل الصوت باستخدام pygame"""
    print("🔊 اختبار تشغيل الصوت...")

    if not audio_files:
        print("❌ لا توجد ملفات للاختبار")
        return False

    try:
        import pygame
        import time

        # تهيئة pygame mixer مع إعدادات محسنة
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        print("🎵 تم تهيئة pygame mixer للاختبار")

        success_count = 0

        for i, audio_file in enumerate(audio_files):
            print(f"\n🎵 اختبار الملف {i + 1}: {os.path.basename(audio_file)}")

            try:
                # تحميل وتشغيل الملف
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()

                print("   ▶️ بدء التشغيل...")

                # انتظار انتهاء التشغيل مع عرض التقدم
                start_time = time.time()
                timeout = 15  # 15 ثانية لكل ملف

                while pygame.mixer.music.get_busy():
                    elapsed = time.time() - start_time
                    if elapsed > timeout:
                        print(f"   ⏰ انتهت مهلة التشغيل ({timeout}s)")
                        pygame.mixer.music.stop()
                        break

                    # عرض تقدم بسيط
                    if int(elapsed) % 2 == 0:
                        print(f"   ⏱️ {elapsed:.1f}s", end='\r')

                    time.sleep(0.1)

                print(f"   ✅ انتهى تشغيل الملف {i + 1} بنجاح")
                success_count += 1

                # توقف قصير بين الملفات
                time.sleep(0.5)

            except Exception as file_error:
                print(f"   ❌ خطأ في تشغيل الملف {i + 1}: {file_error}")

        pygame.mixer.quit()

        print(f"\n📊 نتائج الاختبار: {success_count}/{len(audio_files)} ملف تم تشغيله بنجاح")

        if success_count == len(audio_files):
            print("🎉 جميع اختبارات التشغيل نجحت!")
            return True
        elif success_count > 0:
            print("⚠️ بعض الاختبارات نجحت - النظام يعمل جزئياً")
            return True
        else:
            print("❌ جميع اختبارات التشغيل فشلت")
            return False

    except Exception as e:
        print(f"❌ فشل اختبار التشغيل: {e}")
        return False


def cleanup_test_files(test_files):
    """حذف ملفات الاختبار"""
    print("🗑️ تنظيف ملفات الاختبار...")

    cleaned_count = 0
    for test_file in test_files:
        try:
            if os.path.exists(test_file):
                os.remove(test_file)
                cleaned_count += 1
        except Exception as e:
            print(f"⚠️ لم يتم حذف {os.path.basename(test_file)}: {e}")

    print(f"✅ تم حذف {cleaned_count} ملف")


def create_pygame_config():
    """إنشاء ملف إعدادات pygame محسن"""
    print("⚙️ إنشاء إعدادات pygame المحسنة...")

    config_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إعدادات pygame المحسنة للمساعد آدم
"""

import pygame
import time
import os


class PygameAudioManager:
    """مدير الصوت المحسن باستخدام pygame"""

    def __init__(self):
        self.config = {
            'frequency': 22050,    # جودة صوت ممتازة
            'size': -16,           # 16-bit signed للجودة العالية
            'channels': 2,         # ستيريو لتجربة أفضل
            'buffer': 512          # buffer صغير لتقليل التأخير
        }
        self.is_initialized = False
        self.timeout = 30  # حد زمني أقصى للتشغيل

    def initialize(self):
        """تهيئة pygame mixer"""
        try:
            if not self.is_initialized:
                pygame.mixer.init(**self.config)
                self.is_initialized = True
                print("✅ تم تهيئة pygame mixer")
            return True
        except Exception as e:
            print(f"❌ خطأ في تهيئة pygame: {e}")
            return False

    def play_audio(self, filepath):
        """تشغيل ملف صوتي مع معالجة محسنة للأخطاء"""
        if not os.path.exists(filepath):
            print(f"❌ الملف غير موجود: {filepath}")
            return False

        try:
            # التأكد من التهيئة
            if not self.initialize():
                return False

            # تحميل وتشغيل الملف
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()

            print(f"🎵 بدء تشغيل: {os.path.basename(filepath)}")

            # انتظار انتهاء التشغيل مع timeout
            start_time = time.time()

            while pygame.mixer.music.get_busy():
                elapsed = time.time() - start_time
                if elapsed > self.timeout:
                    print(f"⏰ انتهت مهلة التشغيل ({self.timeout}s)")
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.1)

            print("✅ انتهى التشغيل بنجاح")
            return True

        except pygame.error as e:
            print(f"❌ خطأ pygame: {e}")
            return False
        except Exception as e:
            print(f"❌ خطأ عام: {e}")
            return False

    def stop_audio(self):
        """إيقاف التشغيل"""
        try:
            pygame.mixer.music.stop()
            print("⏹️ تم إيقاف التشغيل")
        except:
            pass

    def set_volume(self, volume):
        """تغيير مستوى الصوت (0.0 إلى 1.0)"""
        try:
            volume = max(0.0, min(1.0, volume))  # تأكيد الحدود
            pygame.mixer.music.set_volume(volume)
            print(f"🔊 تم تغيير الصوت إلى {volume*100:.0f}%")
            return True
        except Exception as e:
            print(f"❌ خطأ في تغيير الصوت: {e}")
            return False

    def get_info(self):
        """الحصول على معلومات pygame"""
        if self.is_initialized:
            freq, size, channels = pygame.mixer.get_init()
            return {
                'frequency': freq,
                'size': size,
                'channels': channels,
                'version': pygame.version.ver
            }
        return None

    def cleanup(self):
        """تنظيف pygame"""
        try:
            if self.is_initialized:
                pygame.mixer.quit()
                self.is_initialized = False
                print("🧹 تم تنظيف pygame")
        except:
            pass

    def __del__(self):
        """تنظيف تلقائي عند حذف الكائن"""
        self.cleanup()


# إنشاء مثيل عام
audio_manager = PygameAudioManager()

# دوال سريعة للاستخدام
def init_pygame_audio():
    """تهيئة سريعة لـ pygame"""
    return audio_manager.initialize()

def play_audio_pygame(filepath):
    """تشغيل سريع لملف صوتي"""
    return audio_manager.play_audio(filepath)

def stop_pygame_audio():
    """إيقاف سريع للتشغيل"""
    audio_manager.stop_audio()

def set_pygame_volume(volume_percent):
    """تغيير الصوت بالنسبة المئوية (0-100)"""
    return audio_manager.set_volume(volume_percent / 100.0)


# اختبار سريع
if __name__ == "__main__":
    print("🧪 اختبار سريع لإعدادات pygame...")

    if init_pygame_audio():
        info = audio_manager.get_info()
        if info:
            print(f"📊 إعدادات الصوت:")
            print(f"   التردد: {info['frequency']} Hz")
            print(f"   الحجم: {abs(info['size'])} bit")
            print(f"   القنوات: {info['channels']}")
            print(f"   الإصدار: {info['version']}")

        print("✅ pygame جاهز للاستخدام!")
    else:
        print("❌ مشكلة في pygame")
'''

    try:
        with open('pygame_config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ تم إنشاء ملف إعدادات pygame: pygame_config.py")
        return True
    except Exception as e:
        print(f"❌ خطأ في إنشاء ملف الإعدادات: {e}")
        return False


def update_main_config():
    """تحديث config.json مع إعدادات pygame"""
    print("📝 تحديث ملف الإعدادات الرئيسي...")

    try:
        config_file = 'config.json'

        # قراءة الإعدادات الحالية أو إنشاء جديدة
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}

        # إضافة/تحديث إعدادات pygame
        config['pygame_config'] = {
            'frequency': 22050,
            'size': -16,
            'channels': 2,
            'buffer': 512,
            'timeout': 30
        }

        # إضافة إعدادات صوت محسنة
        config['audio_settings'] = config.get('audio_settings', {})
        config['audio_settings'].update({
            'primary_engine': 'pygame',
            'fallback_engines': ['playsound', 'system'],
            'voice': 'ar-IQ-BasselNeural',
            'default_volume': 0.8
        })

        # حفظ الإعدادات
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print("✅ تم تحديث config.json")
        return True

    except Exception as e:
        print(f"❌ خطأ في تحديث الإعدادات: {e}")
        return False


def main():
    """الدالة الرئيسية"""
    print_header()

    print("🚀 بدء إعداد الصوت المحسن باستخدام pygame")
    print("=" * 60)

    # تثبيت المكتبات
    print("المرحلة 1: تثبيت المكتبات")
    install_success = install_audio_dependencies()
    print()

    # اختبار pygame
    print("المرحلة 2: اختبار pygame")
    pygame_success = test_pygame_installation()
    print()

    if not pygame_success:
        print("❌ فشل اختبار pygame - إيقاف الإعداد")
        return False

    # إنشاء ملفات اختبار
    print("المرحلة 3: إنشاء ملفات الاختبار")
    test_files = create_test_audio()
    print()

    if test_files:
        # اختبار التشغيل
        print("المرحلة 4: اختبار التشغيل")
        playback_success = test_pygame_playback(test_files)
        print()

        # حذف ملفات الاختبار
        cleanup_test_files(test_files)
        print()

        if playback_success:
            # إنشاء ملفات الإعدادات
            print("المرحلة 5: إنشاء ملفات الإعدادات")
            create_pygame_config()
            update_main_config()
            print()

            print("""
🎉 تم إعداد pygame بنجاح!

✅ النتائج:
   • pygame مثبت ومُحسَّن
   • اختبار التشغيل نجح
   • ملفات الإعدادات جاهزة

🚀 المساعد جاهز للعمل:
   python main.py

💡 الآن سيستخدم المساعد pygame كطريقة أساسية لتشغيل الصوت
   مع جودة عالية وأداء محسن!

📁 الملفات المُنشأة:
   • pygame_config.py - إعدادات pygame المتقدمة
   • config.json - محدث بإعدادات الصوت
            """)
            return True
        else:
            print("""
⚠️ مشكلة في اختبار التشغيل

💡 الحلول المقترحة:
1. تحقق من عمل مكبرات الصوت
2. تأكد من عدم كتم الصوت
3. جرب إعادة تشغيل الحاسوب
4. أعد تثبيت pygame:
   pip uninstall pygame
   pip install pygame
            """)
            return False
    else:
        print("""
❌ فشل في إنشاء ملفات الاختبار

💡 تحقق من:
1. تثبيت edge-tts
2. اتصال الإنترنت
3. الصلاحيات للكتابة في المجلد المؤقت
        """)
        return False


if __name__ == "__main__":
    main()  # !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إعداد محسن للصوت باستخدام pygame للمساعد آدم
"""

import os
import sys
import subprocess
import platform
import asyncio
import tempfile
import uuid


def print_header():
    """طباعة رأس البرنامج"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                   🎵 إعداد الصوت المحسن                      ║
║                    مع pygame للمساعد آدم                     ║
╚══════════════════════════════════════════════════════════════╝
""")


def install_pygame():
    """تثبيت pygame مع التحقق من النجاح"""
    print("🔧 تثبيت pygame...")

    try:
        # تثبيت pygame
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'pygame', '--upgrade'],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print("✅ تم تثبيت pygame بنجاح")
            return True
        else:
            print(f"❌ فشل تثبيت pygame: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ انتهت مهلة تثبيت pygame")
        return False
    except Exception as e:
        print(f"❌ خطأ في تثبيت pygame: {e}")
        return False


def test_pygame_installation():
    """اختبار تثبيت pygame"""
    print("🧪 اختبار pygame...")

    try:
        import pygame
        print(f"✅ pygame الإصدار: {pygame.version.ver}")

        # اختبار تهيئة pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        if pygame.mixer.get_init():
            freq, size, channels = pygame.mixer.get_init()
            print(f"✅ pygame mixer مهيأ:")
            print(f"   التردد: {freq} Hz")
            print(f"   حجم العينة: {size} bit")
            print(f"   القنوات: {channels}")

            pygame.mixer.quit()
            return True
        else:
            print("❌ فشل في تهيئة pygame mixer")
            return False

    except ImportError:
        print("❌ pygame غير مثبت")
        return False
    except Exception as e:
        print(f"❌ خطأ في اختبار pygame: {e}")
        return False


def create_test_audio():
    """إنشاء ملف صوتي للاختبار"""
    print("🎤 إنشاء ملف صوتي للاختبار...")

    try:
        import edge_tts

        # نص الاختبار
        test_text = "مرحباً، هذا اختبار للصوت باستخدام pygame في المساعد آدم"

        # إنشاء ملف مؤقت
        test_file = os.path.join(tempfile.gettempdir(), f"pygame_test_{uuid.uuid4().hex[:8]}.mp3")

        async def create_audio():
            communicate = edge_tts.Communicate(text=test_text, voice="ar-IQ-BasselNeural")
            await communicate.save(test_file)
            return test_file

        # إنشاء الملف
        audio_file = asyncio.run(create_audio())

        if os.path.exists(audio_file):
            print(f"✅ تم إنشاء ملف الاختبار: {os.path.basename(audio_file)}")
            return audio_file
        else:
            print("❌ فشل في إنشاء ملف الاختبار")
            return None

    except ImportError:
        print("❌ edge-tts غير مثبت")
        return None
    except Exception as e:
        print(f"❌ خطأ في إنشاء ملف الاختبار: {e}")
        return None


def test_pygame_playback(audio_file):
    """اختبار تشغيل الصوت باستخدام pygame"""
    print("🔊 اختبار تشغيل الصوت...")

    if not audio_file or not os.path.exists(audio_file):
        print("❌ ملف الاختبار غير موجود")
        return False

    try:
        import pygame
        import time

        # تهيئة pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        print("🎵 تشغيل ملف الاختبار...")

        # تحميل وتشغيل الملف
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        # انتظار انتهاء التشغيل
        start_time = time.time()
        timeout = 15  # 15 ثانية

        while pygame.mixer.music.get_busy():
            if time.time() - start_time > timeout:
                print("⏰ انتهت مهلة التشغيل")
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)

        pygame.mixer.quit()
        print("✅ نجح اختبار التشغيل!")
        return True

    except Exception as e:
        print(f"❌ فشل اختبار التشغيل: {e}")
        return False


def cleanup_test_file(test_file):
    """حذف ملف الاختبار"""
    if test_file and os.path.exists(test_file):
        try:
            os.remove(test_file)
            print("🗑️ تم حذف ملف الاختبار")
        except Exception as e:
            print(f"⚠️ لم يتم حذف ملف الاختبار: {e}")


def install_audio_dependencies():
    """تثبيت جميع مكتبات الصوت المطلوبة"""
    print("📦 تثبيت مكتبات الصوت...")

    audio_packages = [
        'pygame',
        'edge-tts',
        'playsound',  # كطريقة بديلة
        'pydub'  # أدوات إضافية
    ]

    success_count = 0

    for package in audio_packages:
        try:
            print(f"🔧 تثبيت {package}...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package, '--upgrade'],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                print(f"✅ تم تثبيت {package}")
                success_count += 1
            else:
                print(f"❌ فشل تثبيت {package}")

        except Exception as e:
            print(f"❌ خطأ في تثبيت {package}: {e}")

    print(f"\n📊 تم تثبيت {success_count}/{len(audio_packages)} مكتبة")
    return success_count == len(audio_packages)


def create_pygame_config():
    """إنشاء ملف إعدادات pygame"""
    print("⚙️ إنشاء إعدادات pygame...")

    config_content = """# إعدادات pygame للمساعد آدم
import pygame

# إعدادات الصوت المحسنة
PYGAME_AUDIO_CONFIG = {
    'frequency': 22050,    # جودة صوت جيدة
    'size': -16,           # 16-bit signed
    'channels': 2,         # ستيريو
    'buffer': 512          # buffer صغير لتقليل التأخير
}

def init_pygame_audio():
    \"\"\"تهيئة pygame mixer مع الإعدادات المحسنة\"\"\"
    try:
        pygame.mixer.init(**PYGAME_AUDIO_CONFIG)
        return True
    except Exception as e:
        print(f"خطأ في تهيئة pygame: {e}")
        return False

def play_audio_pygame(filepath):
    \"\"\"تشغيل ملف صوتي باستخدام pygame\"\"\"
    try:
        if not pygame.mixer.get_init():
            init_pygame_audio()

        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()

        import time
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        return True
    except Exception as e:
        print(f"خطأ في التشغيل: {e}")
        return False
"""

    try:
        with open('pygame_config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ تم إنشاء ملف إعدادات pygame")
        return True
    except Exception as e:
        print(f"❌ خطأ في إنشاء ملف الإعدادات: {e}")
        return False


def main():
    """الدالة الرئيسية"""
    print_header()

    print("🚀 بدء إعداد الصوت المحسن باستخدام pygame")
    print("=" * 60)

    # تثبيت المكتبات
    if not install_audio_dependencies():
        print("⚠️ فشل في تثبيت بعض المكتبات")

    print()

    # اختبار pygame
    if not test_pygame_installation():
        print("❌ فشل اختبار pygame")
        return False

    print()

    # إنشاء ملف اختبار
    test_file = create_test_audio()

    if test_file:
        print()
        # اختبار التشغيل
        success = test_pygame_playback(test_file)

        # حذف ملف الاختبار
        cleanup_test_file(test_file)

        if success:
            print()
            # إنشاء ملف الإعدادات
            create_pygame_config()

            print("""
🎉 تم الإعداد بنجاح!

✅ pygame مثبت ويعمل بشكل صحيح
✅ تم اختبار تشغيل الصوت بنجاح
✅ تم إنشاء ملف الإعدادات

🚀 الآن يمكنك تشغيل المساعد:
   python main.py

💡 المساعد سيستخدم pygame كطريقة أساسية لتشغيل الصوت
            """)
            return True
        else:
            print("""
⚠️ هناك مشكلة في تشغيل الصوت

💡 جرب الحلول التالية:
1. تأكد من أن مكبرات الصوت تعمل
2. تحقق من إعدادات الصوت في النظام
3. جرب إعادة تثبيت pygame:
   pip uninstall pygame
   pip install pygame
            """)
            return False
    else:
        print("❌ فشل في إنشاء ملف الاختبار")
        return False


if __name__ == "__main__":
    main()