"""
明日方舟寻访记录获取脚本
========================
使用 Playwright 无头浏览器自动登录 ak.hypergryph.com，
拦截 API 响应获取全部寻访数据，追加合并到本地 JSON。

流程：
  1. 读取 daily_tasks/config.json 获取凭证
  2. Playwright 自动登录 → 导航到寻访记录页面
  3. 拦截 API 请求获取 auth headers → 逐分类翻页拉取
  4. 与本地已有记录合并去重 → 保存 raw_data/gacha_records.json

依赖：pip install playwright
首次：python -m playwright install chromium
"""

import sys, os, json, time

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ pip install playwright && python -m playwright install chromium")
    sys.exit(1)

# ─── 路径配置 ──────────────────────────────────────────────────
GACHA_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR    = os.path.abspath(os.path.join(GACHA_DIR, ".."))
CONFIG_FILE = os.path.join(ROOT_DIR, "daily_tasks", "config.json")
RAW_DIR     = os.path.join(GACHA_DIR, "raw_data")
RAW_FILE    = os.path.join(RAW_DIR, "gacha_records.json")

AK_BASE    = "https://ak.hypergryph.com"
LOGIN_PAGE = f"{AK_BASE}/user"
HH_PAGE    = f"{AK_BASE}/user/headhunting"
HEADLESS   = True  # 改为 False 可看浏览器窗口调试
# ──────────────────────────────────────────────────────────────


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ 配置文件不存在: {CONFIG_FILE}")
        print(f"   请在 daily_tasks/config.json 中填写 phone 和 password")
        sys.exit(1)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_existing_records() -> list:
    """加载已有的记录"""
    if os.path.exists(RAW_FILE):
        with open(RAW_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def merge_records(existing: list, new: list) -> list:
    """合并记录，用 (gachaTs, pos) 去重，保持按时间降序"""
    seen = set()
    merged = []
    for r in existing + new:
        key = (r.get("gachaTs", ""), r.get("pos", ""))
        if key not in seen:
            seen.add(key)
            merged.append(r)
    # 按 gachaTs 降序排列（最新的在前）
    merged.sort(key=lambda r: int(r.get("gachaTs", "0")), reverse=True)
    return merged


def do_login(page, phone: str, password: str) -> bool:
    """Playwright 自动登录，返回是否成功。"""

    print("\n[1/2] 自动登录 ...")
    page.goto(LOGIN_PAGE, wait_until="networkidle", timeout=30000)
    time.sleep(2)

    # 点击"登录"
    for sel in ["text=登录", "text=前往登录"]:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=2000):
                el.click()
                break
        except Exception:
            continue
    time.sleep(2)

    # 选择鹰角通行证
    page.mouse.click(580, 380)
    time.sleep(3)

    # 切换到密码登录
    for sel in ["text=密码登录", "text=账号密码"]:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=2000):
                el.click()
                time.sleep(1)
                break
        except Exception:
            continue

    # 填写表单
    frame = page.main_frame
    for f in page.frames:
        if "user.hypergryph.com" in f.url or "as.hypergryph.com" in f.url:
            frame = f
            break

    phone_input = pwd_input = None
    for sel in ["input[placeholder*='手机']", "input[type=tel]", "input[name=phone]"]:
        try:
            el = frame.locator(sel).first
            if el.is_visible(timeout=2000):
                phone_input = el
                break
        except Exception:
            continue
    if not phone_input:
        page.screenshot(path=os.path.join(RAW_DIR, "debug.png"))
        return False

    phone_input.fill(phone)
    time.sleep(0.3)

    for sel in ["input[type=password]", "input[placeholder*='密码']"]:
        try:
            el = frame.locator(sel).first
            if el.is_visible(timeout=2000):
                pwd_input = el
                break
        except Exception:
            continue
    if not pwd_input:
        return False

    pwd_input.fill(password)
    time.sleep(0.3)

    # 勾选协议
    for f in page.frames:
        try:
            el = f.locator("text=已同意").first
            if el.is_visible(timeout=2000):
                box = el.bounding_box()
                if box:
                    page.mouse.click(box["x"] - 15, box["y"] + box["height"] / 2)
                    break
        except Exception:
            pass
    time.sleep(0.5)

    # 提交
    pwd_input.press("Enter")
    time.sleep(2)

    # 等待登录完成
    for i in range(15):
        time.sleep(1)
        try:
            text = page.locator("body").inner_text()[:300]
            if "前往登录" not in text and "当前未登录" not in text:
                print(f"  ✅ 登录成功 ({i+1}s)")
                return True
        except Exception:
            pass

    page.screenshot(path=os.path.join(RAW_DIR, "debug_timeout.png"))
    return False


def fetch_gacha_records(page) -> list:
    """拦截 auth headers → 分类 + 翻页获取全部寻访记录"""
    auth_headers = {}

    def on_request(req):
        nonlocal auth_headers
        if "/user/api/inquiry/gacha" in req.url:
            h = dict(req.headers)
            for key in h:
                if key.lower() not in ("accept", "user-agent", "referer",
                                        "origin", "content-type", "sec-",
                                        "accept-language", "accept-encoding",
                                        "connection", "host", "upgrade-insecure"):
                    if key.lower() not in auth_headers:
                        auth_headers[key.lower()] = h[key]

    cate_data = []

    def on_response(resp):
        if "/user/api/inquiry/gacha" in resp.url and resp.status == 200:
            ct = resp.headers.get("content-type", "")
            if "json" in ct:
                try:
                    body = resp.json()
                    data = body.get("data")
                    if isinstance(data, list) and data and "name" in data[0]:
                        cate_data.extend(data)
                except Exception:
                    pass

    page.on("request", on_request)
    page.on("response", on_response)

    print("\n[2/2] 拉取寻访记录 ...")
    page.goto(HH_PAGE, wait_until="networkidle", timeout=30000)
    time.sleep(5)

    try:
        el = page.locator("text=寻访记录").first
        if el.is_visible(timeout=2000):
            el.click()
            time.sleep(5)
    except Exception:
        pass

    page.remove_listener("request", on_request)
    page.remove_listener("response", on_response)

    if not cate_data:
        print("  ❌ 未获取到分类数据")
        return []

    cats = cate_data
    print(f"  {len(cats)} 个分类: {[c['name'].replace(chr(10),' ') for c in cats]}")

    # 用拦截的 auth headers 逐分类翻页
    auth_js = json.dumps(auth_headers)
    page.evaluate(f"""
        window.__authHeaders = {auth_js};
        window.__apiFetch = async (url) => {{
            const headers = {{ 'Accept': 'application/json', ...window.__authHeaders }};
            const resp = await fetch(url, {{ credentials: 'include', headers }});
            const text = await resp.text();
            try {{ return {{ status: resp.status, body: JSON.parse(text) }}; }}
            catch(e) {{ return {{ status: resp.status, raw: text.substring(0, 300) }}; }}
        }};
        0
    """)

    all_records = []
    for cat in cats:
        cat_id = cat["id"]
        cat_name = cat["name"].replace("\n", " ")
        page_num = 1
        extra = ""

        print(f"\n  [{cat_name}]")
        while True:
            url = f"/user/api/inquiry/gacha/history?category={cat_id}&size=50{extra}"
            result = page.evaluate(f"window.__apiFetch('{url}')")

            if "raw" in result:
                print(f"    非 JSON 响应，跳过")
                break
            if result["status"] != 200:
                print(f"    HTTP {result['status']}")
                break

            body = result["body"]
            if body.get("code") != 0:
                print(f"    API 错误: {body.get('msg')}")
                break

            data = body.get("data") or {}
            items = data.get("list") or []
            has_more = data.get("hasMore", False)

            for item in items:
                item["_category"] = cat_name
            all_records.extend(items)
            print(f"    第{page_num}页: {len(items)}条  累计{len(all_records)}  hasMore={has_more}")

            if not has_more or not items:
                break

            last = items[-1]
            extra = f"&gachaTs={last.get('gachaTs', '')}&pos={last.get('pos', '')}"
            page_num += 1
            time.sleep(0.3)

    return all_records


def main():
    os.makedirs(RAW_DIR, exist_ok=True)

    print("=" * 50)
    print("  明日方舟寻访记录获取")
    print("=" * 50)

    config = load_config()
    phone = config.get("phone", "")
    password = config.get("password", "")
    if not phone or not password:
        print(f"❌ config.json 中缺少 phone 或 password")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="zh-CN",
        )
        page = context.new_page()

        if not do_login(page, phone, password):
            print("❌ 登录失败")
            browser.close()
            return

        new_records = fetch_gacha_records(page)
        browser.close()

    if not new_records:
        print("\n❌ 未获取到任何寻访记录")
        return

    # 合并 & 保存
    existing = load_existing_records()
    merged = merge_records(existing, new_records)

    with open(RAW_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    new_count = len(merged) - len(existing)
    print(f"\n{'='*50}")
    print(f"✅ 本次拉取 {len(new_records)} 条")
    print(f"   已有 {len(existing)} 条 → 合并后 {len(merged)} 条 (新增 {new_count})")
    print(f"💾 {RAW_FILE}")


if __name__ == "__main__":
    main()
