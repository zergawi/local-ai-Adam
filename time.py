# tools/time.py

from langchain.tools import tool
from datetime import datetime
import pytz


@tool
def get_time(city: str = "baghdad") -> str:
    """إرجاع الوقت الحالي في مدينة معينة. إذا لم تحدد مدينة، سيتم عرض وقت بغداد."""
    try:
        city_timezones = {
            "بغداد": "Asia/Baghdad",
            "baghdad": "Asia/Baghdad",
            "نيويورك": "America/New_York",
            "new york": "America/New_York",
            "لندن": "Europe/London",
            "london": "Europe/London",
            "طوكيو": "Asia/Tokyo",
            "tokyo": "Asia/Tokyo",
            "سيدني": "Australia/Sydney",
            "sydney": "Australia/Sydney",
            "دبي": "Asia/Dubai",
            "dubai": "Asia/Dubai",
            "الرياض": "Asia/Riyadh",
            "riyadh": "Asia/Riyadh",
            "القاهرة": "Africa/Cairo",
            "cairo": "Africa/Cairo",
            "مكة": "Asia/Riyadh",
            "mecca": "Asia/Riyadh",
            "الكويت": "Asia/Kuwait",
            "kuwait": "Asia/Kuwait"
        }

        city_key = city.lower().strip()
        timezone_name = None

        # البحث عن المدينة
        for key, tz in city_timezones.items():
            if key.lower() == city_key:
                timezone_name = tz
                break

        if not timezone_name:
            return f"عذراً، لا أعرف المنطقة الزمنية لمدينة {city}. المدن المتاحة: بغداد، نيويورك، لندن، طوكيو، دبي، الرياض، القاهرة، الكويت"

        timezone = pytz.timezone(timezone_name)
        now = datetime.now(timezone)

        # تنسيق الوقت باللغة العربية
        time_12h = now.strftime("%I:%M")
        am_pm = "صباحاً" if now.strftime("%p") == "AM" else "مساءً"
        date_ar = now.strftime("%A, %B %d, %Y")

        # ترجمة أسماء الأيام والشهور للعربية (اختياري)
        day_names = {
            "Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء",
            "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"
        }

        month_names = {
            "January": "يناير", "February": "فبراير", "March": "مارس", "April": "أبريل",
            "May": "مايو", "June": "يونيو", "July": "يوليو", "August": "أغسطس",
            "September": "سبتمبر", "October": "أكتوبر", "November": "نوفمبر", "December": "ديسمبر"
        }

        current_day = now.strftime("%A")
        current_month = now.strftime("%B")

        day_ar = day_names.get(current_day, current_day)
        month_ar = month_names.get(current_month, current_month)

        return f"الوقت الحالي في {city} هو {time_12h} {am_pm}, {day_ar} {now.day} {month_ar} {now.year}"

    except Exception as e:
        return f"عذراً، حدث خطأ في الحصول على الوقت: {str(e)}"