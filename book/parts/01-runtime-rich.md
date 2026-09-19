# بخش ۱: بلوک‌های سازندهٔ اجرا در Java 21

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

