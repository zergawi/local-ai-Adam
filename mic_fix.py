# mic_fix.py - إصلاح وإعداد الميكروفون

import speech_recognition as sr
import time
import threading


def test_specific_microphone(mic_index):
    """اختبار ميكروفون محدد"""
    try:
        recognizer = sr.Recognizer()

        # إعدادات محسنة للميكروفون
        recognizer.energy_threshold = 1000  # حساسية أعلى
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 1.0
        recognizer.phrase_threshold = 0.3
        recognizer.non_speaking_duration = 0.8

        mic = sr.Microphone(device_index=mic_index)

        print(f"🎤 اختبار الميكروفون {mic_index}...")

        with mic as source:
            print("⏱️ ضبط للضوضاء... (أقل وقت)")
            recognizer.adjust_for_ambient_noise(source, duration=1)

            print(f"🔊 مستوى الطاقة بعد الضبط: {recognizer.energy_threshold}")

            print("🎤 قل 'مرحبا' بوضوح...")

            # محاولة الاستماع مع timeout أقل
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=2)
            print("✅ تم التقاط الصوت!")

            # محاولة التعرف
            text = recognizer.recognize_google(audio, language="ar-SA")
            print(f"✅ النص: {text}")
            return True

    except sr.WaitTimeoutError:
        print("❌ انتهت مهلة الانتظار - لا يوجد صوت")
        return False
    except sr.RequestError as e:
        print(f"❌ خطأ في الطلب: {e}")
        return False
    except sr.UnknownValueError:
        print("❌ لم يتم التعرف على الكلام")
        return False
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False


def find_best_microphone():
    """العثور على أفضل ميكروفون"""
    print("🔍 البحث عن أفضل ميكروفون...")

    recognizer = sr.Recognizer()
    microphones = sr.Microphone.list_microphone_names()

    # الميكروفونات المرشحة (تحتوي على "Microphone" في الاسم)
    candidate_mics = []
    for i, name in enumerate(microphones):
        if "microphone" in name.lower() and "input" not in name.lower():
            candidate_mics.append((i, name))
            print(f"🎯 مرشح: {i} - {name}")

    if not candidate_mics:
        print("⚠️ لم نجد ميكروفونات مرشحة، سنجرب الكل")
        candidate_mics = [(i, name) for i, name in enumerate(microphones[:6])]

    # اختبار كل ميكروفون مرشح
    for mic_index, mic_name in candidate_mics:
        print(f"\n🧪 اختبار: {mic_name}")
        if test_specific_microphone(mic_index):
            print(f"🎉 تم العثور على الميكروفون المناسب: {mic_index}")
            return mic_index

    return None


def test_with_adjusted_settings():
    """اختبار مع إعدادات مخففة"""
    print("🔧 اختبار مع إعدادات مخففة...")

    try:
        recognizer = sr.Recognizer()

        # إعدادات مخففة جداً
        recognizer.energy_threshold = 50  # حساسية عالية جداً
        recognizer.dynamic_energy_threshold = False  # إيقاف التعديل التلقائي
        recognizer.pause_threshold = 0.5  # وقت توقف أقل

        with sr.Microphone() as source:
            print("⏱️ بدون ضبط للضوضاء...")

            print("🎤 قل أي شيء بصوت عالي...")

            # استماع مع timeout طويل
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            print("✅ تم التقاط الصوت!")

            # محاولة التعرف
            text = recognizer.recognize_google(audio, language="ar-SA")
            print(f"✅ النص: {text}")
            return True

    except Exception as e:
        print(f"❌ فشل الاختبار المخفف: {e}")
        return False


def create_optimized_config():
    """إنشاء ملف إعدادات محسن للميكروفون"""
    print("📝 إنشاء ملف إعدادات محسن...")

    # العثور على أفضل ميكروفون
    best_mic = find_best_microphone()

    config = {
        "microphone_index": best_mic if best_mic is not None else 1,
        "energy_threshold": 200,
        "dynamic_energy_threshold": True,
        "pause_threshold": 0.8,
        "phrase_threshold": 0.3,
        "non_speaking_duration": 0.8,
        "timeout": 8,
        "phrase_time_limit": 4
    }

    # كتابة الإعدادات
    with open('mic_config.json', 'w', encoding='utf-8') as f:
        import json
        json.dump(config, f, indent=2, ensure_ascii=False)

    print("✅ تم إنشاء ملف mic_config.json")
    print(f"🎯 الميكروفون المُوصى به: {config['microphone_index']}")

    return config


def main():
    print("🚀 إصلاح شامل للميكروفون")
    print("=" * 60)

    # خطوة 1: عرض الميكروفونات
    recognizer = sr.Recognizer()
    microphones = sr.Microphone.list_microphone_names()

    print(f"🎙️ الميكروفونات المتاحة ({len(microphones)}):")
    for i, name in enumerate(microphones):
        print(f"   {i}: {name}")

    print("\n" + "=" * 60)

    # خطوة 2: البحث عن أفضل ميكروفون
    best_mic = find_best_microphone()

    if best_mic is not None:
        print(f"\n🎉 تم العثور على ميكروفون يعمل: {best_mic}")
        config = create_optimized_config()

        print(f"""
✅ الإعداد مكتمل!

🎯 استخدم هذه الإعدادات في main.py:
   MIC_INDEX = {config['microphone_index']}

📝 أو استخدم الإعدادات من ملف mic_config.json

🚀 الآن يمكنك تشغيل main.py بنجاح!
        """)
    else:
        print("\n⚠️ لم نجد ميكروفون يعمل بشكل مثالي")
        print("🔧 جاري اختبار إعدادات مخففة...")

        if test_with_adjusted_settings():
            print("✅ الإعدادات المخففة تعمل!")
            config = {
                "microphone_index": 1,
                "energy_threshold": 50,
                "dynamic_energy_threshold": False,
                "pause_threshold": 0.5,
                "timeout": 10,
                "phrase_time_limit": 5
            }

            with open('mic_config.json', 'w', encoding='utf-8') as f:
                import json
                json.dump(config, f, indent=2, ensure_ascii=False)

            print("📝 تم إنشاء إعدادات مخففة في mic_config.json")
        else:
            print("""
❌ جميع الاختبارات فشلت

💡 الحلول المقترحة:
1. تحقق من إعدادات الخصوصية في Windows:
   Settings → Privacy → Microphone → Allow apps to access microphone

2. تحقق من إعدادات الصوت:
   Control Panel → Sound → Recording → تأكد من تشغيل الميكروفون

3. جرب ميكروفون USB خارجي

4. أعد تشغيل الحاسوب

5. تحديث تعريفات الصوت
            """)


if __name__ == "__main__":
    main()