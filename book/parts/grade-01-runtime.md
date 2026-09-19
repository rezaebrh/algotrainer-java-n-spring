# درجهٔ ۱: از کد جاوا تا زمان اجرا روی JVM

این فصل برای برنامه‌نویس باتجربهٔ C++ است که می‌خواهد مدل زمان اجرای جاوا را دقیق، نه صرفاً با تشبیه‌های سطحی، درک کند. در C++ معمولاً زنجیرهٔ ذهنی شما «منبع → فایل شیء → لینک → کد ماشین» است. در جاوا زنجیره کمی طولانی‌تر است: `javac` بایت‌کد مستقل از پردازنده تولید می‌کند، سپس JVM در زمان اجرای برنامه کلاس‌ها را پیدا، بررسی، پیوند و مقداردهی اولیه می‌کند و در نهایت بخش‌های داغ را به کد ماشین واقعی تبدیل می‌سازد.

```text
.java source
    │
    ├── javac: parse، type-check، تولید bytecode
    ▼
.class files / .jar archive
    │
    ├── classpath + class loader
    ▼
load → verify → link → initialize
    │
    ├── interpreter + profiling + JIT + GC
    ▼
native machine code روی CPU جاری
```

در برابر آن، مسیر متعارف C++ چنین است:

```text
.cpp + headers → compiler → .o → linker → executable + .so/.dll
                                                   │
                                                   ▼
                                      OS loader و dynamic linker
```

تشبیه `.class` به `.o` تا حدی مفید است، اما `.class` کد x86-64 یا ARM64 نیست. در آن دستورهای ماشین مجازی، جدول ثابت‌ها، توصیف نوع‌ها، امضای متدها و داده‌های لازم برای بررسی ایمنی وجود دارد. یک `.o` عموماً کد ماشینِ وابسته به معماری، relocation و قرارداد ABI مشخصی دارد. JVM حق دارد `.class` یکسان را روی دو CPU متفاوت به کد ماشین متفاوتی تبدیل کند.

## JDK، JRE و JVM

**JVM** یا Java Virtual Machine مشخصات ماشین انتزاعی و پیاده‌سازی اجراکنندهٔ آن است. JVM بایت‌کد را اجرا می‌کند، کلاس‌ها را بارگذاری می‌کند، حافظه را مدیریت می‌کند و معمولاً JIT دارد. HotSpot، OpenJ9 و GraalVM پیاده‌سازی‌های مهم JVM هستند؛ پس جاوا مساوی یک runtime خاص نیست.

**JRE** در اصطلاح سنتی، محیط اجرای برنامه بود: JVM به‌علاوهٔ کتابخانه‌های استاندارد. در انتشارهای جدید، JRE مستقل کمتر به‌عنوان محصول جدا عرضه می‌شود و معمولاً JDK کامل نصب می‌کنید یا runtime کوچک‌تری می‌سازید.

**JDK** ابزار توسعه را نیز شامل می‌شود: `java` برای اجرا، `javac` برای کامپایل، `jar` برای ساخت آرشیو، `javadoc`، debugger و ابزارهای تشخیصی مانند `jcmd` و `jstack`. این فرمان‌ها مشخص می‌کنند shell واقعاً کدام نصب را پیدا کرده است:

```bash
java -version
javac -version
which java
which javac
```

نمونهٔ اول کوچک‌ترین برنامهٔ کامل است:

```java
// Hello.java
public class Hello {
    public static void main(String[] args) {
        System.out.println("سلام از JVM");
    }
}
```

```bash
javac Hello.java
java Hello
```

خروجی `javac` فایلی به نام `Hello.class` است. در اجرای `java Hello` نام کلاس را می‌دهیم، نه نام فایل. `java Hello.class` نادرست است، زیرا launcher نام باینری کلاس را انتظار دارد. همچنین چون `Hello` یک کلاس سطح‌بالای `public` است، فایل منبع باید دقیقاً `Hello.java` نام داشته باشد. این الزام نام‌گذاری در C++ برای کلاس public وجود ندارد.

## `javac` و بایت‌کد

`javac` فقط تبدیل‌کنندهٔ متن نیست. این ابزار منبع را parse می‌کند، نام‌ها را resolve می‌کند، نوع‌ها و سطح دسترسی را بررسی می‌کند، genericها را با type erasure پیاده می‌سازد و `.class` تولید می‌کند. خطای نوعی در این مرحله رخ می‌دهد؛ اما نبودن بعضی dependencyها می‌تواند تا زمان اجرا پنهان بماند.

نمونهٔ دوم، کامپایل چند فایل:

```java
// Greeter.java
public class Greeter {
    public static String greet(String name) {
        return "سلام، " + name;
    }
}
```

```java
// UseGreeter.java
public class UseGreeter {
    public static void main(String[] args) {
        System.out.println(Greeter.greet("نورا"));
    }
}
```

```bash
javac Greeter.java UseGreeter.java
java UseGreeter
```

در build واقعی خروجی را از source جدا نگه می‌دارند:

```bash
mkdir -p out
javac -d out Greeter.java UseGreeter.java
java -cp out UseGreeter
```

گزینهٔ `-d out` مقصد class fileهاست. `-cp out` یا `-classpath out` می‌گوید کلاس‌ها کجا جست‌وجو شوند. اگر برنامه را در `out` کامپایل کنید و `-cp out` ندهید، خطای «Could not find or load main class» طبیعی است.

نمونهٔ سوم، مشاهدهٔ دستورهای JVM:

```java
// MathBox.java
public class MathBox {
    static int twice(int n) {
        return n * 2;
    }
}
```

```bash
javac MathBox.java
javap -c -p MathBox
javap -verbose MathBox
```

در خروجی `javap -c` دستورهایی مانند `iload`، `iconst_2`، `imul` و `ireturn` می‌بینید. این‌ها opcodeهای JVM هستند، نه اسمبلی CPU. `-verbose` جدول ثابت‌ها و نسخهٔ class file را نیز نشان می‌دهد.

اگر با JDK جدیدتر کامپایل و با JVM قدیمی اجرا کنید، احتمال `UnsupportedClassVersionError` وجود دارد. برای هدف قراردادن هم‌زمان زبان، bytecode و API نسخهٔ 17 مثلاً چنین بنویسید:

```bash
javac --release 17 -d out Hello.java
```

استفاده از `--release` معمولاً از ترکیب جداگانهٔ `-source` و `-target` مطمئن‌تر است، زیرا APIهای قابل دسترسی را هم محدود می‌کند.

## بارگذاری، verification، linking و initialization

کلاس‌ها لزوماً هنگام شروع process همگی خوانده نمی‌شوند. هر کلاس توسط یک **ClassLoader** با نام کامل خود هویت می‌گیرد. دو کلاس با نام باینری یکسان که از دو class loader متفاوت آمده‌اند، دو نوع متفاوت محسوب می‌شوند؛ موضوعی که در application serverها و سامانه‌های plugin اهمیت جدی دارد.

```text
Bootstrap Class Loader
        │
        ▼
Platform Class Loader
        │
        ▼
Application Class Loader
        │
        ├── out/
        ├── library-a.jar
        └── library-b.jar
```

مدل رایج delegation ابتدا از loader والد می‌پرسد. این کار کمک می‌کند یک JAR برنامه نتواند به‌سادگی `java.lang.String` را جایگزین کند. loader سفارشی می‌تواند سیاست‌های دیگری داشته باشد.

چرخهٔ مفهومی کلاس چنین است:

1. **Loading**: loader، bytes کلاس را از directory، JAR، شبکه یا منبع سفارشی می‌گیرد و آن را به JVM معرفی می‌کند.
2. **Verification**: JVM ساختار `.class` و سازگاری نوعی bytecode را کنترل می‌کند؛ مثلاً stack operand و مقصد پرش‌ها را بررسی می‌کند.
3. **Preparation**: برای فیلدهای static حافظه آماده و مقدار پیش‌فرض (`0`، `false` یا `null`) گذاشته می‌شود.
4. **Resolution**: ارجاع‌های نمادین به کلاس، فیلد و متد حل می‌شوند. JVM می‌تواند بخشی از این کار را lazy انجام دهد.
5. **Initialization**: مقداردهی‌های static و بلوک‌های `static {}` به ترتیب متن اجرا می‌شوند.

مراحل ۲ تا ۴ را معمولاً linking می‌نامند. بر خلاف linker معمول C++، همهٔ resolutionها الزاماً قبل از نخستین خط `main` تمام نمی‌شوند.

نمونهٔ چهارم نشان می‌دهد initialization هنگام استفادهٔ فعال رخ می‌دهد:

```java
// LazyInit.java
class Config {
    static final int PORT = readPort();

    static int readPort() {
        System.out.println("Config initialized");
        return 8080;
    }
}

public class LazyInit {
    public static void main(String[] args) {
        System.out.println("before");
        System.out.println(Config.PORT);
        System.out.println("after");
    }
}
```

```bash
javac LazyInit.java
java LazyInit
```

پیام `Config initialized` میان `before` و مقدار پورت چاپ می‌شود. preparation ابتدا مقدار پیش‌فرض را فراهم کرده است، ولی مقدار `8080` فقط در initialization حاصل می‌شود.

نمونهٔ پنجم، ترتیب initializerها:

```java
// StaticOrder.java
public class StaticOrder {
    static int first = printAndReturn("first", 1);

    static {
        System.out.println("block sees first=" + first);
    }

    static int second = printAndReturn("second", 2);

    static int printAndReturn(String label, int value) {
        System.out.println(label);
        return value;
    }

    public static void main(String[] args) {
        System.out.println("second=" + second);
    }
}
```

```bash
javac StaticOrder.java
java StaticOrder
```

ترتیب خروجی `first`، سپس static block و سپس `second` است. مانند initialization جهانی C++، side effectهای static می‌توانند طراحی را شکننده کنند. شبکه، I/O، ساخت thread و اعتبارسنجی سنگین را در static initializer قرار ندهید مگر واقعاً لازم باشد.

نمونهٔ ششم، failure initialization:

```java
// BrokenInit.java
public class BrokenInit {
    static {
        if (true) {
            throw new RuntimeException("تنظیمات نامعتبر است");
        }
    }

    public static void main(String[] args) {
        System.out.println("never reached");
    }
}
```

نخستین استفاده غالباً `ExceptionInInitializerError` می‌دهد. استفادهٔ بعدی از همان کلاس در همان JVM معمولاً `NoClassDefFoundError` می‌دهد، زیرا کلاس به حالت خطادار رسیده و initialization دوباره انجام نمی‌شود. علت اصلی را در بخش `Caused by:` stack trace پیدا کنید.

## `main` و `static`

نقطهٔ ورود مرسوم جاوا این امضاست:

```java
public static void main(String[] args)
```

نمونهٔ هفتم:

```java
// Arguments.java
public class Arguments {
    public static void main(String[] args) {
        for (int i = 0; i < args.length; i++) {
            System.out.printf("args[%d] = %s%n", i, args[i]);
        }
    }
}
```

```bash
javac Arguments.java
java Arguments one "two words" سه
```

برخلاف `int main(int argc, char** argv)` در C++، `main` یک member متعلق به کلاس است. `static` یعنی launcher برای فراخوانی آن به object نیاز ندارد. متد static به `this` دسترسی ندارد، زیرا نمونه‌ای وجود ندارد. بازگشت `void` کد خروج process را تعیین نمی‌کند؛ برای آن از `System.exit` استفاده کنید.

نمونهٔ هشتم:

```java
// ExitCode.java
public class ExitCode {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.err.println("usage: ExitCode <file>");
            System.exit(64);
        }
        System.out.println("processing " + args[0]);
    }
}
```

```bash
javac ExitCode.java
java ExitCode
printf 'exit status: %s\n' "$?"
```

## package و import در برابر headerها

package بخشی از نام کامل کلاس است و معمولاً با مسیر directory هماهنگ است. `import` یک header را به‌صورت متنی وارد نمی‌کند؛ صرفاً نام کوتاه را برای compiler قابل استفاده می‌سازد. پس نه macro وارد می‌شود، نه implementation تکرار می‌شود و نه به include guard نیاز دارید.

نمونهٔ نهم، پروژهٔ دو package:

```java
// src/com/example/tools/Counter.java
package com.example.tools;

public class Counter {
    private int value;

    public void increment() {
        value++;
    }

    public int value() {
        return value;
    }
}
```

```java
// src/com/example/app/App.java
package com.example.app;

import com.example.tools.Counter;

public class App {
    public static void main(String[] args) {
        Counter counter = new Counter();
        counter.increment();
        System.out.println(counter.value());
    }
}
```

```bash
mkdir -p out
javac -d out src/com/example/tools/Counter.java src/com/example/app/App.java
java -cp out com.example.app.App
```

کلاس اجراشدنی نام کاملاً صلاحیت‌دار `com.example.app.App` دارد. اگر import را بردارید و `com.example.tools.Counter` را در محل استفاده بنویسید، برنامه همان کار را می‌کند. import قرارداد لینک یا زمان اجرا نیست.

package تا حدی مثل namespace C++ است، اما تفاوت مهم دارد: عضو بدون modifier، **package-private** است و فقط code همان package می‌تواند آن را ببیند. namespace در C++ خودبه‌خود access control ایجاد نمی‌کند. در جاوا declaration و implementation غالباً در یک `.java` هستند؛ در C++ header به translation unit متنی تزریق می‌شود.

نمونهٔ دهم، static import:

```java
// StaticImportDemo.java
import static java.lang.Math.max;
import static java.lang.Math.min;

public class StaticImportDemo {
    public static void main(String[] args) {
        int clamped = max(0, min(100, 145));
        System.out.println(clamped);
    }
}
```

static import برای نام‌های واضح مناسب است، اما وارد کردن گستردهٔ نام‌هایی مانند `get`، `of` یا `build` خوانایی و قابلیت جست‌وجو را کم می‌کند.

## classpath و JAR در برابر `.dll` و ABI

classpath فهرستی مرتب از directoryها و JARهاست که JVM و compiler در آن دنبال کلاس می‌گردند. در Linux و macOS جداکننده `:` است؛ در Windows `;`.

```text
Linux/macOS: out:libs/json.jar:libs/logging.jar
Windows:     out;libs/json.jar;libs/logging.jar
```

JAR معمولاً یک فایل ZIP است که `.class`ها، resourceها و manifest را نگه می‌دارد. JAR native shared library نیست. ساخت executable JAR:

```bash
javac -d out src/com/example/tools/Counter.java src/com/example/app/App.java
jar --create --file counter-app.jar --main-class com.example.app.App -C out .
java -jar counter-app.jar
jar --list --file counter-app.jar
```

`--main-class` مقدار `Main-Class` را در manifest می‌گذارد. در C++، `.dll` یا `.so` به ABI پردازنده و compiler وابسته است: calling convention، name mangling، layout ساختار و allocator می‌توانند سازگاری را بشکنند. JAR معمولاً API باینری JVM عرضه می‌کند و از معماری مستقل است، اما binary compatibility تضمین مطلق نیست.

نمونهٔ یازدهم، resource از classpath:

```java
// src/com/example/app/ResourceDemo.java
package com.example.app;

import java.io.InputStream;
import java.nio.charset.StandardCharsets;

public class ResourceDemo {
    public static void main(String[] args) throws Exception {
        try (InputStream in = ResourceDemo.class.getResourceAsStream("/banner.txt")) {
            if (in == null) {
                throw new IllegalStateException("banner.txt not found");
            }
            System.out.println(new String(in.readAllBytes(), StandardCharsets.UTF_8));
        }
    }
}
```

```bash
javac -d out src/com/example/app/ResourceDemo.java
cp banner.txt out/banner.txt
jar --create --file resource-demo.jar --main-class com.example.app.ResourceDemo -C out .
java -jar resource-demo.jar
```

پس از JAR شدن، resource الزاماً یک فایل filesystem نیست؛ با stream آن را بخوانید، نه با فرض وجود path عادی.

خطاهای runtime رایج شبیه dynamic linking هستند، اما اغلب هنگام رسیدن برنامه به مسیر خاص دیده می‌شوند:

- `ClassNotFoundException`: class loader کلاس خواسته‌شده را پیدا نکرد.
- `NoClassDefFoundError`: کلاسی که compile-time حاضر بود، runtime نیست یا initialization آن قبلاً شکست خورده است.
- `NoSuchMethodError`: caller برای متدی کامپایل شده که JAR runtime آن را ندارد.
- `NoSuchFieldError`: همان ناسازگاری برای field.
- `IncompatibleClassChangeError`: شکل member تغییر ناسازگار داشته؛ مثلاً instance به static تبدیل شده است.

ترتیب classpath مهم است. اگر دو JAR هر دو `com.example.Util` را داشته باشند، نخستین نسخه‌ای که loader می‌یابد معمولاً انتخاب می‌شود. این «JAR hell» تا حدی مشابه search order برای DLL یا `LD_LIBRARY_PATH` است. Maven و Gradle graph dependency را مدیریت می‌کنند، اما اصل resolution را حذف نمی‌کنند.

## JIT، warm-up و deoptimization

JVM معمولاً اجرای متد را با interpreter یا کامپایل سبک آغاز می‌کند، profile اجرا جمع می‌کند و سپس متدهای پرتکرار را JIT-compile می‌نماید. JIT می‌تواند inline کند، dispatch مجازی را تخصصی کند، checkهای اضافی را حذف کند، allocationهای بدون escape را کاهش دهد و بعضی lockها را حذف کند.

نمونهٔ دوازدهم:

```java
// Warmup.java
public class Warmup {
    static long sumSquares(int n) {
        long sum = 0;
        for (int i = 0; i < n; i++) {
            sum += (long) i * i;
        }
        return sum;
    }

    public static void main(String[] args) {
        long sink = 0;
        for (int round = 0; round < 8; round++) {
            long start = System.nanoTime();
            for (int i = 0; i < 20_000; i++) {
                sink ^= sumSquares(1_000);
            }
            long elapsed = System.nanoTime() - start;
            System.out.printf("round %d: %.3f ms%n", round, elapsed / 1_000_000.0);
        }
        System.out.println("sink=" + sink);
    }
}
```

```bash
javac Warmup.java
java Warmup
java -XX:+PrintCompilation Warmup
```

ممکن است دورهای بعدی سریع‌تر شوند، ولی این benchmark معتبر نیست. GC، compilation هم‌زمان، فرکانس CPU و حذف محاسبهٔ بی‌اثر نتیجه را تغییر می‌دهند. برای benchmark جدی از JMH استفاده کنید؛ JMH warm-up، fork و اندازه‌گیری درست را مدیریت می‌کند.

JIT با فرض‌های قابل ابطال کار می‌کند. اگر در یک محل فراخوانی همیشه یک implementation دیده باشد، VM شاید call را inline کند. ورود implementation تازه می‌تواند فرض را خراب کند و JVM **deoptimization** انجام دهد: کد بهینه را کنار می‌گذارد و به interpreter یا کد عمومی‌تر بازمی‌گردد.

نمونهٔ سیزدهم:

```java
// Polymorphism.java
interface Formatter {
    int format(int value);
}

final class FastFormatter implements Formatter {
    public int format(int value) { return value + 1; }
}

final class AlternateFormatter implements Formatter {
    public int format(int value) { return value - 1; }
}

public class Polymorphism {
    static int run(Formatter formatter, int count) {
        int total = 0;
        for (int i = 0; i < count; i++) {
            total += formatter.format(i);
        }
        return total;
    }

    public static void main(String[] args) {
        System.out.println(run(new FastFormatter(), 1_000_000));
        System.out.println(run(new AlternateFormatter(), 1_000_000));
    }
}
```

از این نتیجه نگیرید که interface همیشه کند است. JVM ممکن است در workload واقعی آن را عالی بهینه کند یا به‌دلیل polymorphism واقعی نتواند. latency شروع و throughput پایدار را جداگانه بسنجید. برای CLI کوتاه‌عمر warm-up ممکن است هرگز جبران نشود؛ برای سرویس بلندمدت JIT معمولاً مزیت مهمی دارد.

## نمونهٔ چهاردهم و failure modeهای عملی

```java
// src/com/example/model/Account.java
package com.example.model;

public final class Account {
    private final String id;
    private long balance;

    public Account(String id, long openingBalance) {
        if (openingBalance < 0) {
            throw new IllegalArgumentException("negative opening balance");
        }
        this.id = id;
        this.balance = openingBalance;
    }

    public void deposit(long amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("amount must be positive");
        }
        balance += amount;
    }

    public String summary() {
        return id + ": " + balance;
    }
}
```

```java
// src/com/example/app/BankMain.java
package com.example.app;

import com.example.model.Account;

public class BankMain {
    public static void main(String[] args) {
        Account account = new Account("A-17", 500);
        account.deposit(25);
        System.out.println(account.summary());
    }
}
```

```bash
javac -d out src/com/example/model/Account.java src/com/example/app/BankMain.java
java -cp out com.example.app.BankMain
```

| نشانه | دلیل محتمل | نخستین بررسی |
|---|---|---|
| `class X is public... X.java` | نام فایل و public class متفاوت‌اند | نام فایل و class را یکی کنید |
| `package ... does not exist` | source یا dependency در classpath نیست | package، `-cp` و ترتیب build را بررسی کنید |
| `Could not find or load main class` | FQCN یا classpath غلط است | `java -cp out com.example.app.BankMain` را اجرا کنید |
| `Main method not found` | امضای main درست نیست | `public static void main(String[] args)` را بسنجید |
| `UnsupportedClassVersionError` | JVM قدیمی‌تر از bytecode است | runtime را ارتقا دهید یا `--release` بگذارید |
| `NoSuchMethodError` | نسخهٔ dependency زمان اجرا ناسازگار است | JARهای واقعی runtime را فهرست کنید |
| `ExceptionInInitializerError` | static initializer شکست خورده است | علت root در `Caused by` را بخوانید |

## مقایسهٔ فشرده با C++

| موضوع | Java/JVM | C++ متعارف |
|---|---|---|
| خروجی compiler | bytecode و metadata در `.class` | کد ماشین و relocation در `.o` |
| تولید code نهایی | interpreter/JIT در runtime | AOT، اغلب پیش از اجرا |
| قرارداد سازگاری | API، class loading، نسخهٔ JVM | ABI، compiler، معماری، linker |
| dependency source | `import` فقط حل نام است | `#include` متن header را وارد می‌کند |
| entry point | static method در class | global `main` |
| resolution نام | می‌تواند lazy باشد | بیشتر در link/load native |
| بهینه‌سازی | profile واقعی و deopt ممکن | static، LTO یا PGO؛ deopt عادی نیست |
| مدیریت عمر | GC و referenceهای managed | RAII، destructor و ownership صریح |

## برداشت‌های نادرست رایج

### «Java فقط interpret می‌شود؛ پس همیشه از C++ کندتر است»

نادرست است. شروع اجرای یک برنامه ممکن است interpreter، class loading و warm-up را درگیر کند، اما HotSpot بخش‌های داغ را با اطلاعات واقعی workload به کد native تبدیل می‌کند. در عوض، زمان آغاز، مصرف حافظه، pauseهای GC و latency دنباله‌ای را نیز باید جداگانه اندازه گرفت. «کند» یا «سریع» بدون workload، معیار و محیط اندازه‌گیری ادعای فنی نیست.

### «JAR همان executable یا DLL است»

نادرست است. JAR یک archive است که class و resource نگه می‌دارد. `java -jar` ابتدا یک JVM native را اجرا می‌کند و آن JVM محتویات JAR را load می‌کند. DLL یا `.so` تنها زمانی وارد تصویر می‌شود که Java از JNI، Panama FFM یا library native دیگری استفاده کند.

### «`import` همان `#include` است»

نادرست است. `import` یک include متنی نیست و declaration یا implementation را در source فعلی کپی نمی‌کند. import صرفاً اجازه می‌دهد نام کامل یک type را کوتاه‌تر بنویسید. به همین دلیل macro، include guard، include cycle و ODR به همان معنای C++ از این مسیر وجود ندارند.

### «هر class موجود در JAR فوراً load و initialize می‌شود»

نادرست است. JVM معمولاً load و resolution را تا نیاز واقعی به تأخیر می‌اندازد. حتی load شدن با initialization فرق دارد. به‌ویژه، خواندن constantهای compile-time ممکن است بدون initialization کلاس تعریف‌کننده انجام شود.

### «`static` در Java دقیقاً global است»

نادرست است. static member به class تعلق دارد و در عمل به هویت class loader نیز گره خورده است. یک class با نام یکسان که توسط دو loader متفاوت تعریف شده، دو مجموعه static state جدا دارد. همچنین static mutable state معمولاً مسئلهٔ lifecycle و هم‌زمانی ایجاد می‌کند.

### «اگر build سبز است، dependencyها درست‌اند»

نادرست است. build فقط classpath/module path زمان compile را کنترل می‌کند. dependencyهای واقعی زمان اجرا، ترتیب JARها، class loader سفارشی و نسخهٔ JVM ممکن است متفاوت باشند و خطاهایی مانند `NoSuchMethodError` را تازه در مسیر اجرای معین آشکار کنند.

### «برای بهینه‌سازی JVM، چند flag تصادفی کافی است»

نادرست است. flagهای JIT و GC اغلب trade-off دارند و به نسخه، سخت‌افزار و workload وابسته‌اند. ابتدا با profiler، allocation profile، GC log و benchmark درست، گلوگاه را اندازه بگیرید؛ سپس تنها تغییرهای قابل اثبات را نگه دارید.

## تمرین‌ها

1. `Hello.java` را با `javac -d out` کامپایل کنید. تفاوت `java Hello` و `java -cp out Hello` را توضیح دهید.
2. به `StaticOrder` فیلد static سومی بیفزایید که به `second` وابسته باشد. ترتیب خروجی را ابتدا پیش‌بینی و سپس اجرا کنید.
3. import در `App.java` را حذف و نام کامل `com.example.tools.Counter` را بنویسید. توضیح دهید چرا binary خروجی از دید runtime تفاوت بنیادی ندارد.
4. یک متد دارای `if` و یک متد دارای loop بنویسید؛ با `javap -c` دستورهای branch آن‌ها را بیابید.
5. `BrokenInit` را طوری بازنویسی کنید که فقط در حالت `--broken` شکست بخورد. سپس طراحی‌ای ارائه کنید که اعتبارسنجی را به جای static initializer در startup صریح انجام دهد.
6. دو JAR آزمایشی بسازید که کلاسی هم‌نام ولی خروجی متفاوت دارند. ترتیب classpath را تغییر دهید و اثر آن را ثبت کنید.
7. `Warmup` را با اندازهٔ حلقه‌های متفاوت اجرا کنید. چرا میانگین چند اجرای کوتاه، جای JMH را نمی‌گیرد؟
8. `Account` را با package-private کردن constructor خراب کنید و ببینید compiler چگونه مرز package را enforce می‌کند.

## واژه‌نامه

- **Bytecode / بایت‌کد:** دستورهای قابل اجرای JVM، نه کد ماشین یک CPU خاص.
- **Class file:** فایل `.class` شامل bytecode و فرادادهٔ یک class یا interface.
- **Class loader:** مؤلفه‌ای که class bytes را پیدا و به JVM معرفی می‌کند.
- **Classpath:** فهرست directoryها و JARهای جست‌وجوی کلاس و resource.
- **JAR:** آرشیو ZIP استاندارد برای class fileها، resourceها و manifest.
- **Verification:** کنترل ساختار و ایمنی نوعی bytecode پیش از اجرای آن.
- **Linking:** preparation و resolution ارجاع‌های نمادین؛ بخشی از آن ممکن است lazy باشد.
- **Initialization:** اجرای مقداردهی‌های static و static blockها، یک‌بار برای هر کلاس و loader.
- **JIT:** کامپایل‌کنندهٔ زمان اجرا که مسیرهای داغ را به کد ماشین بهینه تبدیل می‌کند.
- **Warm-up:** دورهٔ ابتدایی اجرای JVM که profiling و compilation هنوز در حال شکل‌گیری‌اند.
- **Deoptimization:** بازگشت از کد JIT بسیار تخصصی به اجرای عمومی‌تر وقتی فرض‌های runtime نامعتبر شوند.
- **ABI:** قرارداد باینری native مانند calling convention و layout؛ موضوع اصلی در libraryهای C++ و نه JARهای عادی جاوا.
