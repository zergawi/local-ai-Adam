# 🚀 دليل البدء السريع - المساعد آدم مع pygame
# 🚀 Quick Start Guide - Adam AI Assistant with pygame

[العربية](#arabic) | [English](#english)

---

## <a id="arabic"></a>العربية

### ⚡ التثبيت فائق السرعة

#### 1. الإعداد بأمر واحد
```bash
# تشغيل الإعداد الشامل
python setup_complete.py
```

#### 2. التثبيت اليدوي
```bash
# تثبيت pygame أولاً (الأهم)
pip install pygame --upgrade

# تثبيت باقي المكتبات
pip install edge-tts speech-recognition langchain-ollama psutil requests beautifulsoup4

# اختياري: طرق صوت بديلة
pip install playsound pydub
```

### 🎯 التشغيل

#### Windows:
```bash
# الطريقة الأسهل
start_adam.bat

# أو
python main.py
```

#### Linux/Mac:
```bash
# بعد إنشاؤه
./start_adam.sh

# أو
python main.py
```

### 💬 الاستخدام السريع

1. **🎤 تفعيل**: قل **"آدم"**
2. **👂 انتظر**: "نعم، كيف يمكنني مساعدتك؟"
3. **🗣️ اطلب**: تحدث بوضوح

#### ⚡ أوامر سريعة:

```
🎵 الموسيقى:
"آدم، شغل موسيقى"
"آدم، شغل أغنية فيروز"

💻 البرامج:
"آدم، افتح المتصفح"
"آدم، افتح الحاسبة"
"آدم، اغلق كروم"

🌐 البحث:
"آدم، ما أخبار اليوم؟"
"آدم، ابحث عن الطقس"

📁 الملفات:
"آدم، ابحث عن ملف الصور"
"آدم، انشئ مجلد جديد"

💻 النظام:
"آدم، اعطني معلومات النظام"
"آدم، شو الوقت؟"
```

### 🔧 حل المشاكل السريع

#### 🔊 مشاكل الصوت
```bash
# إعادة تثبيت pygame
pip uninstall pygame
pip install pygame

# اختبار pygame
python -c "import pygame; pygame.mixer.init(); print('✅ pygame يعمل!')"

# اختبار شامل للصوت
python setup_pygame_audio.py
```

#### 🎤 مشاكل الميكروفون
```bash
# عرض الميكروفونات المتاحة
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# تغيير فهرس الميكروفون في config.json
# "mic_index": 1  # جرب أرقام مختلفة
```

#### 🤖 مشاكل النموذج
```bash
# تأكد من تشغيل Ollama
ollama serve

# تحميل النموذج العربي
ollama pull command-r7b-arabic

# اختبار النموذج
ollama run command-r7b-arabic "مرحبا"
```

### ⚙️ الإعدادات السريعة

#### تخصيص الصوت (`config.json`):
```json
{
  "audio_settings": {
    "mic_index": 0,
    "trigger_word": "ادم",
    "voice": "ar-IQ-BasselNeural"
  },
  "pygame_config": {
    "frequency": 22050,
    "channels": 2,
    "timeout": 30
  }
}
```

#### تخصيص الأصوات المتاحة:
- `ar-IQ-BasselNeural` (عراقي - افتراضي)
- `ar-SA-HamedNeural` (سعودي)
- `ar-EG-SalmaNeural` (مصري)

### 🎯 نصائح للأداء الأمثل

#### 🔊 للصوت:
- استخدم ميكروفون خارجي للجودة الأفضل
- تجنب الضوضاء الخلفية
- تحدث على بُعد 15-30 سم من الميكروفون

#### 💻 للنظام:
- أغلق البرامج غير الضرورية
- تأكد من اتصال إنترنت مستقر
- استخدم SSD للأداء الأسرع

### 🆘 المساعدة السريعة

#### الأخطاء الشائعة:

| الخطأ | الحل السريع |
|-------|-------------|
| `ModuleNotFoundError: pygame` | `pip install pygame` |
| `لم يتم التعرف على الصوت` | تحقق من الميكروفون |
| `خطأ في النموذج` | `ollama serve` |
| `فشل تشغيل الصوت` | `python setup_pygame_audio.py` |

---

## <a id="english"></a>English

### ⚡ Lightning Fast Installation

#### 1. One-Command Setup
```bash
# Run comprehensive setup
python setup_complete.py
```

#### 2. Manual Installation
```bash
# Install pygame first (most important)
pip install pygame --upgrade

# Install other libraries
pip install edge-tts speech-recognition langchain-ollama psutil requests beautifulsoup4

# Optional: Alternative audio methods
pip install playsound pydub
```

### 🎯 Running the Assistant

#### Windows:
```bash
# Easiest way
start_adam.bat

# Or
python main.py
```

#### Linux/Mac:
```bash
# After creating it
./start_adam.sh

# Or
python main.py
```

### 💬 Quick Usage

1. **🎤 Activate**: Say **"Adam"**
2. **👂 Wait**: "Yes, how can I help you?"
3. **🗣️ Command**: Speak clearly

#### ⚡ Quick Commands:

```
🎵 Music:
"Adam, play music"
"Adam, play Fairuz song"

💻 Applications:
"Adam, open browser"
"Adam, open calculator"
"Adam, close Chrome"

🌐 Search:
"Adam, what's today's news?"
"Adam, search for weather"

📁 Files:
"Adam, find photo files"
"Adam, create new folder"

💻 System:
"Adam, give me system info"
"Adam, what time is it?"
```

### 🔧 Quick Troubleshooting

#### 🔊 Audio Issues
```bash
# Reinstall pygame
pip uninstall pygame
pip install pygame

# Test pygame
python -c "import pygame; pygame.mixer.init(); print('✅ pygame works!')"

# Comprehensive audio test
python setup_pygame_audio.py
```

#### 🎤 Microphone Issues
```bash
# Show available microphones
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# Change microphone index in config.json
# "mic_index": 1  # Try different numbers
```

#### 🤖 Model Issues
```bash
# Ensure Ollama is running
ollama serve

# Download Arabic model
ollama pull command-r7b-arabic

# Test model
ollama run command-r7b-arabic "Hello"
```

### ⚙️ Quick Settings

#### Audio Configuration (`config.json`):
```json
{
  "audio_settings": {
    "mic_index": 0,
    "trigger_word": "adam",
    "voice": "en-US-AriaNeural"
  },
  "pygame_config": {
    "frequency": 22050,
    "channels": 2,
    "timeout": 30
  }
}
```

#### Available Voices:
- `en-US-AriaNeural` (US English - default)
- `en-GB-SoniaNeural` (British English)
- `ar-IQ-BasselNeural` (Iraqi Arabic)

### 🎯 Performance Tips

#### 🔊 For Audio:
- Use external microphone for better quality
- Avoid background noise
- Speak 15-30 cm from microphone

#### 💻 For System:
- Close unnecessary programs
- Ensure stable internet connection
- Use SSD for faster performance

### 🚀 Advanced Features

#### 🎵 Music Control:
```
"Adam, turn up volume"
"Adam, set volume to 50"
"Adam, play relaxing music"
```

#### 💻 System Management:
```
"Adam, show running processes"
"Adam, shutdown computer in 5 minutes"
"Adam, create folder named MyProjects"
```

#### 🌐 Advanced Search:
```
"Adam, search latest tech news"
"Adam, open YouTube website"
"Adam, tell me about artificial intelligence"
```

### 📊 System Information

#### Performance Requirements:
- **RAM**: 4GB+ (8GB recommended)
- **CPU**: Dual-core processor or better
- **Storage**: 2GB free space
- **Audio**: Microphone + speakers/headphones

#### Supported Operating Systems:
- ✅ Windows 10/11
- ✅ Ubuntu 20.04+
- ✅ macOS 10.15+

### 🆘 Quick Help

#### Common Errors:

| Error | Quick Fix |
|-------|-----------|
| `ModuleNotFoundError: pygame` | `pip install pygame` |
| `Audio not recognized` | Check microphone |
| `Model error` | `ollama serve` |
| `Audio playback failed` | `python setup_pygame_audio.py` |

#### Useful Links:
- 🤖 [Download Ollama](https://ollama.ai)
- 🐍 [Download Python](https://python.org)
- 🎵 [pygame Documentation](https://pygame.org/docs)

## 🎉 You're Ready! | أنت جاهز!

```bash
# Start now! | ابدأ الآن!
python main.py

# Or use quick file | أو استخدم الملف السريع
start_adam.bat
```

**Say "Adam" and enjoy your smart assistant! | قل "آدم" واستمتع بمساعدك الذكي!** 🚀

---

*For advanced support or complex issues, refer to the comprehensive `README.md`.*
*للدعم المتقدم أو المشاكل المعقدة، راجع `README.md` الشامل.*
