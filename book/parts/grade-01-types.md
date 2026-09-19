# درجهٔ ۱ — نوع‌ها، مقدارها و `String` در Java 21

این بخش برای توسعه‌دهنده‌ای نوشته شده است که C++ را خوب می‌شناسد. قیاس با C++ فقط برای ساختن مدل ذهنی است: Java «C++ با garbage collector» نیست. در Java اندازهٔ نوع‌های primitive بخشی از تعریف زبان است، نه تصمیم ABI یا کامپایلر. بنابراین یک `int` روی همهٔ JVMهای سازگار دقیقاً ۳۲ بیت است.

---

## 1. تعریف دقیق نوع و دو خانوادهٔ مقدار

**نوع (type)** مجموعه‌ای از مقدارهای مجاز و عملیاتی است که compiler برای یک expression می‌پذیرد. نوع static هر expression در زمان کامپایل مشخص می‌شود؛ `var` آن را پویا نمی‌کند.

Java دو خانوادهٔ اصلی دارد:

1. **primitive**: مقدار مستقیماً در متغیر است؛ دقیقاً هشت نوع.
2. **reference**: متغیر یا به یک شیء/آرایه اشاره می‌کند یا مقدار `null` دارد.

```text
int count = 7;                       String title = "Java";

count                                title
┌─────────┐                          ┌──────────────┐
│    7    │                          │ reference ───┼──► String object
└─────────┘                          └──────────────┘    ┌────────┐
                                                           │ "Java" │
                                                           └────────┘
```

نمودار، مدل منطقی است؛ Java آدرس حافظه، اندازهٔ reference یا محل فیزیکی شیء را قرارداد زبان نمی‌داند.

**مثال 1 — کپی primitive مستقل است**

```java
int first = 10;
int second = first;
second++;

System.out.println(first);  // 10
System.out.println(second); // 11
```

**مثال 2 — کپی reference شیء را کپی نمی‌کند**

```java
StringBuilder left = new StringBuilder("A");
StringBuilder right = left;
right.append("B");

System.out.println(left);           // AB
System.out.println(left == right);  // true
```

**تصحیح برداشت نادرست:** «reference همان pointer در C++ است.»

هر دو می‌توانند راه رسیدن به شیء باشند، اما Java pointer arithmetic، dereference با `*`، `delete` و تبدیل آزاد reference به عدد ندارد. `null` نیز مقدار ویژهٔ reference است، نه آدرسی برای انجام محاسبه.

---

## 2. هشت primitive با اندازه و بازهٔ ثابت

| Java | بیت | بازه/مقدار | قیاس دقیق C++ | نکته |
|---|---:|---|---|---|
| `boolean` | representation مشخص نیست | `true`، `false` | `bool`، نه لزوماً representation یکسان | عدد نیست |
| `byte` | 8 | -128 تا 127 | `std::int8_t` | signed |
| `short` | 16 | -32,768 تا 32,767 | `std::int16_t` | signed |
| `char` | 16 | 0 تا 65,535 | `char16_t` | UTF-16 code unit، unsigned |
| `int` | 32 | -2³¹ تا 2³¹-1 | `std::int32_t` | literal صحیح معمولاً این نوع است |
| `long` | 64 | -2⁶³ تا 2⁶³-1 | `std::int64_t` | suffix `L` لازم است |
| `float` | 32 | IEEE 754 binary32 | `float` رایج C++ | suffix `F` |
| `double` | 64 | IEEE 754 binary64 | `double` رایج C++ | literal اعشاری پیش‌فرض |

`int`، `long` و `char` خام C++ را با نام‌های همسان Java یکی نگیرید؛ در C++ اندازه و signedness آن‌ها implementation-defined است. `std::int32_t` و هم‌خانواده‌هایش مقایسهٔ درست‌تری هستند.

### `boolean`

**مثال 3 — شرط، عدد نمی‌پذیرد**

```java
boolean enabled = true;
int retries = 1;

if (enabled) {
    System.out.println("فعال");
}
// if (retries) { } // خطای کامپایل: int، boolean نیست
```

در C/C++ صفر و غیرصفر در شرط تبدیل می‌شوند؛ Java چنین تبدیل ضمنی‌ای ندارد.

### integerهای signed و overflow

`byte`، `short`، `int` و `long` اندازهٔ ثابت دارند. overflow integer exception نمی‌دهد و نتیجه modulo 2ⁿ wrap می‌شود.

**مثال 4 — مرز `int`**

```java
int max = Integer.MAX_VALUE;
int wrapped = max + 1;

System.out.println(max);     // 2147483647
System.out.println(wrapped); // -2147483648
```

این با signed overflow در C++ که می‌تواند undefined behavior باشد متفاوت است. اگر overflow خطای domain است، آن را نادیده نگیرید.

**مثال 5 — arithmetic بررسی‌شده**

```java
int price = 2_000_000_000;
int tax = 500_000_000;

int total = Math.addExact(price, tax); // ArithmeticException
```

`Math.addExact`، `subtractExact`، `multiplyExact` و `toIntExact` در صورت خروج نتیجه از بازه exception می‌دهند.

**مثال 6 — تقسیم integer بر صفر**

```java
int count = 9;
int divisor = 0;
// System.out.println(count / divisor); // ArithmeticException: / by zero
```

این را با floating-point اشتباه نگیرید؛ `1.0 / 0.0` برابر `Infinity` است.

### `char` و Unicode

`char` یک واحد ۱۶بیتی UTF-16 است، نه تضمین یک نویسهٔ انسانی یا حتی یک Unicode code point. بسیاری از emojiها از دو `char` (surrogate pair) تشکیل می‌شوند.

**مثال 7 — `char` عددی هم هست**

```java
char latin = 'A';
char persian = 'ش';

System.out.println((int) latin);   // 65
System.out.println((int) persian); // 1588
System.out.println('A' + 1);       // 66، نتیجه int است
```

**مثال 8 — یک emoji، دو code unit**

```java
String rocket = "🚀";

System.out.println(rocket.length()); // 2
System.out.println(rocket.codePointCount(0, rocket.length())); // 1
System.out.println(Integer.toHexString(rocket.charAt(0))); // d83d
```

`String.length()` تعداد UTF-16 code unit را می‌دهد، نه تعداد حرف‌های قابل مشاهده. برای code pointها از `codePoints()`، `codePointCount` و APIهای مرتبط استفاده کنید؛ حتی code point هم لزوماً یک grapheme cluster قابل‌دیدن نیست.

**مثال 9 — escapeهای `char`**

```java
char quote = '\'';
char slash = '\\';
char tab = '\t';
char alef = 'ا';

System.out.println(alef); // ا
```

Unicode escape پیش از tokenization پردازش می‌شود. برای متن عادی، source UTF-8 و literal خوانا غالباً مناسب‌تر از escapeهای فراوان است.

### `float` و `double`

این نوع‌ها تقریبی و دودویی‌اند؛ برای پول معمولاً از کوچک‌ترین واحد integer یا `BigDecimal` (اغلب با ورودی رشته‌ای) استفاده کنید.

**مثال 10 — ۰٫۱ نمایش دودویی دقیق ندارد**

```java
double value = 0.1 + 0.2;
System.out.println(value);        // 0.30000000000000004
System.out.println(value == 0.3); // false
```

**مثال 11 — Infinity و NaN**

```java
double infinity = 1.0 / 0.0;
double invalid = 0.0 / 0.0;

System.out.println(infinity);       // Infinity
System.out.println(invalid);        // NaN
System.out.println(invalid == invalid); // false
System.out.println(Double.isNaN(invalid)); // true
```

**تصحیح برداشت نادرست:** «`boolean` همان ۰ و ۱ است» و «همهٔ تقسیم‌ها بر صفر exception می‌دهند.» در Java، `boolean` عدد نیست؛ فقط تقسیم integer بر صفر exception می‌دهد، ولی floating-point مطابق IEEE 754 رفتار می‌کند.

---

## 3. literalها، suffixها و مرزهای عددی

| نوشتار | نوع/معنا |
|---|---|
| `42` | `int` |
| `42L` | `long`؛ `L` بزرگ بنویسید |
| `3.14` | `double` |
| `3.14F` | `float` |
| `0b1010` | integer دودویی |
| `0xFF` | integer شانزده‌هشتی |
| `072` | integer هشتی |
| `1_000_000` | همان مقدار، با separator خوانایی |
| `'x'` | `char` |
| `"x"` | `String` |

**مثال 12 — suffix برای `long` و `float`**

```java
long population = 8_100_000_000L;
float ratio = 0.75F;
double standard = 0.75;

// long bad = 8_100_000_000; // literal خارج از int است
// float alsoBad = 0.75;     // double به float تبدیل ضمنی نمی‌شود
```

**مثال 13 — baseها و separatorها**

```java
int binary = 0b1010_0110;
int hexadecimal = 0xCAFE_BABE;
int octal = 072;

System.out.println(binary);      // 166
System.out.println(hexadecimal); // -889275714
System.out.println(octal);       // 58
```

`0xCAFE_BABE` به صورت `int` منفی است، زیرا bit علامت آن یک است. برای مقدار مثبت ۳۲بیتی unsigned، `long` با `L` یا APIهای unsigned را آگاهانه به کار ببرید.

**مثال 14 — constant expression در assignment باریک**

```java
byte accepted = 100;
final int constant = 100;
byte acceptedAgain = constant;

int variable = 100;
// byte rejected = variable; // خطای کامپایل
```

constant expression از نوع `int` که در بازهٔ مقصد باشد می‌تواند به `byte`، `short` یا `char` assign شود؛ متغیر `int` عادی چنین امتیازی ندارد.

**مثال 15 — cast validation نیست**

```java
int source = 130;
byte narrowed = (byte) source;
System.out.println(narrowed); // -126
```

cast باریک‌کننده bitهای بالاتر را حذف می‌کند؛ بررسی range انجام نمی‌دهد.

**تصحیح برداشت نادرست:** «هر literal صحیحِ بزرگ خودکار `long` است.» نادرست است. literal صحیح معمولی `int` است و برای `long` باید `L` بدهید. `l` کوچک قانونی اما با `1` اشتباه‌پذیر است.

---

## 4. promotion و تبدیل‌ها

تبدیل widening، مانند `byte → int → long → float → double`، معمولاً ضمنی است. narrowing به cast نیاز دارد و ممکن است مقدار یا دقت را تغییر دهد. `byte`، `short` و `char` در بیشتر عملیات arithmetic ابتدا به `int` promote می‌شوند.

**مثال 16 — جمع دو `byte`، `int` است**

```java
byte a = 20;
byte b = 30;

// byte sum = a + b; // خطا: int به byte تبدیل نمی‌شود
byte sum = (byte) (a + b);
System.out.println(sum); // 50
```

**مثال 17 — `+=` cast ضمنی دارد**

```java
byte score = 10;
score += 120;
System.out.println(score); // -126

// score = score + 120; // خطا
```

`score += 120` تقریباً `score = (byte) (score + 120)` است، ولی left side را فقط یک‌بار evaluate می‌کند. این syntax جلوی overflow را نمی‌گیرد.

**مثال 18 — `char` نیز به `int` promote می‌شود**

```java
char letter = 'A';
int nextCode = letter + 1;
char nextLetter = (char) (letter + 1);

System.out.println(nextCode);   // 66
System.out.println(nextLetter); // B
```

---

## 5. reference type، wrapper و `null`

class، interface، array، enum، record و annotation همگی reference type هستند. primitive نمی‌تواند `null` باشد؛ reference می‌تواند.

| primitive | wrapper |
|---|---|
| `boolean` | `Boolean` |
| `byte` | `Byte` |
| `short` | `Short` |
| `char` | `Character` |
| `int` | `Integer` |
| `long` | `Long` |
| `float` | `Float` |
| `double` | `Double` |

wrapper شیء است: method دارد، در genericها استفاده می‌شود و ممکن است `null` باشد.

**مثال 19 — generic با wrapper**

```java
import java.util.ArrayList;
import java.util.List;

List<Integer> ids = new ArrayList<>();
ids.add(7);          // boxing: int → Integer
int id = ids.get(0); // unboxing: Integer → int
```

`List<int>` قانونی نیست؛ genericهای عادی Java reference type می‌گیرند.

**مثال 20 — unboxing از `null`**

```java
Integer possibleCount = null;

// int count = possibleCount; // NullPointerException در runtime
int safeCount = possibleCount != null ? possibleCount : 0;
System.out.println(safeCount);
```

compiler برای unboxing عملاً `possibleCount.intValue()` لازم دارد. پس خطای ظاهراً سادهٔ assignment، `NullPointerException` است.

**مثال 21 — `==` با wrapper**

```java
Integer smallA = 100;
Integer smallB = 100;
Integer largeA = 1_000;
Integer largeB = 1_000;

System.out.println(smallA == smallB); // ممکن است true؛ تکیه نکنید
System.out.println(largeA == largeB); // معمولاً false
System.out.println(largeA.equals(largeB)); // true
```

`==` میان دو reference identity را می‌سنجد، نه مقدار را. boxing cache ممکن است برای بعضی مقدارها یک شیء مشترک بدهد؛ این قرارداد مقایسهٔ ارزشی نیست.

**مثال 22 — equality امن در حضور `null`**

```java
import java.util.Objects;

Integer expected = 42;
Integer actual = null;

System.out.println(Objects.equals(expected, actual)); // false
System.out.println(Objects.equals(null, null));       // true
// actual.equals(expected); // NullPointerException
```

**تصحیح برداشت نادرست:** «boxing فقط syntax sugar است، پس `null` یا identity اثر ندارد.» wrapper یک شیء واقعی است: می‌تواند `null` باشد و identity مستقل داشته باشد. برای مقدار wrapperها از `equals`، `Objects.equals` یا با احتیاط unboxing کنترل‌شده استفاده کنید.

---

## 6. local variable، field و definite assignment

قانون کلیدی OCP: **fieldها و elementهای array مقدار پیش‌فرض دارند؛ local variableها باید پیش از خواندن definitely assigned باشند.**

| محل declaration | مقدار پیش‌فرض خودکار |
|---|---|
| instance field و `static` field | بله |
| element آرایه | بله |
| local variable | خیر |
| parameter | caller مقدار می‌دهد |

مقدار پیش‌فرض field/array: integerها `0`، floating-pointها `0.0`، `char` برابر `\u0000`، `boolean` برابر `false` و reference برابر `null` است.

**مثال 23 — fieldهای مقداردهی‌نشده**

```java
class Meter {
    int distance;
    boolean calibrated;
    String label;

    void print() {
        System.out.println(distance);   // 0
        System.out.println(calibrated); // false
        System.out.println(label);      // null
    }
}
```

**مثال 24 — local باید روی همهٔ مسیرها مقدار بگیرد**

```java
void show(boolean useDefault) {
    int result;
    if (useDefault) {
        result = 10;
    }
    // System.out.println(result); // خطای کامپایل
}
```

**مثال 25 — دو شاخه، definite assignment را برقرار می‌کنند**

```java
void show(boolean useDefault) {
    int result;
    if (useDefault) {
        result = 10;
    } else {
        result = 20;
    }
    System.out.println(result); // معتبر
}
```

**مثال 26 — array element در برابر local reference**

```java
int[] readings = new int[3];
System.out.println(readings[0]); // 0

String title;
// System.out.println(title); // خطای کامپایل
```

**تصحیح برداشت نادرست:** «Java همهٔ متغیرها را zero-initialize می‌کند.» این فقط برای fieldها و elementهای array درست است، نه local variableها.

---

## 7. `var`: استنتاج محلی، نه dynamic typing

`var` فقط برای local variable دارای initializer است. compiler از initializer یک نوع static مشخص نتیجه می‌گیرد.

**مثال 27 — نوع `var` ثابت است**

```java
var message = "سلام"; // String
var attempts = 3;      // int
var rate = 1.5;        // double

// attempts = "سه"; // خطا: attempts از ابتدا int است
```

**مثال 28 — جایگاه‌های ممنوع `var`**

```java
class VarRules {
    // var field = 1;       // field نمی‌تواند var باشد
    void process() {
        // var unknown;    // initializer لازم است
        // var nothing = null; // null به تنهایی نوع را معلوم نمی‌کند
        var names = java.util.List.of("Ada", "Linus");
        System.out.println(names);
    }
    // void save(var value) { } // parameter معمولی مجاز نیست
}
```

از `var` وقتی استفاده کنید که initializer و نام متغیر، نوع را روشن می‌کنند. این واژه به معنی «هر نوعی در runtime» نیست.

---

## 8. scope و shadowing

scope محدوده‌ای از source است که یک نام در آن دیده می‌شود؛ lifetime زمان وجود runtime یک مقدار/شیء است. این دو یکی نیستند.

**مثال 29 — scope block**

```java
void inspect() {
    int outer = 1;
    if (outer > 0) {
        int inner = 2;
        System.out.println(outer + inner); // 3
    }
    // System.out.println(inner); // خارج از scope
}
```

**مثال 30 — parameter یک field را shadow می‌کند**

```java
class Account {
    private String owner;

    Account(String owner) {
        this.owner = owner;
    }

    void rename(String owner) {
        this.owner = owner;
    }
}
```

`owner` ساده، parameter است؛ `this.owner` field شیء جاری را مشخص می‌کند.

**مثال 31 — local فعال بیرونی را دوباره declare نکنید**

```java
void invalidRedeclaration() {
    int level = 1;
    // if (true) {
    //     int level = 2; // خطای کامپایل
    // }
    System.out.println(level);
}
```

**تصحیح برداشت نادرست:** «مثل C++، block داخلی همیشه می‌تواند local هم‌نام بسازد.» در Java local فعال بیرونی را نمی‌توان با local جدید در block داخلی shadow کرد؛ اما parameter یا local می‌تواند field را shadow کند.

---

## 9. `String`: immutable، pool و equality

`String` primitive نیست، بلکه reference type immutable است. عملیات متنی، متن موجود را mutate نمی‌کنند؛ نتیجه‌ای برمی‌گردانند که باید آن را استفاده کنید.

**مثال 32 — نتیجهٔ `concat` را بگیرید**

```java
String greeting = "سلام";
greeting.concat(" دنیا");
System.out.println(greeting); // سلام

greeting = greeting.concat(" دنیا");
System.out.println(greeting); // سلام دنیا
```

**مثال 33 — identity و محتوای String**

```java
String first = new String("java");
String second = new String("java");

System.out.println(first == second);      // false
System.out.println(first.equals(second)); // true
```

`==` برای reference هویت را می‌سنجد؛ `equals` برای `String` محتوا را.

### pool و `intern()`

literalهای string و constant expressionهای string می‌توانند نمایندهٔ canonical مشترک در pool داشته باشند. این بهینه‌سازی است، نه دلیل استفاده از `==` برای متن.

```text
String a = "book";            String b = new String("book");
         │                               │
         └────────► pooled "book"        └──► شیء جدا با همان محتوا
```

**مثال 34 — literal و `new String`**

```java
String pooledA = "book";
String pooledB = "book";
String separate = new String("book");

System.out.println(pooledA == pooledB);       // true در این مورد
System.out.println(pooledA == separate);      // false
System.out.println(pooledA.equals(separate)); // true
```

**مثال 35 — concatenation compile-time و runtime**

```java
String compileTime = "Ja" + "va";
String literal = "Java";
String part = "Ja";
String runtime = part + "va";

System.out.println(compileTime == literal); // true
System.out.println(runtime == literal);     // false
System.out.println(runtime.equals(literal)); // true
```

وقتی همهٔ operandها constant expression باشند، compiler نتیجه را در compile time می‌سازد. وجود یک مقدار runtime، concatenation را runtime می‌کند. `final String part = "Ja";` می‌تواند constant expression باشد، ولی local غیرfinal بالا نیست.

**مثال 36 — `intern()` برای canonicalization خاص**

```java
String built = new StringBuilder().append("Ja").append("va").toString();
String literal = "Java";

System.out.println(built == literal);          // false
System.out.println(built.intern() == literal); // true
```

برای equality معمولی از `equals` استفاده کنید؛ `intern()` را فقط با نیاز روشن به canonicalization به کار ببرید.

### `equals` و `hashCode`

قرارداد عمومی Java: اگر `a.equals(b)` درست باشد، باید `a.hashCode() == b.hashCode()` هم درست باشد. عکس آن لازم نیست؛ collision ممکن است. `HashMap` و `HashSet` برای یافتن bucket از `hashCode` و برای تشخیص کلید برابر از `equals` بهره می‌برند.

**مثال 37 — `HashMap` کلید معادل را می‌شناسد**

```java
import java.util.HashMap;
import java.util.Map;

Map<String, Integer> scores = new HashMap<>();
scores.put(new String("OCP"), 100);
System.out.println(scores.get("OCP")); // 100
```

**مثال 38 — immutable بودن شیء، reassignment reference را منع نمی‌کند**

```java
String city = "Tehran";
city = city.toUpperCase();
System.out.println(city); // TEHRAN
```

شیء `"Tehran"` تغییر نکرده است؛ متغیر `city` به نتیجهٔ جدید اشاره می‌کند.

**تصحیح برداشت نادرست:** «اگر دو String literal با `==` برابرند، `==` راه درست مقایسهٔ String است.» فقط identity خاص آن نمونه را دیده‌اید. کد runtime، `new String`، ورودی کاربر و concatenation می‌توانند شیء دیگری با همان محتوا بسازند. برای محتوا `equals` یا `Objects.equals` بنویسید.

---

## ۱۰. `final`: ثابت بودن reference، نه لزوماً شیء

`final` روی variable یعنی آن variable پس از assignment نخست دیگر قابل **بازانتساب** نیست. این modifier، object مقصد را immutable نمی‌کند. برای primitive، نتیجه در عمل ثابت ماندن value است؛ برای reference، فقط فلشِ reference ثابت می‌ماند.

```text
final StringBuilder log = new StringBuilder("A");

log ───> StringBuilder { "A" }
          │
          └── append("B") مجاز: حالت object تغییر می‌کند

log = new StringBuilder("C");  // غیرمجاز: فلش log نباید عوض شود
```

### مثال ۳۹ — reference نهایی، object mutable

```java
public class FinalReference {
    public static void main(String[] args) {
        final StringBuilder message = new StringBuilder("start");
        message.append(" + changed");
        // message = new StringBuilder("replacement"); // خطای compile-time
        System.out.println(message);
    }
}
```

خروجی `start + changed` است. `final` بودن `message` جلوی `append` را نمی‌گیرد، چون `append` به همان object می‌رسد. فقط assignment دوباره به variable ممنوع است.

### مثال ۴۰ — `final` parameter همان قرارداد بازانتساب را دارد

```java
class Ticket {
    String status = "open";
}

public class FinalParameter {
    static void close(final Ticket ticket) {
        ticket.status = "closed";
        // ticket = new Ticket(); // خطای compile-time
    }

    public static void main(String[] args) {
        Ticket item = new Ticket();
        close(item);
        System.out.println(item.status);
    }
}
```

خروجی `closed` است. `final` parameter برای caller ownership جدیدی نمی‌سازد و pass-by-value را تغییر نمی‌دهد؛ فقط implementation متد نمی‌تواند copy محلیِ reference را بازانتساب کند.

### مثال ۴۱ — `final` local باید حتماً یک‌بار مقدار بگیرد

```java
public class FinalLocal {
    public static void main(String[] args) {
        final int port;
        if (args.length == 0) {
            port = 8080;
        } else {
            port = Integer.parseInt(args[0]);
        }
        System.out.println(port);
        // port = 9090; // خطای compile-time
    }
}
```

این نمونه هم‌زمان قانون definite assignment را نشان می‌دهد: compiler می‌بیند تمام مسیرهای ممکن پیش از read به `port` مقدار می‌دهند، و نیز تضمین می‌کند هیچ مسیر دومی آن را assign نکند.

برای immutable design، `final` reference را با immutable class ترکیب کنید. مثلاً `final String name` هم reference را ثابت می‌کند و هم object String قابل mutation نیست. در مقابل `final List<String>` فقط reference لیست را ثابت می‌کند؛ محتوای لیست همچنان ممکن است تغییر کند.

---

## دام‌های پرتکرار OCP

1. `char` یک code unit است، نه الزاماً یک emoji یا یک حرف قابل‌دیدن.
2. literal اعشاری `double` است؛ برای `float` از `F` استفاده کنید.
3. integer overflow به‌طور پیش‌فرض exception نمی‌دهد.
4. `byte + byte` از نوع `int` است.
5. cast narrowing، بررسی range نیست.
6. `Integer` ممکن است `null` باشد و unboxing آن NPE بدهد.
7. `==` برای reference identity می‌سنجد؛ `equals` ارزش/محتوا را.
8. field پیش‌فرض دارد، local variable ندارد.
9. `var` نوع استنتاج‌شدهٔ ثابت دارد و field نیست.
10. `String` immutable است، ولی reference آن قابل reassignment است.

---

## تمرین‌ها

1. بازهٔ دقیق `byte` و `short` را بنویسید و معادل fixed-width C++ هر یک را مشخص کنید.
2. خروجی `Integer.MAX_VALUE + 1` را پیش‌بینی کنید و توضیح دهید چرا C++ signed overflow قیاس کاملی نیست.
3. با `Math.multiplyExact` مثالی بسازید که exception بدهد.
4. تفاوت نتیجهٔ `5 / 0` و `5.0 / 0.0` را توضیح دهید.
5. رشتهٔ شامل `🚀` بسازید؛ `length()` و `codePointCount` آن را چاپ و تفاوت را تفسیر کنید.
6. سه literal بنویسید: یک `long` بزرگ، یک `float` و یک integer binary با separator.
7. چرا `byte x = 127; x++;` کامپایل می‌شود ولی `byte y = x + 1;` نه؟
8. مقدار `(byte) 258` را پیش‌بینی و سپس اجرا کنید.
9. `List<Integer>` بسازید و سناریویی طراحی کنید که unboxing از `null` رخ دهد؛ آن را امن کنید.
10. با دو `Integer` هم‌مقدار بزرگ، تفاوت `==` و `equals` را نمایش دهید.
11. classی با fieldهای `int`، `boolean`، `char` و `String` بسازید و مقدارهای پیش‌فرض را چاپ کنید.
12. methodی بنویسید که local variable آن فقط در یک branch مقدار می‌گیرد؛ خطای definite assignment را اصلاح کنید.
13. سه declaration نامعتبر `var` و یک declaration معتبر بنویسید؛ علت هرکدام را شرح دهید.
14. fieldی را با parameter shadow کنید و با `this` assignment درست را انجام دهید.
15. تفاوت `"ab" + "cd"` و `part + "cd"` را با `==` و `equals` آزمایش کنید.
16. سه `String` با literal، `new String` و `StringBuilder` بسازید؛ برای هر زوج identity و content equality را بررسی کنید.
17. یک `HashMap<String, Integer>` بسازید که کلید هنگام `put` با `new String` و هنگام `get` literal باشد؛ علت موفقیت را با `hashCode`/`equals` بیان کنید.
18. برای مبلغ ۰٫۱ + ۰٫۲، راهکار integer کوچک‌ترین واحد یا `BigDecimal` را پیاده‌سازی و دلیل انتخاب را بنویسید.

---

## واژه‌نامه

| اصطلاح | معنی عملی |
|---|---|
| **primitive** | نوع مقداری پایهٔ Java؛ یکی از هشت نوع مشخص زبان |
| **reference type** | نوعی که متغیر آن شیء، آرایه یا `null` را نمایندگی می‌کند |
| **wrapper** | class شیء متناظر primitive، مانند `Integer` برای `int` |
| **boxing** | تبدیل primitive به wrapper |
| **unboxing** | تبدیل wrapper به primitive؛ `null` در این مسیر NPE می‌دهد |
| **definite assignment** | اثبات compiler که local پیش از خواندن مقدار گرفته است |
| **widening conversion** | تبدیل به نوع گسترده‌تر، معمولاً ضمنی |
| **narrowing conversion** | تبدیل به نوع محدودتر با cast و احتمال تغییر مقدار |
| **overflow** | خروج نتیجه از بازهٔ integer؛ در Java wrap modulo رخ می‌دهد |
| **code unit** | واحد ذخیره‌سازی UTF-16؛ همان چیزی که `char` نگه می‌دارد |
| **code point** | شناسهٔ یک عنصر Unicode؛ ممکن است دو code unit بخواهد |
| **scope** | ناحیهٔ source که در آن یک نام قابل استفاده است |
| **shadowing** | پوشاندن نام field/outer declaration با declaration نزدیک‌تر |
| **string pool** | محل canonicalization literalها و constant stringها |
| **interning** | دریافت/ثبت نمایندهٔ canonical یک String با `intern()` |
| **identity** | یکی بودن خودِ شیء؛ با `==` برای reference سنجیده می‌شود |
| **value equality** | برابر بودن محتوا/ارزش؛ برای `String` با `equals` |
| **hashCode contract** | برابری `equals` مستلزم برابری hash code است |
| **immutability** | پس از ساختن شیء، حالت قابل مشاهدهٔ آن تغییر نمی‌کند |
| **constant expression** | expression قابل محاسبه در compile time طبق قواعد زبان |

---

## نقشهٔ ترمیم برای مفهوم‌های آزمون

در آزمون‌های OCP، گزینهٔ گمراه‌کننده معمولاً از یک قانون درست در بافت اشتباه ساخته می‌شود. از این نقشه پس از هر پاسخ غلط استفاده کنید: نخست نوع expression را بنویسید، سپس زمان خطا را مشخص کنید، و فقط بعد نتیجه را پیش‌بینی کنید.

| اگر در quiz این نشانه را دیدید | مفهوم اصلی | خطای محتمل | روش ترمیم کوتاه | نمونه‌های این فصل |
|---|---|---|---|---|
| دو نام object-type و یک mutation | aliasing و assignment reference | تصور object-copy در `b = a` | دو فلش به یک object رسم کنید؛ سپس mutation و reassignment را جداگانه اجرا کنید | ۲، ۳، ۴، ۵ |
| method parameter object را بازانتساب می‌کند | pass-by-value | انتظار تغییر variable در caller | parameter را یک local copy از reference فرض کنید | ۴ |
| `null` کنار method call یا `&&` | null و evaluation order | null-check را پس از dereference گذاشتن | شرط non-null را operand چپ `&&` بگذارید | ۶، ۷، ۸ |
| عدد نزدیک حد type یا cast | range، promotion، narrowing | cast را validation دانستن | نوع هر operand و بازهٔ مقصد را پیش از محاسبه بنویسید | ۹، ۱۰، ۱۱، ۱۷، ۱۸ |
| `byte + byte`، `char + 1` یا `+=` | numeric promotion | انتظار type کوچک در expression | expression را ابتدا `int` فرض کنید؛ استثنای `+=` را جدا حفظ کنید | ۱۱، ۱۶ تا ۱۸ |
| `L`، `F`، binary/octal/hex و underscore | literal syntax | فرض نوع خودکار `long` یا `float` | suffix و base را قبل از assignment تشخیص دهید | ۱۵، ۱۶، ۱۷ |
| `Integer`/`Double` به جای primitive | boxing و unboxing | نادیده گرفتن `null` یا identity | مشخص کنید conversion implicit کجاست و آیا reference ممکن است null باشد | ۲۰ تا ۲۳ |
| `==` میان `Integer` یا `String` | identity در برابر value equality | اعتماد به cache یا pool | برای content/value از `equals` یا `Objects.equals` استفاده کنید | ۲۱، ۲۲، ۳۳ تا ۳۷ |
| literal String، `new String`، concat یا `intern()` | String pool و immutability | تعمیم یک `== true` تصادفی | مسیر ساخت رشته را بررسی و فقط `equals` را معیار محتوا بگیرید | ۳۲ تا ۳۸ |
| local بدون initializer یا branch ناقص | definite assignment | تعمیم default field به local | تمام مسیرهای control flow تا محل read را trace کنید | ۲۳ تا ۲۶ |
| `var` در field/parameter یا با `null` | local type inference | dynamic type پنداشتن `var` | محل declaration و initializer را بررسی کنید؛ نوع inferred را صریح بنویسید | ۲۷، ۲۸ |
| نام field و parameter/local یکسان | scope و shadowing | assignment به parameter به جای field | declaration نزدیک‌تر را پیدا کنید و برای field از `this.` استفاده کنید | ۲۹ تا ۳۱ |

### روال پنج‌مرحله‌ای حل سؤال

1. **نوع‌ها را annotate کنید.** کنار هر literal، variable و expression بنویسید `int`، `Integer`، `String` یا نوع واقعی دیگر.
2. **مرز compile-time/runtime را تعیین کنید.** assignment نامعتبر، local مقداردهی‌نشده و `var` نامعتبر compile نمی‌شوند؛ unboxing null و dereference null runtime failure هستند.
3. **برای referenceها نمودار alias رسم کنید.** هر `new` object تازه است؛ هر assignment reference یک فلش کپی می‌کند.
4. **ترتیب evaluation را اجرا کنید.** به‌خصوص در `&&`، cast، arithmetic و argumentها، نتیجه را از چپ به راست بسازید.
5. **پس از پاسخ، گزینهٔ غلط را توضیح دهید.** اگر نتوانید بگویید چرا گزینهٔ دیگر غلط است، قانون را هنوز به‌صورت حفظی می‌دانید.

### مینی‌آزمون ترمیمی

پیش از دیدن پاسخ، برای هر مورد بگویید: compile-time error، runtime exception یا خروجی؟

```java
// A
Integer n = null;
// System.out.println(n + 1);

// B
String x = "ocp";
String y = new String("ocp");
System.out.println(x == y);

// C
byte b = 127;
b += 1;
System.out.println(b);

// D
int score;
if (args.length > 0) score = 10;
// System.out.println(score);
```

پاسخ: A در صورت uncomment شدن `NullPointerException` از unboxing دارد؛ B مقدار `false` می‌چاپد، چون identity متفاوت است؛ C مقدار `-128` می‌چاپد؛ D در صورت uncomment شدن خطای definite assignment در compile-time است. اگر A، B، C و D را اشتباه پاسخ داده‌اید، به‌ترتیب بخش‌های wrapper/null، String equality، promotion/narrowing و local/default value را دوباره بخوانید.
