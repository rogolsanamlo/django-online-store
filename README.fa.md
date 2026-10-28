# فروشگاه اینترنتی با Django

🇬🇧 [English](README.md)

یک فروشگاه اینترنتی فارسی (راست‌به‌چپ) با Django. پروژه از یک دورهٔ آموزشی ویدیویی (فروشگاه تک‌فروشنده) شروع شد
و بعداً اصلاح و تکمیل شد: درگاه پرداخت **زرین‌پال** که دوباره کار می‌کند، مدیریت موجودی انبار، تست خودکار و تنظیمات امن‌تر.

## امکانات

- مدل کاربر سفارشی (ورود با شماره موبایل)، فعال‌سازی با پیامک (کاوه‌نگار) و بازیابی رمز عبور
- گروه‌بندی کالا، برند، ویژگی‌های پویا و فیلتر، فیلتر قیمت، مرتب‌سازی، صفحه‌بندی و مقایسهٔ کالاها
- سبد خرید مبتنی بر session، کوپن تخفیف و سبد تخفیف
- ثبت سفارش و **پرداخت آنلاین با زرین‌پال** (پشتیبانی از sandbox)
- سابقهٔ پرداخت هر کاربر و فهرست پرداخت‌ها در پنل ادمین
- انبار: بعد از تأیید پرداخت، موجودی خودکار و فقط یک بار کم می‌شود
- نظرات کالا (با تأیید مدیر)، امتیازدهی ۰ تا ۵ و علاقه‌مندی‌ها
- پنل ادمین فارسی با ویرایشگر CKEditor برای توضیحات

## تصاویر

### خرید
<table>
  <tr>
    <td align="center"><img src="docs/screenshots/01-home.png" alt="صفحهٔ اصلی و منوی دسته‌بندی"><br><sub>صفحهٔ اصلی و منوی دسته‌بندی</sub></td>
    <td align="center"><img src="docs/screenshots/02-product-cards.png" alt="کارت محصول: سبد خرید، علاقه‌مندی، مقایسه"><br><sub>کارت محصول: سبد خرید، علاقه‌مندی، مقایسه</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/03-categories.png" alt="دسته‌های محبوب و جدیدترین محصولات"><br><sub>دسته‌های محبوب و جدیدترین محصولات</sub></td>
    <td align="center"><img src="docs/screenshots/04-product-details.png" alt="جزئیات کالا، امتیاز و برند"><br><sub>جزئیات کالا، امتیاز و برند</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/05-reviews.png" alt="دیدگاه مشتریان"><br><sub>دیدگاه مشتریان</sub></td>
    <td align="center"><img src="docs/screenshots/06-compare.png" alt="مقایسهٔ کالاها"><br><sub>مقایسهٔ کالاها</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/07-favorites.png" alt="علاقه‌مندی‌ها"><br><sub>علاقه‌مندی‌ها</sub></td>
    <td align="center"><img src="docs/screenshots/10-cart.png" alt="سبد خرید"><br><sub>سبد خرید</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/11-cart-summary.png" alt="مجموع سبد: حمل و نقل و مالیات"><br><sub>مجموع سبد: حمل و نقل و مالیات</sub></td>
    <td align="center"><img src="docs/screenshots/12-checkout.png" alt="پرداخت و اعمال کد تخفیف"><br><sub>پرداخت و اعمال کد تخفیف</sub></td>
  </tr>
</table>

### حساب کاربری و پرداخت
<table>
  <tr>
    <td align="center"><img src="docs/screenshots/08-register.png" alt="ثبت‌نام با شماره موبایل"><br><sub>ثبت‌نام با شماره موبایل</sub></td>
    <td align="center"><img src="docs/screenshots/09-verify-mobile.png" alt="تأیید شماره موبایل"><br><sub>تأیید شماره موبایل</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/13-zarinpal-sandbox.png" alt="درگاه آزمایشی زرین‌پال"><br><sub>درگاه آزمایشی زرین‌پال</sub></td>
    <td align="center"><img src="docs/screenshots/14-payment-result.png" alt="نتیجهٔ پرداخت و کد رهگیری"><br><sub>نتیجهٔ پرداخت و کد رهگیری</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/15-my-payments.png" alt="سابقهٔ پرداخت‌ها در پنل کاربر"><br><sub>سابقهٔ پرداخت‌ها در پنل کاربر</sub></td>
    <td></td>
  </tr>
</table>

### پنل کاربر و صفحه‌ها
<table>
  <tr>
    <td align="center"><img src="docs/screenshots/25-login.png" alt="ورود با شماره موبایل"><br><sub>ورود با شماره موبایل</sub></td>
    <td align="center"><img src="docs/screenshots/26-remember-password.png" alt="بازیابی رمز عبور"><br><sub>بازیابی رمز عبور</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/22-user-panel.png" alt="پنل کاربری: پروفایل"><br><sub>پنل کاربری: پروفایل</sub></td>
    <td align="center"><img src="docs/screenshots/23-user-panel-orders.png" alt="پنل کاربری: سفارش‌های اخیر"><br><sub>پنل کاربری: سفارش‌های اخیر</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/24-change-password.png" alt="تغییر رمز عبور"><br><sub>تغییر رمز عبور</sub></td>
    <td align="center"><img src="docs/screenshots/19-contact.png" alt="صفحهٔ تماس با ما"><br><sub>صفحهٔ تماس با ما</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/20-about.png" alt="صفحهٔ درباره ما"><br><sub>صفحهٔ درباره ما</sub></td>
    <td align="center"><img src="docs/screenshots/21-terms.png" alt="قوانین و مقررات"><br><sub>قوانین و مقررات</sub></td>
  </tr>
</table>

### پنل مدیریت
<table>
  <tr>
    <td align="center"><img src="docs/screenshots/16-admin-products.png" alt="ادمین: کالاها"><br><sub>ادمین: کالاها</sub></td>
    <td align="center"><img src="docs/screenshots/17-admin-warehouse.png" alt="ادمین: ورود و خروج انبار"><br><sub>ادمین: ورود و خروج انبار</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/18-admin-discount-basket.png" alt="ادمین: سبد تخفیف"><br><sub>ادمین: سبد تخفیف</sub></td>
    <td></td>
  </tr>
</table>

## تفاوت با پروژهٔ دوره

**پرداخت**
- اپ پرداخت دوره با API فعلی زرین‌پال کار نمی‌کرد. آن را با REST API نسخهٔ ۴ زرین‌پال (`requests`: درخواست، انتقال، تأیید)
  از نو نوشتم. کد در `apps/payments/gateway.py` است.
- فقط صاحب سفارش می‌تواند آن را پرداخت کند؛ مبلغ‌ها به تومان ذخیره و برای درگاه به ریال تبدیل می‌شوند.
- تأیید پرداخت idempotent است: رفرش صفحهٔ بازگشت هرگز دو بار موجودی کم نمی‌کند
  (`select_for_update` و `transaction.atomic`).
- پیام نتیجه در session نگه داشته می‌شود، نه در URL.

**تنظیمات و امنیت**
- هیچ رمز و کلیدی در مخزن نیست؛ همه از متغیرهای محیطی (`.env.example`) خوانده می‌شود.
- پیش‌فرض MySQL است و با `DB_ENGINE=sqlite` می‌توان از SQLite استفاده کرد.
- قیمت‌های سفارش از دیتابیس خوانده و در ردیف‌های سفارش ثابت می‌شود.

**کیفیت کد**
- نام فارسی برای اپ‌ها، مدل‌ها و فیلدها در ادمین.
- مجموعه‌تست (احراز هویت، سبد و سفارش، پرداخت، صفحه‌ها، ادمین) که در آن فراخوانی زرین‌پال و ارسال پیامک mock شده است.

## راه‌اندازی سریع

```bash
python -m venv .venv && source .venv/bin/activate     # ویندوز: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # سپس مقادیر را ویرایش کنید
python manage.py migrate
python manage.py seed_data                             # نوع پرداخت، وضعیت سفارش و انواع انبار پیش‌فرض
python manage.py seed_demo                             # اختیاری: دسته‌ها، برندها و کالاهای نمونه
python manage.py createsuperuser
python manage.py runserver
```

پایگاه‌داده پیش‌فرض MySQL است: ابتدا یک دیتابیس خالی بسازید و متغیرهای `DB_*` را در `.env` پر کنید.
برای استفاده از فایل محلی `db.sqlite3` مقدار `DB_ENGINE=sqlite` را بگذارید.

### کد ثبت‌نام در حالت توسعه
برای اجرای محلی کلید پیامک لازم نیست. بدون کلید کاوه‌نگار پیامکی ارسال نمی‌شود و چیزی هم چاپ نمی‌شود؛
کد فعال‌سازی در دیتابیس ذخیره می‌شود (جدول `accounts_customuser`، ستون `active_code`). آن را از همان‌جا
یا در ادمین، بخش کاربران، فیلد «کد فعال سازی» بخوانید.

## روند پرداخت (زرین‌پال)

1. `orders:create_order` سبد خرید را به یک `Order` تبدیل می‌کند (قیمت‌ها از دیتابیس).
2. `orders:checkout_order` آدرس و نوع پرداخت را می‌گیرد و کوپن اعمال می‌کند.
3. `payments:zarinpal_payment` یک `Payment` می‌سازد، *authority* می‌گیرد و کاربر را به درگاه می‌برد.
4. درگاه به `payments:zarinpal_verify` برمی‌گردد و پرداخت با مبلغ ذخیره‌شده تأیید می‌شود.
5. در صورت موفقیت، سفارش پرداخت‌شده ثبت، موجودی یک بار کم و سبد خالی می‌شود.

هنگام توسعه `ZARINPAL_SANDBOX=True` بگذارید.

## تست

```bash
python manage.py test
```

## ساختار پروژه

```
apps/
  accounts/   کاربران، پروفایل، تأیید پیامکی
  products/   کاتالوگ، فیلترها، مقایسه
  orders/     سبد خرید، سفارش، کوپن، تسویه
  payments/   اتصال به زرین‌پال
  warehouses/ ورود و خروج انبار
  discounts/  کوپن و سبد تخفیف
  comment_scoring_favorites/  نظر، امتیاز، علاقه‌مندی
  search/ main/
```

## منبع و سپاس

این پروژه بر پایهٔ دورهٔ فروشگاه اینترنتی Django با نام *دوره آموزشی استادی پایتون در سطح وب* از *مهدی عباسی* ([لینک دوره](https://darsmanco.ir/)) ساخته شده است.
ساختار پروژه، مدل داده و قالب ظاهری از همان دوره است. تغییراتِ بخش «تفاوت با پروژهٔ دوره»، از جمله اپ پرداخت، تست‌ها
و تنظیمات، چیزهایی است که روی آن ساخته‌ام.

در بازنویسی اپ پرداخت، رفع باگ‌ها و نوشتن تست‌ها و مستندات از Claude (دستیار هوش مصنوعی) کمک گرفتم.
پروژه را خودم اجرا و تست کردم، از جمله روند پرداخت sandbox زرین‌پال.

## نکته‌ها

- `django-ckeditor` از CKEditor 4 استفاده می‌کند که دیگر نگهداری نمی‌شود؛ جایگزین مناسب `django-ckeditor-5` است.
- favicon، آیکون‌های `sprite.svg` و آواتار پیش‌فرض (`customer/nophoto.jpg`) در `static/images` هستند.
  تصاویر نمونه (دسته‌ها، اسلایدها، آواتارها، کالاها، لوگوها) در `media/images` هستند؛ تصاویری که از پنل مدیریت آپلود می‌شوند
  (برند، گروه کالا، گالری کالا، CKEditor) در git نادیده گرفته می‌شوند.
- دارایی‌های شخص ثالث: قالب ظاهری، فونت‌ها و بعضی تصاویر نمونه از پروژهٔ دوره آمده‌اند و لایسنس خودشان را دارند.
  پیش از استفادهٔ مجدد یا انتشار آن‌ها لایسنس را بررسی کنید.

## لایسنس

این پروژه تحت لایسنس MIT منتشر شده است (فایل `LICENSE`). این لایسنس فقط شامل کد خودم است؛ دارایی‌های شخص ثالث
(قالب ظاهری، فونت‌ها، بعضی تصاویر نمونه) و مطالب اصلی دوره لایسنس خودشان را دارند.
