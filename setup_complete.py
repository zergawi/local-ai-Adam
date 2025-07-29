#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إعداد شامل للمساعد الصوتي آدم مع التحكم الكامل في النظام
"""

import os
import sys
import subprocess
import platform
import json
import tempfile
import uuid
import asyncio


def print_header():
    """طباعة رأس البرنامج"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                   🚀 المساعد الصوتي آدم                     ║
║                    الإعداد الشامل المطور                    ║
║                                                              ║
║  🎵 تشغيل الموسيقى  💻 التحكم في النظام  🌐 البحث        ║
║  📁 إدارة الملفات   ⚙️ إدارة النظام      🔊 التحكم بالصوت ║
╚══════════════════════════════════════════════════════════════╝
""")


def get_system_info():
    """الحصول على معلومات النظام"""
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": sys.version,
        "architecture": platform.architecture()[0],
        "processor": platform.processor()
    }

    print("🖥️ معلومات النظام:")
    print(f"   نظام التشغيل: {system_info['os']}")
    print(f"   إصدار النظام: {platform.release()}")
    print(f"   إصدار Python: {platform.python_version()}")
    print(f"   المعمارية: {system_info['architecture']}")
    print()

    return system_info


def install_requirements():
    """تثبيت المكتبات المطلوبة"""
    print("📦 جاري تثبيت المكتبات المطلوبة...")

    # قائمة المكتبات الأساسية مرتبة حسب الأولوية
    # تحسين قائمة المكتبات
    essential_packages = [
        'pygame>=2.0.0',  # تحديد إصدار
        'edge-tts>=6.0.0',
        'speech-recognition>=3.8.0',
        'langchain>=0.1.0',
        'langchain-ollama>=0.1.0',
        'psutil>=5.8.0',
        'requests>=2.25.0',
        'beautifulsoup4>=4.9.0',
        'python-dotenv>=0.19.0',
        'pydub>=0.25.0',
        'pytz>=2021.1'
    ]

    # مكتبات خاصة بالنظام
    system_specific = []
    if platform.system().lower() == "windows":
        system_specific.extend(['pycaw', 'pywin32'])

    # مكتبات بديلة
    optional_packages = ['playsound', 'simpleaudio']

    all_packages = essential_packages + system_specific + optional_packages

    success_count = 0
    failed_packages = []

    for package in all_packages:
        try:
            print(f"🔧 تثبيت {package}...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package, '--upgrade'],
                capture_output=True,
                text=True,
                timeout=300  # 5 دقائق لكل مكتبة
            )

            if result.returncode == 0:
                print(f"✅ تم تثبيت {package} بنجاح")
                success_count += 1
            else:
                print(f"❌ فشل تثبيت {package}")
                if package not in optional_packages:  # لا نعتبر الفشل مشكلة للمكتبات الاختيارية
                    failed_packages.append(package)

        except subprocess.TimeoutExpired:
            print(f"⏰ انتهت مهلة تثبيت {package}")
            failed_packages.append(package)
        except Exception as e:
            print(f"❌ خطأ في تثبيت {package}: {e}")
            if package not in optional_packages:
                failed_packages.append(package)

    print(f"\n📊 النتائج:")
    print(f"✅ تم تثبيت {success_count} مكتبة بنجاح")
    if failed_packages:
        print(f"❌ فشل تثبيت {len(failed_packages)} مكتبة: {', '.join(failed_packages)}")
        print("\n💡 يمكنك محاولة تثبيت المكتبات الفاشلة يدوياً:")
        for pkg in failed_packages:
            print(f"   pip install {pkg}")

    return success_count, failed_packages


def setup_directories():
    """إنشاء المجلدات المطلوبة"""
    print("📁 إعداد المجلدات...")

    directories = [
        'audio_files',
        'logs',
        'temp_audio',
        'downloads',
        'user_data'
    ]

    created_count = 0

    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"✅ تم إنشاء مجلد: {directory}")
                created_count += 1
            else:
                print(f"📂 المجلد موجود: {directory}")
        except Exception as e:
            print(f"❌ خطأ في إنشاء المجلد {directory}: {e}")

    print(f"📊 تم إنشاء {created_count} مجلد جديد")
    return created_count


def test_microphone():
    """اختبار الميكروفون"""
    print("🎤 اختبار الميكروفون...")

    try:
        import speech_recognition as sr

        recognizer = sr.Recognizer()
        microphones = sr.Microphone.list_microphone_names()

        print(f"🎙️ تم العثور على {len(microphones)} ميكروفون:")
        for i, mic_name in enumerate(microphones[:5]):  # عرض أول 5 فقط
            print(f"   {i}: {mic_name}")

        if len(microphones) > 5:
            print(f"   ... و {len(microphones) - 5} ميكروفون إضافي")

        # اختبار الميكروفون الافتراضي
        try:
            with sr.Microphone() as source:
                print("🔧 ضبط الميكروفون للضوضاء المحيطة...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("✅ تم ضبط الميكروفون بنجاح")
                return True
        except Exception as e:
            print(f"❌ مشكلة في الميكروفون: {e}")
            return False

    except ImportError:
        print("❌ مكتبة speech_recognition غير مثبتة")
        return False


def test_pygame_audio():
    """اختبار pygame للصوت"""
    print("🔊 اختبار نظام الصوت pygame...")

    try:
        import pygame

        # تهيئة pygame
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


def test_edge_tts():
    """اختبار edge-tts للنطق"""
    print("🗣️ اختبار نظام النطق...")

    try:
        import edge_tts

        # إنشاء ملف اختبار صغير
        async def create_test_audio():
            test_text = "اختبار النطق"
            test_file = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex[:8]}.mp3")

            communicate = edge_tts.Communicate(text=test_text, voice="ar-IQ-BasselNeural")
            await communicate.save(test_file)

            if os.path.exists(test_file):
                # حذف ملف الاختبار
                try:
                    os.remove(test_file)
                except:
                    pass
                return True
            return False

        result = asyncio.run(create_test_audio())
        if result:
            print("✅ نظام النطق يعمل بشكل صحيح")
            return True
        else:
            print("❌ مشكلة في إنشاء الملفات الصوتية")
            return False

    except ImportError:
        print("❌ edge-tts غير مثبت")
        return False
    except Exception as e:
        print(f"❌ خطأ في اختبار النطق: {e}")
        return False


def test_ollama_connection():
    """اختبار الاتصال بـ Ollama"""
    print("🤖 اختبار الاتصال بنموذج الذكاء الاصطناعي...")

    try:
        from langchain_ollama import ChatOllama

        # محاولة إنشاء اتصال
        llm = ChatOllama(model="command-r7b-arabic", reasoning=False)

        # اختبار بسيط
        response = llm.invoke("مرحبا")
        if response:
            print("✅ نموذج الذكاء الاصطناعي متصل ويعمل")
            return True
        else:
            print("❌ مشكلة في الاستجابة من النموذج")
            return False

    except ImportError:
        print("❌ langchain-ollama غير مثبت")
        return False
    except Exception as e:
        print(f"⚠️ تحذير: {e}")
        print("💡 تأكد من تشغيل Ollama وتحميل النموذج:")
        print("   ollama serve")
        print("   ollama pull command-r7b-arabic")
        return False


def create_startup_script():
    """إنشاء سكريپت بدء التشغيل"""
    if platform.system().lower() == "windows":
        print("🪟 إنشاء سكريپت Windows...")

        startup_script = '''@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                   🚀 المساعد الصوتي آدم                     ║
echo ║                    بدء التشغيل السريع                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM التحقق من Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت أو غير موجود في PATH
    echo 💡 قم بتثبيت Python من: https://python.org
    pause
    exit /b 1
)

echo ✅ Python متوفر
echo.

REM التحقق من المجلد الافتراضي
if not exist "main.py" (
    echo ❌ main.py غير موجود في هذا المجلد
    echo 💡 تأكد من تشغيل السكريپت في مجلد المشروع
    pause
    exit /b 1
)

echo 🎯 تشغيل المساعد آدم...
echo 💡 قل "آدم" لتفعيل المساعد
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ❌ حدث خطأ في تشغيل المساعد
    echo 💡 تحقق من الرسائل أعلاه لمعرفة السبب
    echo.
)

pause
'''

        try:
            with open('start_adam.bat', 'w', encoding='utf-8') as f:
                f.write(startup_script)
            print("✅ تم إنشاء سكريپت البدء: start_adam.bat")
            return True
        except Exception as e:
            print(f"❌ خطأ في إنشاء سكريپت البدء: {e}")
            return False
    else:
        print("🐧 إنشاء سكريپت Linux/Mac...")

        startup_script = '''#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                   🚀 المساعد الصوتي آدم                     ║"
echo "║                    بدء التشغيل السريع                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo

# التحقق من Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python غير مثبت"
    echo "💡 قم بتثبيت Python"
    exit 1
fi

echo "✅ Python متوفر"

# التحقق من الملف الرئيسي
if [ ! -f "main.py" ]; then
    echo "❌ main.py غير موجود"
    echo "💡 تأكد من تشغيل السكريپت في مجلد المشروع"
    exit 1
fi

echo "🎯 تشغيل المساعد آدم..."
echo "💡 قل 'آدم' لتفعيل المساعد"
echo

python3 main.py

if [ $? -ne 0 ]; then
    echo
    echo "❌ حدث خطأ في تشغيل المساعد"
    echo "💡 تحقق من الرسائل أعلاه لمعرفة السبب"
fi

read -p "اضغط Enter للإغلاق..."
'''

        try:
            with open('start_adam.sh', 'w', encoding='utf-8') as f:
                f.write(startup_script)

            # جعل الملف قابل للتنفيذ
            os.chmod('start_adam.sh', 0o755)

            print("✅ تم إنشاء سكريپت البدء: start_adam.sh")
            return True
        except Exception as e:
            print(f"❌ خطأ في إنشاء سكريپت البدء: {e}")
            return False


def run_comprehensive_test():
    """اختبار شامل للنظام"""
    print("🧪 تشغيل الاختبار الشامل...")
    print("=" * 50)

    tests = {
        "الميكروفون": test_microphone(),
        "نظام الصوت pygame": test_pygame_audio(),
        "نظام النطق": test_edge_tts(),
        "نموذج الذكاء الاصطناعي": test_ollama_connection(),
    }

    # اختبار المكتبات الأساسية
    essential_modules = [
        ('psutil', 'معلومات النظام'),
        ('requests', 'البحث على الإنترنت'),
        ('bs4', 'معالجة HTML'),
    ]

    for module, description in essential_modules:
        try:
            __import__(module)
            tests[f"مكتبة {description}"] = True
        except ImportError:
            tests[f"مكتبة {description}"] = False

    # عرض النتائج
    print("\n📋 نتائج الاختبار:")
    print("=" * 50)
    passed = 0
    total = len(tests)

    for test_name, result in tests.items():
        status = "✅ نجح" if result else "❌ فشل"
        print(f"   {test_name:<25} {status}")
        if result:
            passed += 1

    print("=" * 50)
    print(f"📊 النتيجة النهائية: {passed}/{total} اختبار نجح ({(passed / total) * 100:.1f}%)")

    if passed == total:
        print("🎉 جميع الاختبارات نجحت! النظام جاهز للعمل")
        return True
    elif passed >= total * 0.7:  # 70% أو أكثر
        print("⚠️ معظم الاختبارات نجحت. النظام قابل للاستخدام مع بعض القيود")
        return True
    else:
        print("❌ عدة اختبارات فشلت. راجع الأخطاء أعلاه")
        return False


def main():
    """الدالة الرئيسية"""
    print_header()

    print("🚀 بدء الإعداد الشامل للمساعد الصوتي آدم")
    print("=" * 60)

    # معلومات النظام
    system_info = get_system_info()

    # إعداد المجلدات
    setup_directories()
    print()

    # تثبيت المكتبات
    success_count, failed = install_requirements()
    print()

    # إنشاء سكريپت البدء
    create_startup_script()
    print()

    # الاختبار الشامل
    success = run_comprehensive_test()

    print("\n" + "=" * 60)

    if success:
        print("""
🎉 تم الإعداد بنجاح!

🚀 طرق تشغيل المساعد:
   1. python main.py
   2. ملف البدء السريع:""")

        if platform.system().lower() == "windows":
            print("      start_adam.bat  (انقر نقر مزدوج)")
        else:
            print("      ./start_adam.sh")

        print("""
📖 تعليمات الاستخدام:
1. قل "آدم" لتفعيل المساعد
2. اطلب منه أي شيء مثل:
   • "شغل موسيقى"
   • "افتح المتصفح" 
   • "ابحث عن أخبار اليوم"
   • "اعرض معلومات النظام"

🔧 ملفات الإعدادات:
   • config.json - الإعدادات الشخصية
   • logs/ - سجلات البرنامج
   • audio_files/ - الملفات الصوتية

🎯 المساعد جاهز للعمل!
        """)
    else:
        print("""
⚠️ الإعداد مكتمل مع بعض المشاكل

💡 إرشادات استكمال الإعداد:
1. راجع الأخطاء أعلاه وحل المشاكل
2. ثبت المكتبات المفقودة يدوياً
3. تأكد من عمل الميكروفون ومكبرات الصوت
4. تحقق من تشغيل Ollama والنموذج العربي:
   ollama serve
   ollama pull command-r7b-arabic

5. جرب تشغيل: python main.py
        """)


if __name__ == "__main__":
    main()