# هوم (Haoma) — راهنمای فارسی

سایت دوزبانهٔ پادکست و wiki اسطوره (English + فارسی/RTL)، ساخته‌شده با [Hugo](https://gohugo.io/) و deploy روی GitHub Pages.

این فایل خلاصهٔ **ویرایش سایت** برای خوانندهٔ فارسی است. جزئیات فنی کامل‌تر در [`README.md`](README.md) است. راهنمای روی خودِ سایت: **[/fa/editor/](https://v4g4b0nd-0x76.github.io/Haoma/fa/editor/)**.

---

## ویرایشگر وب (پیشنهاد اگر نصب نمی‌خواهید)

1. صفحهٔ launcher را باز کنید:  
   <https://v4g4b0nd-0x76.github.io/Haoma/tools/>  
   (دکمهٔ **فارسی** را بزنید اگر متن English دیدید.)
2. روی **Open editor** کلیک کنید.
3. با GitHub وارد شوید (اگر خواست).
4. صبر کنید تا Codespace بالا بیاید.
5. Editor در tab جدید مرورگر باز می‌شود.

بعد صفحه را ویرایش کنید، با **Save** ذخیره کنید، و با **Publish & PR** یک branch بفرستید و pull request باز کنید.

اگر preview خالی بود، در Codespace تب **Ports** → port **1313**.

سایت live فقط read-only است؛ تغییر فایل‌ها فقط در Codespace یا editor محلی انجام می‌شود.

در editor، دکمهٔ **فارسی / English** پایین نوار کناری زبان رابط را عوض می‌کند (راهنماها به فارسی روان؛ واژه‌های فنی مثل Save و Preview انگلیسی می‌مانند).

---

## Binary دسکتاپ (بدون Python)

### Download

1. [Releases](https://github.com/v4g4b0nd-0x76/Haoma/releases) → آخرین tag `editor-v…`
2. از **Assets** فایل مناسب را بگیرید:

| سیستم | فایل |
|---|---|
| Linux | `haoma-editor-linux-amd64` |
| Windows | `haoma-editor-windows-amd64.exe` |
| macOS | `haoma-editor-macos-amd64` |

### کجا بگذارید

Repo را clone کنید (همان پوشه‌ای که `hugo.toml` دارد) و binary را **کنار `hugo.toml`** بگذارید:

```text
Haoma/
  hugo.toml
  haoma-editor-linux-amd64
  content/
  …
```

یا environment variable `HAOMA_ROOT` را روی مسیر آن پوشه بگذارید.

### پیش‌نیازها

Binary فقط جای Python را می‌گیرد. همچنان لازم است:

- [Hugo Extended](https://gohugo.io/installation/) ≥ ۰٫۱۳۹
- git

### اجرا

```bash
# Linux / macOS
cd /path/to/Haoma
chmod +x haoma-editor-linux-amd64
./haoma-editor-linux-amd64
```

Windows: روی `.exe` دوبار کلیک کنید، یا از PowerShell در همان پوشه اجرا کنید.

مرورگر باید `http://localhost:8765/` را باز کند.

---

## Python (اختیاری)

```bash
git clone https://github.com/v4g4b0nd-0x76/Haoma
cd Haoma
python tools/editor.py
```

---

## کدام را انتخاب کنم؟

| وضعیت | پیشنهاد |
|---|---|
| بدون نصب | ویرایشگر وب (`/tools/`) |
| Offline / clone محلی | Binary دسکتاپ |
| توسعه با Python | `python tools/editor.py` |

---

## پیوندهای مفید

- راهنمای روی سایت (فارسی): [/fa/editor/](https://v4g4b0nd-0x76.github.io/Haoma/fa/editor/)
- راهنمای روی سایت (English): [/editor/](https://v4g4b0nd-0x76.github.io/Haoma/editor/)
- مشارکت: [`CONTRIBUTING.fa.md`](CONTRIBUTING.fa.md) · [`CONTRIBUTING.md`](CONTRIBUTING.md)
