# درجهٔ ۱ — آجرهای سازندهٔ Java 21

> **مسیر:** Java 21 / OCP Building Blocks  
> **مخاطب:** برنامه‌نویس C++ که می‌خواهد مدل ذهنی دقیق Java، JVM و مدیریت عمر داده/منبع را بسازد.

این فصل متن آموزشی مستقل است: از اصطلاحات استاندارد Java استفاده می‌کند، اما توضیح‌ها، مثال‌ها، دیاگرام‌ها و تمرین‌ها برای همین مسیر یادگیری نوشته شده‌اند. مقایسه با C++ برای کشف تفاوت قراردادهاست، نه برای یکی‌گرفتن دو مدل اجرایی.

## نقشهٔ یادگیری و خروجی مورد انتظار

پس از این درجه باید بتوانید:

1. مسیر `.java → .class → JVM` را از کامپایل native در C++ جدا کنید؛
2. فرق `package`، `import`، classpath و JAR را با header، linker، DLL و ABI توضیح دهید؛
3. مقدار primitive، reference، هویت، aliasing، `null` و mutation را روی کاغذ دنبال کنید؛
4. هشت primitive، wrapper، boxing/unboxing، `String` و `var` را بی‌دام به‌کار ببرید؛
5. ترتیب مقداردهی static/instance و constructor را پیش‌بینی کنید؛
6. pass-by-value را از «امکان mutation شیء مشترک» تفکیک کنید؛
7. GC را با بستن قطعی file/socket/connection اشتباه نگیرید.

### قرارداد خواندن این فصل

- **قاعدهٔ زبان:** نتیجه‌ای که Java specification برای برنامهٔ قابل مشاهده تعیین می‌کند.
- **جزئیات runtime:** رفتاری که ممکن است در HotSpot یا JVM دیگری رخ دهد؛ برای correctness هرگز به آن تکیه نکنید.
- **ترمیم:** هر جا یک برداشت رایج احتمال دارد مدل ذهنی را منحرف کند، برچسب مفهومِ مناسب برای مرور تطبیقی آمده است.

---

## بخش ۱: بلوک‌های سازندهٔ اجرا در Java 21

> **سطح:** Grade 1 — Java 21 / OCP Building Blocks  
> **مخاطب:** برنامه‌نویس توانمند C++ که به مدل کامپایل، لینک و runtime Java وارد می‌شود.

Java از نظر نحو به C++ نزدیک است، اما زنجیرهٔ ساخت و اجرای آن قرارداد متفاوتی دارد. در C++ معمولاً فایل‌های `.cpp` پس از بسط headerها به فایل‌های شیء مخصوص یک CPU/OS تبدیل می‌شوند و linker آن‌ها را با کتابخانه‌ها ترکیب می‌کند. در Java، `javac` معمولاً **bytecode** قابل‌حمل تولید می‌کند و JVM در زمان اجرا آن را بارگذاری، اعتبارسنجی، پیوند، مقداردهی و—در صورت لزوم—به کد ماشین بهینه تبدیل می‌کند.

```text
منبع Java                 ساخت                    زمان اجرا
─────────                 ────                    ─────────
Hello.java ── javac ──> Hello.class ─┐
                                     ├─ classpath / JAR ──> JVM
کلاس‌های وابسته ── javac ──> *.class ┘                      │
                                                            ▼
              loading → verification → linking → initialization
                                                            │
                                                            ▼
            interpreter → profile hot code → JIT machine code
                                         │
                                         └→ deoptimization، اگر فرضی باطل شود
```

## ۱. JDK، JRE و JVM

### JVM

**JVM** یا Java Virtual Machine ماشین انتزاعی اجرای classfileها و پیاده‌سازی‌های واقعی آن است. JVM پشتهٔ اجرای متدها، heap، نخ‌ها، garbage collection، بارگذاری کلاس، بررسی bytecode و معمولاً JIT را مدیریت می‌کند. HotSpot در OpenJDK نمونهٔ رایجی از پیاده‌سازی JVM است؛ OpenJ9 و GraalVM نیز می‌توانند runtimeهای متفاوتی عرضه کنند.

JVM یک CPU شبیه‌سازی‌شدهٔ ساده نیست. مشخصات JVM نوع‌های Java، فراخوانی متد، استثنا، دسترسی به فیلد و مدل classfile را تعریف می‌کند؛ پیاده‌سازی آن می‌تواند برای x86-64، ARM64 یا معماری دیگر، کد بومی مناسب تولید کند.

### JRE

**JRE** از نظر مفهومی محیط لازم برای اجرای برنامهٔ Java است: JVM به‌اضافهٔ کتابخانه‌های استاندارد runtime. در توزیع‌های مدرن OpenJDK معمولاً نصب جداگانه‌ای با نام JRE مانند گذشته نمی‌بینید؛ JDK کامل نصب می‌شود یا runtime سفارشی با `jlink` ساخته می‌شود. با این حال، این تمایز مفهومی مفید است: اجرای برنامه به کامپایلر نیاز ندارد.

### JDK

**JDK** یا Java Development Kit شامل runtime و ابزار توسعه است: `java`، `javac`، `jar`، `javap`، `jshell`، `javadoc`، `jlink` و ابزارهای تشخیصی دیگر.

```text
JDK
├── ابزار توسعه: javac, jar, javap, jshell, ...
└── runtime (مدل مفهومی JRE)
    ├── کتابخانه‌ها و ماژول‌های استاندارد
    └── JVM
        ├── class loaderها
        ├── interpreter و JIT
        ├── garbage collector
        └── scheduler و مدیریت نخ
```

### مثال ۱: کنترل نسخه و مسیر ابزارها

```bash
java --version
javac --version
which java
which javac
```

نمونهٔ خروجی قابل انتظار:

```text
openjdk 21.0.x ... LTS
OpenJDK Runtime Environment ...
OpenJDK 64-Bit Server VM ...
javac 21.0.x
```

ممکن است `java` و `javac` از دو نصب متفاوت بیایند. با وجود چند JDK، IDE، SDK manager و متغیر `PATH`، این یک علت شایع تفاوت میان build محلی و CI است. نسخهٔ JDK را در ابزار build و محیط CI صریح تعیین کنید.

### مثال ۲: runtime بدون compiler

```bash
javac Hello.java
```

اگر `java --version` کار کند اما shell بگوید `javac: command not found`، runtime در دسترس است ولی JDK یا مسیر آن کامل نیست. این خطا هنوز خطای زبان Java نیست؛ ابزار توسعه غایب است.

## ۲. `javac` و classfile

فایل زیر را در `Hello.java` قرار دهید:

### مثال ۳: کوچک‌ترین برنامه

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("سلام از Java 21");
    }
}
```

```bash
javac Hello.java
java Hello
```

`javac` فایلی به نام `Hello.class` می‌سازد. هنگام اجرای launcher، پسوند `.class` نمی‌نویسید: `java` نام کلاس را می‌گیرد، سپس JVM با classpath آن را پیدا می‌کند.

```text
Hello.java -- javac --> Hello.class -- java Hello --> خروجی
```

مقایسهٔ نزدیک با C++:

```bash
# C++
c++ -std=c++23 hello.cpp -o hello
./hello

# Java
javac Hello.java
java -cp . Hello
```

اما `Hello.class` معادل مستقیم executable یا حتی `.o` نیست. classfile دستورهای ماشین JVM و فراداده‌ای مثل نام superclass، امضای متدها، constant pool، اطلاعات استثنا و annotationها دارد. هنوز برای CPU مشخصی ساخته نشده است.

### مثال ۴: دیدن bytecode

```bash
javac Hello.java
javap -c -verbose Hello
```

در خروجی دستورهایی مانند `getstatic`، `ldc`، `invokevirtual` و `return` خواهید دید. این‌ها دستورهای x86 یا ARM نیستند؛ JVM آن‌ها را تفسیر یا به کد ماشین تبدیل می‌کند.

### مثال ۵: تعیین نسخهٔ هدف

```bash
javac --release 21 Hello.java
```

`--release` هم سطح زبان/API هدف و هم نسخهٔ classfile را هماهنگ می‌کند. برای ساخت Java 21، این گزینه جلوی استفادهٔ ناخواسته از API نسخه‌های دیگر را می‌گیرد.

اگر classfile جدید را روی JVM قدیمی اجرا کنید، خطایی مانند این می‌بینید:

```text
java.lang.UnsupportedClassVersionError:
... class file version 65.0, this version of the Java Runtime
only recognizes up to 61.0
```

Java 21 classfile version 65 و Java 17 version 61 دارد. راه‌حل اجرای JVM جدیدتر است، یا کامپایل با release قدیمی‌تر، به شرطی که syntax و APIهای استفاده‌شده واقعاً سازگار باشند.

## ۳. ساختار فایل منبع

ساختار متعارف compilation unit چنین است:

```text
[package declaration]
[import declarations]
[type declarations]
```

`package`، اگر وجود دارد، باید نخست باشد؛ بعد از آن importها می‌آیند؛ سپس class، interface، enum، record یا annotation تعریف می‌شود. Java header جداگانه و `#include` متنی ندارد.

### مثال ۶: نام فایل و public type

فایل `Printer.java`:

```java
public class Printer {
    public static void print(String message) {
        System.out.println(message);
    }
}
```

یک نوع سطح بالای `public` باید در فایلی باشد که نامش دقیقاً با نام نوع و پسوند `.java` برابر است. قرار دادن همین تعریف در `Tool.java` خطا می‌دهد:

```text
class Printer is public, should be declared in a file named Printer.java
```

### مثال ۷: چند نوع غیرpublic در یک فایل

فایل `Shapes.java`:

```java
class Circle {
    double radius;
}

class Square {
    double side;
}

public class Shapes {
    public static void main(String[] args) {
        Circle circle = new Circle();
        circle.radius = 2.0;
        System.out.println(circle.radius);
    }
}
```

این قانونی است: تنها type عمومی `Shapes` است و نام فایل با آن یکی است. در پروژهٔ واقعی، هر top-level type مهم معمولاً فایل خودش را دارد تا پیمایش و تغییرات آسان‌تر باشند.

### مقایسه با C++

در C++، header اغلب اعلان و `.cpp` تعریف را نگه می‌دارد؛ preprocessor محتوای header را به شکل متن وارد می‌کند و ODR یا include cycle مسئله می‌شود. در Java، compiler definitionها را از source و classpath می‌شناسد. import کد را وارد یا کپی نمی‌کند؛ تنها نام کوتاه را قابل استفاده می‌سازد.

## ۴. package و import

package بخشی از نام کامل یک type است و مرز دسترسی package-private نیز می‌سازد.

### مثال ۸: تعریف packageدار

فایل `src/com/example/math/Adder.java`:

```java
package com.example.math;

public class Adder {
    public static int add(int left, int right) {
        return left + right;
    }
}
```

نام کامل کلاس `com.example.math.Adder` است. کامپایل از ریشهٔ source:

```bash
mkdir -p out
javac -d out src/com/example/math/Adder.java
```

```text
out/
└── com/
    └── example/
        └── math/
            └── Adder.class
```

گزینهٔ `-d out` مسیر خروجی متناسب با نام package را می‌سازد.

### مثال ۹: import و اجرای کلاس packageدار

فایل `src/com/example/app/App.java`:

```java
package com.example.app;

import com.example.math.Adder;

public class App {
    public static void main(String[] args) {
        System.out.println(Adder.add(20, 22));
    }
}
```

```bash
javac -d out src/com/example/math/Adder.java src/com/example/app/App.java
java -cp out com.example.app.App
```

### مثال ۱۰: نام کامل بدون import

```java
package com.example.app;

public class FullyQualifiedApp {
    public static void main(String[] args) {
        System.out.println(com.example.math.Adder.add(7, 8));
    }
}
```

وابستگی همان است؛ فقط syntax متفاوت است.

`import com.example.math.Adder;`:

- فایل `Adder.java` را داخل فایل جاری کپی نمی‌کند؛
- در runtime کلاس را load نمی‌کند؛
- کنترل دسترسی را دور نمی‌زند؛
- مانند `#include` نیست.

Wildcard import هم فقط typeهای مستقیم همان package را در بر می‌گیرد:

```java
import java.util.*; // java.util.concurrent را وارد نمی‌کند
```

**برداشت نادرست:** «package همان پوشه است.» پوشه قرارداد نگاشت و سازمان‌دهی است؛ package یک نام‌فضای زبان و بخشی از هویت دودویی type است.

## ۵. `main` و `static`

نقطهٔ ورود متعارف launcher Java این قرارداد است:

```java
public static void main(String[] args)
```

### مثال ۱۱: entry point

```java
public class EntryPoint {
    public static void main(String[] args) {
        System.out.println("argument count = " + args.length);
    }
}
```

```bash
javac EntryPoint.java
java EntryPoint alpha beta
```

خروجی:

```text
argument count = 2
```

در C++، `main` تابع آزاد است. Java تابع آزاد ندارد؛ `main` عضو class است. `static` یعنی برای فراخوانی آن به instance از class نیاز ندارید. اگر main instance method بود، JVM باید پیش از شروع برنامه تصمیم می‌گرفت کدام constructor را با چه اثر جانبی اجرا کند.

### مثال ۱۲: main غیرstatic

```java
public class BrokenEntryPoint {
    public void main(String[] args) {
        System.out.println("launcher این را نقطهٔ ورود نمی‌داند");
    }
}
```

```bash
javac BrokenEntryPoint.java
java BrokenEntryPoint
```

خطایی مشابه خواهید داشت:

```text
Error: Main method not found in class BrokenEntryPoint
```

### مثال ۱۳: state کلاسی در برابر state شیء

```java
public class Ticket {
    static int issued = 0; // یک مقدار مشترک برای class
    final int serial;      // یک مقدار برای هر object

    Ticket() {
        serial = ++issued;
    }

    public static void main(String[] args) {
        Ticket first = new Ticket();
        Ticket second = new Ticket();
        System.out.println(first.serial + ", " + second.serial);
        System.out.println("issued = " + Ticket.issued);
    }
}
```

خروجی:

```text
1, 2
issued = 2
```

در C++، static data member تشبیه نزدیکی است. اما initialization class در Java بخشی از lifecycle JVM است و ممکن است در نخستین استفادهٔ فعال رخ دهد، نه الزاماً در لحظهٔ بارگذاری process توسط OS.

### مثال ۱۴: static context

```java
public class Counter {
    private int value = 10;

    static void printValue() {
        // System.out.println(value); // خطای کامپایل
    }
}
```

متد static object مشخصی ندارد و نمی‌تواند مستقیم field نمونه را بخواند. راه درست یا دریافت instance است:

```java
static void printValue(Counter counter) {
    System.out.println(counter.value);
}
```

یا تغییر طراحی به state واقعاً مشترک. تبدیل بی‌فکر field به static فقط برای حذف خطا معمولاً bug طراحی می‌سازد.

## ۶. classpath و پیدا کردن کلاس‌ها

classpath فهرستی مرتب از مکان‌هایی است که class loader برای یافتن classfile و resource بررسی می‌کند. هر entry می‌تواند یک directory یا یک JAR باشد.

```text
-cp out:lib/util.jar
    │    │
    │    └── JAR حاوی class و resource
    └────── ریشهٔ ساختار package برای کلاس‌های ساخته‌شده
```

در Linux و macOS جداکنندهٔ entryها معمولاً `:` و در Windows `;` است. classpath را با source path اشتباه نگیرید: classpath معمولاً محل classهای کامپایل‌شده و dependencyها در زمان اجرا/کامپایل است.

### مثال ۱۵: نام کلاس، نه مسیر فایل

با این ساختار:

```text
out/com/example/app/App.class
```

دستور درست چنین است:

```bash
java -cp out com.example.app.App
```

و این الگو نادرست است:

```bash
java -cp out com/example/app/App
```

launcher یک **نام کامل کلاس** می‌خواهد؛ JVM سپس آن را به مسیر نسبی `com/example/app/App.class` در هر classpath entry نگاشت می‌کند.

### مثال ۱۶: classpath شامل JAR

```bash
javac -cp lib/helpers.jar -d out src/com/example/app/App.java
java -cp out:lib/helpers.jar com.example.app.App
```

در Windows:

```bat
java -cp out;lib\helpers.jar com.example.app.App
```

نکتهٔ مهم برای برنامه‌نویس C++: `-I` در compiler C++ مسیر جست‌وجوی headerهاست و `-L`/`-l` به linker مربوط است. `-cp` Java در عمل به هر دو مرحله اثر می‌گذارد، ولی semantic آن «مکان تعریف classها» است، نه متن header و نه صرفاً نام کتابخانهٔ بومی.

### خطاهای متداول runtime

| نشانه | معنای محتمل | نخستین بررسی |
|---|---|---|
| `Could not find or load main class` | نام کامل main class یا classpath غلط است | `-cp` و package declaration |
| `ClassNotFoundException` | کد صریحاً یک کلاس را خواسته ولی loader آن را نیافته | JAR/دایرکتوری dependency |
| `NoClassDefFoundError` | dependency لازم هنگام استفادهٔ واقعی موجود نیست یا initialization قبلی شکست خورده | classpath runtime و علت زنجیره‌ای |
| `UnsupportedClassVersionError` | JVM قدیمی‌تر از classfile است | `java --version` و `javac --release` |

### مثال ۱۷: `ClassNotFoundException` در بارگذاری پویا

```java
public class DynamicLoad {
    public static void main(String[] args) throws ClassNotFoundException {
        Class.forName("com.example.plugin.MissingPlugin");
    }
}
```

اگر class مورد نظر در classpath نباشد، `Class.forName` معمولاً این خطا را می‌اندازد:

```text
java.lang.ClassNotFoundException: com.example.plugin.MissingPlugin
```

این با `NoClassDefFoundError` یکی نیست. اولی اغلب نتیجهٔ درخواست صریح برای نامی است که پیدا نشد. دومی معمولاً وقتی رخ می‌دهد که JVM در مسیر اجرای کدِ قبلاً کامپایل‌شده به definition مورد نیاز نرسد.

### مثال ۱۸: dependency حاضر در compile و غایب در runtime

```java
public class Client {
    static LibraryType value = new LibraryType();

    public static void main(String[] args) {
        System.out.println(value);
    }
}
```

اگر `Client` با `LibraryType` کامپایل شده باشد ولی `LibraryType.class` یا JAR آن در runtime نباشد، احتمالاً خطایی مانند زیر می‌بینید:

```text
java.lang.NoClassDefFoundError: LibraryType
```

در یک محیط build حرفه‌ای، Maven یا Gradle وابستگی‌های compile و runtime را مدل می‌کند؛ اما فهمیدن classpath همچنان ضروری است، چون خطا اغلب در container، test runner، IDE یا script deployment ظاهر می‌شود.

### ترتیب classpath و shadowing

اگر دو entry همان نام کامل کلاس را ارائه کنند، ترتیب جست‌وجو اهمیت دارد:

```text
lib/old-api.jar → com.example.Api نسخهٔ قدیمی
lib/new-api.jar → com.example.Api نسخهٔ جدید

-cp lib/old-api.jar:lib/new-api.jar
     ^ نخستین تعریف قابل‌مشاهده غالباً انتخاب می‌شود
```

این وضع می‌تواند `NoSuchMethodError` بسازد: caller با API جدید کامپایل شده، اما در runtime نسخهٔ قدیمی کلاس load شده است. آن را با خطای کامپایل اشتباه نگیرید؛ امضای متد هنگام build وجود داشته، اما definition loadشده در runtime آن را ندارد.

## ۷. JAR و تفاوت آن با `.o`، `.dll` و ABI

JAR مخفف Java ARchive است و در عمل یک archive مبتنی بر ZIP است. محتویاتش می‌تواند classfile، resource، manifest و metadata باشد.

### مثال ۱۹: ساخت JAR اجرایی

فرض کنید `out/com/example/app/App.class` و وابستگی‌های داخلی آن ساخته شده‌اند:

```bash
jar --create --file app.jar --main-class com.example.app.App -C out .
jar --list --file app.jar
java -jar app.jar
```

محتوا ممکن است چنین باشد:

```text
META-INF/
META-INF/MANIFEST.MF
com/example/app/App.class
com/example/math/Adder.class
```

گزینهٔ `--main-class` مقدار manifest را ثبت می‌کند:

```text
Main-Class: com.example.app.App
```

JAR ذاتاً executable بومی نیست. `java -jar` JVM را اجرا می‌کند، manifest را می‌خواند و کلاس main را از archive پیدا می‌کند.

| موضوع | Java | C++ رایج |
|---|---|---|
| artifact میانی | `.class`، bytecode و metadata | `.o`/`.obj`، کد مخصوص target |
| archive | JAR، معمولاً ZIP | `.a`/`.lib`، archive objectها |
| shared library | اغلب JAR در سطح Java API | `.so`/`.dll` با کد بومی |
| اتصال | class loading و symbolic reference | linker/loader و symbol resolution |
| توافق binary | classfile و JVM specification | ABI، calling convention، symbol mangling |
| وابستگی CPU | معمولاً ندارد | معمولاً دارد |

در C++، تغییر layout یک class یا compiler flags می‌تواند ABI را بشکند، حتی اگر header ظاهراً نزدیک باشد. Java هم compatibility binary دارد، اما تماس معمول میان کلاس‌ها با JVM symbolic referenceها انجام می‌شود، نه با offsetهای vtable یا calling convention مخصوص CPU. حذف یا تغییر امضای public method همچنان می‌تواند consumer کامپایل‌شده را در runtime بشکند.

**برداشت نادرست:** «هر JAR یک برنامهٔ مستقل است.» خیر. JAR می‌تواند فقط یک library باشد، ممکن است main class نداشته باشد، و dependencyهای آن هم لزوماً درون archive نیستند. اصطلاح fat/uber JAR برای archiveای به‌کار می‌رود که dependencyهای بیشتری را هم در خود بسته‌بندی کرده است.

## ۸. چرخهٔ عمر class: loading، verification، linking، initialization

برای تشخیص رفتار static و خطاهای runtime، چهار مرحله را جدا نگه دارید:

```text
درخواست استفاده از نوع T
        │
        ▼
Loading
  خواندن bytes تعریف T و ساخت نمایش runtime آن
        │
        ▼
Linking
  ├── Verification: بررسی سازگاری bytecode با قواعد JVM
  ├── Preparation: تخصیص static fieldها با مقدار پیش‌فرض
  └── Resolution: اتصال referenceهای نمادین در زمان لازم
        │
        ▼
Initialization
  اجرای field initializerهای static و static blockها، به ترتیب متن
        │
        ▼
استفادهٔ فعال از class
```

### loading

class loader بایت‌های class را از directory، JAR یا منبع دیگری می‌گیرد. در برنامهٔ عادی، loaderهای bootstrap، platform و application در زنجیره حضور دارند؛ frameworkهای plugin-oriented، application serverها یا test runnerها ممکن است loaderهای بیشتری بسازند.

```text
Bootstrap loader   → APIهای بنیادین پلتفرم
Platform loader    → APIهای platform
Application loader → classpath برنامه
Custom loader      → plugin یا container خاص
```

یک نتیجهٔ پیشرفته اما مهم: هویت عملی یک class فقط نام `com.example.Plugin` نیست؛ loader تعریف‌کننده نیز مهم است. دو class loader مستقل می‌توانند همین نام کامل را بارگذاری کنند و این دو type برای assignment یا cast لزوماً سازگار نیستند. این موضوع ریشهٔ بعضی `ClassCastException`های ظاهراً نامعقول در plugin systemهاست.

### verification

Verifier bytecode نامعتبر را پیش از اجرا رد می‌کند: استفادهٔ ناسازگار از نوع‌ها، پشتهٔ operand با شکل نادرست، یا پرش غیرقانونی نمونه‌هایی از این محدودیت‌ها هستند. این بخش، همراه type system و access control، بخشی از مدل ایمنی Java است.

این تضمین به معنای نبودن bug یا آسیب‌پذیری نیست؛ null dereference، logic bug، race condition و input validation نادرست همچنان ممکن‌اند. تفاوت با C++ این است که دستکاری دلخواه پشته و calling convention نامعتبر در مسیر عادی Java به undefined behavior بومی تبدیل نمی‌شود؛ JVM bytecode را در مرز runtime کنترل می‌کند.

### preparation و مقدارهای پیش‌فرض

در preparation، static fieldها پیش از initializerهای صریح، مقدار پیش‌فرض نوع خود را می‌گیرند:

| نوع field | مقدار پیش‌فرض |
|---|---|
| `boolean` | `false` |
| `byte`، `short`، `int`، `long`، `char` | صفر مناسب نوع |
| `float`، `double` | `0.0` |
| reference | `null` |

local variableها چنین امتیازی ندارند و باید پیش از خواندن definite assignment داشته باشند.

### مثال ۲۰: ترتیب initializerهای static

```java
public class StaticOrder {
    static int first = report("first", 1);
    static int second = report("second", first + 1);

    static {
        System.out.println("static block: second = " + second);
    }

    static int report(String name, int value) {
        System.out.println(name + " = " + value);
        return value;
    }

    public static void main(String[] args) {
        System.out.println("main: " + second);
    }
}
```

خروجی:

```text
first = 1
second = 2
static block: second = 2
main: 2
```

static field initializerها و static blockها از بالا به پایین و مطابق متن اجرا می‌شوند. این با ترتیب declaration در یک translation unit C++ شباهت دارد، اما trigger lifecycle و محیط JVM متفاوت است.

### initialization و استفادهٔ فعال

کارهایی مانند ساخت instance، فراخوانی static method غیرثابت، و خواندن static field غیرconstant معمولاً initialization class را trigger می‌کنند.

### مثال ۲۱: initialization در نخستین استفادهٔ فعال

```java
class ExpensiveConfig {
    static {
        System.out.println("ExpensiveConfig initialized");
    }

    static String load() {
        return "ready";
    }
}

public class LazyDemo {
    public static void main(String[] args) {
        System.out.println("main started");
        System.out.println(ExpensiveConfig.load());
    }
}
```

خروجی معمول:

```text
main started
ExpensiveConfig initialized
ready
```

مقداردهی static را مکان مناسبی برای I/O، اتصال شبکه یا منطق configuration شکننده فرض نکنید. اثر جانبی static initializer در نخستین استفادهٔ فعال رخ می‌دهد و می‌تواند زمان startup یا مسیر خطا را غیرشفاف کند.

### مثال ۲۲: شکست initialization

```java
class FailingConfig {
    static {
        if (true) {
            throw new IllegalStateException("configuration is invalid");
        }
    }

    static void use() {
        System.out.println("unreachable");
    }
}

public class InitFailure {
    public static void main(String[] args) {
        FailingConfig.use();
    }
}
```

نخستین استفاده معمولاً `ExceptionInInitializerError` می‌دهد که exception اصلی را به‌عنوان cause نگه می‌دارد. استفادهٔ بعدی ممکن است به `NoClassDefFoundError: Could not initialize class ...` برسد. همیشه stack trace نخستین خطا را بیابید؛ خطای بعدی اغلب فقط پیامد آن است.

### مثال ۲۳: compile-time constant و trigger نشدن initialization

```java
class Constants {
    static final int ANSWER = 42;

    static {
        System.out.println("Constants initialized");
    }
}

public class ConstantUse {
    public static void main(String[] args) {
        System.out.println(Constants.ANSWER);
    }
}
```

ممکن است خروجی فقط این باشد:

```text
42
```

`ANSWER` یک compile-time constant است و compiler می‌تواند مقدار را در caller inline کند؛ بنابراین خواندنش لزوماً initialization کلاس صاحب constant را trigger نمی‌کند.

### مثال ۲۴: مقدار static final اما runtime-computed

```java
class RuntimeConstants {
    static final long PID_HINT = ProcessHandle.current().pid();

    static {
        System.out.println("RuntimeConstants initialized");
    }
}

public class RuntimeConstantUse {
    public static void main(String[] args) {
        System.out.println(RuntimeConstants.PID_HINT);
    }
}
```

این مقدار compile-time constant نیست؛ برای محاسبه‌اش initialization لازم است.

**برداشت نادرست:** «`final` یعنی همیشه ثابت کامپایل‌زمان.» `final` یعنی reference یا variable پس از assignment دوباره assign نمی‌شود. اینکه مقدار یک constant expression باشد، پرسش جداگانه‌ای است.

## ۹. JIT، warmup و deoptimization

JVM در آغاز اجرای برنامه ممکن است bytecode را با interpreter اجرا کند. هم‌زمان شمارنده‌ها و profileهایی جمع می‌کند: کدام methodها داغ‌اند، کدام branch بیشتر گرفته می‌شود، گیرندهٔ واقعی یک call virtual چیست، و چه نوع‌هایی در محل allocation دیده شده‌اند. سپس JIT می‌تواند بخش‌های داغ را به کد ماشین بهینه تبدیل کند.

```text
شروع برنامه
   │
   ▼
Interpreter
   │  profile: call count, branch bias, receiver types, allocation behavior
   ▼
Tiered compilation
   │
   ├── compilation سریع‌تر با بهینه‌سازی کمتر
   └── compilation پرهزینه‌تر برای hot pathهای پایدار
             │
             ▼
         machine code بهینه
             │
             └── اگر فرض profile نقض شد → deoptimization → بازگشت/کامپایل مجدد
```

### مثال ۲۵: حلقه برای نشان دادن warmup

```java
public class WarmupDemo {
    static long sumSquares(int limit) {
        long sum = 0;
        for (int i = 0; i < limit; i++) {
            sum += (long) i * i;
        }
        return sum;
    }

    public static void main(String[] args) {
        for (int round = 0; round < 10; round++) {
            long start = System.nanoTime();
            long result = sumSquares(20_000_000);
            long elapsed = System.nanoTime() - start;
            System.out.printf("round=%d result=%d time=%.3f ms%n",
                    round, result, elapsed / 1_000_000.0);
        }
    }
}
```

در بسیاری از JVMها، roundهای ابتدایی با roundهای بعدی یکسان نیستند. اما این benchmark علمی نیست: dead-code elimination، فرکانس CPU، garbage collection، compilation هم‌زمان و بار سیستم نتیجه را تغییر می‌دهند. برای سنجش واقعی از JMH استفاده کنید، چند fork و warmup داشته باشید، و فقط یک عدد startup را «سرعت Java» ننامید.

### deoptimization چیست؟

JIT ممکن است بر پایهٔ profile فرض کند یک call virtual تقریباً همیشه به یک implementation خاص می‌رود؛ سپس آن را inline کند. اگر بعداً implementation دیگری در همان محل ظاهر شود، فرض نقض می‌شود. JVM می‌تواند execution را به وضعیت امن‌تر برگرداند، اطلاعات لازم را بازسازی کند و کدی عمومی‌تر را کامپایل کند. این **deoptimization** نقص نیست؛ بخش طبیعی بهینه‌سازی مبتنی بر حدس‌های profile است.

### مثال ۲۶: call site با رفتار تک‌ریخت و سپس چندریخت

```java
interface Operation {
    int apply(int value);
}

class Increment implements Operation {
    public int apply(int value) { return value + 1; }
}

class DoubleIt implements Operation {
    public int apply(int value) { return value * 2; }
}

public class DispatchProfile {
    static int run(Operation operation, int n) {
        int result = 0;
        for (int i = 0; i < n; i++) {
            result += operation.apply(i);
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println(run(new Increment(), 5_000_000));
        System.out.println(run(new DoubleIt(), 5_000_000));
    }
}
```

این مثال تضمین نمی‌کند چه optimizationی رخ دهد؛ به JVM، flags و profile بستگی دارد. هدف فقط مدل ذهنی است: dispatch پویا لزوماً هزینهٔ ثابتی ندارد؛ JIT ممکن است آن را devirtualize یا inline کند، اما نباید correctness برنامه به چنین optimizationی متکی باشد.

### caveatهای عملی JIT

1. **Startup با throughput یکی نیست.** CLI کوتاه شاید پیش از گرم‌شدن تمام شود؛ server طولانی‌مدت از JIT بیشتر بهره می‌برد.
2. **هر microbenchmark دروغ‌گوست تا وقتی روش آن را ثابت نکنید.** حذف نتیجهٔ محاسبه، constant folding و escape analysis می‌توانند کدی را که گمان می‌کنید می‌سنجید تغییر دهند.
3. **نتیجه روی یک JVM/CPU نسخهٔ جهان‌شمول نیست.** حتی minor update JDK می‌تواند profile و optimizer را تغییر دهد.
4. **allocation همیشه معادل هزینهٔ heap نیست.** escape analysis گاهی objectهای کوتاه‌عمر را حذف یا scalar-replace می‌کند؛ این تضمین زبان نیست.
5. **`System.nanoTime()` ابزار benchmark کامل نیست.** برای timing کوتاه، نوسان و compilation هم‌زمان دارد.

برای مشاهدهٔ تشخیصی، نه برای تنظیم production بدون شناخت، می‌توانید از این گزینه‌ها استفاده کنید:

```bash
java -XX:+PrintCompilation WarmupDemo
java -Xlog:class+load=info -cp out com.example.app.App
```

نام و در دسترس‌بودن بعضی diagnostic flagها با vendor و نسخه فرق دارد. همیشه `java -XX:+PrintFlagsFinal -version` و مستندات JVM مورد استفاده را معیار قرار دهید.

## ۱۰. دیاگرام کامل در برابر زنجیرهٔ C++

```text
C++
───
source.cpp + headers
       │ preprocessor
       ▼
translation unit
       │ compiler
       ▼
object.o (CPU/OS/ABI-specific)
       │ linker + libraries
       ▼
executable / shared library
       │ OS loader
       ▼
machine instructions

Java
────
source.java + API declarations
       │ javac
       ▼
classfile (.class: JVM bytecode + metadata)
       │ jar (اختیاری: archive)
       ▼
classpath / module path
       │ class loader + verifier + linker
       ▼
JVM execution
       ├── interpreter در آغاز یا مسیر سرد
       ├── profiling
       ├── JIT compilation برای مسیر داغ
       └── GC و runtime services
       ▼
machine instructions برای CPU فعلی
```

این مقایسه به معنای «C++ همیشه AOT و Java همیشه JIT» نیست. C++ می‌تواند JIT داشته باشد و Java می‌تواند ahead-of-time یا native image داشته باشد. موضوع این بخش، مدل رایج Java SE با `javac` و JVM است.

## ۱۱. یادداشت‌های رفع سوءبرداشت

- **«Java یک بار کامپایل می‌شود و همه‌جا بدون قید اجرا می‌شود.»** bytecode قابل‌حمل است، اما نسخهٔ JVM، OS integration، native dependency، encoding، timezone، file system و policy deployment همچنان مهم‌اند.
- **«import باعث load شدن کلاس است.»** import فقط نام را در source کوتاه می‌کند.
- **«JAR همان DLL است.»** هر دو artifact توزیع‌اند، اما JAR معمولاً bytecode/resource دارد و DLL معمولاً کد بومی با ABI سیستم‌عامل.
- **«هر static field هنگام startup برنامه مقداردهی می‌شود.»** initialization class اغلب تنبل و وابسته به استفادهٔ فعال است.
- **«static یعنی global.»** static member به class تعلق دارد، نام‌فضا و lifecycle JVM دارد، و با global variable آزاد C++ یکسان نیست.
- **«JIT همیشه برنامه را سریع‌تر می‌کند.»** JIT هزینهٔ warmup دارد و نتیجه به الگوی واقعی اجرا بستگی دارد.
- **«اگر کامپایل شد، runtime هم درست است.»** dependency version، classpath، initialization و محیط runtime می‌توانند شکست‌های دیرهنگام بسازند.

## ۱۲. تمرین‌ها

۱. `Hello` را با `javap -c -verbose` بررسی کنید. نام superclass و دستورهای `main` را در خروجی بیابید.
2. دو کلاس `com.training.model.Book` و `com.training.app.Catalog` بسازید. آن‌ها را با `javac -d out` کامپایل و با نام کامل `Catalog` اجرا کنید.
3. عمداً `-cp out` را حذف کنید و پیام خطا را ثبت کنید. سپس package declaration را از نام اجرا حذف کنید و تفاوت خطا را توضیح دهید.
4. یک JAR اجرایی از تمرین ۲ بسازید. manifest را با استخراج archive یا `jar --list` بررسی کنید.
5. کلاسی با سه static field و دو static block طراحی کنید که ترتیب اجرای دقیق خود را چاپ کند. پیش از اجرا خروجی را پیش‌بینی کنید.
6. یک `static final int` literal و یک `static final int` حاصل `Integer.parseInt("42")` بسازید. برای هر کدام اثر initializer را آزمایش کنید.
7. `WarmupDemo` را اجرا کنید؛ زمان ۱۰ دور را ثبت کنید. سپس توضیح دهید چرا این داده به‌تنهایی benchmark قابل انتشار نیست.
8. یک interface با دو implementation بسازید و همان call site را ابتدا با یک implementation، سپس با هر دو فراخوانی کنید. توضیح دهید JIT چه فرضی *ممکن است* دربارهٔ receiver type داشته باشد.
9. یک JAR قدیمی و جدید فرضی با نام کامل کلاس یکسان بسازید یا شبیه‌سازی کنید. ترتیب classpath را عوض کنید و دلیل shadowing را بنویسید.
10. سناریویی بنویسید که static initializer exception می‌اندازد. زنجیرهٔ exception نخست و خطای استفادهٔ دوم را مقایسه کنید.

## ۱۳. واژه‌نامه

| اصطلاح | تعریف کوتاه |
|---|---|
| **JDK** | کیت توسعه شامل ابزارهایی مانند `javac` و runtime Java |
| **JRE** | نام مفهومی محیط لازم برای اجرای Java: JVM و کتابخانه‌های runtime |
| **JVM** | ماشین مجازی مسئول اجرای classfile و سرویس‌های runtime |
| **bytecode** | دستورهای قابل اجرای JVM، مستقل از ISA پردازنده |
| **classfile** | فایل `.class` شامل bytecode و metadata یک type |
| **classpath** | فهرست مکان‌های جست‌وجوی class/resource توسط loader |
| **JAR** | archive مبتنی بر ZIP برای classfile، resource و manifest |
| **class loader** | مؤلفهٔ مسئول یافتن و تعریف کلاس‌ها در JVM |
| **verification** | بررسی صحت structural/type bytecode پیش از اجرای آن |
| **linking** | مجموعهٔ verification، preparation و resolution برای class |
| **initialization** | اجرای initializerهای static و static blockها |
| **JIT** | کامپایل در زمان اجرا، معمولاً برای کدهای داغ |
| **warmup** | مرحلهٔ اولیهٔ گردآوری profile و کامپایل تدریجی |
| **deoptimization** | بازگشت از کد بهینه وقتی فرض optimizer دیگر درست نیست |
| **ABI** | قرارداد دودویی مانند calling convention و layout که کد بومی برای اتصال نیاز دارد |
| **symbolic reference** | اشارهٔ classfile به type/member با نام و descriptor، پیش از resolve شدن |

## جمع‌بندی

در Java 21، فایل `.java` به یک executable بومی مستقیم تبدیل نمی‌شود. `javac` classfileهای قابل‌انتقال می‌سازد؛ JVM آن‌ها را از classpath یا JAR پیدا می‌کند، bytecode را بررسی و link می‌کند، initialization ایستا را در زمان لازم انجام می‌دهد، و با profile runtime می‌تواند کدهای داغ را JIT کند. برای برنامه‌نویس C++، کلید سازگاری ذهنی این است که `import` را header، JAR را DLL، و classfile را `.o` فرض نکند: شباهت‌هایی دارند، اما مرزهای binding، portability و lifecycle بنیادی متفاوت‌اند.

---

## درجهٔ ۱: داده‌ها، هویت و متن در Java 21

این بخش برای برنامه‌نویسی باتجربهٔ C++ نوشته شده است. در C++ معمولاً میان value، pointer، reference، object lifetime و copy constructor مرزهای نحوی روشنی دارید. در Java نیز این مفاهیم مهم‌اند، اما مدل زبان متفاوت است: متغیرها یا **primitive value** نگه می‌دارند یا **reference value**؛ و assignment و ارسال آرگومان همیشه «by value» است.

```text
primitive                         reference
─────────                         ─────────
int count = 7;                    Book book = new Book("Java");
       │                                  │
       ▼                                  ▼
       7                         ┌───────────────────┐
                                 │ Book object       │
                                 │ title = "Java"    │
                                 └───────────────────┘
```

این دیاگرام جای فیزیکی object را تضمین نمی‌کند. JVM اجازه دارد با escape analysis، garbage collection و بهینه‌سازی‌های دیگر نحوهٔ قرارگیری داده را تغییر دهد. قرارداد زبان دربارهٔ **هویت object**، referenceها و نتیجهٔ عملیات است، نه آدرس حافظهٔ قابل‌مشاهده.

---

## ۱. مدل value و reference

Java دقیقاً هشت نوع primitive دارد. هر نوع دیگر—کلاس، interface، array، enum و record—نوع reference است. یک reference می‌تواند به object اشاره کند یا `null` باشد.

### مثال ۱ — کپی primitive، کپی مقدار است

```java
int left = 10;
int right = left;
right++;

System.out.println(left);   // 10
System.out.println(right);  // 11
```

مانند کپی `int` در C++، دو محل مستقل داریم.

### مثال ۲ — کپی reference، کپی object نیست

```java
class Counter {
    int value;
}

Counter first = new Counter();
first.value = 10;
Counter second = first;
second.value++;

System.out.println(first.value);  // 11
System.out.println(second.value); // 11
```

```text
first  ──┐
         ├──► Counter { value: 11 }
second ──┘
```

این به کپی raw pointer در C++ نزدیک‌تر از copy constructor است؛ اما Java pointer arithmetic، `*` برای dereference و ownership دستی ندارد.

### مثال ۳ — Java «pass by reference» نیست

```java
class Box {
    int number;
}

static void change(Box box) {
    box.number = 99;      // object مشترک تغییر می‌کند
    box = new Box();      // فقط کپی محلی reference عوض می‌شود
    box.number = 5;
}

Box original = new Box();
original.number = 1;
change(original);
System.out.println(original.number); // 99
```

در ورود به متد، خودِ reference به‌صورت value کپی می‌شود:

```text
original ──► Box { number: 1 }
                 ▲
box ─────────────┘

پس از box = new Box():
original ──► Box { number: 99 }
box      ──► Box { number: 5 }
```

پس عبارت دقیق این است: **Java referenceها را by value پاس می‌دهد.** متد می‌تواند object مشترک را mutate کند، اما نمی‌تواند reference متغیر caller را با assignment خودش جایگزین کند.

### مثال ۴ — array نیز object است

```java
int[] first = {1, 2, 3};
int[] second = first;
second[0] = 42;

System.out.println(first[0]);        // 42
System.out.println(first == second); // true
```

> **تلهٔ C++:** `std::array<int, 3> b = a;` عناصر را کپی می‌کند؛ اما `int[] b = a;` در Java فقط reference را کپی می‌کند. برای کپی عناصر از `a.clone()` یا `Arrays.copyOf(a, a.length)` استفاده کنید.

---

## ۲. ساخت object و constructor

`new` معمولاً instance تازه می‌سازد، constructor انتخاب‌شده را اجرا می‌کند و یک reference برمی‌گرداند. constructor نامی همانند کلاس دارد و return type ندارد.

### مثال ۵ — field initializer و constructor

```java
class Lamp {
    String color = "white";

    Lamp() {
        System.out.println("constructor: " + color);
    }
}

Lamp lamp = new Lamp();
// constructor: white
```

برای یک object از subclass، مدل ترتیب مفید این است:

```text
default valueهای fieldها
        ↓
constructor superclass
        ↓
field initializerها و initializer blockهای کلاس فعلی
        ↓
body constructor کلاس فعلی
```

### مثال ۶ — constructor chaining با `this(...)`

```java
class Ticket {
    String code;
    int seats;

    Ticket(String code) {
        this(code, 1);
    }

    Ticket(String code, int seats) {
        this.code = code;
        this.seats = seats;
    }
}

Ticket single = new Ticket("A-17");
System.out.println(single.seats); // 1
```

فراخوانی `this(...)` یا `super(...)` باید نخستین statement constructor باشد. در `this.code = code`، سمت چپ field و سمت راست پارامتر است.

### مثال ۷ — constructor بدون آرگومان همیشه خودکار نیست

```java
class Account {
    Account(String owner) {
        System.out.println(owner);
    }
}

// Account a = new Account(); // DOES NOT COMPILE
Account a = new Account("Mina");
```

فقط وقتی کلاس **هیچ constructorی** اعلام نکرده باشد، compiler یک no-argument constructor ضمنی می‌سازد. با اعلام حتی یک constructor، باید constructorهای لازم را خودتان بنویسید.

### مثال ۸ — مقداردهی field پیش از body constructor

```java
class Meter {
    int reading = 3;

    Meter() {
        reading += 2;
    }
}

Meter meter = new Meter();
System.out.println(meter.reading); // 5
```

در C++ initialisation-list ابزار اصلی ساخت memberهاست. Java چنین syntax مستقیمی ندارد؛ field initializerها به ترتیب declaration اجرا می‌شوند، سپس body constructor.

### اشتباه رایج — انتظار copy constructor ضمنی

```java
class Profile {
    String name;
}

Profile a = new Profile();
a.name = "Raha";
Profile b = a;
b.name = "Nika";
System.out.println(a.name); // Nika
```

**تصحیح:** object جداگانه را صریح بسازید و داده را کپی کنید:

```java
Profile b = new Profile();
b.name = a.name;
```

این shallow copy است. اگر fieldهای mutable reference دارید، برای هرکدام باید آگاهانه تصمیم بگیرید.

---

## ۳. هشت primitive با بازه‌های دقیق

اندازهٔ primitiveهای Java در specification ثابت است؛ برخلاف C++ که `long` و `char` می‌توانند به platform وابسته باشند.

| Java | اندازه | بازهٔ دقیق | مقایسه با C++ | نکته |
|---|---:|---|---|---|
| `byte` | 8 bit | `-128` تا `127` | `std::int8_t` | signed |
| `short` | 16 bit | `-32,768` تا `32,767` | `std::int16_t` | signed |
| `int` | 32 bit | `-2,147,483,648` تا `2,147,483,647` | `std::int32_t` | integer پیش‌فرض |
| `long` | 64 bit | `-9,223,372,036,854,775,808` تا `9,223,372,036,854,775,807` | `std::int64_t` | literal آن `L` می‌خواهد |
| `float` | 32 bit IEEE 754 | تقریباً `±1.4E-45` تا `±3.4028235E38` | `float` | ۶ تا ۷ رقم معنادار |
| `double` | 64 bit IEEE 754 | تقریباً `±4.9E-324` تا `±1.7976931348623157E308` | `double` | اعشاری پیش‌فرض |
| `char` | 16 bit unsigned | `0` تا `65,535` | `char16_t`، نه `char` | یک UTF-16 code unit |
| `boolean` | منطقی | فقط `true` و `false` | `bool` | تبدیل عددی ندارد |

```text
byte  : -2^7  تا 2^7  - 1
short : -2^15 تا 2^15 - 1
int   : -2^31 تا 2^31 - 1
long  : -2^63 تا 2^63 - 1
char  : 0 تا 2^16 - 1
```

Java primitive صحیح unsigned عمومی ندارد. فقط `char` unsigned است. برای عملیات unsigned روی `int` و `long` از APIهایی مانند `Integer.compareUnsigned()` استفاده می‌شود.

### مثال ۹ — arithmetic باریک به `int` ارتقا می‌یابد

```java
byte b = 100;
// b = b + 1; // DOES NOT COMPILE: بهای expression از نوع int است
b += 1;
System.out.println(b); // 101
```

`b += 1` از نظر مفهومی نزدیک به `b = (byte) (b + 1)` است. این تفاوت یکی از دام‌های آزمون است.

### مثال ۱۰ — overflow صحیح، wrap می‌شود

```java
int maximum = Integer.MAX_VALUE;
int wrapped = maximum + 1;
System.out.println(wrapped); // -2147483648
```

برخلاف signed overflow در C++ که undefined behavior است، overflow `int` و `long` در Java با مکمل دو wrap می‌شود. برای تشخیص overflow از `Math.addExact()` استفاده کنید؛ در صورت overflow، `ArithmeticException` می‌دهد.

### مثال ۱۱ — `char`، کاراکتر کامل Unicode نیست

```java
char letter = 'ش';
char digit = '7';

System.out.println((int) letter); // 1588
System.out.println(digit + 1);    // 56؛ char به int promote می‌شود
```

`char` یک واحد ۱۶بیتی UTF-16 است. برخی emojiها دو `char` لازم دارند؛ پس `char` لزوماً یک glyph یا یک code point کامل نیست.

### مثال ۱۲ — `boolean` عدد نیست

```java
boolean ready = true;

// int n = ready; // DOES NOT COMPILE
// if (1) { }     // DOES NOT COMPILE
if (ready) {
    System.out.println("شروع");
}
```

برخلاف C و C++، `0` و `1` جایگزین `false` و `true` نیستند.

### مثال ۱۳ — floating-point و مقایسهٔ تقریبی

```java
System.out.println(0.1 + 0.2 == 0.3); // false

double expected = 0.3;
double actual = 0.1 + 0.2;
System.out.println(Math.abs(expected - actual) < 1e-12); // true
```

`float` و `double` برای پول مناسب نیستند. برای پول، مقدار صحیح کوچک‌ترین واحد یا `BigDecimal` با ورودی `String` را در نظر بگیرید.

---

## ۴. literalها، suffixها و conversion

literal صحیح بدون suffix از نوع `int` است. literal اعشاری بدون suffix از نوع `double` است. underscore فقط خوانایی را بهتر می‌کند و جزو مقدار نیست.

### مثال ۱۴ — decimal، binary، octal و hexadecimal

```java
int decimal = 26;
int binary = 0b11010;
int octal = 032;
int hexadecimal = 0x1A;
long population = 8_000_000_000L;

System.out.println(decimal == binary);      // true
System.out.println(binary == octal);        // true
System.out.println(octal == hexadecimal);   // true
```

صفر آغازین یعنی octal. underscore نمی‌تواند آغاز یا پایان literal، درست بعد از `0x` یا پیش از suffix قرار بگیرد.

### مثال ۱۵ — suffix `F` و `L`

```java
float ratio = 1.5F;
double precise = 1.5;
double scientific = 6.02e23;
long id = 9_000_000_000L;

// float broken = 1.5; // DOES NOT COMPILE: 1.5 یک double است
```

`L` بزرگ را به `l` کوچک ترجیح دهید؛ `l` به `1` شبیه است.

### مثال ۱۶ — narrowing cast صریح می‌خواهد

```java
int wide = 130;
// byte narrow = wide; // DOES NOT COMPILE
byte narrow = (byte) wide;
System.out.println(narrow); // -126
```

اما constant expressionی که در بازه است قابل assignment مستقیم است:

```java
byte okay = 127;
// byte tooLarge = 128; // DOES NOT COMPILE
```

### مثال ۱۷ — promotion و `var`

```java
byte x = 10;
byte y = 20;
var sum = x + y;

System.out.println(sum); // 30
```

`sum` از نوع `int` است؛ arithmetic روی `byte` و `short` معمولاً به `int` promote می‌شود.

---

## ۵. wrapperها، boxing و unboxing

| primitive | wrapper |
|---|---|
| `byte` | `Byte` |
| `short` | `Short` |
| `int` | `Integer` |
| `long` | `Long` |
| `float` | `Float` |
| `double` | `Double` |
| `char` | `Character` |
| `boolean` | `Boolean` |

wrapperها object و immutable هستند. genericها primitive type parameter نمی‌پذیرند، بنابراین `List<Integer>` معتبر است، اما `List<int>` معتبر نیست.

### مثال ۱۸ — autoboxing و unboxing

```java
Integer boxed = 42;
int primitive = boxed;

System.out.println(primitive + 8); // 50
```

compiler به‌ترتیب conversionهایی مانند `Integer.valueOf(42)` و `boxed.intValue()` را درج می‌کند.

### مثال ۱۹ — unboxing از `null`

```java
Integer visits = null;

// int count = visits; // کامپایل می‌شود، اما در runtime NPE می‌دهد
```

خطر در expressionهای ساده نیز وجود دارد:

```java
Integer total = null;
// total++; // NullPointerException؛ ابتدا unboxing انجام می‌شود
```

اصلاحی که قرارداد «نبود مقدار یعنی صفر» را صریح می‌کند:

```java
int safeTotal = (total == null) ? 0 : total;
```

### مثال ۲۰ — `==` برای wrapper هویت را می‌سنجد

```java
Integer smallA = 100;
Integer smallB = 100;
Integer largeA = 1_000;
Integer largeB = 1_000;

System.out.println(smallA == smallB);       // ممکن است true باشد: caching
System.out.println(largeA == largeB);       // معمولاً false
System.out.println(largeA.equals(largeB));  // true
```

به cache wrapper برای منطق برنامه تکیه نکنید. برای برابری مقدار wrapperها از `equals()` استفاده کنید. در expression زیر، وجود primitive باعث unboxing می‌شود:

```java
Integer score = 50;
System.out.println(score == 50); // true
```

اگر `score` برابر `null` باشد، همین expression به `NullPointerException` منجر می‌شود.

---

## ۶. local variable، field و definite assignment

fieldهای instance و static، و elementهای array، مقدار پیش‌فرض دارند. local variable هیچ مقدار پیش‌فرضی ندارد و compiler باید اثبات کند پیش از خواندن assign شده است.

| محل declaration | مقدار پیش‌فرض |
|---|---|
| instance field | `0`، `0.0`، `false`، `\\0` یا `null` |
| static field | همان مقدارهای پیش‌فرض |
| array element | همان مقدارهای پیش‌فرض |
| local variable | هیچ؛ باید پیش از خواندن assign شود |
| parameter | مقدار از caller می‌آید |

### مثال ۲۱ — field default دارد، local ندارد

```java
class Defaults {
    int field;
    String text;
    boolean enabled;

    void show() {
        System.out.println(field);   // 0
        System.out.println(text);    // null
        System.out.println(enabled); // false

        int local;
        // System.out.println(local); // DOES NOT COMPILE
    }
}
```

### مثال ۲۲ — definite assignment وابسته به همهٔ مسیرهاست

```java
int temperature;
boolean sensorAvailable = true;

if (sensorAvailable) {
    temperature = 21;
}

// System.out.println(temperature); // DOES NOT COMPILE
```

اصلاح:

```java
int temperature;
if (sensorAvailable) {
    temperature = 21;
} else {
    temperature = 0;
}
System.out.println(temperature);
```

### مثال ۲۳ — `final` local در هر مسیر فقط یک‌بار

```java
final String mode;
if (args.length == 0) {
    mode = "safe";
} else {
    mode = "fast";
}
System.out.println(mode);
```

`final` reference، object را immutable نمی‌کند؛ فقط assignment مجدد خود reference را ممنوع می‌کند.

### مثال ۲۴ — shadowing field با parameter

```java
class User {
    String name = "guest";

    void rename(String name) {
        name = name.trim();
        this.name = name;
    }
}
```

در خط نخست فقط parameter تغییر می‌کند. `this.name` به field instance جاری اشاره می‌کند.

### مثال ۲۵ — scope یک block

```java
if (true) {
    int retries = 3;
    System.out.println(retries);
}
// System.out.println(retries); // DOES NOT COMPILE
```

یک local در همان scope دوباره قابل declaration نیست:

```java
int level = 1;
// int level = 2; // DOES NOT COMPILE
```

اما local یا parameter می‌تواند field را shadow کند؛ این یکی از دلایل استفادهٔ صریح از `this.field` است.

---

## ۷. `var`: استنتاج نوع local، نه نوع پویا

`var` نوع static و مشخص متغیر را از initializer استنتاج می‌کند. نه `dynamic` است و نه راهی برای تغییر نوع متغیر پس از declaration.

### مثال ۲۶ — نوع از initializer استنتاج می‌شود

```java
var title = "Java 21";                  // String
var pages = 480;                         // int
var tags = new String[] {"jvm", "ocp"}; // String[]

// var empty;       // DOES NOT COMPILE
// var nothing = null; // DOES NOT COMPILE
```

### مثال ۲۷ — `var` انعطاف نوعی نمی‌سازد

```java
var label = "draft";
// label = 12; // DOES NOT COMPILE: label یک String است

Object flexible = "draft";
flexible = 12; // مجاز؛ نوع declaration، Object است
```

`var` فقط برای local variable، index حلقهٔ `for` و resource در try-with-resources است؛ برای field، parameter و return type مجاز نیست. وقتی نوع سمت راست واضح نیست، نوشتن نوع صریح خواناتر است.

---

## ۸. `String`: immutable، pooled و value-like

`String` یک class reference type است، اما immutable است. عملیاتی مانند `toUpperCase()` و `replace()` محتوای String فعلی را تغییر نمی‌دهند.

### مثال ۲۸ — تغییر ظاهری، object تازه

```java
String word = "java";
word.toUpperCase();
System.out.println(word); // java

word = word.toUpperCase();
System.out.println(word); // JAVA
```

### مثال ۲۹ — concatenation و `StringBuilder`

```java
String message = "سلام";
message = message + " دنیا";
System.out.println(message); // سلام دنیا

StringBuilder builder = new StringBuilder();
for (int i = 0; i < 3; i++) {
    builder.append(i);
}
System.out.println(builder.toString()); // 012
```

برای ساخت مرحله‌ای متن در loopهای بزرگ، `StringBuilder` معمولاً مناسب‌تر است. خودِ `StringBuilder` mutable است و برای اشتراک بدون هماهنگی میان threadها طراحی نشده است.

### مثال ۳۰ — literalها و string pool

```java
String first = "ocp";
String second = "ocp";
String third = new String("ocp");

System.out.println(first == second);        // true
System.out.println(first == third);         // false
System.out.println(first.equals(third));    // true
```

```text
String pool:
    "ocp" ◄── first
             └── second

object جدا:
    "ocp" ◄── third
```

literalهای برابر می‌توانند یک instance canonical از string pool را به اشتراک بگذارند. این هرگز دلیل استفاده از `==` برای مقایسهٔ متن نیست.

### مثال ۳۱ — constant expression در برابر runtime concatenation

```java
String pooled = "ja" + "va";
String literal = "java";
String runtimePart = "va";
String runtime = "ja" + runtimePart;

System.out.println(pooled == literal);       // true
System.out.println(runtime == literal);      // false
System.out.println(runtime.equals(literal)); // true
```

در مورد نخست compiler constant folding می‌کند. در مورد دوم، مقدار variable در runtime در expression حضور دارد؛ هویت را فرض نکنید.

### مثال ۳۲ — `intern()`، ابزاری تخصصی

```java
String computed = new String("jvm");
String canonical = computed.intern();

System.out.println(canonical == "jvm"); // true
```

`intern()` نمایندهٔ canonical pool را می‌دهد. برای حل مسئلهٔ معمول برابری متن از آن استفاده نکنید؛ `equals()` درست و واضح است. برای ورودی کنترل‌نشده، پیش از interning گسترده اثر حافظه را اندازه‌گیری کنید.

### مثال ۳۳ — مقایسهٔ String با null-safety

```java
String requested = null;

// requested.equals("admin"); // NullPointerException
boolean admin = "admin".equals(requested);
System.out.println(admin); // false
```

اگر هر دو طرف ممکن است `null` باشند، `Objects.equals(left, right)` انتخاب مناسبی است.

---

## ۹. `==` در برابر `equals()`

برای primitiveها، `==` مقدار را مقایسه می‌کند. برای referenceها، `==` هویت را بررسی می‌کند: آیا دقیقاً همان object هستند؟ `equals()` برابری منطقی را بر اساس قرارداد class می‌سنجد.

| expression | پرسش واقعی |
|---|---|
| `a == b` برای `int` | آیا مقدارها برابرند؟ |
| `a == b` برای reference | آیا یک object مشترک دارند؟ |
| `a.equals(b)` | آیا class آن‌ها را از نظر منطقی برابر می‌داند؟ |

### مثال ۳۴ — class سفارشی بدون override

```java
class Point {
    int x;
    int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
}

Point a = new Point(2, 3);
Point b = new Point(2, 3);
System.out.println(a == b);      // false
System.out.println(a.equals(b)); // false
```

`Object.equals()` به‌صورت پیش‌فرض هویت را مقایسه می‌کند.

### مثال ۳۵ — record، برابری مقداری تولید می‌کند

```java
record Coordinate(int x, int y) { }

Coordinate a = new Coordinate(2, 3);
Coordinate b = new Coordinate(2, 3);

System.out.println(a == b);      // false
System.out.println(a.equals(b)); // true
```

record هویت object را حذف نمی‌کند؛ دو instance جدا هستند. اما `equals()` تولیدشده componentها را مقایسه می‌کند. اگر `equals()` را override می‌کنید، `hashCode()` نیز باید مطابق همان تعریف باشد؛ وگرنه `HashSet` و `HashMap` رفتار ناسازگار خواهند داشت.

---

## ۱۰. نقشهٔ تصمیم سریع برای دام‌های OCP

```text
متغیر primitive است؟
  ├─ بله: == مقدار را مقایسه می‌کند.
  └─ خیر: reference است.
       ├─ می‌خواهی هویت را بدانی؟  → ==
       └─ می‌خواهی محتوای منطقی را بدانی؟ → equals / Objects.equals

wrapper ممکن است null باشد؟
  ├─ بله: پیش از unboxing بررسی کن.
  └─ خیر: arithmetic یا == با primitive، unboxing می‌کند.

local variable است؟
  ├─ بله: پیش از خواندن باید definitely assigned باشد.
  └─ خیر: field/array element مقدار پیش‌فرض دارد.
```

دام‌های پرتکرار:

1. `String a = "x"; String b = new String("x"); a == b` برابر `false` است.
2. `Integer n = null; n + 1` کامپایل می‌شود ولی NPE می‌دهد.
3. `byte b = 1; b = b + 1;` کامپایل نمی‌شود، اما `b += 1` می‌شود.
4. `char` یک UTF-16 code unit است، نه همیشه یک کاراکتر قابل‌نمایش.
5. literal `1.0` یک `double` است؛ برای `float` از `1.0F` استفاده کنید.
6. `new` object جدید می‌سازد؛ assignment reference جدید نمی‌سازد.
7. local variableها برخلاف fieldها default value ندارند.
8. `var n = null` غیرمجاز است، چون compiler نوعی برای استنتاج ندارد.

---

## تمرین‌ها

### تمرین ۱ — پیش‌بینی خروجی

بدون اجرا، خروجی را بنویسید:

```java
class Note {
    String text;
}

Note a = new Note();
a.text = "اول";
Note b = a;
b.text = "دوم";
System.out.println(a.text);
```

### تمرین ۲ — تصحیح کامپایل

هر خط مشکل‌دار را با کمترین تغییر اصلاح کنید:

```java
byte count = 120;
count = count + 2;
float price = 19.99;
var unknown = null;
```

### تمرین ۳ — توضیح NPE

چرا کد زیر compile می‌شود اما ممکن است در runtime شکست بخورد؟ یک نسخهٔ null-safe بنویسید.

```java
Integer retries = null;
if (retries > 0) {
    System.out.println("دوباره تلاش کن");
}
```

### تمرین ۴ — هویت یا برابری

برای هر کاربرد، مشخص کنید `==`، `equals()` یا `Objects.equals()` مناسب‌تر است:

- تشخیص اینکه دو `int` برابرند.
- مقایسهٔ رمز وضعیت با literal `"READY"`، در حالی که ورودی ممکن است `null` باشد.
- تشخیص اینکه callback فعلی همان instance ثبت‌شده است.
- مقایسهٔ دو `String` که هر دو ممکن است `null` باشند.

### تمرین ۵ — constructor

کلاسی به نام `Book` بسازید که fieldهای `title` و `pages` داشته باشد. یک constructor یک‌پارامتری بنویسید که `pages` را `1` قرار دهد و آن را به constructor دوپارامتری chain کند. سپس invariant را اعمال کنید: `pages` نباید منفی باشد.

---

## پاسخ کوتاه تمرین‌ها

1. `دوم`؛ هر دو reference به یک `Note` اشاره دارند.
2. `count += 2;` یا `count = (byte) (count + 2);`، سپس `float price = 19.99F;`، و برای `var` یک initializer با نوع مشخص انتخاب کنید؛ مثلاً `var unknown = "";`.
3. مقایسه، `retries` را unbox می‌کند. نسخه‌ای ساده: `if (retries != null && retries > 0) { ... }`.
4. به‌ترتیب: `==`، `"READY".equals(status)`، `==`، و `Objects.equals(left, right)`.
5. constructor تک‌پارامتری باید با `this(title, 1);` آغاز شود؛ validation را در constructor اصلی انجام دهید.

---

## واژه‌نامه

| اصطلاح | معنی |
|---|---|
| **primitive** | نوع مقداری پایه؛ یکی از هشت نوع زبان، مانند `int` و `boolean` |
| **reference** | مقداری که به object اشاره می‌کند یا `null` است |
| **identity** | یکسان‌بودن دو reference از نظر اشاره به همان object؛ با `==` سنجیده می‌شود |
| **logical equality** | برابر بودن بر اساس قرارداد `equals()`، مانند محتوای یکسان دو String |
| **constructor** | عضو بدون return type که هنگام ساخت object اجرا می‌شود |
| **field** | متغیر عضو instance یا class؛ دارای مقدار پیش‌فرض است |
| **local variable** | متغیر داخل method، constructor یا block؛ پیش از خواندن باید assign شود |
| **definite assignment** | تحلیل compile-time که تضمین می‌کند local variable پیش از استفاده مقدار دارد |
| **shadowing** | پنهان‌شدن نام field توسط local variable یا parameter هم‌نام |
| **boxing** | تبدیل primitive به wrapper، مانند `int` به `Integer` |
| **unboxing** | تبدیل wrapper به primitive؛ wrapper `null` باعث NPE می‌شود |
| **string pool** | مخزن canonical برای String literalها و Stringهای intern‌شده |
| **immutability** | ناتوانی object از تغییر state پس از ساخت؛ ویژگی `String` و wrapperها |
| **narrowing conversion** | تبدیل به نوعی با ظرفیت کمتر، مانند `int` به `byte`؛ معمولاً نیازمند cast |
| **promotion** | ارتقای operandها برای expression، مانند تبدیل `byte + byte` به `int` |

---

## درجهٔ ۱: چرخهٔ عمر شیء و مدیریت منابع در Java

این بخش برای برنامه‌نویسی نوشته شده است که در C++ با سازنده، RAII، عمرِ اشیای خودکار و اشاره‌گرها راحت است. شباهت واژگان گمراه‌کننده است: در Java «شیء» روی heap ساخته می‌شود، اما متغیرِ آن شیء معمولاً فقط یک **مقدار مرجع** است؛ و پایان scope به‌خودی‌خود پایان عمر شیء یا بستن منبع نیست.

---

## 1. ساخت شیء: چه چیزی واقعاً ساخته می‌شود؟

### مثال 1 — ساخت و اعلان جدا هستند

```java
class Lamp {
    int watts;
}

Lamp a;              // فقط یک متغیر مرجع محلی؛ هنوز مقدار ندارد
a = new Lamp();      // شیء ساخته و watts به 0 مقداردهی می‌شود
Lamp b = a;          // یک کپی از مقدار مرجع، نه کپی شیء
```

در C++، `Lamp x;` معمولاً یک شیء با storage مشخص می‌سازد. در Java، `Lamp a;` در متغیر محلی فقط نامی برای نگهداری یک reference است و پیش از مقداردهی حتی خواندن آن خطای کامپایل است. عبارت `new Lamp()` شیء را می‌سازد و مقدار مرجع آن را برمی‌گرداند.

```text
پس از b = a:

a ──┐
    ├──> Lamp { watts: 0 }
b ──┘
```

### مثال 2 — سازندهٔ پیش‌فرض ضمنی

```java
class Beacon {
    String color = "white";
}

Beacon beacon = new Beacon();
System.out.println(beacon.color); // white
```

وقتی هیچ سازنده‌ای در کلاس ننویسید، کامپایلر سازنده‌ای بدون پارامتر می‌افزاید که در نهایت `super()` را فرا می‌خواند. این سازندهٔ ضمنی **تنها وقتی** وجود دارد که شما هیچ سازنده‌ای اعلام نکرده باشید.

### مثال 3 — نوشتن هر سازنده، سازندهٔ بدون‌پارامتر را حذف می‌کند

```java
class Beacon {
    Beacon(String color) { }
}

// Beacon b = new Beacon(); // خطای کامپایل: سازندهٔ Beacon() وجود ندارد
Beacon red = new Beacon("red");
```

برای APIهای قابل استفاده، اگر ساخت بدون آرگومان هم معنای درستی دارد، آن را صریح بنویسید.

### مثال 4 — سازندهٔ صریح بدون‌پارامتر

```java
class Beacon {
    Beacon() {
        System.out.println("created");
    }

    Beacon(String color) {
        System.out.println(color);
    }
}
```

### مثال 5 — سازنده، تابع معمولی نیست

```java
class Point {
    final int x;
    final int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
}
```

سازنده return type ندارد و نامش دقیقاً نام کلاس است. `return 3;` در آن مجاز نیست. با این حال، `return;` برای خروج زودهنگام مجاز است؛ به شرطی که همهٔ fieldهای `final` تا آن نقطه مقدار گرفته باشند.

---

## 2. مقدار پیش‌فرض: field با local یکی نیست

### مثال 6 — fieldها مقدار پیش‌فرض دارند

```java
class Defaults {
    int count;          // 0
    boolean enabled;    // false
    double ratio;       // 0.0
    char marker;        // '\u0000' (کاراکتر NUL)
    String label;       // null
}
```

هر instance field و static field، پیش از اجرای initializerهای صریح، مقدار پیش‌فرض نوع خود را می‌گیرد. این رفتار برای متغیر محلی برقرار نیست.

### مثال 7 — local variable باید قطعاً مقداردهی شود

```java
void printCount(boolean ready) {
    int count;
    if (ready) {
        count = 7;
    }
    // System.out.println(count); // خطای کامپایل: شاید مقدار نگرفته باشد
}
```

کامپایلر Java «definite assignment» را بررسی می‌کند. در C++ خواندن متغیر محلی مقداردهی‌نشده ممکن است رفتار نامعین ایجاد کند؛ در Java، در مسیرهای قابل تشخیص، جلوی آن در زمان کامپایل گرفته می‌شود.

### مثال 8 — local با مقدار صریح درست است

```java
void printCount() {
    int count = 0;
    System.out.println(count);
}
```

### مثال 9 — `null` فقط یک مقدار مرجع است

```java
String title = null;
System.out.println(title);        // null را چاپ می‌کند
// System.out.println(title.length()); // NullPointerException
```

`null` معادل یک شیء تهی یا رشتهٔ خالی نیست. برای referenceهای غیرprimitive یک مقدار ویژه است که به هیچ شیئی اشاره نمی‌کند.

---

## 3. ترتیب مقداردهی: static، سپس instance، سپس بدنهٔ سازنده

برای اولین استفادهٔ فعال از کلاس، ابتدا initialization استاتیک آن کلاس اجرا می‌شود. برای هر `new`، ابتدا حافظهٔ شیء و defaultها، سپس field initializerها و instance initializer blockها به ترتیب متن، و در پایان بدنهٔ سازنده اجرا می‌شوند.

### مثال 10 — trace کامل یک کلاس

```java
class Order {
    static int next = logStatic("static field");

    int id = log("instance field");

    { log("instance block"); }

    Order() {
        log("constructor body");
    }

    static int logStatic(String s) {
        System.out.println(s);
        return 1;
    }

    int log(String s) {
        System.out.println(s);
        return 1;
    }
}

new Order();
```

خروجی:

```text
static field
instance field
instance block
constructor body
```

`static field` فقط یک بار در زمان initialization کلاس چاپ می‌شود. سه خط بعدی با هر `new Order()` تکرار می‌شوند.

### مثال 11 — ترتیب متن field و block مهم است

```java
class Recipe {
    int servings = 2;
    { servings += 1; }
    int total = servings * 4;

    Recipe() {
        System.out.println(total);
    }
}

new Recipe(); // 12
```

ردیابی: defaultهای هر سه field ابتدا `0` هستند؛ سپس `servings = 2`، بعد block آن را `3` می‌کند، سپس `total = 3 * 4` می‌شود. ترتیب، ترتیب ظاهر شدن در متن کلاس است؛ نه ترتیب ذهنی شما و نه ترتیب سازنده.

### مثال 12 — دسترسی غیرمستقیم به field بعدی، default فعلی آن را می‌بیند

```java
class Snapshot {
    int seen = readLater();
    int later = 9;

    int readLater() {
        return later;
    }

    Snapshot() {
        System.out.println(seen + "," + later);
    }
}

new Snapshot(); // 0,9
```

در `seen = later`، خواندن مستقیم fieldی که بعدتر اعلام شده است خطای `illegal forward reference` است. اما فراخوانی متد از این محدودیت نحوی عبور می‌کند: هنگام اجرای `readLater()`، initializer مربوط به `later` هنوز نرسیده، پس field همچنان defaultِ `0` را دارد. سپس `later = 9` اجرا می‌شود. این مثال آموزشی است، نه الگوی پیشنهادی؛ initializerها را با وابستگی رو به جلو طراحی نکنید.

### مثال 13 — staticها نیز ترتیب متنی دارند

```java
class Registry {
    static String first = "A";
    static String combined = first + "B";

    static {
        combined += "C";
    }
}

System.out.println(Registry.combined); // ABC
```

مقایسه با C++: ترتیب initialization بین translation unitها در C++ می‌تواند مسئله‌ساز باشد. Java برای یک کلاس، ترتیب دقیق و تعریف‌شدهٔ متن را دارد؛ ولی initialization یک کلاس فقط با «استفادهٔ فعال» تحریک می‌شود، نه صرفاً با ذکر نام آن در همهٔ موقعیت‌ها.

---

## 4. زنجیرهٔ سازنده و وراثت

هر constructor باید نخستین statement خود را به `this(...)` یا `super(...)` اختصاص دهد، مگر آن‌که کامپایلر `super()` را ضمنی اضافه کند. نمی‌توان هر دو را در یک سازنده نوشت؛ `this(...)` در نهایت به سازنده‌ای می‌رسد که `super(...)` را فرا می‌خواند.

### مثال 14 — constructor chaining با `this`

```java
class Ticket {
    final String code;
    final int priority;

    Ticket(String code) {
        this(code, 0);
    }

    Ticket(String code, int priority) {
        this.code = code;
        this.priority = priority;
    }
}
```

فایدهٔ این الگو، یک نقطهٔ مرکزی برای invariantهاست. به جای کپی‌کردن validation در چند سازنده، سازنده‌های کوتاه‌تر به سازندهٔ کامل‌تر delegation می‌کنند.

### مثال 15 — `this(...)` باید اولین statement باشد

```java
class Ticket {
    Ticket() {
        // System.out.println("before");
        // this("T-1"); // خطا: باید اولین statement باشد
        this("T-1");
    }

    Ticket(String code) { }
}
```

### مثال 16 — ترتیب پایه و فرزند

```java
class Parent {
    int parentField = say("parent field");

    Parent() {
        say("parent constructor");
    }

    int say(String text) {
        System.out.println(text);
        return 1;
    }
}

class Child extends Parent {
    int childField = say("child field");

    Child() {
        say("child constructor");
    }
}

new Child();
```

خروجی:

```text
parent field
parent constructor
child field
child constructor
```

ردیابی ساخت `Child`:

1. `Child()` به شکل ضمنی `super()` را آغاز می‌کند.
2. initializerهای instance در `Parent` اجرا می‌شوند.
3. بدنهٔ `Parent()` اجرا می‌شود.
4. initializerهای instance در `Child` اجرا می‌شوند.
5. بدنهٔ `Child()` اجرا می‌شود.

### مثال 17 — override در سازنده یک دام است

```java
class Parent {
    Parent() {
        describe();
    }

    void describe() { }
}

class Child extends Parent {
    private String name = "ready";

    @Override
    void describe() {
        System.out.println(name);
    }
}

new Child(); // null
```

وقتی `Parent()`، متد virtual را صدا می‌زند، dispatch به `Child.describe()` می‌رود؛ اما `name` هنوز initializer خودش را اجرا نکرده است. در C++ فراخوانی virtual از constructor رفتار dispatch متفاوتی دارد؛ در Java این فراخوانی واقعاً override فرزند را می‌بیند. نتیجه: از فراخوانی متدهای overridable در constructor و initializer پرهیز کنید.

---

## 5. Java همیشه pass-by-value است

Java هیچ pass-by-reference در سطح پارامتر ندارد. اگر پارامتر reference باشد، **مقدار reference** کپی می‌شود. پس تابع می‌تواند شیء مشترک را mutate کند، اما نمی‌تواند متغیر caller را به شیء دیگری rebind کند.

### مثال 18 — primitive: کپی مستقل

```java
static void addOne(int n) {
    n++;
}

int score = 10;
addOne(score);
System.out.println(score); // 10
```

```text
قبل از فراخوانی: score = 10
در addOne:        n = 10  سپس n = 11
پس از بازگشت:     score = 10
```

### مثال 19 — mutation از پشت referenceِ کپی‌شده دیده می‌شود

```java
static void rename(StringBuilder b) {
    b.append("!");
}

StringBuilder name = new StringBuilder("Ada");
rename(name);
System.out.println(name); // Ada!
```

```text
caller: name ─────┐
                  ├──> StringBuilder [A d a]
callee: b ────────┘

b.append("!") همان شیء مشترک را تغییر می‌دهد.
```

### مثال 20 — rebind پارامتر caller را تغییر نمی‌دهد

```java
static void replace(StringBuilder b) {
    b = new StringBuilder("Grace");
    b.append("!");
}

StringBuilder name = new StringBuilder("Ada");
replace(name);
System.out.println(name); // Ada
```

```text
ورود:  name ─┐
             └──> SB("Ada")
        b ───┘

پس از b = new ...:
name ───────────> SB("Ada")
b    ───────────> SB("Grace!")
```

### مثال 21 — تعویض دو reference در یک متد کار نمی‌کند

```java
static void swap(StringBuilder left, StringBuilder right) {
    StringBuilder tmp = left;
    left = right;
    right = tmp;
}

StringBuilder a = new StringBuilder("A");
StringBuilder b = new StringBuilder("B");
swap(a, b);
System.out.println(a + " " + b); // A B
```

اگر هدف تغییر متغیرهای caller است، نتیجه را برگردانید یا وضعیت mutable مشترکی طراحی کنید؛ به «reference parameter» خیالی تکیه نکنید.

### مثال 22 — تغییر محتوا در برابر ساخت رشتهٔ تازه

```java
static void attempt(String s, StringBuilder b) {
    s = s + "!";
    b.append("!");
}

String word = "go";
StringBuilder buffer = new StringBuilder("go");
attempt(word, buffer);
System.out.println(word);   // go
System.out.println(buffer); // go!
```

**تصحیح سوءبرداشت StringBuilder:** این‌که `StringBuilder` بعد از `append` تغییر می‌کند، دلیل pass-by-reference بودن Java نیست. `b` خودش کپی‌شده است؛ هر دو کپی به یک builder mutable اشاره دارند. همچنین `String` immutable است: `s + "!"` شیء string تازه می‌سازد و فقط `s` محلی را به آن bind می‌کند.

---

## 6. `final`: ثابت بودن reference، نه لزوماً شیء

### مثال 23 — reference نهایی، شیء mutable

```java
final StringBuilder audit = new StringBuilder("start");
audit.append(" -> saved");          // مجاز
// audit = new StringBuilder("new"); // خطای کامپایل
```

`final` روی متغیر می‌گوید این متغیر پس از assignment نخست دوباره assignment نمی‌گیرد. نمی‌گوید object تغییرناپذیر است.

### مثال 24 — immutable object و final reference دو مفهوم جدا هستند

```java
StringBuilder mutable = new StringBuilder("x");
mutable.append("y"); // محتوا تغییر می‌کند

final String immutable = "x";
// immutable.append("y"); // اصلاً چنین متدی ندارد
```

`String` immutable است، چه متغیرش `final` باشد چه نباشد. برعکس، `final List` می‌تواند کاملاً mutable بماند. برای object immutable، state را private و final نگه دارید، ورودی mutable را defensive copy کنید، و mutator عمومی ندهید.

### مثال 25 — `final` field باید در هر مسیر سازنده مقدار بگیرد

```java
class ConnectionInfo {
    final String host;

    ConnectionInfo(String host) {
        if (host == null) {
            throw new IllegalArgumentException("host required");
        }
        this.host = host;
    }
}
```

throw شدن سازنده یک مسیر «ساخت موفق» نیست؛ بنابراین الزام `final` را نقض نمی‌کند. اما اگر سازنده عادی تمام شود، هر final instance field باید دقیقاً یک بار مقداردهی شده باشد.

---

## 7. reachability و GC: چه وقت شیء قابل جمع‌آوری است؟

Garbage collector شیئی را که از ریشه‌های زنده (مانند stackهای فعال، static fieldها و ساختارهای runtime) قابل دسترسی نیست، **واجد شرایط** بازیافت می‌داند. این یک قرارداد زمانی دقیق نیست: نه می‌دانید چه وقت GC اجرا می‌شود، نه تضمین دارید پیش از پایان پردازش اجرا شود.

### مثال 26 — از دست رفتن آخرین مسیر

```java
class Note { }

Note note = new Note();
note = null; // شیء قبلی، اگر مسیر دیگری نباشد، قابل جمع‌آوری می‌شود
```

### مثال 27 — چرخه مانع GC نیست

```java
class Node {
    Node next;
}

Node first = new Node();
Node second = new Node();
first.next = second;
second.next = first;
first = null;
second = null;
```

در reference counting خامِ C++، چرخه‌ها مشکل دارند. collector ردیاب Java از rootها آغاز می‌کند؛ اگر هیچ root به این حلقه نرسد، هر دو گره قابل جمع‌آوری‌اند.

### مثال 28 — static می‌تواند شیء را زنده نگه دارد

```java
class Cache {
    static Object retained;
}

Cache.retained = new byte[10_000_000];
// تا زمان تغییر یا پایان عمر class loader، array reachable است
```

این الگو منشأ رایج memory leak در Java است: «نشتی» معمولاً یعنی شیئی که دیگر مفید نیست اما همچنان reachable مانده است، نه الزاماً فراموش‌شدن آزادسازی حافظه.

### مثال 29 — `System.gc()` دستور cleanup نیست

```java
Object data = new Object();
data = null;
System.gc(); // صرفاً درخواست/پیشنهاد به JVM است؛ زمان‌بندی تضمین‌شده نیست
```

به GC برای آزادکردن file descriptor، socket، lock خارجی یا تراکنش تکیه نکنید. `finalize()` نیز سازوکار قابل اتکایی برای cleanup نیست و نباید برای این هدف طراحی شود.

---

## 8. Java در برابر RAII

در C++، object خودکار در خروج از scope destructor اجرا می‌کند؛ بنابراین `std::ifstream` غالباً resource را به‌طور قطعی می‌بندد. Java destructor قطعیِ متناظر ندارد. جمع‌آوری حافظه از مدیریت **منابع خارجی** جداست.

| موضوع | C++ RAII | Java |
|---|---|---|
| پایان scope | destructor برای object خودکار اجرا می‌شود | شیء ممکن است هنوز reachable باشد یا بعداً GC شود |
| آزادسازی heap | smart pointer/مالکیت | GC با reachability |
| فایل/سوکت | destructor اغلب cleanup قطعی | `close()` صریح یا try-with-resources |
| الگوی اصلی | نوع resource-owning | `AutoCloseable` + try-with-resources |

در Java، RAII را از نظر نیت با یک بلوک try-with-resources نزدیک می‌کنید، نه با امید به GC.

### مثال 30 — قرارداد `AutoCloseable`

```java
class Session implements AutoCloseable {
    @Override
    public void close() {
        System.out.println("release external resource");
    }
}

try (Session session = new Session()) {
    System.out.println("use session");
}
```

خروجی:

```text
use session
release external resource
```

منبع در headerِ `try (...)` ساخته می‌شود و Java هنگام خروج از بلوک، چه عادی چه استثنایی، `close()` را فرا می‌خواند.

### مثال 31 — close در return هم انجام می‌شود

```java
static String readLabel() {
    try (Session session = new Session()) {
        return "ok";
    }
}
```

ترتیب مفهومی: مقدار `"ok"` محاسبه می‌شود، `close()` اجرا می‌شود، سپس متد به caller برمی‌گردد. بنابراین `return` راه فرار از cleanup نیست.

### مثال 32 — close در exception هم انجام می‌شود

```java
static void fail() {
    try (Session session = new Session()) {
        throw new IllegalStateException("work failed");
    }
}
```

پیش از انتشار `IllegalStateException`، `session.close()` اجرا می‌شود.

### مثال 33 — منابع متعدد برعکس باز می‌شوند

```java
class Named implements AutoCloseable {
    private final String name;

    Named(String name) { this.name = name; }

    @Override
    public void close() {
        System.out.println("close " + name);
    }
}

try (Named outer = new Named("outer");
     Named inner = new Named("inner")) {
    System.out.println("work");
}
```

خروجی:

```text
work
close inner
close outer
```

این LIFO است و به nested resourceها می‌خورد: inner معمولاً به outer وابسته است، پس اول inner بسته می‌شود.

### مثال 34 — resource موجود را می‌توان در try آورد

```java
Named session = new Named("session");
try (session) {
    System.out.println("using existing variable");
}
// session.close() اجرا شده است
```

متغیر باید effectively final باشد؛ یعنی پس از assignment اولیه reassign نشده باشد. قابل‌مشاهده‌بودن متغیر پس از بلوک به معنای بازبودن resource نیست.

### مثال 35 — `try/finally` معادل دستی، اما پرخطاتر

```java
Session session = new Session();
try {
    System.out.println("use session");
} finally {
    session.close();
}
```

اگر ساخت resource در چند مرحله است یا exceptionهای `close()` را درست مدیریت نکنید، نسخهٔ دستی پیچیده می‌شود. در صورت امکان try-with-resources را ترجیح دهید.

---

## 9. exception اصلی و suppressed exception

اگر bodyِ try exception بدهد و `close()` هم exception بدهد، Java exception body را **primary** نگه می‌دارد و exception close را suppressed به آن متصل می‌کند. این انتخاب عیب اصلی عملیات را پنهان نمی‌کند.

### مثال 36 — exception بسته‌شدن suppressed می‌شود

```java
class ExplodingResource implements AutoCloseable {
    @Override
    public void close() throws Exception {
        throw new Exception("close failed");
    }
}

try (ExplodingResource r = new ExplodingResource()) {
    throw new Exception("work failed");
} catch (Exception e) {
    System.out.println(e.getMessage());                 // work failed
    System.out.println(e.getSuppressed()[0].getMessage()); // close failed
}
```

### مثال 37 — اگر body موفق باشد، exception close همان exception اصلی است

```java
try (ExplodingResource r = new ExplodingResource()) {
    System.out.println("work succeeded");
} catch (Exception e) {
    System.out.println(e.getMessage()); // close failed
    System.out.println(e.getSuppressed().length); // 0
}
```

### مثال 38 — چند close شکست‌خورده و ترتیب suppressedها

```java
class Broken implements AutoCloseable {
    private final String name;
    Broken(String name) { this.name = name; }

    @Override
    public void close() throws Exception {
        throw new Exception("close " + name);
    }
}

try (Broken one = new Broken("one");
     Broken two = new Broken("two")) {
    throw new Exception("body");
} catch (Exception e) {
    System.out.println(e.getMessage()); // body
    for (Throwable suppressed : e.getSuppressed()) {
        System.out.println(suppressed.getMessage());
    }
}
```

خروجی suppressedها نخست `close two` و سپس `close one` است، چون closeها به ترتیب معکوس آغاز شده‌اند. در logging production، suppressed exceptionها را نیز ثبت کنید؛ آن‌ها می‌توانند نشانهٔ خرابی شبکه، flush نشدن داده یا cleanup ناقص باشند.

---

## 10. سوءبرداشت‌های پرتکرار و جایگزین دقیق آن‌ها

1. **«Java reference یعنی C++ reference.»** خیر. متغیر Java مقداری را نگه می‌دارد که می‌تواند reference باشد، و آن مقدار به پارامتر کپی می‌شود. نزدیک‌ترین قیاس عملی اغلب pass-by-value یک pointer در C++ است، نه `T&`.
2. **«`final` شیء را immutable می‌کند.»** خیر. `final` جلوی assignment مجدد همان variable را می‌گیرد؛ mutability خود شیء به طراحی کلاس بستگی دارد.
3. **«StringBuilder نشان می‌دهد Java pass-by-reference است.»** خیر. append، object مشترک را mutate می‌کند؛ assignment جدید فقط parameter محلی را rebind می‌کند.
4. **«خروج از scope فایل را می‌بندد.»** خیر. scope متغیر محلی تمام می‌شود، اما زمان GC معلوم نیست. resource را با try-with-resources ببندید.
5. **«GC memory leak را ناممکن می‌کند.»** خیر. reference ناخواسته در cache، listener، static collection یا `ThreadLocal` می‌تواند object را reachable نگه دارد.
6. **«هر کلاس سازندهٔ بدون‌پارامتر دارد.»** فقط وقتی هیچ constructor اعلام نکرده باشید، کامپایلر آن را تولید می‌کند.
7. **«ترتیب fieldها مهم نیست.»** initializerها به ترتیب متن اجرا می‌شوند؛ وابستگی مبهم میان آن‌ها طراحی شکننده است.
8. **«در constructor پایه، صدا زدن متد overrideشده بی‌خطر است.»** خیر. state فرزند ممکن است هنوز default باشد.

---

## 11. تمرین‌های تشخیصی

### تمرین 1 — خروجی و دلیل

```java
class Counter {
    static int shared = print("S");
    int own = print("F");

    Counter() { print("C"); }

    static int print(String s) {
        System.out.print(s);
        return 1;
    }
}

new Counter();
new Counter();
```

خروجی را بنویسید و مشخص کنید هر حرف مربوط به class initialization، instance initialization یا constructor است.

### تمرین 2 — اصلاح API

کلاس زیر باید هم ساخت بدون آرگومان و هم ساخت با نام را پشتیبانی کند. آن را طوری بازنویسی کنید که منطق initialization تکرار نشود.

```java
class User {
    User(String name) { }
}
```

### تمرین 3 — mutation یا rebinding؟

بدون اجرا، خروجی را پیش‌بینی کنید.

```java
static void change(StringBuilder x) {
    x.append("1");
    x = new StringBuilder("B");
    x.append("2");
}

StringBuilder value = new StringBuilder("A");
change(value);
System.out.println(value);
```

سپس دو نمودار reference رسم کنید: درست قبل و درست بعد از assignment دوم به `x`.

### تمرین 4 — طراحی immutable

کلاسی به نام `Money` بسازید که مقدار `long cents` و کد ارز `String currency` داشته باشد، پس از ساخت تغییر نکند و متدی مثل `plus(Money other)` شیء تازه برگرداند. دربارهٔ ناسازگاری currency تصمیم صریح بگیرید.

### تمرین 5 — ترتیب وراثت

برای `Parent` و `Child` مثال 16 یک instance initializer دیگر به هر کلاس اضافه کنید. خروجی کامل `new Child()` را پیش‌بینی و سپس اجرا کنید. چرا جای initializer در متن کلاس نتیجه را عوض می‌کند؟

### تمرین 6 — cleanup قابل اعتماد

یک `AutoCloseable` آزمایشی بنویسید که در `close()` نام خود را چاپ می‌کند. سه resource تو در تو بسازید، از body با `return` خارج شوید و ترتیب چاپ را توضیح دهید.

### تمرین 7 — suppressed exception

نسخه‌ای از مثال 38 بسازید که body موفق شود ولی هر دو `close()` شکست بخورند. exception اصلی کدام است و کدام exception suppressed می‌شود؟

---

## 12. مسیر ترمیم تطبیقی

هدف «حفظ‌کردن خروجی» نیست؛ باید بتوانید مدل state را روی کاغذ اجرا کنید. پس از هر تمرین، پاسخ خود را با این نشانه‌ها دسته‌بندی کنید.

| برچسب ترمیمی | مشاهده در پاسخ | تشخیص | فعالیت ترمیمی کوتاه | معیار عبور |
|---|---|---|---|---|
| `[ترمیم:alias]` | فکر می‌کنید `swap(a,b)` caller را عوض می‌کند | خلط value با alias | مثال 21 را با دو پیکان و دو قاب زمانی رسم کنید | بتوانید بگویید کدام assignment فقط parameter را عوض می‌کند |
| `[ترمیم:binding-state]` | `final StringBuilder` را immutable می‌نامید | خلط binding و state | برای سه نوع `final StringBuilder`، `StringBuilder` و `String` عملیات مجاز را فهرست کنید | mutation و rebinding را جداگانه پیش‌بینی کنید |
| `[ترمیم:definite-assignment]` | انتظار دارید local field مانند `0` باشد | انتقال نادرست مدل C++/C | مثال‌های 6 تا 8 را بدون مقداردهی compile کنید | علت خطای definite assignment را بیان کنید |
| `[ترمیم:control-flow-cleanup]` | `close()` را فقط در مسیر عادی حساب می‌کنید | مدل ناقص control flow | مثال‌های 31 و 32 را به صورت timeline `body → close → return/throw` بنویسید | در هر exit path cleanup را نشان دهید |
| `[ترمیم:suppression]` | exception close را گم می‌کنید | ناآشنایی با suppression | `getSuppressed()` را به logger آزمایشی اضافه کنید | exception primary و suppressed را نام ببرید |
| `[ترمیم:inheritance-order]` | خروجی constructor پایه را با state کامل فرزند انتظار دارید | درک ناقص initialization inheritance | مثال 17 را trace کنید و `name` را در هر گام بنویسید | دلیل `null` را بدون گفتن «باگ JVM» توضیح دهید |

پیشنهاد ترتیب یادگیری: نخست مثال‌های 6، 10 و 16 را دستی trace کنید؛ سپس 18 تا 22 را با نمودار alias حل کنید؛ در پایان 30 تا 38 را با جدول مسیرهای عادی، `return` و exception مرور کنید. اگر در هر مرحله پاسخ اشتباه بود، برچسب همان ردیف را انتخاب کنید و به مثال پایهٔ آن برگردید، نه این‌که فقط خروجی را حفظ کنید.

---

## واژه‌نامه

- **reference / مرجع:** مقداری که می‌تواند به یک شیء اشاره کند یا `null` باشد؛ خود شیء نیست.
- **object / شیء:** instance یک کلاس که state و رفتار دارد.
- **default value / مقدار پیش‌فرض:** مقدار اولیهٔ خودکار fieldهای instance/static، مانند `0`، `false` و `null`.
- **definite assignment / مقداردهی قطعی:** تحلیل کامپایلر برای اطمینان از مقدارداشتن local پیش از خواندن آن.
- **initializer / مقداردهنده:** field initializer یا blockی که هنگام initialization اجرا می‌شود.
- **constructor chaining / زنجیره‌سازی سازنده:** delegation با `this(...)` یا حرکت به سازندهٔ پایه با `super(...)`.
- **mutation / تغییر درجا:** تغییر state همان شیء، مانند `StringBuilder.append`.
- **rebinding / اتصال مجدد:** assignment یک reference variable به reference دیگر.
- **immutable / تغییرناپذیر:** شیئی که state قابل تغییرِ مشاهده‌پذیر ندارد؛ مستقل از `final` بودن متغیر نگهدارنده.
- **reachability / دسترس‌پذیری:** امکان رسیدن به شیء از GC rootها از طریق زنجیرهٔ referenceها.
- **garbage collection / جمع‌آوری زباله:** بازیابی حافظهٔ شیءهای غیرقابل‌دسترسی با زمان‌بندی نامعین.
- **RAII:** الگوی C++ که عمر resource را به عمر object گره می‌زند و cleanup را در destructor انجام می‌دهد.
- **AutoCloseable:** قرارداد Java برای نوعی که `close()` دارد و می‌تواند در try-with-resources استفاده شود.
- **try-with-resources:** ساختار `try (...)` که resourceها را هنگام خروج می‌بندد.
- **suppressed exception / استثنای سرکوب‌شده:** exception ثانویهٔ `close()` که هنگام وجود exception اولیه به آن attach می‌شود.

---

## دام‌ها و اصلاح برداشت‌ها

این جدول دفترچهٔ ترمیم است، نه فهرست نکته‌های حفظی. اگر یکی از ستون‌های نخست پاسخ شما را توصیف می‌کند، concept کنار آن باید در مرور بعدی اولویت بگیرد.

| برداشت نادرست | مدل دقیق | برچسب ترمیم |
|---|---|---|
| پارامتر `StringBuilder` می‌تواند متغیر caller را به شیء تازه وصل کند | Java همیشه value را کپی می‌کند؛ در reference، value کپی‌شده هنوز به همان object می‌رسد | `pass-by-value`, `references` |
| `final` یعنی object تغییرناپذیر است | `final` فقط rebinding متغیر/reference را می‌بندد؛ mutability قرارداد خود object است | `final`, `immutability` |
| GC فایل و socket را می‌بندد | GC زمان قطعی ندارد و ownership منبع خارجی را مدیریت نمی‌کند؛ `try (...)` می‌کند | `garbage-collection`, `try-with-resources` |
| literalهای `String` را می‌توان با `==` سنجید | pool ممکن است identity مشترک بسازد، اما قرارداد مقایسهٔ متن `equals()` است | `strings`, `equals-identity` |
| `import` مثل `#include` متن را وارد می‌کند | `import` فقط نام type را کوتاه می‌کند؛ نه source paste می‌کند و نه dependency runtime را فراهم می‌کند | `imports`, `classpath` |
| `var` نوع پویا می‌سازد | نوع static در زمان کامپایل و از initializer محلی استنتاج می‌شود | `var`, `variables` |
| local مانند field از صفر شروع می‌شود | local پیش از خواندن باید definitely assigned باشد؛ field/array element default نوعی دارند | `definite-assignment`, `variables` |

### درمان اصلیِ `StringBuilder`: mutation در برابر rebinding

```java
static void update(StringBuilder value) {
    value.append("!");
    value = new StringBuilder("new");
}

var text = new StringBuilder("old");
update(text);
System.out.println(text);
```

خروجی **`old!`** است، نه `new`.

```text
caller: text  ─┐                 بعد از append: هر دو → "old!"
               ├──> "old"       بعد از rebind: value → "new"
callee: value ─┘                                  text  → "old!"
```

`append` وضعیت object مشترک را عوض می‌کند. assignment دوم فقط متغیر محلی `value` را عوض می‌کند. اگر API باید object جایگزین‌شده را به caller برگرداند، باید آن را return کند:

```java
static StringBuilder replaced(StringBuilder value) {
    return new StringBuilder("new");
}
```

### پیش‌نگرِ inheritance و interface: قاعدهٔ ساختگی «nearest wins» نداریم

این بخش برای جلوگیری از انتقال یک مدل غلط به درجه‌های بعدی است؛ جزئیات کامل آنجا می‌آید.

1. فراخوانی یک method نمونهٔ overrideشدنی از constructor می‌تواند به override زیرکلاس dispatch شود، هنگامی که fieldهای زیرکلاس هنوز مقداردهی نشده‌اند. پس constructor نباید به behavior overrideشدنی تکیه کند.
2. fieldها **پنهان** می‌شوند، نه اینکه مانند instance methodها polymorphic dispatch شوند:

   ```java
   class Parent { String label = "P"; }
   class Child extends Parent { String label = "C"; }
   Parent value = new Child();
   System.out.println(value.label); // P: نوع reference تعیین‌کننده است
   ```

3. static methodها هم **hidden** هستند، نه overridden؛ انتخابشان با نوع مرجع/نام class در زمان کامپایل پیوند دارد.
4. `protected` در package دیگر فقط «هر reference» را برای subclass باز نمی‌کند؛ دسترسی باید از درون subclass و از receiver مناسبِ نوع subclass انجام شود. این محدودیت برای جلوگیری از دسترسی نامرتبطِ cross-package است.
5. method interface بدون body به‌طور ضمنی `public` است؛ implementation نمی‌تواند visibility را کمتر کند.
6. methodهای `private` و `static` در interface inherited نمی‌شوند؛ static را از نام خود interface صدا بزنید.
7. در default methodها قانون واقعی چنین است: method یک class بر default interface غلبه دارد؛ default یک interface خاص‌تر بر parent آن غلبه دارد؛ و defaultهای interfaceهای نامرتبط، class را وادار به resolve صریح می‌کنند. `static`، `private` و `final` قواعد جدا دارند.

### نقشهٔ مرور خطا به تمرین بعدی

| اگر خطا این بود | تمرین ترمیمی بعدی | نتیجهٔ مورد انتظار |
|---|---|---|
| `new` را خروجی مثال `StringBuilder` دانستید | آرایه را mutate و سپس پارامتر را reassign کنید | اثر mutation را از rebind جدا کنید |
| `final StringBuilder` را immutable نامیدید | `append()` و assignment دوم را کنار هم compile کنید | binding و state را جدا توضیح دهید |
| `System.gc()` را cleanup دانستید | یک `AutoCloseable` با پیام `close` در return و exception بنویسید | زمان close را به block، نه GC، گره بزنید |
| `==` را برای `String` برگزیدید | literal، `new String` و concatenation runtime را مقایسه کنید | identity و equality را جدا کنید |
| `var` را dynamic دانستید | پس از `var count = 1` یک `String` assign کنید | خطای static type را پیش‌بینی کنید |

## چک‌لیست پایان درجهٔ ۱

پیش از ورود به درجهٔ ۲، بدون اجرای برنامه باید بتوانید پاسخ دهید:

- چرا `java -cp out pkg.Main` نام کلاس می‌خواهد، نه مسیر فایل؟
- چرا `List<Integer>` مجاز اما `List<int>` نامجاز است؟
- چرا `Integer value = null; int x = value;` خطرناک است؟
- چرا `final` reference و immutable object یک مفهوم نیستند؟
- چرا `try-with-resources` در return و exception هم `close()` را اجرا می‌کند؟
- چرا warm-up/JIT یا escape analysis نباید خروجی برنامهٔ شما را تغییر دهند؟

## تمرین پروژه‌ای پایان درجهٔ ۱

یک `LibraryLauncher` در package `ir.learning.library` بسازید که یک `static final String` برای نام برنامه، یک class `Book` با constructor، دو reference alias به یک `Book`، و یک `try-with-resources` برای خواندن فایل داشته باشد. آن را با `javac -d out` بسازید و با نام کامل class اجرا کنید. سپس توضیح دهید کدام رفتارها «قاعدهٔ زبان» و کدام‌ها «جزئیات runtime» هستند.
