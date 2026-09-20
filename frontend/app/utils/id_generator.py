import random
import datetime
from app.config import CATEGORY_DISPLAY

def generate_complaint_id(category: str = "Other") -> str:
    """
    Generates a unique, standardized Tamil Nadu Grievance Tracking ID.
    Format: TN-{CAT_CODE}-{YYYYMM}-{RANDOM6}
    Example: TN-WTR-202609-482194, TN-ELE-202609-901412
    """
    cat_code = CATEGORY_DISPLAY.get(category, {}).get("code", "OTH")
    now = datetime.datetime.utcnow()
    year_month = now.strftime("%Y%m")
    random_digits = f"{random.randint(100000, 999999)}"
    
    return f"TN-{cat_code}-{year_month}-{random_digits}"
