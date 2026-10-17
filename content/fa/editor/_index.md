---
title: "چگونه هوم را ویرایش کنیم"
tagline: "ویرایشگر وب (Codespace) و binary دسکتاپ — بدون IDE"
grade: راهنما
reviewed: 2026-10-17
sources:
  - "مستندات پروژهٔ هوم (همین repository)"
---

دو راه برای ویرایش هوم دارید: در **مرورگر** (اگر نمی‌خواهید چیزی نصب کنید، همین را پیشنهاد می‌کنیم) یا با **binary دسکتاپ** روی کامپیوتر خودتان. هر دو همان editor را باز می‌کنند: draft، preview زنده، map studio، و **Publish & PR**.

## ۱. ویرایشگر وب (ساده‌ترین راه)

با Chrome، Firefox، Safari یا Edge کار می‌کند. فقط یک حساب رایگان GitHub لازم است.

1. صفحهٔ launcher را باز کنید: [**/tools/**](/tools/) در همین سایت  
   (نسخهٔ آنلاین: <https://v4g4b0nd-0x76.github.io/Haoma/tools/>).
2. روی **Open editor** کلیک کنید.
3. اگر خواست، با GitHub وارد شوید (sign in).
4. کمی صبر کنید تا Codespace خصوصی بالا بیاید — وقتی prebuild آماده باشد اغلب کمتر از یک دقیقه است.
5. Editor **خودش** در یک tab جدید مرورگر باز می‌شود.

بعد از آن:

- صفحه‌ها، themeها یا mapها را در پنل‌ها ویرایش کنید.
- وقتی می‌خواهید تغییرها واقعاً در پروژه نوشته شوند **Save** را بزنید؛ تا آن لحظه فقط draft هستند.
- برای push کردن branch و باز کردن pull request از **Publish & PR** استفاده کنید.

اگر قاب preview خالی ماند، در Codespace تب **Ports** را باز کنید و port **1313** را باز کنید.

> خودِ سایت live فقط read-only است. فقط Codespace شما (یا editor محلی) می‌تواند فایل‌ها را عوض کند.

## ۲. Binary دسکتاپ (بدون Python)

اگر ترجیح می‌دهید روی کامپیوتر خود کار کنید و Python نصب نکنید، از این روش استفاده کنید.

### Download

1. صفحهٔ **[Releases](https://github.com/v4g4b0nd-0x76/Haoma/releases)** را در GitHub باز کنید.
2. آخرین release با tag `editor-v…` را باز کنید (مثلاً `editor-v1.0.0`).
3. از بخش **Assets** فایل مناسب سیستم خود را بگیرید:

| سیستم شما | فایل |
|---|---|
| Linux ۶۴بیتی | `haoma-editor-linux-amd64` |
| Windows ۶۴بیتی | `haoma-editor-windows-amd64.exe` |
| macOS (ساخت amd64) | `haoma-editor-macos-amd64` |

### کجا بگذاریدش

Binary باید پوشهٔ پروژهٔ هوم را پیدا کند (همان جایی که `hugo.toml` هست).

**چیدمان پیشنهادی:**

```text
Haoma/                          ← clone گیت همین repo
  hugo.toml
  content/
  …
  haoma-editor-linux-amd64      ← binary اینجاست (کنار hugo.toml)
```

یا binary را هر جا بگذارید و environment variable بگذارید:

- `HAOMA_ROOT` = مسیر کامل پوشهٔ پروژه (همان که `hugo.toml` دارد).

### هنوز روی کامپیوتر لازم است

Binary فقط جای **Python** را می‌گیرد. همچنان لازم دارید:

1. **[Hugo Extended](https://gohugo.io/installation/)** نسخهٔ ۰٫۱۳۹ یا بالاتر (`hugo version` باید کلمهٔ `extended` را نشان دهد)
2. **git**

### اجرا

**Linux / macOS**

```bash
cd /path/to/Haoma
chmod +x haoma-editor-linux-amd64   # یک‌بار
./haoma-editor-linux-amd64
```

**Windows**

1. Repo هوم را clone یا download کنید.
2. `haoma-editor-windows-amd64.exe` را در همان پوشه بگذارید (کنار `hugo.toml`).
3. روی `.exe` دوبار کلیک کنید، یا از PowerShell / Command Prompt اجرا کنید.

مرورگر باید `http://localhost:8765/` را باز کند (آدرس در terminal هم چاپ می‌شود).

### اگر مرورگر باز نشد

خودتان این آدرس را باز کنید: [http://localhost:8765/](http://localhost:8765/)

### توقف editor

در پنجرهٔ terminal که برنامه در آن اجراست `Ctrl+C` بزنید. در Windows اگر با دوبارکلیک باز کرده‌اید، همان پنجره را ببندید.

## ۳. اختیاری: Python از داخل repo

اگر از قبل روی repo کار می‌کنید:

```bash
git clone https://github.com/v4g4b0nd-0x76/Haoma
cd Haoma
python tools/editor.py
```

همان UIِ binary دسکتاپ و Codespace وب است.

## کدام را انتخاب کنم؟

| وضعیت | پیشنهاد |
|---|---|
| بدون نصب، از هر کامپیوتر | **ویرایشگر وب** (`/tools/`) |
| Offline، یا repo را clone دارید | **Binary دسکتاپ** |
| با Python راحتید | `python tools/editor.py` |

## کمک می‌خواهید؟

- مشکل را گزارش کنید: روی هر صفحه **گزارش اصلاح** را بزنید، یا در GitHub یک issue باز کنید.
- جزئیات بیشتر برای مشارکت‌کنندگان: در repo فایل `README.fa.md` و بخش‌های ۵ و ۱۰ در `README.md`.
