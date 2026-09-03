"""
بارگذاری متغیرهای محیطی و ثابت‌های سراسریِ پیکربندی پروژه.
"""

from dotenv import load_dotenv

load_dotenv()

# ==================== اتصال دیتابیس و مدل ====================

from pathlib import Path

# مسیر ریشه پروژه (یک سطح بالاتر از src)
ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(ROOT_DIR / "bank_database.db")