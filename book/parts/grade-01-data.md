# درجهٔ ۱: داده‌ها، هویت و متن در Java 21

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
| instance field | `0`، `0.0`، `false`، ` ` یا `null` |
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
