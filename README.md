# همراه فارسی Java و Spring

این پروژه یک کتاب همراهِ فارسی برای مسیر Java 21 تا Spring و یک خوانندهٔ ترمینالی سبک است. متن فصل‌ها مستقل نوشته می‌شود؛ مثال‌ها، تمرین‌ها و پرسش‌ها ترجمه یا بازتولید متن منبع نیستند.

## ساختار

```text
java-spring-farsi-book/
├── README.md
├── reader.py                         # خوانندهٔ CLI، فقط با کتابخانهٔ استاندارد
├── quiz_engine.py                    # انتخاب و زمان‌بندی تطبیقیِ پرسش‌ها
├── rtl.py                            # راست‌چین‌سازی و isolateهای Unicode برای ترمینال
├── tools/
│   └── validate_quiz.py              # اعتبارسنجی بانک‌ها؛ --merge فقط با تصمیم آگاهانه
└── book/
    ├── 01-building-blocks.md         # فصل منتشرشدهٔ درجهٔ ۱: پایه‌های Java 21
    ├── parts/                        # قطعه‌های منبع prose برای فصل درجهٔ ۱
    └── quiz/
        ├── grade-01.json             # بانک کاملِ درجهٔ ۱
        ├── grade-02.json … grade-12.json
        └── .parts/                   # قطعه‌های منبع JSON برای ساخت بانک‌ها
```

## پیش‌نیاز و اجرا

به Python 3.10 یا جدیدتر نیاز دارید و هیچ وابستگی خارجی لازم نیست.

```bash
python3 /home/snapp/Downloads/java-spring-farsi-book/reader.py list
python3 /home/snapp/Downloads/java-spring-farsi-book/reader.py read 1
```

در حالت مطالعه، صفحه‌بندی از عرض و ارتفاع فعلی ترمینال استفاده می‌کند. فرمان‌های تعاملی:

```text
Enter یا n     صفحهٔ بعد
p              صفحهٔ قبل
g 12           رفتن به صفحهٔ ۱۲
c              فهرست فصل‌ها
s              وضعیت محلی
q              خروج
```

فرمان‌های تکمیلی:

```bash
python3 /home/snapp/Downloads/java-spring-farsi-book/reader.py status
python3 /home/snapp/Downloads/java-spring-farsi-book/reader.py quiz grade-01 --count 5
python3 /home/snapp/Downloads/java-spring-farsi-book/reader.py review --count 5
```

وضعیت مطالعه و پاسخ‌ها، به‌طور پیش‌فرض، اینجا ذخیره می‌شود:

```text
$XDG_STATE_HOME/java-spring-farsi-book/progress.json
```

اگر `XDG_STATE_HOME` تنظیم نشده باشد، مسیر پیش‌فرض `~/.local/state/java-spring-farsi-book/progress.json` است. برای پروفایل یا آزمون جداگانه:

```bash
python3 /home/snapp/Downloads/java-spring-farsi-book/reader.py \
  --state /tmp/java-book-progress.json read 1
```

## خواننده و مرور تطبیقی

- صفحه‌بندی Markdown بر اساس اندازهٔ فعلی ترمینال، حرکت صفحه و ادامه از آخرین محل
- ذخیرهٔ محلیِ پیشرفت، پاسخ‌ها و mastery؛ پرونده‌های کتاب تغییر نمی‌کنند
- پرسش‌های `mcq`، چندانتخابی، درست/نادرست و پاسخ کوتاه
- انتخاب بدون تکرار در هر جلسه؛ پاسخ غلط اخیر در ابتدای مرور بعدی می‌آید
- این رفتار با CLI بررسی شده است: پاسخ غلط اخیر، نخستین پرسش جلسهٔ مرور بعدی است و هیچ شناسه‌ای در یک جلسه تکرار نمی‌شود
- وزن‌دهی به مفهوم‌های ضعیف، سطح فعلی و پیش‌نیازها، با انتخاب تصادفی وزن‌دار برای باقی جلسه
- فاصله‌گذاری پاسخ‌های درست: ۱، ۳، ۷، ۱۴ و ۳۰ روز؛ پاسخ غلط بلافاصله برای مرور واجد شرایط است
- نمایش راست‌چین فارسی با isolateهای Unicode برای عبارت‌های انگلیسی، کد inline و عددها؛ بلوک‌های Java چپ‌چین می‌مانند

اگر emulator ترمینال شما خودش متن دوزبانه را درست مدیریت می‌کند و isolateها ظاهر نامناسبی دارند، فقط برای همان اجرا حالت سازگاری را فعال کنید:

```bash
JAVABOOK_BIDI=off python3 reader.py read 1
```

`book/parts/*.md` قطعه‌های prose اولیهٔ فصل درجهٔ ۱ هستند و خواننده آن‌ها را نمی‌خواند؛ فصل منتشرشده از پیش در `book/01-building-blocks.md` گردآوری شده است. در مقابل، `book/quiz/.parts/*.json` ورودیِ `tools/validate_quiz.py --merge` است. گزینهٔ `--merge` بانک‌های نهایی را بازنویسی می‌کند؛ بنابراین فقط هنگام بازسازی آگاهانهٔ بانک‌ها از آن استفاده کنید.

`book/` یک فرمان CLI نیست؛ این دستور نامعتبر است:

```bash
./reader.py book/
```

برای خواندن، از فرمان زیر استفاده کنید:

```bash
python3 reader.py read 1
```

## نقشهٔ ۱۲ درجه

| درجه | موضوع |
|---|---|
| ۱ | runtime و building blocks: JVM، نوع‌ها، reference، lifecycle و resourceها |
| ۲ | operatorها و control flow |
| ۳ | Core API و methodها |
| ۴ | طراحی شیءگرا در Java |
| ۵ | interface، record، sealed type و polymorphism مدرن |
| ۶ | lambda، generic و collection |
| ۷ | stream، exception، I/O و reliability |
| ۸ | module، concurrency و virtual thread |
| ۹ | Spring Core container و dependency injection |
| ۱۰ | Spring Boot مدرن |
| ۱۱ | backend: MVC/REST، data، transaction و security |
| ۱۲ | production: Actuator، observability، deployment و integration |

فصل منتشرشدهٔ فعلی درجهٔ ۱، محیط اجرا، source structure، `main`، package/import، object/reference، primitive/wrapper، `String`، variable/scope، constructor/initialization، pass-by-value، GC و try-with-resources را پوشش می‌دهد. بانک‌های درجه‌های ۲ تا ۱۲ پرسش‌های seed برای مسیر بعدی دارند.
