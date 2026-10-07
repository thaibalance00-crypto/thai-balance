import base64
import calendar
import hashlib
import hmac
import json
import os
import secrets as pysecrets
import sqlite3
from datetime import date, datetime

import pandas as pd
import streamlit as st

# ============================================================
# Thai Balance
# ระบบดูแลสุขภาพแบบองค์รวม ผสมผสานแพทย์แผนไทย โภชนาการ และ AI
# ============================================================

DB_PATH = "thai_balance.db"
ADDRESS_CSV = "thai_address.csv"  # คอลัมน์: zipcode,province,amphoe,tambon (ถ้ามี)

st.set_page_config(
    page_title="Thai Balance",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS
# ============================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Noto Sans Thai', sans-serif; }
.stApp { background: #f7faf6; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }

.block-container {
    max-width: 1450px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

.tb-header {
    background: #ffffff;
    border-bottom: 1px solid #dfece4;
    padding: 12px 18px;
    border-radius: 0 0 18px 18px;
    margin-bottom: 12px;
}
.tb-brand { display: flex; align-items: center; gap: 14px; }
.tb-leaf {
    width: 52px; height: 52px; border-radius: 50%;
    background: #e5f3e9; display: flex;
    align-items: center; justify-content: center; font-size: 30px;
}
.tb-title { color: #176344; font-size: 30px; font-weight: 800; line-height: 1.05; }
.tb-subtitle { color: #5f7569; font-size: 14px; margin-top: 3px; }
.tb-pill {
    background: #edf7e9; border: 1px solid #d2e7cb; color: #3b6849;
    border-radius: 16px; padding: 10px 16px; font-size: 13px; text-align: center;
}

.hero {
    background: linear-gradient(90deg, #eaf6ea, #f8f4e7);
    border: 1px solid #d8e8d8; border-radius: 22px;
    padding: 25px 30px; margin: 12px 0 18px 0;
}
.hero h1 { color: #176344; margin: 0; font-size: 30px; }
.hero p { color: #5b7164; margin: 8px 0 0 0; font-size: 16px; }

.panel {
    background: #ffffff; border: 1px solid #dce9df; border-radius: 18px;
    padding: 20px; box-shadow: 0 5px 18px rgba(35, 91, 64, .06); margin-bottom: 16px;
}
.panel-title { color: #176344; font-size: 21px; font-weight: 800; margin-bottom: 8px; }
.panel-sub { color: #6b7e73; font-size: 13px; margin-bottom: 15px; }

.section-title { color: #176344; font-size: 18px; font-weight: 800; margin: 4px 0 2px 0; }
.section-hint { color: #6b7e73; font-size: 13px; margin-bottom: 10px; }

.flow-item { display: flex; gap: 10px; margin: 10px 0; }
.flow-num {
    min-width: 32px; height: 32px; border-radius: 50%;
    background: #2c8a65; color: #fff; display: flex;
    align-items: center; justify-content: center; font-weight: 800;
}
.flow-text strong { color: #245b48; }
.flow-text small { color: #68796f; }

.metric-card {
    background: #ffffff; border: 1px solid #dce9df; border-radius: 16px;
    padding: 15px; text-align: center;
}
.metric-value { color: #176344; font-size: 25px; font-weight: 800; }
.metric-label { color: #6b7d73; font-size: 12px; }

.profile-row { padding: 8px 0; border-bottom: 1px dashed #e2ece5; }
.profile-label { color: #6b7d73; font-size: 12px; }
.profile-value { color: #1d3d2f; font-size: 16px; font-weight: 600; }
.avatar-ph {
    width: 170px; height: 170px; border-radius: 50%; background: #e5f3e9;
    display: flex; align-items: center; justify-content: center; font-size: 80px;
}

.warning {
    background: #fff7df; border: 1px solid #efd48d; border-radius: 14px;
    padding: 12px 14px; color: #775d16;
}
.danger {
    background: #fff0ef; border: 1px solid #e9b9b5; border-radius: 14px;
    padding: 12px 14px; color: #8a3b35;
}
.success-box {
    background: #eff9f0; border: 1px solid #c9e5ce; border-radius: 14px;
    padding: 12px 14px; color: #2f6840;
}

.stButton > button {
    border-radius: 12px; border: 0; background: #2b8a66;
    color: white; font-weight: 700; min-height: 42px;
}
.stButton > button:hover { background: #176344; color: white; }
[data-testid="stFormSubmitButton"] > button {
    border-radius: 12px; border: 0; background: #2b8a66;
    color: white; font-weight: 700; min-height: 42px;
}
[data-testid="stFormSubmitButton"] > button:hover { background: #176344; color: white; }
[data-testid="stForm"] { border-color: #dce9df; border-radius: 16px; background: #ffffff; }
/* แถบหัวเว็บ (แถวคอลัมน์ที่มี .tb-anchor) */
div[data-testid="stHorizontalBlock"]:has(.tb-anchor) {
    background: #ffffff; border-bottom: 1px solid #dfece4;
    padding: 12px 18px; border-radius: 0 0 18px 18px; margin-bottom: 12px;
    align-items: center;
}
.stDownloadButton > button { border-radius: 12px; }
div[data-testid="stMetric"] {
    background: #ffffff; border: 1px solid #dce9df; border-radius: 14px; padding: 8px;
}

[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] {
    display: none !important;
}
[data-testid="stPopover"] button {
    min-height: 52px; width: auto; min-width: 56px; font-size: 16px; font-weight: 700;
    border-radius: 14px; background: #ffffff; color: #176344;
    border: 1px solid #dce9df; box-shadow: 0 3px 10px rgba(35, 91, 64, .10);
    padding: 4px 14px; gap: 8px;
}
.tb-pill-wrap { display: flex; justify-content: flex-end; }
[data-testid="stPopover"] button:hover { background: #eaf6ea; color: #176344; }
.bot-badge {
    display: inline-block; background: #eaf6ea; border: 1px solid #cfe5c8;
    color: #176344; border-radius: 999px; padding: 3px 12px; font-size: 12px;
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# DATABASE
# ============================================================
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_columns(conn, table, columns):
    """เพิ่มคอลัมน์ใหม่ให้ฐานข้อมูลเดิม (ไม่ทำให้ข้อมูลเก่าหาย)"""
    existing = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
    for name, ddl in columns.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            full_name TEXT NOT NULL,
            citizen_id TEXT,
            birthdate TEXT,
            gender TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS health_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            cc TEXT,
            pi TEXT,
            ph TEXT,
            fh TEXT,
            chronic TEXT,
            weight REAL,
            height REAL,
            bmi REAL,
            constitution TEXT,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            meal_date TEXT NOT NULL,
            meal_time TEXT,
            meal_type TEXT,
            food_name TEXT NOT NULL,
            ingredients TEXT,
            amount TEXT,
            calories REAL,
            image BLOB,
            image_type TEXT,
            note TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ex_date TEXT NOT NULL,
            ex_time TEXT,
            ex_type TEXT NOT NULL,
            duration_min REAL,
            intensity TEXT,
            calories REAL,
            note TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS ai_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )
    ensure_columns(conn, "users", {
        "postal_code": "TEXT",
        "province": "TEXT",
        "district": "TEXT",
        "subdistrict": "TEXT",
        "house_no": "TEXT",
        "profile_image": "BLOB",
        "profile_image_type": "TEXT",
        "role": "TEXT DEFAULT 'user'",
        "is_active": "INTEGER DEFAULT 1",
        "last_login": "TEXT",
    })
    ensure_columns(conn, "health_data", {"history_json": "TEXT"})
    conn.commit()
    conn.close()


init_db()

# ============================================================
# DATE / ADDRESS HELPERS
# ============================================================
THAI_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
]


def parse_date(value, default=date(1995, 1, 1)):
    try:
        return date.fromisoformat(str(value))
    except Exception:
        return default


def thai_date_input(label, value=None, key="thai_date"):
    """ตัวเลือก วัน / เดือน / ปี (พ.ศ.) คืนค่าเป็น datetime.date"""
    value = value or date(1995, 1, 1)
    st.markdown(f"**{label}**")

    this_be = date.today().year + 543
    years = list(range(this_be, this_be - 121, -1))
    year_be_default = value.year + 543
    year_index = years.index(year_be_default) if year_be_default in years else 0

    c1, c2, c3 = st.columns([1, 1.7, 1.2])
    with c1:
        day = st.selectbox("วัน", list(range(1, 32)), index=value.day - 1, key=f"{key}_d")
    with c2:
        month = st.selectbox(
            "เดือน", list(range(1, 13)), index=value.month - 1,
            format_func=lambda m: THAI_MONTHS[m - 1], key=f"{key}_m",
        )
    with c3:
        year_be = st.selectbox("ปี (พ.ศ.)", years, index=year_index, key=f"{key}_y")

    year = year_be - 543
    last_day = calendar.monthrange(year, month)[1]
    if day > last_day:
        st.caption(f"เดือนนี้มีแค่ {last_day} วัน ระบบปรับเป็นวันที่ {last_day} ให้อัตโนมัติ")
        day = last_day
    result = date(year, month, day)
    if result > date.today():
        st.caption("วันเกิดเป็นอนาคตไม่ได้ ระบบปรับเป็นวันนี้ให้")
        result = date.today()
    return result


def thai_date_text(d):
    d = parse_date(d)
    return f"{d.day} {THAI_MONTHS[d.month - 1]} {d.year + 543}"


@st.cache_data(show_spinner=False)
def load_address_data():
    """โหลดฐานข้อมูลที่อยู่ไทย: ใช้ไฟล์ thai_address.csv ถ้ามี ไม่งั้นใช้ข้อมูลตัวอย่าง"""
    if os.path.exists(ADDRESS_CSV):
        try:
            df = pd.read_csv(ADDRESS_CSV, dtype=str).fillna("")
            df = df.rename(columns={
                "postcode": "zipcode", "postal_code": "zipcode",
                "district": "amphoe", "subdistrict": "tambon",
            })
            return df[["zipcode", "province", "amphoe", "tambon"]]
        except Exception:
            pass
    rows = []
    sample = {
        ("10110", "กรุงเทพมหานคร", "เขตคลองเตย"): ["คลองเตย", "คลองตัน", "พระโขนง"],
        ("21000", "ระยอง", "เมืองระยอง"): ["ท่าประดู่", "เชิงเนิน", "ตะพง", "ปากน้ำ", "ทับมา", "น้ำคอก", "เนินพระ"],
        ("50200", "เชียงใหม่", "เมืองเชียงใหม่"): ["ศรีภูมิ", "พระสิงห์", "หายยา"],
        ("40000", "ขอนแก่น", "เมืองขอนแก่น"): ["ในเมือง", "ศิลา", "บึงเนียม"],
    }
    for (z, p, a), tambons in sample.items():
        for t in tambons:
            rows.append({"zipcode": z, "province": p, "amphoe": a, "tambon": t})
    return pd.DataFrame(rows)


def _index_of(options, value):
    try:
        return options.index(value)
    except ValueError:
        return 0


def address_input(prefix, saved=None):
    """รหัสไปรษณีย์ → จังหวัด → อำเภอ → ตำบล + บ้านเลขที่"""
    saved = saved or {}
    df = load_address_data()

    postal = st.text_input(
        "รหัสไปรษณีย์", value=saved.get("postal_code") or "", max_chars=5,
        key=f"{prefix}_postal", help="กรอกรหัสไปรษณีย์ 5 หลัก แล้วกด Enter",
    ).strip()

    province = district = subdistrict = ""
    matches = df[df["zipcode"] == postal] if len(postal) == 5 else df.iloc[0:0]

    if len(postal) == 5 and matches.empty:
        st.warning(
            "ไม่พบรหัสไปรษณีย์นี้ในฐานข้อมูลที่มี กรุณากรอกเอง "
            "(หรือวางไฟล์ thai_address.csv เพื่อให้ครบทุกพื้นที่)"
        )
        province = st.text_input("จังหวัด", value=saved.get("province") or "", key=f"{prefix}_prov_txt")
        district = st.text_input("อำเภอ/เขต", value=saved.get("district") or "", key=f"{prefix}_dist_txt")
        subdistrict = st.text_input("ตำบล/แขวง", value=saved.get("subdistrict") or "", key=f"{prefix}_sub_txt")
    elif not matches.empty:
        provinces = sorted(matches["province"].unique())
        province = st.selectbox(
            "จังหวัด", provinces, index=_index_of(provinces, saved.get("province")), key=f"{prefix}_prov"
        )
        districts = sorted(matches[matches["province"] == province]["amphoe"].unique())
        district = st.selectbox(
            "อำเภอ/เขต", districts, index=_index_of(districts, saved.get("district")), key=f"{prefix}_dist"
        )
        tambons = sorted(
            matches[(matches["province"] == province) & (matches["amphoe"] == district)]["tambon"].unique()
        )
        subdistrict = st.selectbox(
            "ตำบล/แขวง", tambons, index=_index_of(tambons, saved.get("subdistrict")), key=f"{prefix}_sub"
        )
    else:
        st.caption("กรอกรหัสไปรษณีย์ 5 หลัก ระบบจะแสดงจังหวัด อำเภอ ตำบลให้เลือก")

    house_no = st.text_input(
        "บ้านเลขที่ / หมู่ / ซอย / ถนน", value=saved.get("house_no") or "", key=f"{prefix}_house"
    )
    return {
        "postal_code": postal,
        "province": province,
        "district": district,
        "subdistrict": subdistrict,
        "house_no": house_no.strip(),
    }


def format_address(a):
    if not a:
        return "-"
    bkk = (a.get("province") or "").startswith("กรุงเทพ")
    parts = []
    if a.get("house_no"):
        parts.append(a["house_no"])
    if a.get("subdistrict"):
        parts.append(("แขวง" if bkk else "ต.") + a["subdistrict"].replace("แขวง", ""))
    if a.get("district"):
        parts.append(a["district"] if bkk else "อ." + a["district"].replace("อำเภอ", ""))
    if a.get("province"):
        parts.append(a["province"] if bkk else "จ." + a["province"])
    if a.get("postal_code"):
        parts.append(a["postal_code"])
    return " ".join(parts) if parts else "-"


# ============================================================
# AUTH / USERS
# ============================================================
def hash_password(password, salt=None):
    salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000
    ).hex()
    return salt, digest


def verify_password(password, salt, stored_hash):
    _, digest = hash_password(password, salt)
    return hmac.compare_digest(digest, stored_hash)


def register_user(username, password, full_name, citizen_id, birthdate, gender,
                  phone, email, addr):
    conn = get_conn()
    try:
        salt, password_hash = hash_password(password)
        conn.execute(
            """
            INSERT INTO users
            (username, password_hash, salt, full_name, citizen_id, birthdate,
             gender, phone, email, address, postal_code, province, district,
             subdistrict, house_no, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username.strip(), password_hash, salt, full_name.strip(),
                citizen_id.strip(), str(birthdate), gender, phone.strip(),
                email.strip(), format_address(addr),
                addr["postal_code"], addr["province"], addr["district"],
                addr["subdistrict"], addr["house_no"],
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        return True, "สมัครสมาชิกสำเร็จ"
    except sqlite3.IntegrityError:
        return False, "ชื่อผู้ใช้นี้มีอยู่แล้ว"
    finally:
        conn.close()


def get_secret(name):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name)


def ensure_admin():
    """สร้างตาราง log และบัญชีแอดมินเริ่มต้น (ถ้ายังไม่มีแอดมินเลย)
    ตั้งค่าได้ด้วย ADMIN_USERNAME / ADMIN_PASSWORD (st.secrets หรือ environment)
    ถ้าไม่ตั้งรหัสผ่าน ระบบจะสุ่มรหัสและพิมพ์ใน terminal ครั้งเดียว"""
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER,
            action TEXT NOT NULL,
            detail TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    has_admin = conn.execute("SELECT 1 FROM users WHERE role = 'admin' LIMIT 1").fetchone()
    if not has_admin:
        username = (get_secret("ADMIN_USERNAME") or "admin").strip()
        password = get_secret("ADMIN_PASSWORD")
        existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            conn.execute("UPDATE users SET role = 'admin' WHERE id = ?", (existing["id"],))
        else:
            generated = not password
            password = password or pysecrets.token_urlsafe(9)
            salt, pw_hash = hash_password(password)
            conn.execute(
                """
                INSERT INTO users (username, password_hash, salt, full_name, birthdate,
                                   gender, created_at, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'admin', 1)
                """,
                (username, pw_hash, salt, "ผู้ดูแลระบบ", "1990-01-01", "ชาย",
                 datetime.now().isoformat(timespec="seconds")),
            )
            if generated:
                print(f"[Thai Balance] สร้างบัญชีแอดมิน username={username} password={password} "
                      "(เปลี่ยนรหัสผ่านทันที หรือตั้ง ADMIN_PASSWORD)", flush=True)
    conn.commit()
    conn.close()


ensure_admin()


def login_user(username, password):
    """คืนค่า (user, error)"""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username.strip(),)
    ).fetchone()
    if row and verify_password(password, row["salt"], row["password_hash"]):
        if row["is_active"] == 0:
            conn.close()
            return None, "บัญชีนี้ถูกระงับการใช้งาน กรุณาติดต่อผู้ดูแลระบบ"
        conn.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now().isoformat(timespec="seconds"), row["id"]),
        )
        conn.commit()
        conn.close()
        return dict(get_user(row["id"])), None
    conn.close()
    return None, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"


def get_user(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user(user_id, f, addr, image=None, image_type=None):
    sets = [
        "full_name=?", "citizen_id=?", "birthdate=?", "gender=?", "phone=?",
        "email=?", "address=?", "postal_code=?", "province=?", "district=?",
        "subdistrict=?", "house_no=?",
    ]
    vals = [
        f["full_name"].strip(), f["citizen_id"].strip(), str(f["birthdate"]),
        f["gender"], f["phone"].strip(), f["email"].strip(), format_address(addr),
        addr["postal_code"], addr["province"], addr["district"],
        addr["subdistrict"], addr["house_no"],
    ]
    if image is not None:
        sets += ["profile_image=?", "profile_image_type=?"]
        vals += [image, image_type]
    vals.append(user_id)
    conn = get_conn()
    conn.execute(f"UPDATE users SET {', '.join(sets)} WHERE id=?", vals)
    conn.commit()
    conn.close()


def update_birthdate(user_id, birthdate):
    conn = get_conn()
    conn.execute("UPDATE users SET birthdate=? WHERE id=?", (str(birthdate), user_id))
    conn.commit()
    conn.close()


def refresh_session_user():
    u = st.session_state.get("user")
    if u:
        fresh = get_user(u["id"])
        if fresh:
            st.session_state.user = fresh
            return fresh
    return u


# ============================================================
# HEALTH / MEALS / CHAT DB
# ============================================================
def get_health(user_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM health_data WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else {}


def get_history(health):
    try:
        return json.loads(health.get("history_json") or "{}")
    except Exception:
        return {}


def save_health(user_id, data):
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO health_data
        (user_id, cc, pi, ph, fh, chronic, weight, height, bmi, constitution,
         history_json, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id, data["cc"], data["pi"], data["ph"], data["fh"],
            json.dumps(data["chronic"], ensure_ascii=False),
            data["weight"], data["height"], data["bmi"], data["constitution"],
            json.dumps(data["history"], ensure_ascii=False),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()


def save_meal(user_id, meal):
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO meals
        (user_id, meal_date, meal_time, meal_type, food_name, ingredients,
         amount, calories, image, image_type, note, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id, meal["meal_date"], meal["meal_time"], meal["meal_type"],
            meal["food_name"], meal["ingredients"], meal["amount"],
            meal["calories"], meal["image"], meal["image_type"], meal["note"],
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()


def get_meals(user_id, limit=None):
    conn = get_conn()
    query = """
        SELECT id, meal_date, meal_time, meal_type, food_name,
               ingredients, amount, calories, image, image_type, note, created_at
        FROM meals
        WHERE user_id = ?
        ORDER BY meal_date DESC, meal_time DESC, id DESC
    """
    params = [user_id]
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


EXERCISE_MET = {
    "เดินเร็ว": 4.0, "วิ่ง": 8.5, "ปั่นจักรยาน": 6.8, "ว่ายน้ำ": 7.0,
    "โยคะ": 2.8, "ยกน้ำหนัก/เวทเทรนนิ่ง": 5.0, "แอโรบิก/เต้น": 6.5,
    "มวยไทย/ศิลปะการต่อสู้": 7.5, "แบดมินตัน/เทนนิส": 5.5,
    "ฟุตบอล/บาสเกตบอล": 7.0, "ไทเก็ก/ชี่กง": 3.0, "อื่น ๆ": 4.0,
}
INTENSITY_FACTOR = {"เบา": 0.8, "ปานกลาง": 1.0, "หนัก": 1.25}


def estimate_exercise_calories(ex_type, minutes, intensity, weight):
    met = EXERCISE_MET.get(ex_type, 4.0) * INTENSITY_FACTOR.get(intensity, 1.0)
    w = weight or 60
    return round(met * float(w) * (float(minutes) / 60.0), 0)


def save_exercise(user_id, ex):
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO exercises
        (user_id, ex_date, ex_time, ex_type, duration_min, intensity, calories, note, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id, ex["ex_date"], ex["ex_time"], ex["ex_type"], ex["duration_min"],
            ex["intensity"], ex["calories"], ex["note"],
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()


def get_exercises(user_id, limit=None):
    conn = get_conn()
    query = """
        SELECT id, ex_date, ex_time, ex_type, duration_min, intensity, calories, note
        FROM exercises WHERE user_id = ?
        ORDER BY ex_date DESC, ex_time DESC, id DESC
    """
    params = [user_id]
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_chat(user_id, role, message):
    conn = get_conn()
    conn.execute(
        "INSERT INTO ai_chat (user_id, role, message, created_at) VALUES (?, ?, ?, ?)",
        (user_id, role, message, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def get_chat(user_id, limit=20):
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT role, message, created_at FROM ai_chat
        WHERE user_id = ? ORDER BY id DESC LIMIT ?
        """,
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def clear_chat(user_id):
    conn = get_conn()
    conn.execute("DELETE FROM ai_chat WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# ============================================================
# HEALTH / FOOD ANALYSIS
# ============================================================
def calc_bmi(weight, height_cm):
    if not weight or not height_cm or height_cm <= 0:
        return None
    h = height_cm / 100
    return round(weight / (h * h), 1)


BMI_TABLE = [
    # (ต่ำสุด, สูงสุด(ไม่รวม), ช่วง BMI, สถานะ, ความเสี่ยง)
    (None, 18.5, "น้อยกว่า 18.5", "น้ำหนักต่ำกว่าเกณฑ์ (ผอม)", "เสี่ยงขาดสารอาหาร ร่างกายอ่อนเพลียง่าย"),
    (18.5, 23.0, "18.5 – 22.9", "น้ำหนักปกติ (สุขภาพดี)", "มีความเสี่ยงต่ำที่สุด ห่างไกลโรคที่เกิดจากความอ้วน"),
    (23.0, 25.0, "23.0 – 24.9", "น้ำหนักเกิน (ท้วม)", "เริ่มมีความเสี่ยงเพิ่มขึ้น ต้องควบคุมอาหาร"),
    (25.0, 30.0, "25.0 – 29.9", "โรคอ้วนระดับ 1", "เสี่ยงต่อโรคเรื้อรัง เช่น ความดันโลหิตสูง เบาหวาน"),
    (30.0, None, "30.0 ขึ้นไป", "โรคอ้วนระดับ 2 (อ้วนมาก)", "เสี่ยงอันตรายต่อโรคหัวใจและหลอดเลือดสูงมาก"),
]


def bmi_row(bmi):
    if bmi is None:
        return None
    for lo, hi, *_ in BMI_TABLE:
        if (lo is None or bmi >= lo) and (hi is None or bmi < hi):
            return BMI_TABLE[[r[0:2] for r in BMI_TABLE].index((lo, hi))]
    return None


def bmi_status(bmi):
    row = bmi_row(bmi)
    return row[3] if row else "ยังไม่มีข้อมูล"


def render_bmi_explainer(weight=None, height_cm=None, bmi=None):
    """แสดงเฉพาะค่า BMI ของผู้ใช้ พร้อมสถานะและความเสี่ยงของช่วงนั้น"""
    with st.container(border=True):
        st.markdown("#### ⚖️ BMI ของคุณ")
        row = bmi_row(bmi)
        if row is None:
            st.info("ยังไม่มีข้อมูลน้ำหนัก/ส่วนสูง กรุณากรอกในหน้า 'สุขภาพ / ซักประวัติ'")
            return
        st.markdown(f"### {bmi}")
        st.write(f"**สถานะ:** {row[3]}")
        st.write(f"**ความเสี่ยง:** {row[4]}")
        if weight and height_cm:
            st.caption(f"น้ำหนัก {weight:g} กก. • ส่วนสูง {height_cm:g} ซม.")


def render_constitution_explainer(constitution):
    """แสดงข้อมูลเฉพาะธาตุเจ้าเรือนของผู้ใช้"""
    with st.container(border=True):
        if constitution not in CONSTITUTION_GUIDE:
            st.markdown("#### 🌿 ธาตุเจ้าเรือน")
            st.info("กรุณากรอกวันเดือนปีเกิดในหน้าโปรไฟล์ (ปุ่ม ☰ มุมซ้ายบน) เพื่อดูธาตุเจ้าเรือนของคุณ")
            return
        g = CONSTITUTION_GUIDE[constitution]
        st.markdown(f"#### {g['icon']} {constitution}")
        st.write(f"**ลักษณะเด่น:** {g['เด่น']}")
        st.write(f"**อาหารที่ควรทาน:** {g['ควร']}")
        st.write(f"**สิ่งที่ควรเลี่ยง:** {g['เลี่ยง']}")
        st.caption("เป็นข้อมูลทั่วไป ไม่ใช่การวินิจฉัยทางแพทย์แผนไทย")


def constitution_from_birthdate(birthdate):
    """จัดธาตุเจ้าเรือนตามเดือนเกิด (ข้อมูลทั่วไปเพื่อประกอบคำแนะนำ ไม่ใช่การวินิจฉัย
    ควรให้แพทย์แผนไทยประเมินอีกครั้ง)"""
    month = birthdate.month
    if month in (1, 2, 3):
        return "ธาตุไฟ"
    if month in (4, 5, 6):
        return "ธาตุลม"
    if month in (7, 8, 9):
        return "ธาตุน้ำ"
    return "ธาตุดิน"


CONSTITUTION_GUIDE = {
    "ธาตุไฟ": {
        "icon": "🔥",
        "เดือน": "มกราคม – มีนาคม",
        "เด่น": "ระบบเผาผลาญดี ขี้ร้อน หงุดหงิดง่าย",
        "ควร": "อาหารรสขม เย็น จืด",
        "เลี่ยง": "อาหารรสหวาน เผ็ด เปรี้ยว เค็มจัด แอลกอฮอล์ ชา และกาแฟ",
    },
    "ธาตุลม": {
        "icon": "🌬️",
        "เดือน": "เมษายน – มิถุนายน",
        "เด่น": "ผอมบาง ผิวแห้ง ขี้หนาว อารมณ์เปลี่ยนแปลงง่าย",
        "ควร": "อาหารรสเผ็ดร้อน (เช่น ขิง ข่า ตะไคร้) ช่วยขับลม",
        "เลี่ยง": "อาหารรสหวานหรือมันมากเกินไป",
    },
    "ธาตุน้ำ": {
        "icon": "💧",
        "เดือน": "กรกฎาคม – กันยายน",
        "เด่น": "รูปร่างอวบสมบูรณ์ ผิวพรรณสดใส ใจเย็น แต่อาจมีเสมหะหรือชื้นในร่างกายง่าย",
        "ควร": "อาหารรสเปรี้ยวและรสขม (เช่น มะนาว ส้มโอ มะเขือเทศ)",
        "เลี่ยง": "นม เนย และอาหารเค็มหรือโซเดียมสูง",
    },
    "ธาตุดิน": {
        "icon": "🌍",
        "เดือน": "ตุลาคม – ธันวาคม",
        "เด่น": "รูปร่างหนา กระดูกใหญ่ มั่นคง แข็งแรง แต่อาจป่วยด้วยเรื่องระบบย่อยอาหาร",
        "ควร": "อาหารรสฝาด หวาน มัน และเค็มพอดี",
        "เลี่ยง": "ของทอด และอาหารมันจัด",
    },
}


FOOD_KEYWORDS = {
    "ข้าว": 200, "ข้าวมันไก่": 650, "กะเพรา": 550, "ผัด": 450, "ทอด": 500,
    "แกง": 300, "ต้ม": 180, "ส้มตำ": 250, "ก๋วยเตี๋ยว": 400, "ขนม": 250,
    "ชาเย็น": 250, "กาแฟ": 120, "น้ำหวาน": 180, "ผลไม้": 100, "สลัด": 180,
}


def estimate_calories(food_name, amount=""):
    text = (food_name or "").lower()
    for key, kcal in FOOD_KEYWORDS.items():
        if key in text:
            return float(kcal)
    return 300.0


def analyze_meal(food_name, ingredients="", amount=""):
    text = f"{food_name} {ingredients} {amount}".lower()
    risks, tips = [], []

    if any(x in text for x in ["ทอด", "กรอบ", "หมูสามชั้น"]):
        risks.append("มีแนวโน้มไขมันสูง")
        tips.append("พิจารณาลดอาหารทอดหรือเลือกวิธีต้ม/นึ่ง/ย่าง")
    if any(x in text for x in ["เค็ม", "ปลาเค็ม", "บะหมี่กึ่ง", "น้ำปลา"]):
        risks.append("อาจมีโซเดียมสูง")
        tips.append("ลดเครื่องปรุงเค็มและชิมก่อนปรุงเพิ่ม")
    if any(x in text for x in ["หวาน", "ชาเย็น", "น้ำหวาน", "ขนม"]):
        risks.append("อาจมีน้ำตาลสูง")
        tips.append("ลดน้ำตาลหรือเลือกเครื่องดื่มไม่หวาน")
    if any(x in text for x in ["ผัก", "สลัด", "ผลไม้"]):
        tips.append("มีผัก/ผลไม้ ช่วยเพิ่มใยอาหาร")
    if not risks:
        risks.append("ยังไม่พบความเสี่ยงจากคำสำคัญที่บันทึก")
    if not tips:
        tips.append("ควรรับประทานให้หลากหลายและเหมาะกับความต้องการของแต่ละบุคคล")

    return {"calories": estimate_calories(food_name, amount), "risks": risks, "tips": tips}


def risk_alert(user, health, meals):
    alerts = []
    bmi = health.get("bmi")
    if bmi is not None and bmi >= 25:
        alerts.append("BMI อยู่ในกลุ่มน้ำหนักเกิน/อ้วน ควรติดตามน้ำหนักและพฤติกรรมการกินอย่างสม่ำเสมอ")
    if bmi is not None and bmi < 18.5:
        alerts.append("BMI อยู่ในกลุ่มน้ำหนักน้อย ควรประเมินการได้รับพลังงานและสารอาหาร")
    if health.get("chronic"):
        try:
            chronic = [c for c in json.loads(health["chronic"]) if c != "ไม่มีโรคประจำตัว"]
        except Exception:
            chronic = []
        if chronic:
            alerts.append("มีโรคประจำตัว: คำแนะนำอาหารควรพิจารณาร่วมกับโรคประจำตัวและยาที่ใช้อยู่")

    hist = get_history(health)
    if hist.get("ph_drug_allergy_choice") == "มี" or hist.get("ph_food_allergy_choice") == "มี":
        alerts.append("มีประวัติแพ้ยา/แพ้อาหาร ควรตรวจสอบส่วนประกอบก่อนรับประทานหรือใช้ยาทุกครั้ง")
    try:
        sleep = float(hist.get("lf_sleep_hours") or 0)
        if 0 < sleep < 6:
            alerts.append("ชั่วโมงนอนค่อนข้างน้อย (ต่ำกว่า 6 ชม./วัน) ควรปรับเวลาพักผ่อน")
    except (TypeError, ValueError):
        pass
    if hist.get("lf_smoking") not in (None, "", "ไม่สูบ"):
        alerts.append("มีการสูบบุหรี่ ควรพิจารณาปรึกษาเรื่องการลด/เลิกบุหรี่")
    if hist.get("lf_alcohol") in ("สัปดาห์ละหลายครั้ง", "ทุกวัน"):
        alerts.append("ดื่มแอลกอฮอล์ค่อนข้างบ่อย ควรลดปริมาณและความถี่")

    if meals:
        analyses = [analyze_meal(m["food_name"], m["ingredients"], m["amount"])["risks"] for m in meals]
        high_fat = sum("ไขมันสูง" in r for risks in analyses for r in risks)
        high_salt = sum("โซเดียมสูง" in r for risks in analyses for r in risks)
        if high_fat >= 2:
            alerts.append("พบมื้ออาหารที่มีแนวโน้มไขมันสูงหลายมื้อ")
        if high_salt >= 2:
            alerts.append("พบมื้ออาหารที่มีแนวโน้มโซเดียมสูงหลายมื้อ")
    return alerts


# ============================================================
# AI — OpenAI (ถ้ามี API key) + โหมดตอบจากข้อมูลในระบบ (สำรอง)
# ============================================================
def get_openai_key():
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def ai_text_response(prompt, user_context="", history=None):
    """คืนค่า (คำตอบ, ข้อความผิดพลาด) ถ้าเรียก AI ไม่ได้ คำตอบจะเป็น None"""
    api_key = get_openai_key()
    if not api_key:
        return None, "ยังไม่ได้ตั้งค่า OPENAI_API_KEY"

    convo = ""
    for h in (history or []):
        who = "ผู้ใช้" if h["role"] == "user" else "AI"
        convo += f"{who}: {h['message']}\n"

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-6-luna"),
            instructions=(
                "คุณคือ 'หมอไทยบอท' ผู้ช่วยด้านแพทย์แผนไทยเบื้องต้นของระบบ Thai Balance "
                "ตอบภาษาไทย กระชับ เข้าใจง่าย อธิบายตามหลักแพทย์แผนไทย (ธาตุ 4 ตรีโทษ "
                "สมุนไพรพื้นบ้านที่ใช้กันทั่วไป อาหาร การนวด/ประคบ) และไม่วินิจฉัยโรค "
                "ทุกครั้งที่แนะนำสมุนไพรให้ระบุข้อควรระวัง (ตั้งครรภ์ โรคประจำตัว ยาที่ใช้ประจำ การแพ้) "
                "และบอกอาการที่ควรไปพบแพทย์ทันที แยกคำแนะนำทั่วไปออกจากข้อมูลที่ยังไม่แน่ใจ"
            ),
            input=(
                f"บริบทผู้ใช้:\n{user_context}\n\n"
                f"ประวัติการสนทนาล่าสุด:\n{convo}\n"
                f"คำถามใหม่:\n{prompt}"
            ),
        )
        return response.output_text, None
    except Exception as exc:
        return None, str(exc)



# ============================================================
# หมอไทยบอท — ฐานความรู้แพทย์แผนไทยเบื้องต้น (ข้อมูลทั่วไป ไม่ใช่การวินิจฉัย)
# ============================================================
THAI_MED_KB = [
    {
        "title": "หลักแพทย์แผนไทยเบื้องต้น",
        "keywords": ["ธาตุ", "ตรีโทษ", "วาตะ", "ปิตตะ", "เสมหะ", "แพทย์แผนไทย", "หมอไทย"],
        "text": (
            "แพทย์แผนไทยมองว่าสุขภาพดีคือภาวะที่ **ธาตุ 4 (ดิน น้ำ ลม ไฟ)** สมดุลกัน "
            "และมี **ตรีโทษ** (วาตะ-ลม, ปิตตะ-ความร้อน/น้ำดี, เสมหะ-ความชุ่มชื้น) อยู่ในระดับพอดี\n\n"
            "เมื่อธาตุเสียสมดุล เช่น จากอาหาร อากาศ ฤดูกาล การพักผ่อน หรืออารมณ์ ก็อาจเกิดอาการต่าง ๆ ได้ "
            "โดยทั่วไปเชื่อว่าฤดูร้อนธาตุไฟ/ปิตตะเด่น ฤดูฝนธาตุลม/วาตะเด่น และฤดูหนาวธาตุน้ำ/เสมหะเด่น\n\n"
            "การดูแลเบื้องต้นคือกินอาหารให้เหมาะกับร่างกายและฤดูกาล นอนให้พอ ออกกำลังกายเบา ๆ "
            "และจัดการความเครียด"
        ),
    },
    {
        "title": "ไข้",
        "keywords": ["ไข้", "ตัวร้อน", "ตัวรุม", "ยาเขียวหอม"],
        "text": (
            "การดูแลเมื่อมีไข้ต่ำ ๆ: พักผ่อนให้พอ จิบน้ำหรือน้ำสมุนไพรอุ่น ๆ บ่อย ๆ "
            "เช็ดตัวด้วยน้ำอุ่นเพื่อช่วยระบายความร้อน และกินอาหารย่อยง่าย เช่น ข้าวต้ม แกงจืด\n\n"
            "ตำรับพื้นบ้านที่มักกล่าวถึงคือ ยาเขียวหอม (ใช้ตามฉลาก) และฟ้าทะลายโจร (ในกรณีไข้หวัดทั่วไป)\n\n"
            "**ควรพบแพทย์:** ไข้ 39 °C ขึ้นไป ไข้ไม่ลงภายใน 2–3 วัน ซึม ชัก หายใจเหนื่อย ผื่นขึ้นพร้อมไข้ "
            "หรือเป็นเด็กเล็ก/ผู้สูงอายุ/หญิงตั้งครรภ์"
        ),
    },
    {
        "title": "หวัด ไอ เจ็บคอ",
        "keywords": ["หวัด", "ไอ", "เจ็บคอ", "น้ำมูก", "ฟ้าทะลายโจร", "มะแว้ง", "ขิง"],
        "text": (
            "อาการหวัดเบื้องต้น: พักผ่อน ดื่มน้ำอุ่น ล้างมือ ใส่หน้ากากเมื่อมีอาการ\n\n"
            "สมุนไพรที่ใช้กันทั่วไป:\n"
            "• **ฟ้าทะลายโจร** — บรรเทาหวัด เจ็บคอ ใช้ตามขนาดบนฉลาก ไม่ควรใช้ต่อเนื่องเกินที่ฉลากกำหนด "
            "ห้ามใช้ในผู้แพ้ และควรปรึกษาแพทย์ถ้าตั้งครรภ์หรือมีโรคตับ/ไต\n"
            "• **ผลมะแว้ง / มะขามป้อม / น้ำขิงอุ่น ๆ** — ช่วยบรรเทาอาการไอ ระคายคอ\n\n"
            "**ควรพบแพทย์:** ไข้สูง หายใจลำบาก เจ็บหน้าอก ไอเป็นเลือด หรืออาการไม่ดีขึ้นใน 5–7 วัน"
        ),
    },
    {
        "title": "ท้องอืด แน่นท้อง จุกเสียด",
        "keywords": ["ท้องอืด", "แน่นท้อง", "จุกเสียด", "ท้องเฟ้อ", "ขับลม", "ขมิ้น", "กะเพรา", "กระเพรา", "ยาธาตุ"],
        "text": (
            "แนวทางเบื้องต้น: กินช้า ๆ แบ่งเป็นมื้อเล็ก ๆ เลี่ยงอาหารมัน ของหมักดอง น้ำอัดลม "
            "และไม่นอนทันทีหลังกิน\n\n"
            "สมุนไพรที่ใช้ขับลม/บรรเทาท้องอืด:\n"
            "• **ขิง** — น้ำขิงอุ่น ๆ ช่วยลดคลื่นไส้ ท้องอืด (ระวังหากใช้ยาละลายลิ่มเลือด)\n"
            "• **ขมิ้นชัน** — ใช้บรรเทาจุกเสียด แน่นท้อง ตามขนาดบนฉลาก "
            "(ระวังในผู้มีนิ่วในถุงน้ำดี/ท่อน้ำดีอุดตัน และผู้ใช้ยาละลายลิ่มเลือด)\n"
            "• **กะเพรา / ยาธาตุน้ำขาว** — ช่วยขับลม\n\n"
            "**ควรพบแพทย์:** ปวดท้องรุนแรง อาเจียนมาก ถ่ายดำ/มีเลือด น้ำหนักลดโดยไม่ทราบสาเหตุ"
        ),
    },
    {
        "title": "ท้องผูก",
        "keywords": ["ท้องผูก", "ถ่ายยาก", "มะขามแขก", "ขับถ่าย"],
        "text": (
            "เริ่มจากปรับพฤติกรรม: ดื่มน้ำให้พอ กินผัก ผลไม้ที่มีกาก (เช่น มะละกอสุก ส้มโอ แก้วมังกร) "
            "ออกกำลังกายเบา ๆ และถ่ายเป็นเวลา\n\n"
            "ยาสมุนไพรระบายอย่าง **มะขามแขก** ใช้ตามฉลากเป็นครั้งคราว ไม่ควรใช้ต่อเนื่อง "
            "และห้ามใช้ในหญิงตั้งครรภ์หรือผู้ปวดท้องรุนแรงโดยไม่ทราบสาเหตุ\n\n"
            "**ควรพบแพทย์:** ท้องผูกเรื้อรังเกิน 2 สัปดาห์ ถ่ายมีเลือดปน หรือลำไส้เปลี่ยนนิสัยอย่างชัดเจน"
        ),
    },
    {
        "title": "ท้องเสีย",
        "keywords": ["ท้องเสีย", "ท้องร่วง", "ถ่ายเหลว"],
        "text": (
            "สิ่งสำคัญที่สุดคือป้องกันการขาดน้ำ: จิบ **ผงเกลือแร่ (ORS)** บ่อย ๆ "
            "กินอาหารอ่อน เช่น ข้าวต้ม เลี่ยงนม ของมัน ของเผ็ด\n\n"
            "**ควรพบแพทย์:** ถ่ายเป็นเลือด มีไข้สูง อาเจียนมาก ปัสสาวะน้อย ซึม ท้องเสียเกิน 2 วัน "
            "หรือเป็นเด็กเล็ก/ผู้สูงอายุ"
        ),
    },
    {
        "title": "นอนไม่หลับ / เครียด",
        "keywords": ["นอนไม่หลับ", "หลับยาก", "เครียด", "นอนน้อย", "วิตกกังวล"],
        "text": (
            "แนวทางเบื้องต้น: เข้านอน-ตื่นให้เป็นเวลา งดคาเฟอีนช่วงบ่าย-เย็น ลดหน้าจอก่อนนอน "
            "อาบน้ำอุ่น ฝึกหายใจช้า ๆ หรือสวดมนต์/นั่งสมาธิสั้น ๆ\n\n"
            "ตามแนวแพทย์แผนไทย การนวดผ่อนคลาย (เช่น ศีรษะ คอ บ่า ฝ่าเท้า) และอาหารอุ่นย่อยง่ายช่วยลดธาตุลมที่กำเริบ\n\n"
            "**ควรพบแพทย์:** นอนไม่หลับต่อเนื่องเกิน 2–3 สัปดาห์ รู้สึกเศร้า สิ้นหวัง หรือมีความคิดทำร้ายตนเอง"
        ),
    },
    {
        "title": "ปวดเมื่อย / นวด / ประคบ",
        "keywords": ["ปวดเมื่อย", "ปวดหลัง", "ปวดคอ", "ปวดไหล่", "ออฟฟิศซินโดรม", "นวด", "ประคบ", "กล้ามเนื้อ"],
        "text": (
            "สำหรับปวดเมื่อยกล้ามเนื้อทั่วไป: พักการใช้งานหนัก ยืดเหยียดเบา ๆ ปรับท่านั่งทำงาน "
            "ลุกเดินทุก 30–60 นาที\n\n"
            "• **นวดไทย** ช่วยคลายกล้ามเนื้อและเพิ่มการไหลเวียน\n"
            "• **ลูกประคบสมุนไพร** (ไพล ขมิ้นชัน ตะไคร้ การบูร) ประคบอุ่นช่วยลดตึง ไม่ควรประคบบริเวณที่บวมแดงร้อนจัด "
            "แผลเปิด หรือเมื่อมีไข้\n\n"
            "**ควรพบแพทย์:** ปวดร้าวลงขา ชา อ่อนแรง ปวดหลังจากอุบัติเหตุ หรือปวดไม่ดีขึ้นใน 1–2 สัปดาห์"
        ),
    },
    {
        "title": "ปวดศีรษะ",
        "keywords": ["ปวดหัว", "ปวดศีรษะ", "ไมเกรน", "เวียนหัว"],
        "text": (
            "แนวทางเบื้องต้น: พักในที่เงียบ ดื่มน้ำให้พอ ลดคาเฟอีน/อดนอน นวดคลายกล้ามเนื้อคอ บ่า ไหล่ "
            "และอาจใช้ยาหม่อง/น้ำมันสมุนไพรทาบริเวณขมับหรือต้นคอ (ระวังผิวแพ้ง่ายและเด็กเล็ก)\n\n"
            "**ไปพบแพทย์ทันที:** ปวดรุนแรงฉับพลัน ปวดร่วมกับชา อ่อนแรง พูดไม่ชัด ตามัว คอแข็ง ไข้สูง หรือปวดหลังศีรษะกระแทก"
        ),
    },
    {
        "title": "สมุนไพรและข้อควรระวัง",
        "keywords": ["สมุนไพร", "ยาสมุนไพร", "ชาสมุนไพร", "ยาหม่อง", "ผลข้างเคียง"],
        "text": (
            "สมุนไพรไม่ได้ปลอดภัยเสมอไป ข้อควรระวังทั่วไป:\n"
            "• เลือกผลิตภัณฑ์ที่มีทะเบียนยา/อย. และใช้ตามขนาดบนฉลาก\n"
            "• หญิงตั้งครรภ์/ให้นมบุตร เด็กเล็ก ผู้มีโรคตับ ไต หัวใจ หรือใช้ยาประจำ "
            "(โดยเฉพาะยาละลายลิ่มเลือด ยาเบาหวาน ยาความดัน) ควรปรึกษาแพทย์หรือเภสัชกรก่อน\n"
            "• หยุดใช้ทันทีหากมีผื่น คัน หายใจลำบาก คลื่นไส้อาเจียนมาก\n"
            "• ไม่ควรใช้สมุนไพรแทนการรักษาโรคเรื้อรังโดยไม่ปรึกษาแพทย์"
        ),
    },
]


def thai_med_answer(prompt, user, health):
    """ค้นฐานความรู้แพทย์แผนไทยด้วยคำสำคัญ คืนข้อความคำตอบ หรือ None ถ้าไม่เจอ"""
    scored = []
    for entry in THAI_MED_KB:
        score = sum(1 for k in entry["keywords"] if k in prompt)
        if score:
            scored.append((score, entry))
    if not scored:
        return None
    scored.sort(key=lambda x: -x[0])
    chosen = [e for _, e in scored[:2]]

    parts = []
    for e in chosen:
        parts.append(f"**🌿 {e['title']}**\n\n{e['text']}")

    hist = get_history(health)
    try:
        chronic = [c for c in json.loads(health.get("chronic") or "[]") if c != "ไม่มีโรคประจำตัว"]
    except Exception:
        chronic = []
    if chronic or hist.get("ph_regular_meds") or hist.get("ph_drug_allergy_choice") == "มี" \
            or hist.get("ph_food_allergy_choice") == "มี":
        parts.append(
            "⚠️ ในข้อมูลของคุณมีโรคประจำตัว/ยาที่ใช้ประจำ/ประวัติแพ้ "
            "ควรปรึกษาแพทย์หรือเภสัชกรก่อนใช้สมุนไพรทุกครั้ง"
        )
    cons = health.get("constitution")
    if cons in CONSTITUTION_GUIDE:
        parts.append(f"💡 ธาตุเจ้าเรือน (ต้นแบบ) ของคุณคือ {cons} — ควรเลี่ยง: {CONSTITUTION_GUIDE[cons]['เลี่ยง']}")
    parts.append("_ข้อมูลทั่วไปตามแพทย์แผนไทยเบื้องต้น ไม่ใช่การวินิจฉัยหรือการรักษา หากอาการรุนแรงควรพบแพทย์_")
    return "\n\n".join(parts)


def local_ai_answer(prompt, user, health, meals):
    """ตอบจากข้อมูลที่ผู้ใช้บันทึกไว้ เมื่อยังไม่ได้ต่อ OpenAI"""
    p = prompt.lower()
    hist = get_history(health)
    bmi = health.get("bmi")
    cons = health.get("constitution")
    guide = CONSTITUTION_GUIDE.get(cons)
    lines = []

    kb_answer = thai_med_answer(p, user, health)
    if kb_answer:
        return kb_answer

    if any(k in p for k in ["อาหาร", "กิน", "มื้อ", "แคลอรี", "ควรกิน", "เมนู"]):
        if guide:
            lines.append(f"จากธาตุเจ้าเรือน ({cons}) แบบต้นแบบ: ควรพิจารณา {guide['ควร']}")
            lines.append(f"ควรจำกัด: {guide['เลี่ยง']}")
        if meals:
            total = sum((m.get("calories") or 0) for m in meals)
            lines.append(f"คุณบันทึกอาหารไว้ {len(meals)} มื้อ พลังงานรวมประมาณ {total:.0f} kcal")
        for a in risk_alert(user, health, meals)[:2]:
            lines.append("• " + a)
        if not lines:
            lines.append("ควรกินให้หลากหลาย เพิ่มผัก ลดหวาน มัน เค็ม และกินให้เป็นเวลา")
    elif any(k in p for k in ["bmi", "น้ำหนัก", "ผอม", "อ้วน", "ลดน้ำหนัก"]):
        if bmi:
            lines.append(f"BMI ของคุณ {bmi} ({bmi_status(bmi)})")
            if bmi >= 23:
                lines.append("แนะนำปรับการกินและออกกำลังกายต่อเนื่อง ลดน้ำตาลและของทอด")
            elif bmi < 18.5:
                lines.append("ควรเพิ่มพลังงานและโปรตีนอย่างเหมาะสม และปรึกษาผู้เชี่ยวชาญ")
            else:
                lines.append("อยู่ในเกณฑ์ที่ดี ควรรักษาพฤติกรรมเดิมต่อไป")
        else:
            lines.append("ยังไม่มีข้อมูลน้ำหนัก/ส่วนสูง กรุณากรอกในหน้า 'ข้อมูลส่วนตัว + ซักประวัติ'")
    elif any(k in p for k in ["นอน", "หลับ", "พักผ่อน"]):
        h = hist.get("lf_sleep_hours")
        lines.append(f"คุณบันทึกเวลานอนไว้ประมาณ {h} ชม./วัน" if h else "ยังไม่มีข้อมูลการนอนในระบบ")
        lines.append("ผู้ใหญ่โดยทั่วไปควรนอนประมาณ 7–9 ชั่วโมง เข้านอนเป็นเวลา และลดคาเฟอีนช่วงเย็น")
    elif any(k in p for k in ["ออกกำลัง", "เดิน", "วิ่ง"]):
        ex = hist.get("lf_exercise")
        lines.append(f"ความถี่การออกกำลังกายที่บันทึก: {ex}" if ex else "ยังไม่มีข้อมูลการออกกำลังกายในระบบ")
        lines.append("เป้าหมายทั่วไปคือกิจกรรมแอโรบิกระดับปานกลางราว 150 นาที/สัปดาห์ เริ่มจากน้อยแล้วค่อยเพิ่ม")
    elif any(k in p for k in ["ธาตุ", "แพทย์แผนไทย"]):
        if guide:
            lines.append(f"ธาตุเจ้าเรือน (ต้นแบบ): {cons} — {guide['เด่น']}")
            lines.append("การจัดธาตุในระบบเป็นการสาธิต ควรให้แพทย์แผนไทยประเมินจริงอีกครั้ง")
        else:
            lines.append("ยังไม่มีข้อมูลธาตุเจ้าเรือน กรุณาบันทึกข้อมูลสุขภาพก่อน")
    elif any(k in p for k in ["อาการ", "ปวด", "ไข้", "เจ็บ", "ป่วย"]):
        cc = health.get("cc")
        if cc:
            lines.append(f"อาการสำคัญที่คุณบันทึกไว้: {cc}")
        lines.append("ระบบนี้ไม่สามารถวินิจฉัยโรคได้ หากอาการรุนแรง เป็นต่อเนื่อง หรือมีไข้สูง หายใจลำบาก เจ็บหน้าอก ควรพบแพทย์ทันที")
    else:
        lines.append(f"สวัสดีคุณ {user.get('full_name', '')} ฉันช่วยตอบเรื่องอาหาร BMI การนอน การออกกำลังกาย และธาตุเจ้าเรือนจากข้อมูลที่คุณบันทึกได้")
        if bmi:
            lines.append(f"ตอนนี้ BMI ของคุณ {bmi} ({bmi_status(bmi)})")
        lines.append("ลองถามเช่น \"วันนี้ควรปรับอาหารอย่างไร\" หรือ \"BMI ของฉันเป็นอย่างไร\"")

    lines.append("\n_หมายเหตุ: เป็นข้อมูลทั่วไป ไม่ใช่การวินิจฉัยหรือการรักษา_")
    return "\n\n".join(lines)


def ai_image_analysis(image_bytes, image_type, user_context=""):
    api_key = get_openai_key()
    if not api_key:
        return (
            "โหมดสาธิต: ยังไม่ได้ตั้งค่า OPENAI_API_KEY จึงไม่สามารถวิเคราะห์ภาพด้วย AI ได้ "
            "กรุณาบันทึกชื่ออาหาร/ส่วนประกอบเพื่อให้ระบบวิเคราะห์เบื้องต้นแทน"
        )
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{image_type};base64,{b64}"
        response = client.responses.create(
            model=os.getenv("OPENAI_VISION_MODEL", "gpt-6-luna"),
            instructions=(
                "วิเคราะห์ภาพอาหารเพื่อช่วยบันทึกข้อมูลโภชนาการเบื้องต้น "
                "ตอบภาษาไทย ห้ามระบุปริมาณสารอาหารอย่างแม่นยำหากมองจากภาพไม่พอ "
                "ให้บอกชื่ออาหารที่คาดว่าเห็น ส่วนประกอบที่สังเกตได้ "
                "ความเสี่ยงด้านหวานมันเค็ม และข้อเสนอแนะทั่วไป"
            ),
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": f"บริบทผู้ใช้: {user_context}"},
                    {"type": "input_image", "image_url": data_url},
                ],
            }],
        )
        return response.output_text
    except Exception as exc:
        return f"ไม่สามารถวิเคราะห์ภาพด้วย AI ได้: {exc}"


# ============================================================
# UI HELPERS
# ============================================================
def _avatar_css(user):
    """ใส่รูปโปรไฟล์ในปุ่ม ☰ (ถ้าไม่มีรูปจะใช้ไอคอน 👤 ในข้อความปุ่มแทน)"""
    img = user.get("profile_image")
    if not img:
        return ""
    mime = user.get("profile_image_type") or "image/png"
    b64 = base64.b64encode(img).decode()
    return (
        "<style>[data-testid=\"stPopover\"] button::before {"
        "content:''; display:inline-block; width:36px; height:36px; border-radius:50%;"
        f"background:url(data:{mime};base64,{b64}) center/cover no-repeat;"
        "border:2px solid #cfe5c8; flex-shrink:0;}</style>"
    )


def render_header():
    user = st.session_state.get("user")
    brand = """
        <div class="tb-brand">
            <div class="tb-leaf">🌿</div>
            <div style="flex:1">
                <div class="tb-title">Thai Balance</div>
                <div class="tb-subtitle">สมดุลชีวิต ด้วยภูมิปัญญาไทย และเทคโนโลยีสมัยใหม่</div>
            </div>
        </div>
    """
    pill = """
        <div class="tb-pill">ระบบดูแลสุขภาพแบบองค์รวม<br>ผสมผสานแพทย์แผนไทย โภชนาการ และ AI</div>
    """
    if not user:
        st.markdown(
            f'<div class="tb-header"><div class="tb-brand" style="width:100%">'
            f'<div class="tb-leaf">🌿</div><div style="flex:1">'
            f'<div class="tb-title">Thai Balance</div>'
            f'<div class="tb-subtitle">สมดุลชีวิต ด้วยภูมิปัญญาไทย และเทคโนโลยีสมัยใหม่</div></div>'
            f'{pill}</div></div>',
            unsafe_allow_html=True,
        )
        return

    fresh = get_user(user["id"]) or user
    col_brand, col_pill, col_menu = st.columns([5, 3.2, 2.3])
    with col_brand:
        st.markdown('<span class="tb-anchor"></span>' + brand, unsafe_allow_html=True)
    with col_pill:
        st.markdown(pill, unsafe_allow_html=True)
    with col_menu:
        st.markdown(_avatar_css(fresh), unsafe_allow_html=True)
        icon = "" if fresh.get("profile_image") else "👤 "
        with st.popover(f"{icon}{fresh['full_name']}  ☰", help="เมนูผู้ใช้ / โปรไฟล์"):
            if fresh.get("profile_image"):
                st.image(fresh["profile_image"], width=90)
            st.markdown(f"**{fresh['full_name']}**")
            st.caption("ผู้ดูแลระบบ" if is_admin(fresh) else "ข้อมูลผู้ใช้")
            st.button(
                "🙍 ดูโปรไฟล์ของฉัน", use_container_width=True, key="menu_profile",
                on_click=goto, args=("profile",),
            )
            if st.button("ออกจากระบบ", use_container_width=True, key="menu_logout"):
                for k in ("user", "page", "menu", "edit_profile", "pending_prompt", "hx_step"):
                    st.session_state.pop(k, None)
                st.session_state.user = None
                try:
                    st.query_params.clear()
                except Exception:
                    pass
                st.rerun()


def panel(title, subtitle=None):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(f'<div class="panel-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="panel-sub">{subtitle}</div>', unsafe_allow_html=True)


def close_panel():
    st.markdown("</div>", unsafe_allow_html=True)


def section(title, hint=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if hint:
        st.markdown(f'<div class="section-hint">{hint}</div>', unsafe_allow_html=True)


def context_for_ai(user, health, meals):
    chronic = health.get("chronic", "[]")
    try:
        chronic = ", ".join(json.loads(chronic))
    except Exception:
        pass
    h = get_history(health)
    return (
        f"ชื่อ: {user.get('full_name')}\n"
        f"เพศ: {user.get('gender')}\n"
        f"วันเกิด: {user.get('birthdate')}\n"
        f"น้ำหนัก: {health.get('weight')} กก.\n"
        f"ส่วนสูง: {health.get('height')} ซม.\n"
        f"BMI: {health.get('bmi')} ({bmi_status(health.get('bmi'))})\n"
        f"ธาตุเจ้าเรือน: {health.get('constitution')}\n"
        f"โรคประจำตัว: {chronic}\n"
        f"อาการสำคัญ: {health.get('cc')}\n"
        f"แพ้ยา: {h.get('ph_drug_allergy_choice', '')} {h.get('ph_drug_allergy', '')}\n"
        f"แพ้อาหาร: {h.get('ph_food_allergy_choice', '')} {h.get('ph_food_allergy', '')}\n"
        f"ยาที่ใช้ประจำ: {h.get('ph_regular_meds', '')}\n"
        f"การนอน: {h.get('lf_sleep_hours', '')} ชม. คุณภาพ {h.get('lf_sleep_quality', '')}\n"
        f"ออกกำลังกาย: {h.get('lf_exercise', '')}\n"
        f"สูบบุหรี่: {h.get('lf_smoking', '')} / แอลกอฮอล์: {h.get('lf_alcohol', '')}\n"
        f"อาชีพ: {h.get('lf_occupation', '')}\n"
        f"มื้ออาหารที่บันทึก: {len(meals)} มื้อ\n"
        f"บันทึกออกกำลังกาย: {len(get_exercises(user['id']))} ครั้ง"
    )


# ============================================================
# AUTH PAGE
# ============================================================
GENDERS = ["ชาย", "หญิง"]


def auth_page():
    render_header()
    st.markdown(
        """
        <div class="hero">
            <h1>สมดุลชีวิต เริ่มต้นจากข้อมูลของคุณ</h1>
            <p>บันทึกข้อมูลสุขภาพ อาหาร พฤติกรรมการกิน และรับคำแนะนำเฉพาะบุคคล</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _pad_l, center, _pad_r = st.columns([1, 2.4, 1])

    with center:
        panel("🔐 เข้าสู่ระบบ / สมัครสมาชิก", "เริ่มต้นใช้งาน Thai Balance")
        tab_login, tab_register = st.tabs(["เข้าสู่ระบบ", "สมัครสมาชิก"])

        with tab_login:
            # ใช้ st.form เพื่อให้กด Enter ที่ช่องชื่อผู้ใช้/รหัสผ่านแล้วเข้าสู่ระบบได้ทันที
            with st.form("login_form"):
                username = st.text_input("ชื่อผู้ใช้", key="login_user")
                password = st.text_input("รหัสผ่าน", type="password", key="login_pass")
                login_submit = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True)
            if login_submit:
                user, login_err = login_user(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error(login_err)

        with tab_register:
            c1, c2 = st.columns(2)
            with c1:
                r_user = st.text_input("ชื่อผู้ใช้ *", key="r_user")
                r_name = st.text_input("ชื่อ-นามสกุล *", key="r_name")
                r_citizen = st.text_input("เลขบัตรประชาชน", max_chars=13, key="r_citizen")
                r_gender = st.radio("เพศ", GENDERS, horizontal=True, key="r_gender")
                r_phone = st.text_input("เบอร์โทรศัพท์", key="r_phone")
                r_email = st.text_input("อีเมล", key="r_email")
            with c2:
                r_birth = thai_date_input("วันเดือนปีเกิด", date(1995, 1, 1), key="r_birth")
                st.markdown("**ที่อยู่**")
                r_addr = address_input("reg")
                r_pass = st.text_input("รหัสผ่าน *", type="password", key="r_pass")
                r_confirm = st.text_input("ยืนยันรหัสผ่าน *", type="password", key="r_confirm")

            accept = st.checkbox("ยอมรับเงื่อนไขและการใช้ข้อมูลเพื่อการดูแลสุขภาพ")
            if st.button("🌿 สมัครสมาชิก", use_container_width=True, key="register_btn"):
                if not r_user or not r_name or not r_pass:
                    st.error("กรุณากรอกชื่อผู้ใช้ ชื่อ-นามสกุล และรหัสผ่าน")
                elif len(r_pass) < 8:
                    st.error("รหัสผ่านควรมีอย่างน้อย 8 ตัวอักษร")
                elif r_pass != r_confirm:
                    st.error("รหัสผ่านไม่ตรงกัน")
                elif r_citizen and not (r_citizen.isdigit() and len(r_citizen) == 13):
                    st.error("เลขบัตรประชาชนต้องเป็นตัวเลข 13 หลัก")
                elif r_phone and not r_phone.isdigit():
                    st.error("เบอร์โทรศัพท์ต้องเป็นตัวเลขเท่านั้น")
                elif not accept:
                    st.error("กรุณายอมรับเงื่อนไขก่อนสมัครสมาชิก")
                else:
                    ok, msg = register_user(
                        r_user, r_pass, r_name, r_citizen, r_birth,
                        r_gender, r_phone, r_email, r_addr,
                    )
                    if ok:
                        st.success(msg + " กรุณาเข้าสู่ระบบ")
                    else:
                        st.error(msg)
        close_panel()


# ============================================================
# DASHBOARD (ตัดกล่อง Input / กระบวนการ / Output ออกแล้ว)
# ============================================================
def dashboard_page():
    user = refresh_session_user()
    health = get_health(user["id"])
    meals = get_meals(user["id"])

    st.markdown(
        """
        <div class="hero">
            <h1>ดูแลสุขภาพแบบองค์รวมในแบบที่เป็นคุณ 🌿</h1>
            <p>บันทึกข้อมูลสุขภาพและอาหาร แล้วรับรายงานและคำแนะนำเฉพาะบุคคล</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    bmi_val = health.get("bmi")
    constitution = constitution_from_birthdate(parse_date(user.get("birthdate"))) if user.get("birthdate") else None
    c_icon = CONSTITUTION_GUIDE[constitution]["icon"] + " " if constitution else ""

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (len(meals), "มื้ออาหารที่บันทึก"),
        (bmi_val if bmi_val is not None else "-", "BMI"),
        (f"{c_icon}{constitution}" if constitution else "-", "ธาตุเจ้าเรือน"),
        (bmi_status(bmi_val), "สถานะ BMI"),
    ]
    for col, (val, label) in zip((c1, c2, c3, c4), cards):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{val}</div>'
                f'<div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    ex_left, ex_right = st.columns(2, gap="large")
    with ex_left:
        render_constitution_explainer(constitution)
    with ex_right:
        render_bmi_explainer(health.get("weight"), health.get("height"), bmi_val)

    st.markdown("<br>", unsafe_allow_html=True)
    panel("🛡️ ระยะความปลอดภัย")
    alerts = risk_alert(user, health, meals)
    if alerts:
        for a in alerts:
            st.markdown(f'<div class="warning">⚠️ {a}</div><br>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-box">✓ ยังไม่พบการแจ้งเตือนจากข้อมูลที่บันทึกในระบบ</div>', unsafe_allow_html=True)
    st.caption("ระบบเป็นเครื่องมือช่วยติดตามสุขภาพ ไม่ใช่การวินิจฉัยหรือการรักษาโรค")
    close_panel()


# ============================================================
# PROFILE PAGE (โปรไฟล์ + แก้ไข + บันทึก)
# ============================================================
def profile_page():
    user = refresh_session_user()
    editing = st.session_state.get("edit_profile", False)
    health = get_health(user["id"])
    saved_h = get_history(health)

    st.button("← กลับหน้าหลัก", key="pf_back", on_click=goto, args=("home",))
    panel("🙍 โปรไฟล์ของฉัน", "ข้อมูลส่วนตัว รูปโปรไฟล์ และที่อยู่ — กดแก้ไขเพื่อบันทึกข้อมูลใหม่")
    c_img, c_info = st.columns([1, 2.4], gap="large")

    with c_img:
        if user.get("profile_image"):
            st.image(user["profile_image"], width=170)
        else:
            st.markdown('<div class="avatar-ph">👤</div>', unsafe_allow_html=True)

    with c_info:
        if not editing:
            rows = [
                ("ชื่อ-นามสกุล", user.get("full_name") or "-"),
                ("เบอร์โทรศัพท์", user.get("phone") or "-"),
                ("อีเมล", user.get("email") or "-"),
                ("เพศ", user.get("gender") or "-"),
                ("วันเดือนปีเกิด", thai_date_text(user.get("birthdate"))),
                ("เลขบัตรประชาชน", user.get("citizen_id") or "-"),
                ("ที่อยู่", format_address(user) if user.get("province") or user.get("house_no") else (user.get("address") or "-")),
                ("น้ำหนัก", f"{_fmt_num(health['weight'])} กก." if health.get("weight") else "-"),
                ("ส่วนสูง", f"{_fmt_num(health['height'])} ซม." if health.get("height") else "-"),
            ]
            for label, val in rows:
                st.markdown(
                    f'<div class="profile-row"><div class="profile-label">{label}</div>'
                    f'<div class="profile-value">{val}</div></div>',
                    unsafe_allow_html=True,
                )
            lf_rows = lifestyle_rows(saved_h)
            st.markdown("##### 🧘 การใช้ชีวิตและพฤติกรรมสุขภาพ")
            if lf_rows:
                for label, val in lf_rows:
                    st.markdown(
                        f'<div class="profile-row"><div class="profile-label">{label}</div>'
                        f'<div class="profile-value">{val}</div></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("ยังไม่ได้กรอก — กดแก้ไขข้อมูลเพื่อเพิ่ม (ข้อมูลส่วนนี้จะถูกใช้ในแบบซักประวัติข้อ 5)")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✏️ แก้ไขข้อมูล", key="pf_edit_btn"):
                st.session_state.edit_profile = True
                st.rerun()
        else:
            photo = st.file_uploader("รูปโปรไฟล์ (เว้นว่างไว้ถ้าไม่เปลี่ยน)", type=["jpg", "jpeg", "png", "webp"], key="pf_photo")
            if photo:
                st.image(photo, width=120)
            f_name = st.text_input("ชื่อ-นามสกุล *", value=user.get("full_name") or "", key="pf_name")
            f_phone = st.text_input("เบอร์โทรศัพท์", value=user.get("phone") or "", key="pf_phone")
            f_email = st.text_input("อีเมล", value=user.get("email") or "", key="pf_email")
            f_citizen = st.text_input("เลขบัตรประชาชน", value=user.get("citizen_id") or "", max_chars=13, key="pf_citizen")
            f_gender = st.radio(
                "เพศ", GENDERS, horizontal=True,
                index=_index_of(GENDERS, user.get("gender")), key="pf_gender",
            )
            f_birth = thai_date_input("วันเดือนปีเกิด", parse_date(user.get("birthdate")), key="pf_birth")
            st.markdown("**ที่อยู่**")
            f_addr = address_input("pf", user)

            st.markdown("**ข้อมูลร่างกาย**")
            w1, w2 = st.columns(2)
            with w1:
                f_weight = st.number_input(
                    "น้ำหนัก (กก.)", min_value=1.0, max_value=300.0,
                    value=float(health["weight"]) if health.get("weight") else None,
                    step=0.1, placeholder="เช่น 60", key="pf_weight",
                )
            with w2:
                f_height = st.number_input(
                    "ส่วนสูง (ซม.)", min_value=50.0, max_value=250.0,
                    value=float(health["height"]) if health.get("height") else None,
                    step=0.5, placeholder="เช่น 160", key="pf_height",
                )
            st.markdown("**🧘 การใช้ชีวิตและพฤติกรรมสุขภาพ** (ใช้เป็นข้อ 5 ของแบบซักประวัติ)")
            LF = HistoryForm(saved_h, prefix="pf_lf_")
            lifestyle_form(LF)

            b1, b2 = st.columns(2)
            with b1:
                save_clicked = st.button("💾 บันทึกข้อมูลใหม่", use_container_width=True, key="pf_save")
            with b2:
                cancel_clicked = st.button("ยกเลิก", use_container_width=True, key="pf_cancel")

            if cancel_clicked:
                st.session_state.edit_profile = False
                st.rerun()
            if save_clicked:
                if not f_name.strip():
                    st.error("กรุณากรอกชื่อ-นามสกุล")
                elif f_citizen and not (f_citizen.isdigit() and len(f_citizen) == 13):
                    st.error("เลขบัตรประชาชนต้องเป็นตัวเลข 13 หลัก")
                elif f_phone and not f_phone.isdigit():
                    st.error("เบอร์โทรศัพท์ต้องเป็นตัวเลขเท่านั้น")
                else:
                    update_user(
                        user["id"],
                        {
                            "full_name": f_name, "citizen_id": f_citizen,
                            "birthdate": f_birth, "gender": f_gender,
                            "phone": f_phone, "email": f_email,
                        },
                        f_addr,
                        image=photo.getvalue() if photo else None,
                        image_type=photo.type if photo else None,
                    )
                    fresh_user = refresh_session_user()
                    # บันทึกน้ำหนัก/ส่วนสูง/พฤติกรรม เป็นข้อมูลสุขภาพแถวใหม่ (เฉพาะเมื่อมีการเปลี่ยนแปลง)
                    new_hist = {**saved_h, **LF.out}
                    body_changed = (
                        f_weight and f_height
                        and (f_weight != health.get("weight") or f_height != health.get("height"))
                    )
                    lf_changed = any(saved_h.get(k) != v for k, v in LF.out.items())
                    if body_changed or lf_changed:
                        w_final = f_weight if f_weight else health.get("weight")
                        h_final = f_height if f_height else health.get("height")
                        _save_body(
                            fresh_user, health, saved_h,
                            saved_h.get("status") or "ปกติ", w_final, h_final,
                            history=new_hist,
                            summaries=(health.get("cc", ""), health.get("pi", ""), health.get("ph", ""), health.get("fh", "")),
                            keep_chronic=True,
                        )
                    st.session_state.edit_profile = False
                    st.success("บันทึกข้อมูลโปรไฟล์เรียบร้อยแล้ว")
                    st.rerun()
    close_panel()


# ============================================================
# HEALTH PROFILE + ซักประวัติ
# ============================================================
class HistoryForm:
    """ตัวช่วยสร้างกล่องข้อความ/ตัวเลือก โดยดึงค่าที่เคยบันทึกมาเติมให้อัตโนมัติ"""

    def __init__(self, saved, prefix="hx_"):
        self.saved = saved or {}
        self.out = {}
        self.prefix = prefix

    def text(self, key, label, area=False, placeholder=""):
        fn = st.text_area if area else st.text_input
        v = fn(label, value=self.saved.get(key, ""), placeholder=placeholder, key=f"{self.prefix}{key}")
        self.out[key] = v
        return v

    def select(self, key, label, options):
        idx = _index_of(options, self.saved.get(key))
        v = st.selectbox(label, options, index=idx, key=f"{self.prefix}{key}")
        self.out[key] = v
        return v

    def multi(self, key, label, options):
        default = [x for x in self.saved.get(key, []) if x in options]
        v = st.multiselect(label, options, default=default, key=f"{self.prefix}{key}")
        self.out[key] = v
        return v

    def number(self, key, label, min_value, max_value, default, step=1.0):
        try:
            val = float(self.saved.get(key, default))
        except (TypeError, ValueError):
            val = float(default)
        val = min(max(val, float(min_value)), float(max_value))
        v = st.number_input(
            label, min_value=float(min_value), max_value=float(max_value),
            value=val, step=float(step), key=f"{self.prefix}{key}",
        )
        self.out[key] = v
        return v


CHRONIC_OPTIONS = [
    "ไม่มีโรคประจำตัว", "เบาหวาน", "ความดันโลหิตสูง", "ไขมันในเลือดสูง",
    "โรคหัวใจและหลอดเลือด", "โรคไต", "โรคตับ", "โรคกระเพาะ/กรดไหลย้อน",
    "โรคหอบหืด/ปอด", "มะเร็ง", "อื่น ๆ",
]
SYMPTOM_OPTIONS = [
    "ไข้", "ไอ", "เจ็บคอ", "ปวดศีรษะ", "คลื่นไส้/อาเจียน", "ท้องเสีย",
    "ท้องผูก", "ปวดท้อง", "เหนื่อยง่าย", "นอนไม่หลับ", "ผื่น/คัน", "อื่น ๆ",
]
FAMILY_DISEASES = [
    "ไม่มี/ไม่ทราบ", "เบาหวาน", "ความดันโลหิตสูง", "โรคหัวใจ", "มะเร็ง",
    "โรคทางพันธุกรรม", "โรคติดต่อที่อาจเกี่ยวข้อง", "อื่น ๆ",
]
DURATION_UNITS = ["นาที", "ชั่วโมง", "วัน", "สัปดาห์", "เดือน", "ปี"]


LIFESTYLE_FIELDS = [
    ("lf_meals_per_day", "รับประทานอาหารกี่มื้อ/วัน", ""),
    ("lf_meal_times", "เวลาที่รับประทานอาหาร", ""),
    ("lf_sleep_hours", "นอนหลับ (ชม./วัน)", ""),
    ("lf_sleep_quality", "หลับสนิทไหม", ""),
    ("lf_exercise", "ออกกำลังกายบ่อยแค่ไหน", ""),
    ("lf_exercise_type", "ประเภทการออกกำลังกาย", ""),
    ("lf_smoking", "การสูบบุหรี่", ""),
    ("lf_smoking_detail", "รายละเอียดการสูบบุหรี่", ""),
    ("lf_alcohol", "การดื่มแอลกอฮอล์", ""),
    ("lf_alcohol_detail", "รายละเอียดการดื่ม", ""),
    ("lf_drugs", "การใช้สารเสพติด", ""),
    ("lf_drugs_detail", "รายละเอียดสารเสพติด", ""),
    ("lf_occupation", "อาชีพ", ""),
    ("lf_job_nature", "ลักษณะงาน", ""),
    ("lf_urine_times", "ปัสสาวะ (ครั้ง/วัน)", ""),
    ("lf_urine_color", "สีปัสสาวะ", ""),
    ("lf_stool_times", "อุจจาระ (ครั้ง/วัน)", ""),
    ("lf_stool_color", "สีอุจจาระ", ""),
    ("lf_stool_char", "ลักษณะอุจจาระ", ""),
    ("lf_medication_use", "การใช้ยา/อาหารเสริม/สมุนไพร", ""),
    ("lf_environment", "สภาพความเป็นอยู่/สิ่งแวดล้อม", ""),
]


def lifestyle_form(F):
    """แบบกรอกการใช้ชีวิตและพฤติกรรมสุขภาพ (เดิมคือข้อ 5 ของแบบซักประวัติ) — ใช้ในหน้าข้อมูลส่วนตัว"""
    l1, l2 = st.columns(2)
    with l1:
        F.select("lf_meals_per_day", "รับประทานอาหารกี่มื้อ/วัน", ["1 มื้อ", "2 มื้อ", "3 มื้อ", "มากกว่า 3 มื้อ"])
        F.text("lf_meal_times", "เวลาที่รับประทานอาหาร", placeholder="เช่น 07:30, 12:00, 18:30")
        F.number("lf_sleep_hours", "นอนหลับกี่ชั่วโมง/วัน", 0, 24, 7, 0.5)
        F.select("lf_sleep_quality", "หลับสนิทไหม", ["หลับสนิท", "หลับ ๆ ตื่น ๆ", "หลับยาก", "นอนไม่หลับบ่อย"])
        F.select("lf_exercise", "ออกกำลังกายบ่อยแค่ไหน", ["ไม่ออกกำลังกาย", "1–2 ครั้ง/สัปดาห์", "3–4 ครั้ง/สัปดาห์", "5 ครั้งขึ้นไป/สัปดาห์"])
        F.text("lf_exercise_type", "ประเภทการออกกำลังกาย", placeholder="เช่น เดินเร็ว วิ่ง โยคะ")
        F.select("lf_smoking", "การสูบบุหรี่", ["ไม่สูบ", "เคยสูบแต่เลิกแล้ว", "สูบบางครั้ง", "สูบทุกวัน"])
        F.text("lf_smoking_detail", "รายละเอียดการสูบบุหรี่ (จำนวนมวน/วัน, สูบมากี่ปี)")
        F.select("lf_alcohol", "การดื่มแอลกอฮอล์", ["ไม่ดื่ม", "นาน ๆ ครั้ง", "สัปดาห์ละ 1–2 ครั้ง", "สัปดาห์ละหลายครั้ง", "ทุกวัน"])
        F.text("lf_alcohol_detail", "รายละเอียดการดื่ม (ชนิด/ปริมาณ)")
        F.select("lf_drugs", "การใช้สารเสพติด", ["ไม่ใช้", "เคยใช้", "ใช้อยู่"])
        F.text("lf_drugs_detail", "รายละเอียด (ถ้ามี)")
    with l2:
        F.text("lf_occupation", "อาชีพ")
        F.text("lf_job_nature", "ลักษณะงาน", area=True, placeholder="เช่น นั่งโต๊ะนาน ยืนตลอด เข้ากะ ใช้แรงงาน สัมผัสสารเคมี")
        F.number("lf_urine_times", "ปัสสาวะวันละกี่ครั้ง", 0, 50, 5)
        F.select("lf_urine_color", "สีปัสสาวะ", ["เหลืองใส", "เหลืองเข้ม", "ขุ่น", "แดง/ชมพู", "อื่น ๆ"])
        F.number("lf_stool_times", "อุจจาระวันละกี่ครั้ง", 0, 20, 1)
        F.select("lf_stool_color", "สีอุจจาระ", ["น้ำตาล/เหลืองน้ำตาล", "เขียว", "ดำ", "แดง/มีเลือดปน", "ซีด/เทา"])
        F.select("lf_stool_char", "ลักษณะอุจจาระ", ["ปกติ", "แข็ง/ท้องผูก", "เหลว/ท้องเสีย", "มีมูก"])
        F.text("lf_medication_use", "การใช้ยา/อาหารเสริม/สมุนไพร", area=True)
        F.text("lf_environment", "สภาพความเป็นอยู่/สิ่งแวดล้อม", area=True, placeholder="เช่น อยู่คนเดียว/กับครอบครัว ใกล้โรงงาน ฝุ่น มลพิษ น้ำดื่ม")


def lifestyle_rows(h):
    rows = []
    for key, label, _ in LIFESTYLE_FIELDS:
        v = h.get(key)
        if v in (None, "", []):
            continue
        rows.append((label, _fmt_num(v) if isinstance(v, (int, float)) else str(v)))
    return rows


def _fmt_num(v):
    try:
        v = float(v)
        return str(int(v)) if v == int(v) else str(v)
    except (TypeError, ValueError):
        return str(v)


def build_summaries(h):
    cc = ""
    if h.get("cc_symptom"):
        cc = f"{h['cc_symptom']} ระยะเวลา {_fmt_num(h.get('cc_duration_num'))} {h.get('cc_duration_unit', '')}"
    pi_parts = [
        f"เริ่มเมื่อ: {h.get('pi_onset')}" if h.get("pi_onset") else "",
        f"อาการเริ่มต้น: {h.get('pi_initial')}" if h.get("pi_initial") else "",
        f"ลักษณะ: {h.get('pi_course')}" if h.get("pi_course") else "",
        f"ดีขึ้นเมื่อ: {h.get('pi_better')}" if h.get("pi_better") else "",
        f"แย่ลงเมื่อ: {h.get('pi_worse')}" if h.get("pi_worse") else "",
        ("อาการร่วม: " + ", ".join(h.get("pi_associated", []) + ([h["pi_associated_other"]] if h.get("pi_associated_other") else []))) if (h.get("pi_associated") or h.get("pi_associated_other")) else "",
    ]
    ph_parts = [
        ("โรคเดิม: " + ", ".join(h.get("ph_diseases", []))) if h.get("ph_diseases") else "",
        f"นอน รพ.: {h.get('ph_hospital_detail')}" if h.get("ph_hospital") == "เคย" else "",
        f"ผ่าตัด: {h.get('ph_surgery_detail')}" if h.get("ph_surgery") == "เคย" else "",
        f"อุบัติเหตุ: {h.get('ph_accident_detail')}" if h.get("ph_accident") == "เคย" else "",
        f"แพ้ยา: {h.get('ph_drug_allergy')}" if h.get("ph_drug_allergy_choice") == "มี" else "",
        f"แพ้อาหาร: {h.get('ph_food_allergy')}" if h.get("ph_food_allergy_choice") == "มี" else "",
        f"ยาประจำ: {h.get('ph_regular_meds')}" if h.get("ph_regular_meds") else "",
        f"วัคซีน: {h.get('ph_vaccine')}" if h.get("ph_vaccine") else "",
    ]
    fh_parts = [
        ("บิดา: " + ", ".join(h.get("fh_father", []))) if h.get("fh_father") else "",
        ("มารดา: " + ", ".join(h.get("fh_mother", []))) if h.get("fh_mother") else "",
        ("พี่น้อง: " + ", ".join(h.get("fh_siblings", []))) if h.get("fh_siblings") else "",
        f"เพิ่มเติม: {h.get('fh_detail')}" if h.get("fh_detail") else "",
    ]
    join = lambda xs: "; ".join(x for x in xs if x)
    return cc, join(pi_parts), join(ph_parts), join(fh_parts)


def _save_body(user, health, saved, status, weight, height, history=None, summaries=None, keep_chronic=False):
    """บันทึกข้อมูลสุขภาพ (น้ำหนัก/ส่วนสูง/BMI/ธาตุ + ประวัติ) เป็นแถวใหม่"""
    bmi = calc_bmi(weight, height)
    constitution = constitution_from_birthdate(parse_date(user.get("birthdate")))
    history = dict(history if history is not None else saved)
    history["status"] = status
    if summaries is None:
        cc, pi, ph, fh = (health.get("cc", ""), health.get("pi", ""), health.get("ph", ""), health.get("fh", ""))
        try:
            chronic = json.loads(health.get("chronic") or "[]")
        except Exception:
            chronic = []
    else:
        cc, pi, ph, fh = summaries
        if keep_chronic:
            try:
                chronic = json.loads(health.get("chronic") or "[]")
            except Exception:
                chronic = []
        else:
            chronic = list(history.get("ph_diseases", []))
            if history.get("ph_diseases_other"):
                chronic.append(history["ph_diseases_other"])
    save_health(
        user["id"],
        {
            "cc": cc, "pi": pi, "ph": ph, "fh": fh, "chronic": chronic,
            "weight": weight, "height": height, "bmi": bmi,
            "constitution": constitution, "history": history,
        },
    )


def _on_status_change():
    """บันทึกสถานะทันทีเมื่อเปลี่ยน — ถ้าเลือก 'ป่วย' ให้เด้งไปกรอกแบบซักประวัติเลย"""
    user = st.session_state.get("user")
    if not user:
        return
    status = st.session_state.get("hs_status")
    health = get_health(user["id"])
    saved = get_history(health)
    _save_status_only(user, health, saved, status)
    if status == "ป่วย":
        goto("history")


def _save_status_only(user, health, saved, status):
    """บันทึกสถานะลงข้อมูลสุขภาพ โดยคงค่าเดิมทั้งหมด (น้ำหนัก/ส่วนสูง/ประวัติ)"""
    try:
        chronic = json.loads(health.get("chronic") or "[]")
    except Exception:
        chronic = []
    history = dict(saved)
    history["status"] = status
    weight, height = health.get("weight"), health.get("height")
    save_health(
        user["id"],
        {
            "cc": health.get("cc", ""), "pi": health.get("pi", ""),
            "ph": health.get("ph", ""), "fh": health.get("fh", ""),
            "chronic": chronic, "weight": weight, "height": height,
            "bmi": calc_bmi(weight, height),
            "constitution": constitution_from_birthdate(parse_date(user.get("birthdate"))),
            "history": history,
        },
    )


def health_status_page():
    """สุขภาพ: แสดงเฉพาะสถานะ (ปกติ/ป่วย)
    น้ำหนัก/ส่วนสูงแก้ได้ที่ข้อมูลส่วนตัว • เลือก 'ป่วย' แล้วจะเด้งไปแบบซักประวัติทันที"""
    user = refresh_session_user()
    health = get_health(user["id"])
    saved = get_history(health)
    options = ["ปกติ", "ป่วย"]

    panel("🩺 สุขภาพของฉัน", "เลือกสถานะสุขภาพตอนนี้ — หากเลือก \"ป่วย\" ระบบจะพาไปกรอกแบบซักประวัติอาการทันที")
    st.markdown("##### สถานะ")
    status = st.radio(
        "สถานะสุขภาพตอนนี้", options, horizontal=True,
        index=_index_of(options, saved.get("status")), key="hs_status",
        label_visibility="collapsed", on_change=_on_status_change,
    )

    if status == "ป่วย":
        st.markdown(
            '<div class="warning">🤒 สถานะปัจจุบัน: ป่วย — กรอกหรืออัปเดตแบบซักประวัติอาการได้ที่ปุ่มด้านล่าง</div>',
            unsafe_allow_html=True,
        )
        if health.get("cc"):
            st.caption(f"อาการสำคัญที่บันทึกล่าสุด: {health['cc']}")
        st.button(
            "📝 ไปที่แบบซักประวัติอาการ", key="go_history", use_container_width=True,
            on_click=goto, args=("history",),
        )
    else:
        st.markdown('<div class="success-box">✓ สถานะปัจจุบัน: ปกติ</div>', unsafe_allow_html=True)
    st.caption("น้ำหนัก ส่วนสูง และพฤติกรรมสุขภาพ แก้ไขได้ที่ ☰ → โปรไฟล์ของฉัน")
    close_panel()


def _hx_next(n):
    """callback ของปุ่ม/Enter ในแต่ละส่วน: เปิดส่วนถัดไป"""
    if st.session_state.get("hx_step", 1) <= n:
        st.session_state.hx_step = n + 1
        st.session_state.hx_focus = n + 1


def _focus_script(idx):
    """โฟกัสช่องแรกของส่วนที่เพิ่งเด้งขึ้นมา เพื่อให้พิมพ์ต่อและกด Enter ได้เลย"""
    import streamlit.components.v1 as components
    components.html(
        f"""
        <script>
        setTimeout(function() {{
            try {{
                const forms = window.parent.document.querySelectorAll('div[data-testid="stForm"]');
                const f = forms[{idx - 1}];
                if (!f) return;
                f.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                const inp = f.querySelector('input, textarea');
                if (inp) inp.focus({{preventScroll: true}});
            }} catch (e) {{}}
        }}, 350);
        </script>
        """,
        height=0,
    )


def history_page():
    """แบบซักประวัติอาการ — ส่วน 1–4 เด้งขึ้นมาทีละส่วนเมื่อกด Enter, ส่วน 5 ดึงจากข้อมูลส่วนตัว"""
    user = refresh_session_user()
    health = get_health(user["id"])
    saved = get_history(health)
    F = HistoryForm(saved)
    step = st.session_state.get("hx_step", 1)

    st.button("← กลับหน้าสุขภาพ", key="hx_back", on_click=goto, args=("health",))
    panel("📝 ซักประวัติอาการ", "กรอกทีละส่วน แล้วกด Enter (หรือปุ่ม ถัดไป) เพื่อไปส่วนต่อไป ข้อมูลจะถูกใช้ให้ AI ตอบได้ตรงกับคุณมากขึ้น")
    st.progress(min(step, 5) / 5, text=f"ส่วนที่ {min(step, 5)} / 5")

    def btn_label(n):
        if n < step:
            return "✓ อัปเดตส่วนนี้ (Enter)"
        return "ถัดไป ▶ (กด Enter)" if n < 4 else "ไปส่วนสุดท้าย ▶ (กด Enter)"

    # 1) อาการสำคัญ
    with st.form("hx_form_1"):
        section("1. อาการสำคัญ (Chief Complaint)", "อาการหลักที่ทำให้มาพบแพทย์/มาโรงพยาบาล ระบุ อาการ + ระยะเวลาที่เป็น")
        F.text("cc_symptom", "อาการหลัก", placeholder="เช่น ปวดศีรษะ")
        d1, d2 = st.columns(2)
        with d1:
            F.number("cc_duration_num", "ระยะเวลาที่เป็น", 0, 1000, 1)
        with d2:
            F.select("cc_duration_unit", "หน่วย", DURATION_UNITS)
        st.form_submit_button(btn_label(1), use_container_width=True, on_click=_hx_next, args=(1,))

    # 2) รายละเอียดอาการปัจจุบัน
    if step >= 2:
        with st.form("hx_form_2"):
            section("2. รายละเอียดอาการเจ็บป่วยครั้งนี้ (Present Illness)", "ตั้งแต่เริ่มมีอาการจนถึงปัจจุบัน")
            F.text("pi_onset", "เริ่มมีอาการเมื่อไหร่", placeholder="เช่น เมื่อ 3 วันก่อน / ตั้งแต่เช้าวันจันทร์")
            F.text("pi_initial", "อาการเริ่มต้นเป็นอย่างไร")
            F.select("pi_course", "อาการเป็นต่อเนื่องหรือเป็น ๆ หาย ๆ", ["ต่อเนื่อง", "เป็น ๆ หาย ๆ"])
            F.text("pi_better", "อะไรทำให้อาการดีขึ้น", placeholder="เช่น พักผ่อน กินยา")
            F.text("pi_worse", "อะไรทำให้อาการแย่ลง", placeholder="เช่น ออกแรง อากาศร้อน กินอาหารบางอย่าง")
            F.multi("pi_associated", "มีอาการอื่นร่วมด้วยหรือไม่ (เลือกได้หลายข้อ)", SYMPTOM_OPTIONS)
            F.text("pi_associated_other", "อาการร่วมอื่น ๆ (ถ้ามี)")
            st.form_submit_button(btn_label(2), use_container_width=True, on_click=_hx_next, args=(2,))

    # 3) ประวัติในอดีต
    if step >= 3:
        with st.form("hx_form_3"):
            section("3. ประวัติการเจ็บป่วยในอดีต (Past History)")
            F.multi("ph_diseases", "เคยเป็นโรคอะไรบ้าง / โรคประจำตัว", CHRONIC_OPTIONS)
            F.text("ph_diseases_other", "โรคอื่น ๆ (ระบุ)")

            a1, a2 = st.columns([1, 2])
            with a1:
                F.select("ph_hospital", "เคยเข้ารับการรักษา/นอนโรงพยาบาลหรือไม่", ["ไม่เคย", "เคย"])
            with a2:
                F.text("ph_hospital_detail", "รายละเอียด (โรค/ปีที่รักษา/โรงพยาบาล)")
            b1, b2 = st.columns([1, 2])
            with b1:
                F.select("ph_surgery", "เคยผ่าตัดหรือไม่", ["ไม่เคย", "เคย"])
            with b2:
                F.text("ph_surgery_detail", "รายละเอียดการผ่าตัด")
            e1, e2 = st.columns([1, 2])
            with e1:
                F.select("ph_accident", "เคยประสบอุบัติเหตุรุนแรงหรือไม่", ["ไม่เคย", "เคย"])
            with e2:
                F.text("ph_accident_detail", "รายละเอียดอุบัติเหตุ")
            g1, g2 = st.columns([1, 2])
            with g1:
                F.select("ph_drug_allergy_choice", "ประวัติแพ้ยา", ["ไม่มี", "มี"])
            with g2:
                F.text("ph_drug_allergy", "ระบุชื่อยาที่แพ้และอาการที่เกิด")
            h1, h2 = st.columns([1, 2])
            with h1:
                F.select("ph_food_allergy_choice", "ประวัติแพ้อาหาร", ["ไม่มี", "มี"])
            with h2:
                F.text("ph_food_allergy", "ระบุอาหารที่แพ้และอาการที่เกิด")
            F.text("ph_regular_meds", "ยาที่รับประทานเป็นประจำ", placeholder="ชื่อยา ขนาด และความถี่")
            F.text("ph_vaccine", "ประวัติการได้รับวัคซีน (ถ้าเกี่ยวข้อง)", placeholder="เช่น ไข้หวัดใหญ่ COVID-19 บาดทะยัก")
            st.form_submit_button(btn_label(3), use_container_width=True, on_click=_hx_next, args=(3,))

    # 4) ประวัติครอบครัว
    if step >= 4:
        with st.form("hx_form_4"):
            section("4. ประวัติการเจ็บป่วยของบุคคลในครอบครัว (Family History)", "โดยเฉพาะโรคที่อาจถ่ายทอดทางพันธุกรรม")
            F.multi("fh_father", "บิดามีโรคประจำตัวอะไรหรือไม่", FAMILY_DISEASES)
            F.multi("fh_mother", "มารดามีโรคประจำตัวอะไรหรือไม่", FAMILY_DISEASES)
            F.multi("fh_siblings", "พี่น้องมีโรคประจำตัวอะไรหรือไม่", FAMILY_DISEASES)
            F.text("fh_detail", "รายละเอียดเพิ่มเติม (เช่น ญาติคนอื่น / ชนิดของมะเร็ง / โรคพันธุกรรม)")
            st.form_submit_button(btn_label(4), use_container_width=True, on_click=_hx_next, args=(4,))

    # 5) พฤติกรรมสุขภาพ — ดึงจากข้อมูลส่วนตัว
    if step >= 5:
        with st.container(border=True):
            section("5. การใช้ชีวิตและพฤติกรรมสุขภาพ (Personal & Social History)", "ดึงมาจากข้อมูลส่วนตัวของคุณโดยอัตโนมัติ")
            rows = lifestyle_rows(saved)
            if rows:
                lc1, lc2 = st.columns(2)
                for i, (label, val) in enumerate(rows):
                    with (lc1 if i % 2 == 0 else lc2):
                        st.markdown(
                            f'<div class="profile-row"><div class="profile-label">{label}</div>'
                            f'<div class="profile-value">{val}</div></div>',
                            unsafe_allow_html=True,
                        )
            else:
                st.info("ยังไม่มีข้อมูลการใช้ชีวิต/พฤติกรรมสุขภาพในข้อมูลส่วนตัว")
            st.button(
                "✏️ ไปกรอก/แก้ไขที่ข้อมูลส่วนตัว", key="hx_to_profile",
                on_click=_go_profile_edit,
            )

        if st.button("💾 บันทึกประวัติ", use_container_width=True, key="hx_save", type="primary"):
            history = {**saved, **F.out}  # คงค่าข้อ 5 (lf_*) และค่าอื่นเดิมไว้
            summaries = build_summaries(history)
            _save_body(
                user, health, saved, "ป่วย",
                health.get("weight"), health.get("height"),
                history=history, summaries=summaries,
            )
            st.success("บันทึกประวัติเรียบร้อยแล้ว")

    if st.session_state.pop("hx_focus", None):
        _focus_script(st.session_state.get("hx_step", 1))
    close_panel()


def _go_profile_edit():
    st.session_state.edit_profile = True
    goto("profile")


# ============================================================
# MEAL LOG PAGE
# ============================================================
def meal_page():
    """บันทึกอาหาร + บันทึกการออกกำลังกาย (รวมหน้าเดียว แยกเป็นแท็บ)"""
    user = refresh_session_user()
    health = get_health(user["id"])
    tab_meal, tab_ex = st.tabs(["🍲 บันทึกอาหาร", "🏃 บันทึกการออกกำลังกาย"])
    with tab_meal:
        _meal_tab(user, health)
    with tab_ex:
        _exercise_tab(user, health)


def _exercise_tab(user, health):
    panel("🏃 บันทึกการออกกำลังกาย", "บันทึกกิจกรรมที่ทำวันนี้ ระบบจะประมาณพลังงานที่เผาผลาญจากน้ำหนักในข้อมูลส่วนตัว")
    weight = health.get("weight")
    if not weight:
        st.caption("ยังไม่มีน้ำหนักในข้อมูลส่วนตัว — ระบบจะใช้ 60 กก. ในการประมาณพลังงาน (แก้ได้ที่ ☰ → โปรไฟล์ของฉัน)")

    c1, c2 = st.columns(2)
    with c1:
        ex_date = st.date_input("วันที่", value=date.today(), key="ex_date")
        ex_type = st.selectbox("ประเภทการออกกำลังกาย", list(EXERCISE_MET), key="ex_type")
        ex_type_other = ""
        if ex_type == "อื่น ๆ":
            ex_type_other = st.text_input("ระบุกิจกรรม", key="ex_type_other")
    with c2:
        ex_time = st.time_input("เวลาเริ่ม", value=datetime.now().time().replace(second=0, microsecond=0), key="ex_time")
        duration = st.number_input("ระยะเวลา (นาที)", min_value=1, max_value=600, value=30, step=5, key="ex_duration")
        intensity = st.radio("ความหนัก", list(INTENSITY_FACTOR), index=1, horizontal=True, key="ex_intensity")
    ex_note = st.text_area("หมายเหตุ", key="ex_note", height=80)

    est = estimate_exercise_calories(ex_type, duration, intensity, weight)
    st.caption(f"ประมาณพลังงานที่ใช้: {est:.0f} kcal")

    if st.button("💾 บันทึกการออกกำลังกาย", use_container_width=True, key="ex_save"):
        name = ex_type_other.strip() if ex_type == "อื่น ๆ" and ex_type_other.strip() else ex_type
        save_exercise(
            user["id"],
            {
                "ex_date": str(ex_date), "ex_time": ex_time.strftime("%H:%M"),
                "ex_type": name, "duration_min": duration, "intensity": intensity,
                "calories": est, "note": ex_note,
            },
        )
        st.success("บันทึกการออกกำลังกายแล้ว")
    close_panel()

    panel("รายการออกกำลังกายล่าสุด")
    rows = get_exercises(user["id"], limit=10)
    if not rows:
        st.info("ยังไม่มีรายการออกกำลังกาย")
    else:
        total_min = sum(r["duration_min"] or 0 for r in rows)
        total_cal = sum(r["calories"] or 0 for r in rows)
        m1, m2, m3 = st.columns(3)
        m1.metric("จำนวนครั้ง (ล่าสุด)", len(rows))
        m2.metric("เวลารวม", f"{total_min:.0f} นาที")
        m3.metric("พลังงานรวม", f"{total_cal:.0f} kcal")
        for r in rows:
            with st.expander(f"{r['ex_date']} {r['ex_time']} • {r['ex_type']} • {r['duration_min']:.0f} นาที"):
                st.write(f"ความหนัก: **{r['intensity']}**")
                st.write(f"พลังงานประมาณ: **{(r['calories'] or 0):.0f} kcal**")
                if r["note"]:
                    st.write("หมายเหตุ:", r["note"])
    close_panel()


def _meal_tab(user, health):
    panel("🍲 บันทึกอาหาร / ถ่ายรูป", "เพิ่มรูปอาหารหรือกรอกข้อมูลอาหารเพื่อวิเคราะห์เบื้องต้น")
    c1, c2 = st.columns([1, 1.3])
    with c1:
        uploaded = st.file_uploader("รูปอาหาร", type=["jpg", "jpeg", "png", "webp"])
        if uploaded:
            st.image(uploaded, caption="ภาพอาหาร", use_container_width=True)
    with c2:
        meal_date = st.date_input("วันที่", value=date.today())
        meal_time = st.time_input("เวลา", value=datetime.now().time().replace(second=0, microsecond=0))
        meal_type = st.selectbox("มื้ออาหาร", ["เช้า", "กลางวัน", "เย็น", "ว่าง"])
        food_name = st.text_input("ชื่ออาหาร *", placeholder="เช่น ข้าวกะเพราไก่ไข่ดาว")
        ingredients = st.text_area("ส่วนประกอบ", placeholder="เช่น ข้าว ไก่ ใบกะเพรา ไข่ น้ำปลา")
        amount = st.text_input("ปริมาณโดยประมาณ", placeholder="เช่น 1 จาน / 250 กรัม")
        note = st.text_area("หมายเหตุ")

    if st.button("💾 บันทึกมื้ออาหาร", use_container_width=True):
        if not food_name.strip():
            st.error("กรุณาระบุชื่ออาหาร")
        else:
            image_bytes = uploaded.getvalue() if uploaded else None
            image_type = uploaded.type if uploaded else None
            analysis = analyze_meal(food_name, ingredients, amount)
            save_meal(
                user["id"],
                {
                    "meal_date": str(meal_date),
                    "meal_time": meal_time.strftime("%H:%M"),
                    "meal_type": meal_type,
                    "food_name": food_name,
                    "ingredients": ingredients,
                    "amount": amount,
                    "calories": analysis["calories"],
                    "image": image_bytes,
                    "image_type": image_type,
                    "note": note,
                },
            )
            st.success("บันทึกอาหารแล้ว")
            st.rerun()
    close_panel()

    if uploaded:
        panel("🤖 วิเคราะห์ภาพอาหารด้วย AI")
        if st.button("วิเคราะห์ภาพนี้", use_container_width=True):
            context = context_for_ai(user, health, get_meals(user["id"]))
            with st.spinner("กำลังวิเคราะห์ภาพ..."):
                result = ai_image_analysis(uploaded.getvalue(), uploaded.type, context)
            st.write(result)
        close_panel()

    panel("รายการอาหารล่าสุด")
    meals = get_meals(user["id"], limit=10)
    if not meals:
        st.info("ยังไม่มีรายการอาหาร")
    else:
        for meal in meals:
            analysis = analyze_meal(meal["food_name"], meal["ingredients"], meal["amount"])
            with st.expander(f"{meal['meal_date']} {meal['meal_time']} • {meal['meal_type']} • {meal['food_name']}"):
                c1, c2 = st.columns([1, 2])
                with c1:
                    if meal["image"]:
                        st.image(meal["image"], caption="ภาพที่บันทึก", use_container_width=True)
                with c2:
                    st.write(f"พลังงานประมาณ: **{meal['calories'] or analysis['calories']:.0f} kcal**")
                    st.write("ส่วนประกอบ:", meal["ingredients"] or "-")
                    st.write("ปริมาณ:", meal["amount"] or "-")
                    st.write("ความเสี่ยง:", ", ".join(analysis["risks"]))
                    st.write("คำแนะนำ:", " ".join(analysis["tips"]))
    close_panel()


# ============================================================
# REPORT / STATISTICS PAGE
# ============================================================
def report_page():
    user = refresh_session_user()
    health = get_health(user["id"])
    meals = get_meals(user["id"])

    panel("📊 รายงาน / สถิติ", "เปรียบเทียบการกิน คำนวณแคลอรี และดูแนวโน้ม")
    if not meals:
        st.info("กรุณาบันทึกอาหารอย่างน้อย 1 มื้อเพื่อสร้างรายงาน")
        close_panel()
        return

    df = pd.DataFrame(meals)
    df["calories"] = pd.to_numeric(df["calories"], errors="coerce").fillna(0)
    df["meal_date"] = pd.to_datetime(df["meal_date"])
    daily = df.groupby("meal_date", as_index=False)["calories"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("จำนวนมื้อ", len(df))
    c2.metric("พลังงานเฉลี่ย/มื้อ", f"{df['calories'].mean():.0f} kcal")
    c3.metric("พลังงานรวม", f"{df['calories'].sum():.0f} kcal")

    st.markdown("### 📈 แนวโน้มพลังงานรายวัน")
    st.line_chart(daily.set_index("meal_date")[["calories"]])

    st.markdown("### 🍽️ เปรียบเทียบประเภทมื้อ")
    st.bar_chart(df.groupby("meal_type")["calories"].sum().sort_values(ascending=False))

    st.markdown("### ⚠️ วิเคราะห์ความเสี่ยงจากพฤติกรรม")
    alerts = risk_alert(user, health, meals)
    if alerts:
        for item in alerts:
            st.markdown(f'<div class="warning">⚠️ {item}</div><br>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-box">✓ ยังไม่พบความเสี่ยงเด่นจากข้อมูลที่บันทึก</div>', unsafe_allow_html=True)

    report_text = (
        f"Thai Balance - รายงานผู้ใช้ {user['full_name']}\n"
        f"จำนวนมื้อ: {len(df)}\n"
        f"พลังงานเฉลี่ยต่อมื้อ: {df['calories'].mean():.0f} kcal\n"
        f"พลังงานรวม: {df['calories'].sum():.0f} kcal\n"
        f"BMI: {health.get('bmi', '-')}\n"
        f"ธาตุเจ้าเรือน: {health.get('constitution', '-')}\n"
        f"แจ้งเตือน: {'; '.join(alerts) if alerts else 'ไม่พบ'}\n"
    )
    st.download_button(
        "⬇️ ดาวน์โหลดรายงานแบบข้อความ",
        data=report_text.encode("utf-8"),
        file_name="thai_balance_report.txt",
        mime="text/plain",
        use_container_width=True,
    )
    close_panel()


# ============================================================
# AI CHAT PAGE
# ============================================================
def ai_chat_page():
    user = refresh_session_user()
    health = get_health(user["id"])
    meals = get_meals(user["id"])
    history = get_chat(user["id"], limit=30)

    panel("🧑‍⚕️ หมอไทยบอท", "ถาม-ตอบแพทย์แผนไทยเบื้องต้น ธาตุเจ้าเรือน สมุนไพร อาหาร และการดูแลตนเอง")
    st.markdown(
        '<div class="warning">⚠️ บอทให้ข้อมูลทั่วไป ไม่ใช่แพทย์ ไม่วินิจฉัยโรค และไม่ควรใช้แทนการตรวจรักษา '
        'หากมีอาการรุนแรงให้พบแพทย์ทันที</div>',
        unsafe_allow_html=True,
    )
    if not get_openai_key():
        st.caption("ตอนนี้บอทตอบจากฐานความรู้แพทย์แผนไทยในระบบและข้อมูลที่คุณบันทึก (ตั้งค่า OPENAI_API_KEY เพื่อให้ตอบได้อิสระมากขึ้น)")
    st.markdown("<br>", unsafe_allow_html=True)

    quick = [
        "ธาตุเจ้าเรือนคืออะไร",
        "เป็นหวัด เจ็บคอ ดูแลอย่างไร",
        "ท้องอืด แน่นท้อง ใช้สมุนไพรอะไรได้",
        "นอนไม่หลับ ทำอย่างไรดี",
    ]
    cols = st.columns(len(quick))
    for i, (col, q) in enumerate(zip(cols, quick)):
        with col:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state.pending_prompt = q

    if not history:
        with st.chat_message("assistant", avatar="🌿"):
            st.write(
                "สวัสดีค่ะ ฉันคือ **หมอไทยบอท** ถามเรื่องธาตุเจ้าเรือน สมุนไพร อาการเบื้องต้น "
                "การนวด/ประคบ หรืออาหารที่เหมาะกับคุณได้เลย"
            )

    for item in history:
        if item["role"] == "user":
            with st.chat_message("user"):
                st.write(item["message"])
        else:
            with st.chat_message("assistant", avatar="🌿"):
                st.write(item["message"])

    prompt = st.chat_input("เช่น เป็นหวัดควรกินสมุนไพรอะไรได้บ้าง?")
    if not prompt:
        prompt = st.session_state.pop("pending_prompt", None)
    if prompt:
        recent = history[-8:]
        save_chat(user["id"], "user", prompt)
        context = context_for_ai(user, health, meals)
        with st.spinner("หมอไทยบอทกำลังตอบ..."):
            answer, err = ai_text_response(prompt, context, recent)
        if answer is None:
            answer = local_ai_answer(prompt, user, health, meals)
            if err and "OPENAI_API_KEY" not in err:
                answer += f"\n\n_(เรียก OpenAI ไม่สำเร็จ จึงตอบจากฐานความรู้ในระบบแทน: {err})_"
        save_chat(user["id"], "assistant", answer)
        st.rerun()

    if history and st.button("🗑️ ล้างประวัติแชต", key="clear_chat"):
        clear_chat(user["id"])
        st.rerun()
    close_panel()


# ============================================================
# ADMIN — จัดการข้อมูลเบื้องหลัง
# ============================================================
def is_admin(user):
    return bool(user) and user.get("role") == "admin"


def log_admin(admin_id, action, detail=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO admin_log (admin_id, action, detail, created_at) VALUES (?, ?, ?, ?)",
        (admin_id, action, detail, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def _df(sql, params=()):
    conn = get_conn()
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()


def _exec(sql, params=()):
    conn = get_conn()
    conn.execute(sql, params)
    conn.commit()
    conn.close()


def mask_id(v):
    v = str(v or "")
    return ("•" * (len(v) - 4) + v[-4:]) if len(v) > 4 else v


def admin_delete_user(uid):
    conn = get_conn()
    for table in ("meals", "exercises", "ai_chat", "health_data"):
        conn.execute(f"DELETE FROM {table} WHERE user_id = ?", (uid,))
    conn.execute("DELETE FROM users WHERE id = ?", (uid,))
    conn.commit()
    conn.close()


def _csv_button(label, df, filename, key):
    st.download_button(
        label, data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=filename, mime="text/csv", key=key, use_container_width=True,
    )


USER_COLS = "id, username, full_name, gender, birthdate, phone, email, address, citizen_id, role, is_active, created_at, last_login"


def admin_page():
    me = refresh_session_user()
    if not is_admin(me):
        st.error("หน้านี้สำหรับผู้ดูแลระบบเท่านั้น")
        return

    panel("🛠️ ผู้ดูแลระบบ", "จัดการผู้ใช้ และข้อมูลเบื้องหลังของ Thai Balance (การกระทำสำคัญจะถูกบันทึกในล็อก)")
    t_over, t_users, t_meals, t_chat, t_data = st.tabs(
        ["📈 ภาพรวม", "👥 ผู้ใช้", "🍲 อาหาร", "💬 แชต", "🗄️ ข้อมูล / สำรอง / ล็อก"]
    )

    users_df = _df(f"SELECT {USER_COLS} FROM users ORDER BY id")

    # ---------- ภาพรวม ----------
    with t_over:
        n_meals = _df("SELECT COUNT(*) AS n FROM meals")["n"][0]
        n_chat = _df("SELECT COUNT(*) AS n FROM ai_chat")["n"][0]
        n_health = _df("SELECT COUNT(*) AS n FROM health_data")["n"][0]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("ผู้ใช้ทั้งหมด", len(users_df))
        c2.metric("แอดมิน", int((users_df["role"] == "admin").sum()))
        c3.metric("ถูกระงับ", int((users_df["is_active"] == 0).sum()))
        c4.metric("มื้ออาหาร", int(n_meals))
        c5.metric("ข้อความแชต", int(n_chat))

        latest = _df(
            """
            SELECT h.* FROM health_data h
            JOIN (SELECT user_id, MAX(id) AS mid FROM health_data GROUP BY user_id) m ON h.id = m.mid
            """
        )
        sick = 0
        for _, r in latest.iterrows():
            try:
                if json.loads(r["history_json"] or "{}").get("status") == "ป่วย":
                    sick += 1
            except Exception:
                pass
        st.write(f"ผู้ใช้ที่กรอกข้อมูลสุขภาพแล้ว **{len(latest)}** คน • สถานะ \"ป่วย\" **{sick}** คน • บันทึกสุขภาพทั้งหมด {int(n_health)} รายการ")

        if len(users_df):
            tmp = users_df.copy()
            tmp["วันที่"] = tmp["created_at"].str[:10]
            st.markdown("**ผู้ใช้สมัครใหม่รายวัน**")
            st.bar_chart(tmp.groupby("วันที่").size())
        meals_daily = _df("SELECT substr(meal_date, 1, 10) AS d, COUNT(*) AS n FROM meals GROUP BY d ORDER BY d")
        if len(meals_daily):
            st.markdown("**จำนวนมื้ออาหารที่บันทึกรายวัน**")
            st.bar_chart(meals_daily.set_index("d")["n"])

    # ---------- ผู้ใช้ ----------
    with t_users:
        q = st.text_input("ค้นหา (ชื่อผู้ใช้ / ชื่อ / เบอร์ / อีเมล)", key="adm_q").strip().lower()
        view = users_df.copy()
        view["citizen_id"] = view["citizen_id"].map(mask_id)
        if q:
            mask = view[["username", "full_name", "phone", "email"]].fillna("").astype(str).apply(
                lambda col: col.str.lower().str.contains(q, regex=False)
            ).any(axis=1)
            view = view[mask]
        st.dataframe(view, use_container_width=True, hide_index=True)

        if users_df.empty:
            st.info("ยังไม่มีผู้ใช้")
        else:
            labels = {int(r["id"]): f"{int(r['id'])} — {r['username']} ({r['full_name']})" for _, r in users_df.iterrows()}
            uid = st.selectbox("เลือกผู้ใช้เพื่อดู/จัดการ", list(labels), format_func=lambda i: labels[i], key="adm_uid")
            target = get_user(uid)
            is_self = uid == me["id"]

            with st.container(border=True):
                st.markdown(f"#### {target['full_name']}  ·  `{target['username']}`")
                st.write(f"บทบาท: **{'แอดมิน' if target.get('role') == 'admin' else 'ผู้ใช้'}**  •  สถานะ: **{'ใช้งานได้' if target.get('is_active') != 0 else 'ถูกระงับ'}**")
                st.write(f"เพศ: {target.get('gender') or '-'}  •  วันเกิด: {thai_date_text(target.get('birthdate'))}  •  โทร: {target.get('phone') or '-'}  •  อีเมล: {target.get('email') or '-'}")
                st.write("ที่อยู่:", format_address(target) if target.get("province") or target.get("house_no") else (target.get("address") or "-"))
                h = get_health(uid)
                if h:
                    hist = get_history(h)
                    st.write(
                        f"BMI: {h.get('bmi', '-')} ({bmi_status(h.get('bmi'))})  •  ธาตุ: {h.get('constitution', '-')}  •  "
                        f"สถานะ: {hist.get('status', '-')}  •  อัปเดต: {h.get('updated_at', '-')}"
                    )
                    with st.expander("ประวัติซักประวัติ (ล่าสุด)"):
                        for label, key in (("อาการสำคัญ", "cc"), ("อาการปัจจุบัน", "pi"), ("ประวัติอดีต", "ph"), ("ประวัติครอบครัว", "fh")):
                            st.write(f"**{label}:**", h.get(key) or "-")
                else:
                    st.caption("ผู้ใช้นี้ยังไม่มีข้อมูลสุขภาพ")

            st.markdown("##### การจัดการ")
            if is_self:
                st.caption("นี่คือบัญชีของคุณ — ไม่สามารถเปลี่ยนบทบาท ระงับ หรือลบตัวเองได้ (ป้องกันระบบไม่มีแอดมิน)")
            a1, a2 = st.columns(2)
            with a1:
                role_opts = ["user", "admin"]
                new_role = st.selectbox(
                    "บทบาท", role_opts, index=_index_of(role_opts, target.get("role") or "user"),
                    format_func=lambda r: "แอดมิน" if r == "admin" else "ผู้ใช้", key=f"adm_role_{uid}", disabled=is_self,
                )
                if st.button("บันทึกบทบาท", key=f"adm_role_btn_{uid}", disabled=is_self):
                    _exec("UPDATE users SET role = ? WHERE id = ?", (new_role, uid))
                    log_admin(me["id"], "change_role", f"user={uid} role={new_role}")
                    st.success("เปลี่ยนบทบาทแล้ว")
                    st.rerun()
            with a2:
                active = target.get("is_active") != 0
                st.write("สถานะบัญชี:", "✅ ใช้งานได้" if active else "⛔ ถูกระงับ")
                if st.button("ระงับบัญชี" if active else "เปิดใช้งานบัญชี", key=f"adm_act_{uid}", disabled=is_self):
                    _exec("UPDATE users SET is_active = ? WHERE id = ?", (0 if active else 1, uid))
                    log_admin(me["id"], "toggle_active", f"user={uid} active={0 if active else 1}")
                    st.rerun()

            b1, b2 = st.columns(2)
            with b1:
                new_pw = st.text_input("ตั้งรหัสผ่านใหม่ให้ผู้ใช้ (อย่างน้อย 8 ตัว)", type="password", key=f"adm_pw_{uid}")
                if st.button("รีเซ็ตรหัสผ่าน", key=f"adm_pw_btn_{uid}"):
                    if len(new_pw) < 8:
                        st.error("รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร")
                    else:
                        salt, pw_hash = hash_password(new_pw)
                        _exec("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?", (pw_hash, salt, uid))
                        log_admin(me["id"], "reset_password", f"user={uid}")
                        st.success("รีเซ็ตรหัสผ่านแล้ว")
            with b2:
                confirm = st.checkbox("ยืนยันลบผู้ใช้นี้และข้อมูลทั้งหมด (กู้คืนไม่ได้)", key=f"adm_del_ck_{uid}", disabled=is_self)
                if st.button("🗑️ ลบผู้ใช้", key=f"adm_del_{uid}", disabled=is_self or not confirm):
                    admin_delete_user(uid)
                    log_admin(me["id"], "delete_user", f"user={uid} username={target['username']}")
                    st.success("ลบผู้ใช้แล้ว")
                    st.rerun()

    # ---------- อาหาร ----------
    with t_meals:
        opts = [0] + [int(i) for i in users_df["id"]]
        names = {0: "ทุกคน"} | {int(r["id"]): f"{r['username']} ({r['full_name']})" for _, r in users_df.iterrows()}
        sel = st.selectbox("ผู้ใช้", opts, format_func=lambda i: names[i], key="adm_meal_user")
        sql = (
            "SELECT m.id, u.username, m.meal_date, m.meal_time, m.meal_type, m.food_name, "
            "m.ingredients, m.amount, m.calories, m.note FROM meals m JOIN users u ON u.id = m.user_id"
        )
        mdf = _df(sql + (" WHERE m.user_id = ?" if sel else "") + " ORDER BY m.meal_date DESC, m.id DESC", (sel,) if sel else ())
        st.dataframe(mdf, use_container_width=True, hide_index=True)
        if len(mdf):
            d1, d2 = st.columns([2, 1])
            with d1:
                del_id = st.selectbox("เลือกรหัสมื้ออาหารที่จะลบ", list(mdf["id"]), key="adm_meal_del_id")
            with d2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("ลบมื้อนี้", key="adm_meal_del"):
                    _exec("DELETE FROM meals WHERE id = ?", (int(del_id),))
                    log_admin(me["id"], "delete_meal", f"meal={int(del_id)}")
                    st.rerun()

    # ---------- แชต ----------
    with t_chat:
        sel_c = st.selectbox("ผู้ใช้", opts, format_func=lambda i: names[i], key="adm_chat_user")
        sql = "SELECT c.id, u.username, c.role, c.message, c.created_at FROM ai_chat c JOIN users u ON u.id = c.user_id"
        cdf = _df(sql + (" WHERE c.user_id = ?" if sel_c else "") + " ORDER BY c.id DESC LIMIT 500", (sel_c,) if sel_c else ())
        st.dataframe(cdf, use_container_width=True, hide_index=True)
        if sel_c:
            ck = st.checkbox("ยืนยันลบประวัติแชตของผู้ใช้นี้ทั้งหมด", key="adm_chat_ck")
            if st.button("🗑️ ลบประวัติแชต", key="adm_chat_del", disabled=not ck):
                clear_chat(sel_c)
                log_admin(me["id"], "clear_chat", f"user={sel_c}")
                st.rerun()

    # ---------- ข้อมูล / สำรอง / ล็อก ----------
    with t_data:
        st.markdown("**ส่งออกข้อมูล (CSV)** — ไม่รวมรหัสผ่าน/รูปภาพ")
        e1, e2, e3, e4, e5 = st.columns(5)
        with e1:
            _csv_button("👥 ผู้ใช้", _df(f"SELECT {USER_COLS} FROM users"), "users.csv", "exp_users")
        with e2:
            _csv_button("🩺 สุขภาพ", _df("SELECT id, user_id, cc, pi, ph, fh, chronic, weight, height, bmi, constitution, history_json, updated_at FROM health_data"), "health_data.csv", "exp_health")
        with e3:
            _csv_button("🍲 อาหาร", _df("SELECT id, user_id, meal_date, meal_time, meal_type, food_name, ingredients, amount, calories, note, created_at FROM meals"), "meals.csv", "exp_meals")
        with e5:
            _csv_button("🏃 ออกกำลังกาย", _df("SELECT id, user_id, ex_date, ex_time, ex_type, duration_min, intensity, calories, note, created_at FROM exercises"), "exercises.csv", "exp_ex")
        with e4:
            _csv_button("💬 แชต", _df("SELECT * FROM ai_chat"), "ai_chat.csv", "exp_chat")

        st.markdown("**สำรองฐานข้อมูลทั้งไฟล์**")
        try:
            with open(DB_PATH, "rb") as fh:
                st.download_button(
                    "⬇️ ดาวน์โหลด thai_balance.db", data=fh.read(), file_name="thai_balance_backup.db",
                    mime="application/octet-stream", key="exp_db", use_container_width=True,
                )
            st.caption("ไฟล์นี้มีข้อมูลส่วนบุคคลและรหัสผ่านแบบแฮช เก็บรักษาให้ปลอดภัย")
        except Exception as exc:
            st.warning(f"อ่านไฟล์ฐานข้อมูลไม่ได้: {exc}")

        st.markdown("**ล็อกการทำงานของแอดมิน (ล่าสุด 200 รายการ)**")
        st.dataframe(
            _df("SELECT l.id, u.username AS admin, l.action, l.detail, l.created_at FROM admin_log l LEFT JOIN users u ON u.id = l.admin_id ORDER BY l.id DESC LIMIT 200"),
            use_container_width=True, hide_index=True,
        )
    close_panel()


# ============================================================
# NAVIGATION — หน้าที่เปิดได้ผ่านลิงก์ในเบราว์เซอร์ เช่น http://localhost:8501/?page=history
# ============================================================
MENU = {
    "home": "🏠 หน้าหลัก",
    "health": "🩺 สุขภาพ / ซักประวัติ",
    "meal": "🍲 บันทึกอาหาร / ออกกำลังกาย",
    "report": "📊 รายงาน / สถิติ",
    "chat": "🧑‍⚕️ หมอไทยบอท",
    "admin": "🛠️ ผู้ดูแลระบบ",
}
ALL_PAGES = list(MENU) + ["profile", "history"]


def menu_options(user):
    return [v for k, v in MENU.items() if k != "admin" or is_admin(user)]
LABEL_TO_PAGE = {v: k for k, v in MENU.items()}


def _menu_label(page):
    if page == "history":
        return MENU["health"]
    return MENU.get(page)  # profile -> None (ไม่เลือกในเมนูบน)


def goto(page):
    if page not in ALL_PAGES:
        page = "home"
    if page == "history" and st.session_state.get("page") != "history":
        st.session_state.hx_step = 1
    st.session_state.page = page
    st.session_state["menu"] = _menu_label(page)
    try:
        st.query_params["page"] = page
    except Exception:
        pass


def on_menu_change():
    label = st.session_state.get("menu")
    if label in LABEL_TO_PAGE:
        goto(LABEL_TO_PAGE[label])


# ============================================================
# APP MAIN
# ============================================================
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    auth_page()
else:
    user = get_user(st.session_state.user["id"])
    if not user or user.get("is_active") == 0:
        st.session_state.clear()
        st.rerun()
    st.session_state.user = user

    # อ่านหน้าจาก URL (?page=...) ครั้งแรกที่เปิด
    if "page" not in st.session_state:
        try:
            first = st.query_params.get("page", "home")
        except Exception:
            first = "home"
        goto(first)

    render_header()

    # เมนูบน (หน้าหลักของระบบ)
    st.radio(
        "เมนูหลัก", menu_options(user), index=None, horizontal=True,
        label_visibility="collapsed", key="menu", on_change=on_menu_change,
    )

    page = st.session_state.get("page", "home")
    if page == "profile":
        profile_page()
    elif page == "health":
        health_status_page()
    elif page == "history":
        history_page()
    elif page == "meal":
        meal_page()
    elif page == "report":
        report_page()
    elif page == "chat":
        ai_chat_page()
    elif page == "admin" and is_admin(user):
        admin_page()
    else:
        dashboard_page()

    st.markdown(
        """
        <div style="text-align:center;color:#668073;margin-top:25px;padding:18px">
            Thai Balance — ดูแลสุขภาพคุณ ในแบบที่เป็นคุณ ♡
        </div>
        """,
        unsafe_allow_html=True,
    )




 