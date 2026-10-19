# درجهٔ ۳: String، immutability و API آن در Java 21

> **مسیر:** Java 21 / OCP Core API  
> **مخاطب:** برنامه‌نویس C++ که می‌خواهد `String` و `StringBuilder` را به‌عنوان API روزمره (نه نوع ابتدایی) بفهمد و از دام‌های معروف آن (== ، interning، concat در loop) دوری کند.

`String` در Java یک **reference type** است که نشان‌دهندهٔ دنباله‌ای از کاراکترهای UTF-16 است. سه ویژگی آن در استفادهٔ روزمره تعیین‌کننده‌اند: **immutability** (هر String قابل تغییر نیست)، **literal pool** (literal های یکسان به یک reference اشاره می‌کنند)، و **API غنی** (متدهایی مثل `substring`، `indexOf`، `split`، `replace`). این فصل هر سه را با دقت بررسی می‌کند و به `StringBuilder` و `String.format` نیز می‌پردازد.

مقایسه با C++: `std::string` در C++ قابل تغییر است و مقایسه با `==` محتوا را می‌سنجد. در Java، `==` روی reference **هویت** را مقایسه می‌کند؛ برای محتوا از `.equals()` استفاده کنید. این تفاوت منبع اصلی bug در کدهای منتقل‌شده است.

## نقشهٔ یادگیری و خروجی مورد انتظار

پس از این درجه باید بتوانید:

1. تشخیص دهید چه زمانی `==` روی String درست کار می‌کند و چه زمانی نباید به آن تکیه کنید؛
2. از متدهای `length`، `charAt`، `substring`، `indexOf`، `contains`، `split`، `replace`، `trim`/`strip` به‌درستی استفاده کنید؛
3. `StringBuilder` را در حلقهٔ concat به‌جای `+` به‌کار ببرید و تفاوت performance را توضیح دهید؛
4. `String.format` را با `%s`/`%d`/`%.2f` برای خروجی ساخت‌یافته بنویسید؛
5. text block (`"""..."""`) را برای رشته‌های چندخطی به‌کار ببرید.

### قرارداد خواندن این فصل

- **قاعدهٔ زبان:** نتیجه‌ای که JLS برای برنامهٔ قابل مشاهده تعیین می‌کند.
- **جزئیات runtime:** رفتار string pool در JVM و رفتار interning.
- **ترمیم:** هر جا یک برداشت رایج مدل ذهنی را منحرف می‌کند، برچسب مفهوم آمده است.

---

## ۱. immutability

هر String در Java **immutable** است: پس از ساخت، محتوای آن قابل تغییر نیست. متدهایی مثل `toUpperCase`، `replace`، `trim` **یک String جدید** برمی‌گردانند و String اصلی دست‌نخورده باقی می‌ماند:

```java
String s = "java";
String t = s.toUpperCase();   // t = "JAVA"، ولی s هنوز "java" است
System.out.println(s);        // java
System.out.println(t);        // JAVA
```

این رفتار سه فایده دارد:

1. **Thread-safety ذاتی:** چون String تغییر نمی‌کند، می‌تواند بین threadها به اشتراک گذاشته شود بدون synchronization.
2. **Hash ثابت:** وقتی String به‌عنوان key در HashMap استفاده می‌شود، hash آن تغییر نمی‌کند (در غیر این صورت hash table خراب می‌شد).
3. **Caching امکان‌پذیر است:** JVM می‌تواند String literalهای یکسان را در یک reference نگه دارد (string pool).

محدودیت: در حلقه‌هایی که String را مرتب concat می‌کنند (`s = s + piece;`)، هر iteration یک object جدید می‌سازد. اگر ده‌ها هزار iteration دارید، overhead garbage collection محسوس می‌شود. راه‌حل: `StringBuilder` (در §۵).

> **تلهٔ C++:** در C++ `std::string` قابل تغییر است. `s.toUpperCase()` در بعضی implementationها درجا تغییر می‌کند، در بعضی دیگر new می‌سازد. در Java رفتار کاملاً مشخص است: **همیشه** String جدید.

## ۲. literal pool و interning

وقتی در source code یک String literal می‌نویسید (`"hello"`)، JVM آن را در یک منطقهٔ خاص از heap به نام **string pool** قرار می‌دهد. اگر literal دیگری با همان محتوا در همان classloader دیده شود، reference به همان object برمی‌گردد. در نتیجه:

```java
String a = "hello";
String b = "hello";
System.out.println(a == b);   // true — هر دو به یک reference اشاره می‌کنند
```

این رفتار فقط برای **literal** (compile-time constant) کار می‌کند. وقتی String در runtime ساخته می‌شود (`new String(...)`، concat با `+`، متدهای factory)، object جدید در heap معمولی ساخته می‌شود و به pool تعلق ندارد:

```java
String c = new String("hello");
System.out.println(a == c);            // false — c در pool نیست
System.out.println(a.equals(c));       // true — محتوا یکسان

String d = "hel" + "lo";               // compile-time constant → pooled
System.out.println(a == d);            // true

String e = "hel";
String f = e + "lo";                   // runtime concat → not pooled
System.out.println(a == f);            // false
```

### متد `intern()`

اگر می‌خواهید String ساخته‌شده در runtime را وارد pool کنید، از `intern()` استفاده کنید:

```java
String c = new String("hello").intern();
System.out.println(a == c);            // true — intern شده
```

`intern()` ابتدا pool را جست‌وجو می‌کند؛ اگر String برابر وجود داشت، همان reference برمی‌گردد؛ وگرنه String به pool اضافه می‌شود. کاربرد اصلی: یکتایی reference برای مقایسهٔ سریع (`==` به‌جای `equals`). اما intern خودش هزینه دارد (جست‌وجو در pool) و در برنامه‌های حساس به memory می‌تواند مشکل‌ساز شود.

> **تلهٔ C++:** در C++ چیزی به نام string literal pool وجود ندارد (هر literal در read-only memory است ولی guarantee اشتراک نیست). در Java این رفتار **مشخص** است و بیشتر برنامه‌نویس‌ها انتظارش را ندارند.

## ۳. `==` در برابر `equals`

قاعدهٔ صریح: **روی String، همیشه از `equals()` استفاده کنید**، مگر اینکه واقعاً منظورتان مقایسهٔ reference باشد.

```java
String a = "hello";
String b = new String("hello");
System.out.println(a == b);          // false — دو object متفاوت
System.out.println(a.equals(b));     // true — محتوا یکسان
```

`equals` در کلاس String به‌صراحت sequence کاراکترها را مقایسه می‌کند. این رفتار contract کلاس `Object` را override می‌کند (که در آن `==` رفتار پیش‌فرض است).

### حساسیت به null

`a.equals(b)` اگر `a` null باشد، `NullPointerException` می‌دهد. برای null-safe مقایسه از `Objects.equals(a, b)` استفاده کنید (در `java.util`):

```java
Objects.equals(a, b);     // اگر هر دو null → true، اگر یکی null → false، وگرنه a.equals(b)
```

> **تلهٔ C++:** در C++ `==` روی `std::string` محتوا را مقایسه می‌کند. در Java `==` هویت را می‌سنجد. این تفاوت بزرگ‌ترین منبع bug در port از C++ به Java است.

## ۴. String API — متدهای پرکاربرد

این زیربخش مهم‌ترین متدهای `String` را فهرست می‌کند. همهٔ آن‌ها در OCP 21 و interviewها تست می‌شوند.

### `length` و `isEmpty`

```java
String s = "java";
s.length();       // 4 — field نیست، method است (برخلاف array)
s.isEmpty();      // true اگر length == 0
s.isBlank();      // true اگر فقط whitespace داشته باشد (Java 11+)
```

`isEmpty` فقط خالی بودن کاراکتری را چک می‌کند؛ `isBlank` شامل space، tab، newline نیز می‌شود.

### `charAt` و code unit

```java
String s = "java";
s.charAt(0);      // 'j' — کاراکتر UTF-16، نه codepoint
```

هر `char` یک **UTF-16 code unit** است (16 بیت). برای کاراکترهای خارج از BMP (مثل بعضی emoji)، به دو code unit نیاز است (surrogate pair). اگر با codepoint کار می‌کنید، از `codePointAt` استفاده کنید.

### `substring(begin, end)`

```java
String s = "Hello, World";
s.substring(7);          // "World" — از index 7 تا انتها
s.substring(0, 5);      // "Hello" — از 0 تا 5 (exclusive)
```

`begin` شامل می‌شود، `end` خیر. اگر خارج از محدوده باشد، `StringIndexOutOfBoundsException`.

### `indexOf` و `lastIndexOf`

```java
String s = "banana";
s.indexOf('a');          // 1 — اولین occurrence
s.lastIndexOf('a');      // 5 — آخرین occurrence
s.indexOf("na");         // 2 — اولین substring
s.indexOf('a', 3);       // 3 — از index 3 شروع کن
s.indexOf('z');          // -1 — پیدا نشد
```

`indexOf` در صورت نیافتن `-1` برمی‌گرداند (نه exception). برای چک وجود داشتن: `s.indexOf(x) >= 0` یا `s.contains(x)` (که از Java 1.5 وجود دارد).

### `contains`، `startsWith`، `endsWith`

```java
String s = "Hello, World";
s.contains("World");     // true
s.startsWith("Hello");   // true
s.endsWith("ld");        // true
```

### `replace` و `replaceAll`

```java
String s = "I love Java";
s.replace('o', '0');           // "I l0ve Java" — تک‌کاراکتر، literal
s.replaceAll("\\d+", "N");     // regex — همهٔ sequences رقمی
s.replaceFirst("\\d", "N");    // فقط اولین occurrence، regex
```

`replace(CharSequence, CharSequence)` literal است؛ `replaceAll` و `replaceFirst` **regex** هستند. این تفاوت مهم است: `s.replace(".", "!")` همهٔ کاراکترها را عوض می‌کند ولی `s.replaceAll(".", "!")` هر کاراکتر را جداگانه با `!` جایگزین می‌کند (نقطه در regex = "هر کاراکتر").

### `split`

```java
String s = "a,b,,c";
s.split(",");          // ["a", "b", "", "c"] — empty در انتها نگه داشته می‌شود
s.split(",", -1);      // صریح: -1 یعنی trailing empty هم نگه داشته شود
s.split(",", 0);       // پیش‌فرض: trailing empty حذف می‌شود → ["a", "b", ""]
```

متد `split` در حالت پیش‌فرض trailing emptyها را حذف می‌کند. اگر لازم دارید همهٔ بخش‌ها بمانند، `split(regex, -1)` بنویسید.

### `trim` و `strip`

```java
String s = "  hello  \n";
s.trim();          // "hello" — whitespace ASCII (≤ U+0020)
s.strip();         // "hello" — Unicode-aware (Java 11+)
s.stripLeading();  // فقط ابتدا
s.stripTrailing(); // فقط انتها
```

`trim` فقط whitespace ASCII را حذف می‌کند. `strip` (از Java 11) از `Character.isWhitespace` استفاده می‌کند و Unicode-aware است. در code جدید، `strip` ترجیح داده می‌شود.

### `toUpperCase` و `toLowerCase`

این متدها **محلی (locale)** حساس‌اند:

```java
String s = "istanbul";
s.toUpperCase();                      // "ISTANBUL" — locale پیش‌فرض
s.toUpperCase(Locale.ROOT);           // locale-independent، برای Turk-ish i مشکل ندارد
s.toUpperCase(new Locale("tr"));      // "İSTANBUL" — ترکی، نقطه‌دار
```

برای خروجی machine-readable (مثل کلید در hash map) از `Locale.ROOT` استفاده کنید تا نتیجه تحت تأثیر زبان سیستم نباشد.

> **تلهٔ C++:** در C++ locale handling در `std::tolower`/`std::toupper` پیچیده‌تر است. در Java، متد بدون آرگومان از default locale استفاده می‌کند که می‌تواند غیرمنتظره باشد.

## ۵. `StringBuilder` و concat در حلقه

`+` برای concat ساده راحت است، ولی در حلقه‌ای که N بار اجرا می‌شود، N-1 object موقت می‌سازد. `StringBuilder` این مشکل را حل می‌کند:

```java
// ✗ کند در حلقهٔ بزرگ
String s = "";
for (int i = 0; i < 1000; i++) {
    s = s + i;        // هر iteration یک String جدید، s قبلی garbage می‌شود
}

// ✓ بهینه
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append(i);
}
String s = sb.toString();   // فقط یک String در انتها
```

`StringBuilder` mutable است: `append` درجا تغییر می‌کند. capacity داخلی به‌صورت خودکار رشد می‌کند (معمولاً دو برابر). در پایان، `toString()` یک String جدید برمی‌گرداند.

### تفاوت `StringBuffer` و `StringBuilder`

`StringBuffer` نسخهٔ قدیمی‌تر است که `synchronized` است (thread-safe). `StringBuilder` (Java 5+) نسخهٔ ناهمزمان و سریع‌تر. در code تک‌نخی (که اکثر اوقات است)، `StringBuilder` ترجیح داده می‌شود.

### `String.join` و `String.concat`

برای concat با delimiter، `String.join(delimiter, elements)` ساده‌تر از حلقه است:

```java
String s = String.join(", ", "java", "python", "go");  // "java, python, go"
String[] arr = {"a", "b", "c"};
String s2 = String.join("-", arr);                     // "a-b-c"
```

> **تلهٔ C++:** در C++ `s += piece` در همان `std::string` تغییر ایجاد می‌کند (in-place). در Java `s = s + piece` **همیشه** String جدید می‌سازد. اگر در حلقهٔ بزرگ هستید، باید StringBuilder بنویسید.

## ۶. `String.format` و printf-style

`String.format(template, args...)` الگوی C-style printf را برای String می‌سازد. placeholderها:

- `%s` — String
- `%d` — integer
- `%f` — float/double
- `%.2f` — دو رقم اعشار
- `%n` — newline (platform-independent، به‌جای `\n`)
- `%05d` — عرض ۵، با صفر پر شود

```java
String s = String.format("%s is %d years old", "Java", 27);
String t = String.format("%.2f", 3.14159);    // "3.14"
String u = String.format("%05d", 42);          // "00042"
```

برای چاپ به console بدون ساختن String، `System.out.printf(template, args...)` مستقیماً چاپ می‌کند.

> **تلهٔ C++:** در C++ `printf` varargs است و type-unsafe (اگر `%d` و `double` بدهید، UB). در Java `String.format` type-safe است و در صورت ناسازگاری type، `IllegalFormatConversionException` می‌دهد.

## ۷. text blocks (Java 15+)

text block یک literal چندخطی است که با `"""` شروع و تمام می‌شود:

```java
String json = """
        {
            "name": "java",
            "version": 21
        }
        """;
```

قواعد:

- delimiter شروع سه `"` پشت سر هم است که بلافاصله newline دارد.
- محتوا همان‌طور که نوشته شده، در String قرار می‌گیرد (به‌علاوهٔ indent management خودکار).
- `"""` در میان متن با `\`escape می‌شود: `\"\"\"`.
- line break در انتهای خط (قبل از newline بعدی) با `\` ادامه می‌یابد: `"""\` ادامه در خط بعد`.

text block در JSON، SQL، HTML template بسیار مفید است. برای indent مدیریت، خط اول و آخر indent یکسان معمولاً توصیه می‌شود.

> **تلهٔ C++:** در C++23 raw string literal (`R"(...)"`) نزدیک‌ترین معادل است، ولی Java text block escape rule متفاوت دارد (`\"""` نه `"""`).

## مثال‌های اجرایی و تحلیل

### مثال 1 — run id=g3-string-immutable

<!-- verify: run id=g3-string-immutable -->
```java
class StringImmutable {
    public static void main(String[] args) {
        String s = "java";
        String t = s.toUpperCase();
        System.out.println("s=" + s);
        System.out.println("t=" + t);
        System.out.println("same? " + (s == t));
    }
}
```

خروجی:
```text
s=java
t=JAVA
same? false
```

`toUpperCase` یک String جدید می‌سازد و s اصلی تغییر نمی‌کند.

### مثال 2 — run id=g3-pool-vs-new

<!-- verify: run id=g3-pool-vs-new -->
```java
class PoolVsNew {
    public static void main(String[] args) {
        String a = "hello";
        String b = "hello";
        String c = new String("hello");
        System.out.println("a==b: " + (a == b));
        System.out.println("a==c: " + (a == c));
        System.out.println("a==c.intern(): " + (a == c.intern()));
    }
}
```

خروجی:
```text
a==b: true
a==c: false
a==c.intern(): true
```

literalها shared هستند، `new String` نه، `intern()` را به pool برمی‌گرداند.

### مثال 3 — run id=g3-substring-bound

<!-- verify: run id=g3-substring-bound -->
```java
class SubstringBound {
    public static void main(String[] args) {
        String s = "Hello, World";
        System.out.println(s.substring(7));
        System.out.println(s.substring(0, 5));
        try {
            s.substring(20);
        } catch (StringIndexOutOfBoundsException e) {
            System.out.println("caught");
        }
    }
}
```

خروجی:
```text
World
Hello
caught
```

`substring(begin, end)` end را شامل نمی‌کند؛ خارج از محدوده exception می‌دهد.

### مثال 4 — run id=g3-replace-vs-replaceall

<!-- verify: run id=g3-replace-vs-replaceall -->
```java
class ReplaceVsReplaceAll {
    public static void main(String[] args) {
        String s = "1+2=3";
        System.out.println(s.replace("+", "-"));
        System.out.println(s.replaceAll("\\d", "N"));
    }
}
```

خروجی:
```text
1-2=3
N+N=N
```

`replace` literal است، `replaceAll` regex (در اینجا `\\d` = هر رقم).

### مثال 5 — run id=g3-split-trailing

<!-- verify: run id=g3-split-trailing -->
```java
class SplitTrailing {
    public static void main(String[] args) {
        String s = "a,b,,c,";             // یک کامای trailing اضافه
        String[] parts1 = s.split(",", 0);   // trailing empty حذف می‌شود
        String[] parts2 = s.split(",", -1);  // همه نگه داشته می‌شود
        System.out.println("default: " + parts1.length);
        System.out.println("explicit -1: " + parts2.length);
    }
}
```

خروجی:
```text
default: 4
explicit -1: 5
```

پیش‌فرض (`limit=0`) trailing empty را حذف می‌کند. `-1` همه را نگه می‌دارد.

### مثال 6 — run id=g3-stringbuilder-loop

<!-- verify: run id=g3-stringbuilder-loop -->
```java
class StringBuilderLoop {
    public static void main(String[] args) {
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= 5; i++) {
            sb.append(i).append(",");
        }
        sb.setLength(sb.length() - 1);   // حذف آخرین کاما
        System.out.println(sb);
    }
}
```

خروجی:
```text
1,2,3,4,5
```

`append` زنجیر می‌شود. `setLength` انتهای builder را کوتاه می‌کند.

### مثال 7 — run id=g3-string-format

<!-- verify: run id=g3-string-format -->
```java
class StringFormat {
    public static void main(String[] args) {
        String s1 = String.format("%s is %d", "Java", 21);
        String s2 = String.format("%.3f", Math.PI);
        String s3 = String.format("%05d", 7);
        System.out.println(s1);
        System.out.println(s2);
        System.out.println(s3);
    }
}
```

خروجی:
```text
Java is 21
3.142
00007
```

`%.3f` سه رقم اعشار، `%05d` عرض ۵ با صفر.

### مثال 8 — run id=g3-text-block

<!-- verify: run id=g3-text-block -->
```java
class TextBlock {
    public static void main(String[] args) {
        String json = """
                {
                  "lang": "java",
                  "version": 21
                }""";
        System.out.println(json);
    }
}
```

خروجی:
```text
{
  "lang": "java",
  "version": 21
}
```

text block بدون escape کاراکتر newline.
