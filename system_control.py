# tools/system_control.py

import os
import sys
import subprocess
import platform
import psutil
import glob
from langchain.tools import tool
from pathlib import Path
import json
import time
import webbrowser

# استيراد مشروط لـ winreg (فقط على Windows)
try:
    import winreg
except ImportError:
    winreg = None  # للأنظمة غير Windows


class SystemController:
    def __init__(self):
        self.system = platform.system().lower()
        self.music_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma']
        self.video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.m4v']

        # مجلدات الموسيقى الشائعة - محسنة
        self.common_music_dirs = []

        # إضافة المجلدات حسب نظام التشغيل
        if self.system == "windows":
            # مجلدات Windows
            user_profile = os.path.expanduser("~")
            self.common_music_dirs = [
                os.path.join(user_profile, "Music"),
                os.path.join(user_profile, "Downloads"),
                os.path.join(user_profile, "Desktop"),
                "C:/Users/Public/Music",
                "D:/Music",
                "E:/Music",
            ]
        else:
            # مجلدات Linux/Mac
            user_home = os.path.expanduser("~")
            self.common_music_dirs = [
                os.path.join(user_home, "Music"),
                os.path.join(user_home, "Downloads"),
                os.path.join(user_home, "Desktop"),
                "/usr/share/sounds",
                "/home/music",
            ]

        # تصفية المجلدات الموجودة فقط
        self.common_music_dirs = [d for d in self.common_music_dirs if d and os.path.exists(d)]

        print(f"🎵 مجلدات الموسيقى المتاحة: {len(self.common_music_dirs)}")

    def find_application_path(self, app_name):
        """البحث الذكي عن مسار التطبيق"""
        print(f"🔍 البحث عن مسار التطبيق: {app_name}")

        if self.system == "windows":
            return self._find_windows_app(app_name)
        elif self.system == "darwin":  # macOS
            return self._find_mac_app(app_name)
        else:  # Linux
            return self._find_linux_app(app_name)

    def _find_windows_app(self, app_name):
        """البحث عن التطبيقات في Windows"""
        # خريطة التطبيقات الشائعة مع مساراتها المحتملة
        common_apps = {
            'chrome': [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME')),
                "chrome.exe"  # من PATH
            ],
            'firefox': [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                "firefox.exe"
            ],
            'edge': [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                "msedge.exe"
            ],
            'notepad': ["notepad.exe"],
            'calculator': ["calc.exe"],
            'paint': ["mspaint.exe"],
            'explorer': ["explorer.exe"],
            'cmd': ["cmd.exe"],
            'powershell': ["powershell.exe"],
            'task manager': ["taskmgr.exe"],
            'control panel': ["control.exe"],
            'word': [
                r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
                r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE"
            ],
            'excel': [
                r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE"
            ],
            'vscode': [
                r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.getenv('USERNAME')),
                r"C:\Program Files\Microsoft VS Code\Code.exe"
            ],
            'vlc': [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
            ]
        }

        # الترجمات العربية
        arabic_to_english = {
            'كروم': 'chrome',
            'فايرفوكس': 'firefox',
            'ايدج': 'edge',
            'المفكرة': 'notepad',
            'الحاسبة': 'calculator',
            'الرسام': 'paint',
            'مستكشف الملفات': 'explorer',
            'مدير المهام': 'task manager',
            'لوحة التحكم': 'control panel',
            'وورد': 'word',
            'اكسل': 'excel'
        }

        # تحويل الاسم العربي إلى إنجليزي
        app_key = app_name.lower()
        if app_key in arabic_to_english:
            app_key = arabic_to_english[app_key]

        # البحث في الأسماء الشائعة
        for key in common_apps:
            if key in app_key or app_key in key:
                app_key = key
                break

        # البحث عن المسار
        if app_key in common_apps:
            for path in common_apps[app_key]:
                if os.path.exists(path):
                    print(f"✅ تم العثور على التطبيق: {path}")
                    return path

        # البحث في Registry
        registry_path = self._search_windows_registry(app_name)
        if registry_path:
            return registry_path

        # البحث في Program Files
        program_files_path = self._search_program_files(app_name)
        if program_files_path:
            return program_files_path

        # محاولة تشغيل مباشر (قد يكون في PATH)
        return app_name

    def _search_windows_registry(self, app_name):
        """البحث في سجل Windows"""
        if not winreg:
            return None

        try:
            # البحث في App Paths
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths") as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if app_name.lower() in subkey_name.lower():
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                path = winreg.QueryValue(subkey, "")
                                if os.path.exists(path):
                                    print(f"✅ تم العثور على التطبيق في Registry: {path}")
                                    return path
                    except:
                        continue
        except:
            pass
        return None

    def _search_program_files(self, app_name):
        """البحث في مجلدات Program Files"""
        search_dirs = [
            "C:/Program Files",
            "C:/Program Files (x86)",
            f"C:/Users/{os.getenv('USERNAME')}/AppData/Local/Programs"
        ]

        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue

            try:
                for root, dirs, files in os.walk(search_dir):
                    # تحديد عمق البحث لتجنب البطء
                    level = root.replace(search_dir, '').count(os.sep)
                    if level > 3:  # حد أقصى 3 مستويات
                        continue

                    for file in files:
                        if (app_name.lower() in file.lower() and
                                file.endswith('.exe')):
                            full_path = os.path.join(root, file)
                            print(f"✅ تم العثور على التطبيق في Program Files: {full_path}")
                            return full_path
            except:
                continue
        return None

    def _find_mac_app(self, app_name):
        """البحث عن التطبيقات في macOS"""
        common_apps = {
            'chrome': 'Google Chrome',
            'firefox': 'Firefox',
            'safari': 'Safari',
            'terminal': 'Terminal',
            'finder': 'Finder'
        }

        app_key = app_name.lower()
        if app_key in common_apps:
            return common_apps[app_key]
        return app_name

    def _find_linux_app(self, app_name):
        """البحث عن التطبيقات في Linux"""
        common_apps = {
            'chrome': 'google-chrome',
            'firefox': 'firefox',
            'terminal': 'gnome-terminal',
            'files': 'nautilus'
        }

        app_key = app_name.lower()
        if app_key in common_apps:
            return common_apps[app_key]
        return app_name

    def find_music_files(self, query=""):
        """البحث عن الملفات الموسيقية مع تحسينات"""
        print(f"🔍 البحث عن ملفات موسيقية تحتوي على: '{query}'")
        found_files = []

        for music_dir in self.common_music_dirs:
            try:
                print(f"🔍 البحث في: {music_dir}")

                for ext in self.music_extensions:
                    # إذا كان هناك استعلام بحث محدد
                    if query.strip():
                        pattern = os.path.join(music_dir, f"**/*{query}*{ext}")
                    else:
                        # إذا لم يكن هناك استعلام، ابحث عن جميع الملفات الموسيقية
                        pattern = os.path.join(music_dir, f"**/*{ext}")

                    files = glob.glob(pattern, recursive=True)
                    found_files.extend(files)

                    if files:
                        print(f"✅ وجد {len(files)} ملف بامتداد {ext} في {music_dir}")

            except Exception as e:
                print(f"⚠️ خطأ في البحث في {music_dir}: {e}")
                continue

        # إزالة التكرارات وترتيب النتائج
        found_files = list(set(found_files))
        found_files.sort()

        print(f"📊 إجمالي الملفات الموجودة: {len(found_files)}")

        # عرض أول 10 ملفات للمراجعة
        if found_files:
            print("🎵 أول 10 ملفات موسيقية:")
            for i, file in enumerate(found_files[:10], 1):
                filename = os.path.basename(file)
                print(f"   {i}. {filename}")

        return found_files[:20]  # إرجاع أول 20 ملف

    def play_music_file(self, filepath):
        """تشغيل ملف موسيقي مع طرق متعددة"""
        print(f"🎵 محاولة تشغيل: {os.path.basename(filepath)}")

        try:
            if self.system == "windows":
                # Windows - استخدام start
                subprocess.Popen(['start', filepath], shell=True)
                print("✅ تم تشغيل الملف باستخدام Windows Media Player")
            elif self.system == "darwin":  # macOS
                subprocess.run(["open", filepath])
                print("✅ تم تشغيل الملف باستخدام QuickTime Player")
            else:  # Linux
                # جرب عدة مشغلات للينكس
                players = ['vlc', 'mplayer', 'mpv', 'audacious', 'rhythmbox']
                for player in players:
                    try:
                        subprocess.Popen([player, filepath])
                        print(f"✅ تم تشغيل الملف باستخدام {player}")
                        return True
                    except FileNotFoundError:
                        continue

                # إذا لم يعمل أي مشغل، استخدم xdg-open
                subprocess.run(["xdg-open", filepath])
                print("✅ تم تشغيل الملف باستخدام المشغل الافتراضي")

            return True

        except Exception as e:
            print(f"❌ خطأ في تشغيل الملف: {e}")
            return False

    def open_application(self, app_name):
        """فتح تطبيق مع البحث الذكي"""
        try:
            print(f"🚀 محاولة فتح التطبيق: {app_name}")

            # البحث عن مسار التطبيق
            app_path = self.find_application_path(app_name)

            if self.system == "windows":
                if app_path and os.path.exists(app_path):
                    # إذا وجدنا مسار صحيح
                    subprocess.Popen([app_path])
                    print(f"✅ تم فتح التطبيق: {app_path}")
                    return True
                else:
                    # محاولة فتح مباشر
                    try:
                        subprocess.Popen(app_path, shell=True)
                        print(f"✅ تم فتح التطبيق: {app_path}")
                        return True
                    except:
                        # محاولة أخيرة - فتح عبر المتصفح للمواقع
                        if app_name.lower() in ['chrome', 'كروم', 'متصفح']:
                            webbrowser.open('http://google.com')
                            print("✅ تم فتح المتصفح الافتراضي")
                            return True
                        return False

            elif self.system == "darwin":  # macOS
                subprocess.run(["open", "-a", app_path])
                return True
            else:  # Linux
                subprocess.Popen(app_path)
                return True

        except Exception as e:
            print(f"❌ خطأ في فتح التطبيق: {e}")
            return False

    def get_running_processes(self):
        """الحصول على العمليات الجارية"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes[:20]  # أول 20 عملية

    def kill_process_by_name(self, process_name):
        """إنهاء عملية بالاسم"""
        killed = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    proc.kill()
                    killed.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return killed

    def get_system_info(self):
        """معلومات النظام"""
        info = {
            "نظام التشغيل": f"{platform.system()} {platform.release()}",
            "المعالج": platform.processor(),
            "الذاكرة الكلية": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
            "الذاكرة المتاحة": f"{round(psutil.virtual_memory().available / (1024 ** 3), 2)} GB",
            "استخدام المعالج": f"{psutil.cpu_percent()}%",
            "استخدام الذاكرة": f"{psutil.virtual_memory().percent}%"
        }
        return info

    def create_folder(self, folder_path):
        """إنشاء مجلد"""
        try:
            os.makedirs(folder_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"خطأ في إنشاء المجلد: {e}")
            return False

    def list_directory(self, directory_path="."):
        """عرض محتويات مجلد"""
        try:
            if not os.path.exists(directory_path):
                return []

            items = []
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                item_type = "مجلد" if os.path.isdir(item_path) else "ملف"
                items.append(f"{item} ({item_type})")

            return items[:20]  # أول 20 عنصر
        except Exception as e:
            print(f"خطأ في قراءة المجلد: {e}")
            return []

    def shutdown_system(self, delay_minutes=1):
        """إيقاف تشغيل النظام"""
        try:
            delay_seconds = delay_minutes * 60
            if self.system == "windows":
                subprocess.run(["shutdown", "/s", "/t", str(delay_seconds)])
            elif self.system == "darwin":  # macOS
                subprocess.run(["sudo", "shutdown", "-h", f"+{delay_minutes}"])
            else:  # Linux
                subprocess.run(["sudo", "shutdown", "-h", f"+{delay_minutes}"])
            return True
        except Exception as e:
            print(f"خطأ في إيقاف التشغيل: {e}")
            return False

    def restart_system(self, delay_minutes=1):
        """إعادة تشغيل النظام"""
        try:
            delay_seconds = delay_minutes * 60
            if self.system == "windows":
                subprocess.run(["shutdown", "/r", "/t", str(delay_seconds)])
            elif self.system == "darwin":  # macOS
                subprocess.run(["sudo", "shutdown", "-r", f"+{delay_minutes}"])
            else:  # Linux
                subprocess.run(["sudo", "shutdown", "-r", f"+{delay_minutes}"])
            return True
        except Exception as e:
            print(f"خطأ في إعادة التشغيل: {e}")
            return False


# إنشاء مثيل من المتحكم
system_controller = SystemController()


@tool
def play_music(query: str = "") -> str:
    """تشغيل موسيقى. يمكنك البحث عن أغنية معينة أو تشغيل أي موسيقى متاحة.

    Args:
        query: كلمات البحث للعثور على أغنية معينة (اختياري)

    Returns:
        str: رسالة توضح نتيجة العملية
    """
    try:
        print(f"🎵 تم استدعاء أداة play_music مع الاستعلام: '{query}'")

        # البحث عن الملفات الموسيقية
        music_files = system_controller.find_music_files(query)

        if not music_files:
            # إذا لم نجد ملفات بالاستعلام المحدد، جرب بحث عام
            if query.strip():
                print(f"🔄 لم نجد ملفات بـ '{query}', جاري البحث العام...")
                music_files = system_controller.find_music_files("")

            if not music_files:
                return f"❌ لم أجد أي ملفات موسيقية في المجلدات المتاحة.\n\n📁 المجلدات المفحوصة:\n" + \
                    "\n".join([f"• {folder}" for folder in system_controller.common_music_dirs]) + \
                    "\n\n💡 تأكد من وجود ملفات موسيقية بصيغ: " + ", ".join(system_controller.music_extensions)

        # اختيار أول ملف مناسب
        selected_file = music_files[0]
        filename = os.path.basename(selected_file)

        print(f"🎵 تم اختيار الملف: {filename}")

        # تشغيل الملف
        if system_controller.play_music_file(selected_file):
            result = f"🎵 جاري تشغيل: {filename}"

            # إضافة معلومات إضافية عن الملفات المتاحة
            if len(music_files) > 1:
                result += f"\n\n🎶 ملفات أخرى متاحة ({len(music_files) - 1}):"
                for i, file in enumerate(music_files[1:6], 1):  # عرض أول 5 ملفات إضافية
                    result += f"\n{i}. {os.path.basename(file)}"

                if len(music_files) > 6:
                    result += f"\n... و {len(music_files) - 6} ملف إضافي"

            # إضافة نصائح للمستخدم
            if query.strip():
                result += f"\n\n💡 تم البحث عن: '{query}'"
            else:
                result += f"\n\n💡 لتشغيل أغنية معينة، قل: 'شغل أغنية [اسم الأغنية]'"

            return result
        else:
            return f"❌ فشل في تشغيل الملف: {filename}\n\n💡 تأكد من وجود مشغل موسيقى في النظام"

    except Exception as e:
        error_msg = f"❌ خطأ في تشغيل الموسيقى: {str(e)}"
        print(error_msg)
        return error_msg


@tool
def open_app(app_name: str) -> str:
    """فتح تطبيق أو برنامج في النظام."""
    try:
        print(f"💻 محاولة فتح التطبيق: {app_name}")

        if system_controller.open_application(app_name):
            return f"✅ تم فتح {app_name} بنجاح"
        else:
            return f"❌ لم أتمكن من فتح {app_name}.\n\n💡 تأكد من أن التطبيق مثبت أو جرب:\n• افتح كروم\n• افتح فايرفوكس\n• افتح الحاسبة\n• افتح المفكرة"
    except Exception as e:
        return f"❌ خطأ في فتح التطبيق: {str(e)}"


@tool
def show_system_info() -> str:
    """عرض معلومات النظام والأداء."""
    try:
        info = system_controller.get_system_info()
        result = "📊 معلومات النظام:\n\n"
        for key, value in info.items():
            result += f"{key}: {value}\n"
        return result
    except Exception as e:
        return f"خطأ في الحصول على معلومات النظام: {str(e)}"


@tool
def list_processes() -> str:
    """عرض العمليات الجارية في النظام."""
    try:
        processes = system_controller.get_running_processes()
        result = "🔄 العمليات الجارية:\n\n"
        for i, proc in enumerate(processes[:15], 1):
            result += f"{i}. {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']}%\n"
        return result
    except Exception as e:
        return f"خطأ في عرض العمليات: {str(e)}"


@tool
def close_program(program_name: str) -> str:
    """إغلاق برنامج أو تطبيق."""
    try:
        killed = system_controller.kill_process_by_name(program_name)
        if killed:
            return f"✅ تم إغلاق: {', '.join(killed)}"
        else:
            return f"❌ لم أجد برنامج باسم '{program_name}' للإغلاق"
    except Exception as e:
        return f"خطأ في إغلاق البرنامج: {str(e)}"


@tool
def create_new_folder(folder_name: str, location: str = ".") -> str:
    """إنشاء مجلد جديد."""
    try:
        folder_path = os.path.join(location, folder_name)
        if system_controller.create_folder(folder_path):
            return f"✅ تم إنشاء المجلد: {folder_path}"
        else:
            return f"❌ فشل في إنشاء المجلد: {folder_name}"
    except Exception as e:
        return f"خطأ في إنشاء المجلد: {str(e)}"


@tool
def list_files(directory: str = ".") -> str:
    """عرض محتويات مجلد معين."""
    try:
        items = system_controller.list_directory(directory)
        if not items:
            return f"المجلد '{directory}' فارغ أو غير موجود"

        result = f"📁 محتويات المجلد '{directory}':\n\n"
        for i, item in enumerate(items, 1):
            result += f"{i}. {item}\n"

        return result
    except Exception as e:
        return f"خطأ في عرض محتويات المجلد: {str(e)}"


@tool
def shutdown_computer(delay_minutes: int = 1) -> str:
    """إيقاف تشغيل الحاسوب بعد مدة معينة (بالدقائق)."""
    try:
        if system_controller.shutdown_system(delay_minutes):
            return f"⚠️ سيتم إيقاف تشغيل الحاسوب خلال {delay_minutes} دقيقة"
        else:
            return "❌ فشل في جدولة إيقاف التشغيل"
    except Exception as e:
        return f"خطأ في إيقاف التشغيل: {str(e)}"


@tool
def restart_computer(delay_minutes: int = 1) -> str:
    """إعادة تشغيل الحاسوب بعد مدة معينة (بالدقائق)."""
    try:
        if system_controller.restart_system(delay_minutes):
            return f"⚠️ سيتم إعادة تشغيل الحاسوب خلال {delay_minutes} دقيقة"
        else:
            return "❌ فشل في جدولة إعادة التشغيل"
    except Exception as e:
        return f"خطأ في إعادة التشغيل: {str(e)}"


@tool
def find_files(filename: str, search_directory: str = None) -> str:
    """البحث عن ملفات في النظام."""
    try:
        if search_directory is None:
            search_directory = os.path.expanduser("~")  # البحث في مجلد المستخدم

        found_files = []
        for root, dirs, files in os.walk(search_directory):
            for file in files:
                if filename.lower() in file.lower():
                    found_files.append(os.path.join(root, file))
                    if len(found_files) >= 10:  # حد أقصى 10 ملفات
                        break
            if len(found_files) >= 10:
                break

        if found_files:
            result = f"🔍 وجدت {len(found_files)} ملف يحتوي على '{filename}':\n\n"
            for i, file_path in enumerate(found_files, 1):
                result += f"{i}. {os.path.basename(file_path)}\n   📂 {os.path.dirname(file_path)}\n\n"
            return result
        else:
            return f"❌ لم أجد أي ملفات تحتوي على '{filename}'"

    except Exception as e:
        return f"خطأ في البحث عن الملفات: {str(e)}"


@tool
def open_website(url: str) -> str:
    """فتح موقع ويب في المتصفح الافتراضي."""
    try:
        import webbrowser

        # إضافة بروتوكول إذا لم يكن موجوداً
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        webbrowser.open(url)
        return f"✅ تم فتح الموقع: {url}"
    except Exception as e:
        return f"خطأ في فتح الموقع: {str(e)}"


@tool
def set_volume(volume_level: int) -> str:
    """تغيير مستوى الصوت (من 0 إلى 100)."""
    try:
        if not 0 <= volume_level <= 100:
            return "❌ مستوى الصوت يجب أن يكون بين 0 و 100"

        if system_controller.system == "windows":
            # استخدام pycaw لنظام ويندوز
            try:
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                from comtypes import CLSCTX_ALL
                from ctypes import cast, POINTER

                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterScalarVolume(volume_level / 100.0, None)

                return f"🔊 تم تغيير مستوى الصوت إلى {volume_level}%"
            except ImportError:
                return "❌ يجب تثبيت pycaw: pip install pycaw"
        else:
            return "❌ تغيير الصوت متاح حالياً فقط لنظام ويندوز"

    except Exception as e:
        return f"خطأ في تغيير مستوى الصوت: {str(e)}"