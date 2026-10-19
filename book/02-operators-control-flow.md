# فصل ۲ — عملگرها و جریان کنترل

> **مسیر:** Java 21 / Operators and Control Flow  
> **مخاطب:** برنامه‌نویس C++ که می‌خواهد مقدار، نوع و مسیر اجرای Java را پیش از اجرا پیش‌بینی کند.

این فصل متن آموزشی مستقل است: توضیح‌ها، مثال‌ها و تمرین‌ها برای همین مسیر نوشته شده‌اند و بازتولید متن تجاری نیستند.
نحو Java به C++ نزدیک دیده می‌شود، اما در عملگرها و کنترل جریان، شباهت نشانه‌ها جایگزین قواعد type، promotion، evaluation order و scope نمی‌شود.

## نقشهٔ یادگیری و خروجی مورد انتظار

پس از این فصل باید بتوانید:

1. نوع نتیجهٔ expressionهای عددی را، به‌ویژه برای `byte`، `short` و `char`، پیش‌بینی کنید؛
2. widening، narrowing، cast، truncation و overflow را از هم جدا کنید؛
3. نتیجهٔ `/`، `%`، bitwise و هر سه shift را روی کاغذ محاسبه کنید؛
4. میان short-circuit و eager evaluation، و میان equality مقدار و identity فرق بگذارید؛
5. `if`، ternary، switch statement و switch expression را با دلیل انتخاب کنید؛
6. `for`، enhanced-for، `while`، `do-while` و loop بی‌نهایت را با invariant بخوانید؛
7. label، scope و definite assignment را پیش از رسیدن به compiler تشخیص دهید.

### قرارداد خواندن این فصل

- **قاعدهٔ زبان:** نتیجهٔ قابل مشاهده‌ای که Java 21 برای برنامه تعیین می‌کند، نه حدس یک IDE یا رفتار اتفاقی یک JVM.
- **نشانگر بررسی:** هر بلوک Java با `<!-- verify: run id=... -->`، `<!-- verify: compile-fail id=... -->` یا `<!-- verify: skip id=... -->` مشخص است. `python3 tools/verify_examples.py --chapter 2` مثال‌های `run` را compile/run و خروجی مجاور را مقایسه می‌کند، برای `compile-fail` شکست کامپایل را لازم می‌داند و `skip` را گزارش می‌کند.
- **ترمیم:** هر جا reflex رایج C++ یا shortcut ذهنی ممکن است bug بسازد، تلهٔ C++ و برداشت نادرست صریح آمده است.

---

## 1. numeric promotion

Java پیش از هر عملگر دودویی حسابی (`+`، `-`، `*`، `/`، `%`، رابطه‌ای روی عدد، و حتی برخی موارد مثل مقایسهٔ ترکیبی) قاعده‌ای به نام **binary numeric promotion** را اجرا می‌کند: اگر هر کدام از operandها از نوع `double` باشد، همه به `double` تبدیل می‌شوند؛ وگرنه اگر `float` باشد، به `float`؛ وگرنه اگر `long` باشد، به `long`؛ وگرنه هر دو به `int` ارتقا می‌یابند. این قاعده به مقدار فعلی variable نگاه نمی‌کند؛ به **type اعلام‌شده** نگاه می‌کند. در نتیجه `byte a = 40; byte b = 2;` و `a + b` حتی وقتی هر دو در دامنهٔ `byte` جا می‌گیرند، یک `int` می‌سازد. unary `+`، `-` و `~` نیز همین قاعده را دارند: `~b` روی `byte` یک `int` می‌دهد.

این رفتار دلیل تاریخی دارد: در JVM عملگرهای حسابی integral، نوع `int` و `long` را می‌شناسند و نوع کوچک‌تر ندارند؛ promotion در سطح زبان انجام می‌شود تا bytecode ساده بماند. نتیجهٔ عملی این است که اگر نتیجه را به variable کوچک‌تر انتساب می‌دهید، cast لازم دارید:

```java
byte a = 40, b = 2;
byte sum = (byte) (a + b);   // a + b یک int است؛ cast صریح لازم است
int natural = a + b;          // بدون cast، در int جا می‌گیرد
```

اگر مقدار در دامنه نباشد، cast همان `int` بیت‌به‌بیت را low-byte می‌کند و signed-interpret می‌خواند — همان low-bit-preserving narrowing که در §۲ می‌بینید. promotion با **conversion** متفاوت است: conversion در assignment رخ می‌دهد، promotion در expression؛ هر دو از یک جدول widening پیروی می‌کنند اما promotion هرگز نمی‌تواند lossy باشد (پس cast نمی‌خواهد).

```text
byte ─┐
short ─┼── binary numeric promotion ──> int
char ──┘
int  ────────────────────────────────> int
long  ───────────────────────────────> long
float ───────────────────────────────> float
double ──────────────────────────────> double
```

> **تلهٔ C++:** در C++ نوع‌های کوچک‌تر در expression integer promotion می‌شوند (مشابه) اما قاعده‌های `int`/`unsigned int` روی پلتفرم‌های مختلف فرق دارد و `unsigned` می‌تواند promotion را عوض کند. در Java، `byte`/`short` هرگز `unsigned` نیستند و promotion همیشه به `int` امضا‌دار است.

## 2. widening، narrowing و cast

Widening معمولاً implicit است؛ narrowing می‌تواند range، bit یا بخش اعشاری را از دست بدهد و باید آگاهانه با cast اعلام شود. Cast validation دامنه نیست.
برای خواندن code، ابتدا type و valueها را جدا کنید؛ سپس مسیر control را روی کاغذ trace کنید. Output تنها تأیید است، نه جایگزین reasoning.

- int به long widening است.
- int به byte narrowing و low-bit preserving است.
- double به int بخش کسری را به سوی صفر حذف می‌کند.
- char یک UTF-16 code unit بدون علامت است.

| مسیر | cast | اثر |
|---|---:|---|
| `byte → int` | خیر | widening دقیق |
| `int → byte` | بله | bitهای بالا حذف می‌شوند |
| `double → int` | بله | fraction به سوی صفر حذف می‌شود |
| `char → int` | خیر | code unit عددی می‌شود |

widening همیشه value-preserving است: هر `int` در `long` با همان علامت و magnitude جا می‌گیرد، هر `char` در `int` به شکل کد واحدش خوانده می‌شود، و هر `float` کوچک‌تر از حدود `double` دقیقاً قابل نمایش است. در نتیجه کامپایلر اجازه می‌دهد widening را بدون cast بنویسید. اما narrowing ارزش را محدود می‌کند و کامپایلر نمی‌تواند تشخیص بدهد آیا در دامنهٔ مقصد هست یا نه؛ بنابراین cast صریح لازم است و **validation را به شما واگذار می‌کند.** اگر عدد در دامنه نباشد، دو حالت رخ می‌دهد:

- **integral narrowing** فقط low-bitها را نگه می‌دارد و آن‌ها را با signed interpretation می‌خواند. `int x = 300; byte b = (byte) x;` می‌شود `44` (نه `-56` — محاسبه را باید با bit pattern انجام دهید نه با `300 mod 256`).
- **floating-to-integral** ابتدا fraction را به سمت صفر حذف می‌کند (`(int) -3.7` می‌شود `-3`، نه `-4`)، سپس اگر نتیجه در دامنهٔ نوع integral نباشد، مقدار `min` یا `max` آن نوع برگردانده می‌شود (`Integer.MAX_VALUE` یا `Integer.MIN_VALUE`).

`char` یک **UTF-16 code unit بدون علامت** است — وقتی به `int` widen می‌شود مقداری بین `0` و `65535` می‌دهد. این رفتار با `byte` فرق دارد: `byte` امضا‌دار است و `-1` در `int` همان `-1` می‌شود، نه `255`. در نتیجه مقایسهٔ `char` با عدد (`'A' == 65`) در Java درست کار می‌کند ولی ترکیب `byte` با عدد منفی نیازمند دقت است.

```java
int big = 0x10FFFF;          // بزرگ‌تر از کد واحد UTF-16
char low = (char) big;        // فقط 16 bit پایین؛ 0xFFFF
int reconstructed = low;      // 65535، نه 0x10FFFF
```

> **تلهٔ C++:** در C++ narrowing implicit در initializer braced-list مجاز نیست (`int x{3.7};` خطا می‌دهد) اما در `=` و expression مجاز است و truncation رخ می‌دهد. در Java، narrowing بدون cast **همیشه** خطای کامپایل است. این تفاوت ظاهری، در code واقعی تفاوت رفتاری بزرگی ایجاد می‌کند: Java شما را مجبور می‌کند قبل از lossy conversion صریح فکر کنید.

## 3. arithmetic، division و modulo

برای integralها، `/` تقسیم صحیح با **truncation به سوی صفر** است. اگر هر دو operand integral باشند (پس از numeric promotion)، نتیجه integral می‌ماند حتی اگر مقدار صفر اعشاری طبیعی باشد. `7 / 2` می‌شود `3`، `7 / -2` می‌شود `-3` (نه `-4`)، `-7 / 2` می‌شود `-3`. برای داشتن fraction باید **پیش از operation** یک operand floating-point باشد: `7 / 2.0` می‌شود `3.5`، `7.0 / 2` می‌شود `3.5`، `7.0 / 2.0` می‌شود `3.5`. اگر بعد از محاسبه cast کنید (`(double) (7 / 2)`) دیر شده — integer division قبلاً انجام شده و فقط یک `3.0` به دست می‌آورید.

علامت `%` (remainder) **از dividend** می‌آید، نه divisor. `7 % 2` می‌شود `1`، `7 % -2` می‌شود `1` (نه `-1`)، `-7 % 2` می‌شود `-1`. این با تسهیم ریاضی فرق دارد: `Math.floorMod(7, -2)` می‌شود `-1` (هم‌علامت divisor) و `Math.floorMod(-7, 2)` می‌شود `1`. برای **index حلقوی** که می‌خواهید `[0, n)` بماند، `Math.floorMod` نتیجهٔ صحیح‌تری می‌دهد:

```java
int[] ring = new int[10];
for (int step = -3; step <= 3; step++) {
    int idx = Math.floorMod(step, ring.length);   // همیشه 0..9
    ring[idx]++;
}
// ring[0] = 1 (step=-10, 0), ring[1] = 1, ..., ring[7] = 1
// ring[8] = 0, ring[9] = 0
```

overflow integral در Java **wrap دو مکمل تعریف‌شده** دارد — یعنی `Integer.MAX_VALUE + 1` قطعاً `Integer.MIN_VALUE` می‌شود، نه exception و نه undefined behavior. این تعریف‌شدگی ابزار خوبی برای hash و cryptography نیست (برای آن‌ها `Math.addExact` و `Math.multiplyExact` وجود دارد که در overflow پرتاب می‌کنند) ولی برای شمارنده‌های wrap-around راحت است.

```java
int x = Integer.MAX_VALUE;
int y = x + 1;              // -2147483648
long z = 1L << 63;          // Long.MIN_VALUE
int safe = Math.addExact(1, 1);  // 2
int bad  = Math.addExact(Integer.MAX_VALUE, 1);  // ArithmeticException
```

> **تلهٔ C++:** در C++ signed overflow **رفتار تعریف‌نشده** است؛ کامپایلر آزاد است هر کاری بکند، از جمله حذف کامل `if (x + 1 > x)`. در Java، wrap قطعی و قابل آزمایش است. اگر کد Java را به C++ ترجمه می‌کنید، هر جا به wrap تکیه کرده‌اید، در C++ باید `-fwrapv` یا نوع unsigned اضافه کنید.

## 4. bitwise و shift

`&`، `|`، `^` و `~` روی bitهای integral کار می‌کنند. برای flagها literal باینری (`0b0010_0100`) یا hexadecimal (`0x24`) معمولاً خواناتر از decimal است و underscore بین رقم‌ها برای جداسازی مجاز است. سه عملگر shift رفتار متفاوتی دارند: `<<` (left shift) و `>>` (arithmetic/sign-extending right shift) و `>>>` (logical/zero-fill right shift). تفاوت `>>` و `>>>` فقط زمانی دیده می‌شود که عدد **منفی** باشد — برای مثبت یکسان‌اند.

**نکتهٔ بسیار مهم:** shift count در `int` فقط **5 bit پایین** مؤثر است؛ یعنی اگر بنویسید `1 << 33` روی `int`، مقدار `33` به `33 & 31 = 1` تبدیل می‌شود و نتیجه `2` می‌شود، نه خطا و نه `0`. روی `long` فقط 6 bit پایین مؤثر است (mod 64). این رفتار قطعی است ولی اکثر برنامه‌نویس‌ها انتظارش را ندارند:

```java
int a = 1 << 33;       // 2  (33 mod 32 = 1)
int b = 1 << 32;       // 1  (32 mod 32 = 0)
int c = 1 << 64;       // 1  (64 mod 32 = 0)
long d = 1L << 33;     // 8589934592  (33 mod 64 = 33)
int e = -1 >>> 29;     // 7  (همهٔ 32 بیت می‌چرخند، سمت چپ صفر می‌آید)
```

`>>>` ابزار اصلی کار با bit pattern مستقل از علامت است — مثلاً برای ساختن unsigned-view از `int`، استخراج 16 بیت بالا، یا مقایسه بدون توجه به sign bit.

| موضوع | Java | C++ رایج |
|---|---|---|
| shift راست zero-fill | `>>>` | `>>` روی unsigned type |
| integer unsigned عمومی | primitive جدا ندارد | `unsigned int` و هم‌خانواده‌ها |
| signed overflow | wrap تعریف‌شده | رفتار تعریف‌نشده |
| shift count mod | `% (bits)` بی‌صدا | رفتار تعریف‌نشده در C++14- |

> **تلهٔ C++:** در C++ اگر shift count منفی یا بزرگ‌تر از width نوع باشد، **رفتار تعریف‌نشده** است. در Java، count همیشه به `count & (width-1)` نرمال می‌شود. اگر از C++ کدی منتقل می‌کنید که به `count` بزرگ متکی است، در Java نتیجهٔ متفاوت می‌گیرید — و این تفاوت در runtime کشف می‌شود نه در compile.

## 5. comparison و logical

عملگرهای relational (`==`، `!=`، `<`، `<=`، `>`، `>=`، `instanceof`) یک `boolean` تولید می‌کنند. Java **numeric truthiness ندارد**: شرط `if`، `while` و سه‌تاییِ for باید دقیقاً `boolean` باشد. `if (count)` کامپایل نمی‌شود؛ باید `if (count != 0)` یا predicate domain بنویسید. این یک تصمیم طراحی است که از یک دستهٔ کامل bug جلوگیری می‌کند (مثلاً `if (pointer)` در C که گاهی null و گاهی non-null است).

`==` روی primitive **value** را مقایسه می‌کند، روی reference **identity** را. این برای boxed typeها (`Integer`، `Long`) یک تلهٔ معروف است: `Integer a = 100; Integer b = 100; a == b` می‌شود `true` (cache داخلی برای `-128..127`)، اما `Integer c = 200; Integer d = 200; c == d` می‌شود `false` (اشیاء متفاوت). همیشه برای boxed typeها از `.equals()` استفاده کنید. `NaN` هم استثنا است: هیچ مقداری (حتی خودش) با `==` برابر `NaN` نیست؛ `NaN == NaN` می‌شود `false`. برای تست `NaN` باید `Float.isNaN(x)` یا `Double.isNaN(x)` بنویسید.

`&&` و `||` **short-circuit** هستند: اگر نتیجه از operand چپ معلوم باشد، operand راست اصلاً evaluate نمی‌شود. این رفتار دو فایده دارد: (1) عملکرد، (2) ایمنی — مثلاً `if (obj != null && obj.isReady())` بدون null-check جداگانه. `&` و `|` روی boolean **قانونی** هستند ولی **eager**: همیشه operand راست را evaluate می‌کنند. در expression سادهٔ boolean معمولاً اشتباه‌اند (احتمالاً منظورتان short-circuit بود) ولی در bitmask روی flagها کاربرد دارند.

```java
boolean a = expensiveCheck();   // پرهزینه
boolean b = a && cheapCheck();  // اگر a=false، cheapCheck اجرا نمی‌شود
boolean c = a & cheapCheck();   // هر دو همیشه اجرا می‌شوند
```

| expression | ارزیابی راست؟ | کاربرد پیش‌فرض |
|---|---:|---|
| `a && b` با `a=false` | خیر | guard |
| `a || b` با `a=true` | خیر | fallback |
| `a & b` | بله | bitwise/eager آگاهانه |
| `a | b` | بله | bitwise/eager آگاهانه |

> **تلهٔ C++:** در C++ `&&` و `||` نیز short-circuit هستند ولی `&` و `|` روی integral **bitwise** هستند و overload به boolean ندارند مگر explicit. در Java، overload روی boolean استاندارد است و اغلب منبع bug می‌شود: کدی که `&` می‌نویسد در حالی که منظورش `&&` بوده، در test کوچک درست کار می‌کند و در production با side-effect کشف می‌شود.

## 6. assignment، precedence و ternary

Precedence syntax را تعیین می‌کند، نه intention را. هر جا خواننده ممکن است ترتیب را اشتباه بگیرد، parentheses یا statementهای کوچک‌تر راه‌حل‌اند. جدول precedence استاندارد (از بالا به پایین، چپ‌به‌راست associative مگر خلافش گفته شود):

```text
1.  postfix         x++  x--  method()  arr[i]  obj.field
2.  unary           ++x  --x  +x  -x  ~x  !x  (type)x
3.  multiplicative  *   /   %
4.  additive        +   -
5.  shift           <<  >>  >>>
6.  relational      <  <=  >  >=  instanceof
7.  equality        ==  !=
8.  bitwise AND     &
9.  bitwise XOR     ^
10. bitwise OR      |
11. logical AND     &&
12. logical OR      ||
13. ternary         ? :
14. assignment      =  +=  -=  *=  /=  %=  &=  ^=  |=  <<=  >>=  >>>=
```

`x++` (postfix) **مقدار قدیم** را برمی‌گرداند و سپس افزایش می‌دهد؛ `++x` (prefix) ابتدا افزایش می‌دهد و سپس مقدار جدید را برمی‌گرداند. در expression سادهٔ standalone (`x++;`) تفاوتی ندارند. در ترکیب (`arr[index++] = 0`) تفاوت دیده می‌شود. تلهٔ معروف: `int x = 5; x = x++;` مقدار `5` را به `x` انتساب می‌دهد (postfix مقدار قدیم 5 را برمی‌گرداند، سپس `x` به 6 افزایش می‌یابد، اما assignment با 5 آن را بازنویسی می‌کند). نتیجه `x == 5`.

**compound assignment** یک ویژگی ظریف دارد: `x += y` معادل `x = (T)(x + y)` است که در آن `T` نوع `x` است. این یعنی compound assignment **implicit narrowing** انجام می‌دهد، حتی اگر نتیجهٔ `x + y` در دامنه نباشد:

```java
byte b = 100;
b += 200;        // کامپایل می‌شود! b = (byte)(100 + 200) = (byte)300 = 44
// b = b + 200;  // خطای کامپایل: نمی‌توان int را به byte انتساب داد
```

این رفتار گاهی مفید است (می‌خواهید wrap-around شود)، گاهی خطرناک (انتظار دارید overflow تشخیص داده شود). در codeی که عددی دقیق می‌خواهید، به جای `+=` از `x = (T) (x + y)` cast صریح استفاده کنید تا intent روشن باشد.

ternary فقط branch انتخاب‌شده را evaluate می‌کند. نوع expression در صورت نیاز **numeric promotion** می‌شود تا common type پیدا شود:

```java
int a = 1;
double b = 2.0;
double c = true ? a : b;     // 1.0 — a به double promotion می‌یابد
int    d = true ? 1 : 2.0;   // خطای کامپایل: common type double است
Object e = flag ? "yes" : 42;  // String و Integer، common type Serializable (?)
```

> **تلهٔ C++:** در C++ ternary می‌تواند lvalue باشد و در سمت چپ assignment بنشیند (`(cond ? a : b) = 5;` معتبر است). در Java ternary **همیشه rvalue** است — نمی‌توان به آن assign کرد. این محدودیت جلوی یک دسته bug را می‌گیرد.

## 7. if و if/else

`if` یک statement یا block را در صورت true بودن condition انتخاب می‌کند. در زنجیرهٔ `if`/`else if`/`else`، نخستین condition true برنده است و بقیه ارزیابی نمی‌شوند (short-circuit منطقی، نه ارزیابی واقعی predicate). این ترتیب اهمیت دارد: **range تخصصی‌تر را پیش از range عمومی‌تر بنویسید.** compiler هیچ تحلیلی روی overlap منطقی rangeها انجام نمی‌دهد — اگر بنویسید `if (x > 0)` و سپس `if (x > 100)` به ترتیب اشتباه، هر دو می‌توانند اجرا شوند (اگرچه در عمل else-if جلوی آن را می‌گیرد). boundaryها (کوچک‌تر، کوچک‌تر-مساوی) را **همیشه** صریح تست کنید.

```java
if (score >= 90) grade = 'A';
else if (score >= 80) grade = 'B';   // اگر 95 باشد، اینجا نمی‌رسد
else if (score >= 70) grade = 'C';
else if (score >= 60) grade = 'D';
else grade = 'F';
```

**همیشه brace بنویسید** حتی برای یک statement. اگر `if (cond) doSomething();` بنویسید و بعد یک debug `System.out.println` اضافه کنید بدون brace، فقط debug شرطی می‌شود نه `doSomething` — یک bug کلاسیک. IDEها هشدار می‌دهند ولی قانون ساده این است: brace همیشه.

```java
if (ready) send();           // خطرناک اگر statement دوم اضافه شود
if (ready) {
    send();
}
```

**empty statement** (`;`) یک statement تهی است و می‌تواند به‌طور ناخواسته بنشیند:

```java
if (ready);     // empty statement شرطی — بلاک بعدی بدون شرط اجرا می‌شود
    send();     // ⚠ این همیشه اجرا می‌شود
```

از الگوی **guard clause** (return زودهنگام) برای کاهش nesting استفاده کنید. اگر شرط نامعتبر است، در اولین خط برگردید:

```java
// ✗ deep nesting
String describe(Account a) {
    if (a != null) {
        if (a.isActive()) {
            if (a.hasBalance()) {
                return a.type() + ": " + a.balance();
            }
        }
    }
    return "inactive";
}

// ✓ guards
String describe(Account a) {
    if (a == null) return "inactive";
    if (!a.isActive()) return "inactive";
    if (!a.hasBalance()) return "inactive";
    return a.type() + ": " + a.balance();
}
```

> **تلهٔ C++:** در C++ if می‌تواند initializer داشته باشد (C++17): `if (auto it = m.find(k); it != m.end())`. در Java 21 این syntax موجود نیست ولی pattern matching for-switch (preview) در آینده نزدیک می‌آید. فعلاً برای محدود کردن scope یک متغیر، یک block صریح بنویسید.

## 8. switch statement

switch برای انتخاب valueهای گسسته است، نه rangeهای باز. **colon form** (`case x:`) **fall-through** دارد مگر اینکه `break`، `return`، `throw` یا پایان statement list کنترل را قطع کند. این رفتار legacy از C++ است و منبع اصلی bug است — اگر `break` را فراموش کنید، execution به case بعدی می‌ریزد. **arrow form** (`case x ->`) این مشکل را ندارد: فقط همان case اجرا می‌شود. پیش‌فرض، همیشه arrow form را انتخاب کنید مگر واقعاً به fall-through نیاز داشته باشید.

case label باید **compile-time constant** و **یکتا** باشد (duplication خطای کامپایل است). selector type می‌تواند `byte`/`short`/`char`/`int` (و boxed)، `String`، enum، یا در نسخه‌های جدیدتر pattern-matching types باشد. `long`، `float`، `double` و `boolean` مجاز نیستند.

```java
String day = "MON";
int working = switch (day) {                 // arrow form
    case "MON", "TUE", "WED", "THU", "FRI" -> 1;
    case "SAT", "SUN" -> 0;
};
```

fall-through **عمدی** می‌تواند مفید باشد وقتی چند case می‌خواهند **بدنهٔ مشترک** داشته باشند. در این صورت معمولاً کامنت می‌گذارند تا intent روشن باشد:

```java
switch (month) {
    case 1: case 3: case 5: case 7: case 8: case 10: case 12:
        days = 31;                          // shared body برای همهٔ این case
        break;
    case 4: case 6: case 9: case 11:
        days = 30;
        break;
    case 2:
        days = leapYear ? 29 : 28;
        break;
}
```

`default` مسیر valueهای پوشش‌نداده را می‌گیرد. اگر نباشد، هیچ اتفاقی نمی‌افتد وقتی هیچ case مطابق نیست — execution بعد از switch ادامه می‌یابد. این رفتار در `switch` statement قانونی است ولی در `switch` expression خطای کامپایل است (exhaustiveness).

| شکل | fall-through | value تولید می‌کند |
|---|---:|---:|
| `case x:` statement | ممکن است (با break قطع می‌شود) | خیر |
| `case x ->` statement | خیر | خیر |
| switch expression | خیر | بله |

> **تلهٔ C++:** در C++ switch `case` label باید integral constant باشد و `enum class` مجاز نیست مگر با unscoped enum. در Java، `String` و `enum` مستقیماً پشتیبانی می‌شوند — این تفاوت ساختاری، switch را در Java برای command-pattern و dispatch بسیار مفیدتر می‌کند.
## 9. switch expression و yield

switch expression value تولید می‌کند و arrow form fall-through ندارد. هر مسیر باید value بدهد یا exception پرتاب کند — اگر مسیری value ندهد، **خطای کامپایل** است (exhaustiveness). این یعنی compiler تعداد case labelها و نوع result را بررسی می‌کند و شما را مجبور می‌کند همهٔ stateها را پوشش دهید.

دو شکل arm وجود دارد. **arrow arm** (`case x -> value;`) مستقیماً value می‌دهد و expression است. **block arm** (`case x -> { ...; yield v; }`) یک block دارد که با `yield v;` value را برمی‌گرداند. `yield` فقط در switch expression مجاز است؛ در method، `return` نقش آن را دارد. `yield` نه `break` است نه `return` — بلکه value را به context بیرونی switch برمی‌گرداند بدون اینکه از method خارج شود.

```java
int days = switch (month) {
    case 1, 3, 5, 7, 8, 10, 12 -> 31;
    case 4, 6, 9, 11          -> 30;
    case 2 -> {
        int d = leapYear ? 29 : 28;
        yield d;                              // value از block arm بیرون می‌رود
    }
};
```

**Exhaustiveness** برای enum کامل: اگر همهٔ constantهای enum را case کنید، `default` لازم نیست؛ اگر یکی را از قلم بیندازید، خطای کامپایل می‌گیرید. این برخلاف `if`/`else` است که هیچ compiler-check ندارد. برای `String` و `int` معمولاً `default` لازم است چون مقدار ممکن است هر چیزی باشد.

| selector type | exhaustiveness |
|---|---|
| enum کامل | اگر همه constantها case شوند، default لازم نیست |
| sealed type | اگر همه subtypeها case شوند، default لازم نیست |
| String / int | معمولاً default لازم است |
| sealed + record (preview) | exhaustive با pattern matching |

> **تلهٔ C++:** در C++17 `if`/`switch` می‌تواند initializer داشته باشد ولی expression-form وجود ندارد. `switch` در C++ همیشه statement است. expression-form یک قابلیت مخصوص Java 14+ است که نوشتن dispatch تمیز را ممکن می‌کند — مثلاً `String label = switch (state) { ... };` به جای intermediate variable.
## 10. for و enhanced-for

for سه قسمت دارد: **initializer** (یک‌بار اجرا می‌شود)، **condition** (پیش از هر iteration چک می‌شود)، **update** (پس از هر iteration اجرا می‌شود). initializer و update می‌توانند خالی باشند (`for (;;)`)، و condition اگر خالی باشد true در نظر گرفته می‌شود (loop بی‌نهایت). initializer می‌تواند چند متغیر با هم تعریف کند (`for (int i=0, j=n; i<j; i++, j--)`) ولی فقط **یک نوع** می‌تواند اعلام شود (همه `int` یا همه `var`).

```java
for (int i = 0; i < 10; i++) { /* ... */ }   // ساده
for (int i = 0, j = 9; i < j; i++, j--) { } // دو متغیر هم‌نوع
for (;;) { /* break لازم دارد */ }            // بی‌نهایت
```

`continue` در for ابتدا **update** و سپس **condition** را می‌بیند. این ترتیب مهم است: اگر condition در update بعدی false شود، loop تمام می‌شود؛ اگر update side-effect منفی داشته باشد (مثل `i--`)، iteration بعدی ممکن است infinite شود.

**enhanced-for** (for-each) برای پیمایش collection و array بدون نیاز به index است. متغیر loop **کپی** element فعلی است — تغییر آن، element اصلی را عوض نمی‌کند:

```java
int[] a = {1, 2, 3};
for (int x : a) x = 0;
System.out.println(a[1]);   // 2 — تغییر x آرایه را عوض نکرد

List<String> names = new ArrayList<>(List.of("ali", "reza"));
for (String s : names) s = s.toUpperCase();   // فقط کپی محلی
// names هنوز ["ali", "reza"] است
```

اگر element‌ها reference به object mutable باشند (مثل `List<StringBuilder>`)، تغییر **از طریق متد** object قابل مشاهده است، ولی reassign کردن متغیر loop نه:

```java
List<StringBuilder> list = new ArrayList<>();
list.add(new StringBuilder("a"));
list.add(new StringBuilder("b"));
for (StringBuilder sb : list) sb.append("!");   // object مشترک تغییر می‌کند
// list اکنون [a!, b!] دارد — append روی خود object بود
```

برای **حذف در حین پیمایش**، enhanced-for کار نمی‌کند — `ConcurrentModificationException` می‌دهد. سه گزینهٔ استاندارد:

```java
// 1. Iterator با remove() explicit
for (Iterator<String> it = list.iterator(); it.hasNext(); ) {
    if (it.next().isEmpty()) it.remove();
}

// 2. removeIf (default در Collection از Java 8)
list.removeIf(s -> s.isEmpty());

// 3. for-each روی کپی
for (String s : new ArrayList<>(list)) {
    if (s.isEmpty()) list.remove(s);
}
```

> **تلهٔ C++:** در C++11 range-based for با `auto&&` می‌تواند mutate کند (`for (auto& x : v) x = 0;`)، ولی `auto` (by value) کپی می‌دهد. در Java همیشه کپی است — `for (int x : a)` هیچ راهی برای mutate خانهٔ array از طریق `x` نیست. این محدودیت intentional است: enhanced-for **read-mostly** است.
## 11. while، do-while و loop بی‌نهایت

`while` condition را **پیش از** body می‌سنجد — اگر false باشد، body اصلاً اجرا نمی‌شود. `do-while` condition را **پس از** body می‌سنجد — body حداقل یک بار اجرا می‌شود حتی اگر condition false باشد. `for (;;)` و `while (true)` هر دو loop بی‌نهایت‌اند و نیاز به `break`، `return` یا exception دارند.

```java
int n = 0;
while (n < 3) System.out.println(n++);   // 0, 1, 2
// do-while حداقل یک بار
do { System.out.println("once"); } while (false);   // چاپ: once
// infinite
for (;;) { if (done) break; }
```

**do-while** زمانی مفید است که body باید حداقل یک بار اجرا شود (مثل menu prompt، retry loop با حداقل یک تلاش، یا validation که ابتدا می‌پرسد و بعد تکرار می‌کند). `while` برای حالت zero-or-more مناسب‌تر است (مثل polling تا زمانی که resource آماده شود).

**invariant** گزاره‌ای است که در ابتدای هر iteration برقرار است. اگر بتوانید invariant را بنویسید، loop را می‌فهمید. **پیشرفت** شرطی است که تضمین می‌کند loop به سمت termination می‌رود (counter کم/زیاد می‌شود، pointer جلو می‌رود). اگر invariant و progress واضح نیست، loop باگ دارد.

```java
// ✗ پیشرفت مبهم
int x = 1;
while (x != 50) { x = x + ((x % 2 == 0) ? 1 : 2); }
// این چه می‌کند؟ چه وقت تمام می‌شود؟

// ✓ پیشرفت روشن
for (int x = 0; x < 50; x++) { /* یک iteration، یک افزایش */ }
```

**event loop** (مثل server) loop بی‌نهایت مشروع است، ولی ownership توقف روشن می‌خواهد: signal handler، shutdown hook، یا condition بیرونی. mutation شرط پایان را پنهان نکنید — اگر `done = true` در عمق چند method رخ می‌دهد، trace کردن سخت می‌شود.

> **تلهٔ C++:** در C++ `for` initializer می‌تواند declaration قدیمی (`for (int i = 0; ...)`) باشد ولی متغیر بعد از loop در scope نیست. در Java initializer متغیر را در scope block بیرونی for تعریف می‌کند (`for (int i = 0; ...; )` در Java 21، پس از پایان for، `i` در scope نیست). رفتار مشابه است.
## 12. labels، scope و definite assignment

**label** نام statement است، نه goto عمومی. `break label;` فقط statement labelدار را تمام می‌کند؛ `continue label;` فقط loop labelدار را به iteration بعدی می‌برد. label باید دقیقاً قبل از statement هدف بیاید و بدون `:` نوشته می‌شود (برخلاف C++ که `label:` دارد):

```java
outer: for (int i = 0; i < 3; i++) {
    inner: for (int j = 0; j < 3; j++) {
        if (j == 1) continue outer;       // ادامه iteration بعدی outer
        if (i == 1 && j == 1) break outer; // خروج از outer تماماً
    }
}
```

label نمی‌تواند به هر statement اشاره کند (مثل `if`) و نمی‌تواند به method دیگری بپرد. labelها برای **خروج زودهنگام از nested loop** مفیداند، ولی در بیشتر موارد extraction به method یا استفاده از flag واضح‌تر است.

**scope** قابلیت دیدن identifier را تعیین می‌کند. block scope در `{}` ایجاد می‌شود: متغیر اعلام‌شده در block فقط تا انتهای block قابل دسترسی است. initializer for متغیر را در scope خود for می‌سازد — پس از `for (int i = 0; ...; )`، `i` در scope بیرونی **نیست** (این تفاوت با C++ post-2017 است که initializer for متغیر را در scope block for می‌گذارد، نه بیرونی):

```text
{
  for (int index = 0; index < 3; index++) {
      int inside = index;          // inside فقط در این block
  }
  // index و inside اینجا در scope نیستند
}
```

**definite assignment (DA)** قانونی است که compiler بررسی می‌کند تا مطمئن شود local variable پیش از read مقدار گرفته است. اگر در شاخه‌ای از control مقداردهی نشده باشد، خطای کامپایل است:

```java
int x;
if (cond) x = 1;
System.out.println(x);    // خطای کامپایل: x ممکن است مقداردهی نشده باشد

int y;
if (cond) y = 1; else y = 2;
System.out.println(y);    // OK — هر دو شاخه مقداردهی شده

int z;
if (cond) z = 1;
else return;
System.out.println(z);    // OK — اگر به اینجا رسیدیم، z مقدار دارد
```

قوانین DA در JLS §16 تعریف شده‌اند. اگر `final` باشد، علاوه بر DA باید **exactly-once** باشد (یا در همهٔ شاخه‌های if/else، یا در یک حلقه که invariant دارد).

> **تلهٔ C++:** در C++ DA وجود ندارد — local primitive بدون initializer مقدار indeterminate دارد و read آن رفتار تعریف‌نشده است. در Java، primitive local بدون initializer **خطای کامپایل** می‌دهد. این یک ایمنی بنیادی است: نمی‌توانید متغیر uninitialized را تصادفاً بخوانید. تنها استثنا: field‌های object قبل از سازنده مقدار پیش‌فرض (۰، false، null) دارند (که خودش منبع bug متفاوتی است).
## مثال‌های اجرایی و تحلیل

### مثال 1 — run id=promotion-sum

<!-- verify: run id=promotion-sum -->
```java
class PromotionSum { public static void main(String[] args) { byte a=40,b=2; int total=a+b; System.out.println(total); } }
```

خروجی:
```text
42
```
نتیجه int است؛ مقدار 42 فقط نمونه است.

### مثال 2 — compile-fail id=promotion-fail

<!-- verify: compile-fail id=promotion-fail -->
```java
class PromotionFail { public static void main(String[] args) { byte b=1; b=b+1; } }
```
این شکست عمدی نشان می‌دهد assignment معمولی narrowing implicit ندارد.

### مثال 3 — run id=promotion-compound

<!-- verify: run id=promotion-compound -->
```java
class PromotionCompound { public static void main(String[] args) { byte b=127; b+=1; System.out.println(b); } }
```

خروجی:
```text
-128
```
`b += 1` narrowing ضمنی دارد و به معنی safe arithmetic نیست.

### مثال 4 — run id=cast-truncate

<!-- verify: run id=cast-truncate -->
```java
class CastTruncate { public static void main(String[] args) { System.out.println((int)3.99); System.out.println((int)-3.99); } }
```

خروجی:
```text
3
-3
```
Cast به int floor نیست.

### مثال 5 — run id=cast-char

<!-- verify: run id=cast-char -->
```java
class CastChar { public static void main(String[] args) { char c='A'; int n=c; System.out.println(n); System.out.println((char)(n+1)); } }
```

خروجی:
```text
65
B
```
char یک code unit است، نه تضمین یک کاراکتر انسانی کامل.

### مثال 6 — run id=cast-wrap

<!-- verify: run id=cast-wrap -->
```java
class CastWrap { public static void main(String[] args) { System.out.println((byte)260); } }
```

خروجی:
```text
4
```
low byte باقی می‌ماند.

### مثال 7 — run id=division

<!-- verify: run id=division -->
```java
class Division { public static void main(String[] args) { System.out.println(7/2); System.out.println(7/2.0); System.out.println(-7/2); } }
```

خروجی:
```text
3
3.5
-3
```
نوع operation پیش از assignment تعیین می‌شود.

### مثال 8 — run id=modulo

<!-- verify: run id=modulo -->
```java
class Modulo { public static void main(String[] args) { System.out.println(-7%3); System.out.println(7%-3); System.out.println(-7%-3); } }
```

خروجی:
```text
-1
1
-1
```
برای index حلقوی غیرمنفی، `Math.floorMod` را بررسی کنید.

### مثال 9 — run id=overflow

<!-- verify: run id=overflow -->
```java
class Overflow { public static void main(String[] args) { System.out.println(Integer.MAX_VALUE+1); } }
```

خروجی:
```text
-2147483648
```
برای پول و capacity به wrap تکیه نکنید.

### مثال 10 — run id=bitwise

<!-- verify: run id=bitwise -->
```java
class Bitwise { public static void main(String[] args) { int f=0b10110; System.out.println(f&0b00110); System.out.println(f^0b00110); } }
```

خروجی:
```text
6
16
```
برای debug، binary output از decimal گویاتر است.

### مثال 11 — run id=shifts

<!-- verify: run id=shifts -->
```java
class Shifts { public static void main(String[] args) { int n=-8; System.out.println(n>>1); System.out.println(n>>>1); System.out.println(3<<2); } }
```

خروجی:
```text
-4
2147483644
12
```
`>>>` از چپ صفر وارد می‌کند.

### مثال 12 — run id=shift-count

<!-- verify: run id=shift-count -->
```java
class ShiftCount { public static void main(String[] args) { System.out.println(1<<32); System.out.println(1L<<64); } }
```

خروجی:
```text
1
1
```
count مؤثر با bitهای پایین محاسبه می‌شود.

### مثال 13 — run id=boolean

<!-- verify: run id=boolean -->
```java
class BooleanCondition { public static void main(String[] args) { int count=2; if(count>0) System.out.println("has items"); } }
```

خروجی:
```text
has items
```
Java numeric truthiness ندارد.

### مثال 14 — run id=float-equality

<!-- verify: run id=float-equality -->
```java
class FloatEquality { public static void main(String[] args) { double s=0.1+0.2; System.out.println(s==0.3); System.out.println(s); } }
```

خروجی:
```text
false
0.30000000000000004
```
Tolerance باید از domain بیاید.

### مثال 15 — run id=short-circuit

<!-- verify: run id=short-circuit -->
```java
class ShortCircuit { static boolean p(String s,boolean v){System.out.println(s);return v;} public static void main(String[] args){boolean r=p("left",false)&&p("right",true);System.out.println(r);} }
```

خروجی:
```text
left
false
```
سمت راست evaluate نشد.

### مثال 16 — run id=eager

<!-- verify: run id=eager -->
```java
class Eager { static boolean p(String s,boolean v){System.out.println(s);return v;} public static void main(String[] args){boolean r=p("left",false)&p("right",true);System.out.println(r);} }
```

خروجی:
```text
left
right
false
```
`&` برای boolean هر دو سمت را اجرا می‌کند.

### مثال 17 — run id=increment

<!-- verify: run id=increment -->
```java
class Increment { public static void main(String[] args) { int x=5; System.out.println(x++); System.out.println(++x); System.out.println(x); } }
```

خروجی:
```text
5
7
7
```
expression پر mutation را به statementهای جدا تبدیل کنید.

### مثال 18 — run id=ternary

<!-- verify: run id=ternary -->
```java
class Ternary { public static void main(String[] args) { int score=72; String r=score>=60?"pass":"retry"; System.out.println(r); } }
```

خروجی:
```text
pass
```
برای منطق چندمرحله‌ای if/else خواناتر است.

### مثال 19 — run id=if-range

<!-- verify: run id=if-range -->
```java
class IfRange { public static void main(String[] args) { int s=85; if(s>=90)System.out.println("A"); else if(s>=80)System.out.println("B"); else System.out.println("other"); } }
```

خروجی:
```text
B
```
condition تخصصی‌تر را اول بنویسید.

### مثال 20 — run id=switch-colon

<!-- verify: run id=switch-colon -->
```java
class SwitchColon { public static void main(String[] args) { int d=6; switch(d){case 6:case 7:System.out.println("weekend");break;default:System.out.println("weekday");} } }
```

خروجی:
```text
weekend
```
دو label اینجا عمداً body مشترک دارند.

### مثال 21 — run id=switch-arrow

<!-- verify: run id=switch-arrow -->
```java
class SwitchArrow { public static void main(String[] args) { String s="S"; int d=switch(s){case "N"->0;case "E","W"->1;case "S"->2;default->-1;};System.out.println(d); } }
```

خروجی:
```text
2
```
arrow arm fall-through ندارد.

### مثال 22 — run id=switch-yield

<!-- verify: run id=switch-yield -->
```java
class SwitchYield { public static void main(String[] args) { int m=2; int d=switch(m){case 2->{int y=2024;yield y%4==0?29:28;}default->30;};System.out.println(d); } }
```

خروجی:
```text
29
```
yield value expression را تولید می‌کند.

### مثال 23 — run id=switch-enum

<!-- verify: run id=switch-enum -->
```java
class SwitchEnum { enum Light{RED,YELLOW,GREEN} public static void main(String[] args){Light l=Light.GREEN;String r=switch(l){case RED->"stop";case YELLOW->"wait";case GREEN->"go";};System.out.println(r);} }
```

خروجی:
```text
go
```
enum کامل coverage دارد.

### مثال 24 — run id=for-continue

<!-- verify: run id=for-continue -->
```java
class ForContinue { public static void main(String[] args) { for(int i=0;i<5;i++){if(i%2==0)continue;System.out.print(i);} } }
```

خروجی:
```text
13
```
continue update را حذف نمی‌کند.

### مثال 25 — run id=enhanced-for

<!-- verify: run id=enhanced-for -->
```java
class EnhancedFor { public static void main(String[] args) { int s=0;for(int n:new int[]{2,3,4})s+=n;System.out.println(s); } }
```

خروجی:
```text
9
```
n یک copy primitive است.

### مثال 26 — run id=while

<!-- verify: run id=while -->
```java
class WhileZero { public static void main(String[] args) { int n=3;while(n<3)System.out.println("body");System.out.println("done"); } }
```

خروجی:
```text
done
```
while پیش از body شرط را می‌سنجد.

### مثال 27 — run id=do-while

<!-- verify: run id=do-while -->
```java
class DoWhile { public static void main(String[] args) { int n=3;do{System.out.println("body");}while(n<3); } }
```

خروجی:
```text
body
```
body دست‌کم یک بار اجرا می‌شود.

### مثال 28 — run id=infinite

<!-- verify: run id=infinite -->
```java
class InfiniteLoop { public static void main(String[] args) { int n=0;for(;;){if(++n==3)break;}System.out.println(n); } }
```

خروجی:
```text
3
```
exit path loop بی‌شرط را قابل audit می‌کند.

### مثال 29 — run id=label-break

<!-- verify: run id=label-break -->
```java
class LabelBreak { public static void main(String[] args) { int hits=0;search:for(int r=0;r<3;r++)for(int c=0;c<3;c++){hits++;if(r==1&&c==1)break search;}System.out.println(hits); } }
```

خروجی:
```text
5
```
break statement labelدار را تمام می‌کند.

### مثال 30 — run id=label-continue

<!-- verify: run id=label-continue -->
```java
class LabelContinue { public static void main(String[] args) { int n=0;rows:for(int r=0;r<3;r++)for(int c=0;c<3;c++){if(c==1)continue rows;n++;}System.out.println(n); } }
```

خروجی:
```text
3
```
continue به iteration بعدی loop نام‌دار می‌رود.

### مثال 31 — compile-fail id=definite-assignment

<!-- verify: compile-fail id=definite-assignment -->
```java
class DefiniteAssignment { public static void main(String[] args) { int value;if(args.length>0)value=1;System.out.println(value); } }
```
compiler proof مقداردهی همه مسیرها را ندارد.

### مثال 32 — skip id=fragment reason=not-standalone

<!-- verify: skip id=fragment -->
```java
for (int i = 0; i < 3; i++) { System.out.println(i); }
```
این snippet عمداً compilation unit مستقل نیست.

### مثال 33 — run id=precedence-puzzle

<!-- verify: run id=precedence-puzzle -->
```java
class PrecedencePuzzle { public static void main(String[] args) { System.out.println(1 + 2 + "3"); System.out.println("1" + 2 + 3); System.out.println(1 + 2 * 3); System.out.println(true ? 1 : 2.0); } }
```

خروجی:
```text
33
123
7
1.0
```

عملگر `+` از چپ به راست ارزیابی می‌شود؛ اولین String، بقیه را به String تبدیل می‌کند. ternary نوع common را انتخاب می‌کند (در اینجا `double`).

### مثال 34 — run id=labeled-break-exit

<!-- verify: run id=labeled-break-exit -->
```java
class LabeledBreakExit { public static void main(String[] args) { int hits=0; search:for(int r=0;r<4;r++)for(int c=0;c<4;c++){hits++;if(r==2&&c==1)break search;}System.out.println(hits); } }
```

خروجی:
```text
10
```

`break search` هر دو loop را با هم تمام می‌کند. hits شامل 4×r=0 (4) + 4×r=1 (4) + r=2 تا c=1 (2) = 10.

### مثال 35 — run id=shift-mask

<!-- verify: run id=shift-mask -->
```java
class ShiftMask { public static void main(String[] args) { System.out.println(1<<33); System.out.println(-8>>>29); System.out.println(-8>>29); } }
```

خروجی:
```text
2
7
-1
```

`1<<33` روی int فقط پنج bit پایین count را می‌بیند، پس معادل `1<<1`. `>>>` zero-fill می‌کند؛ `>>` sign-extend.

## مقایسه‌های لازم با C++

این بخش تفاوت‌های ظریف Java و C++ را در topic‌های درس جمع می‌کند تا هنگام port کردن mindset، دام‌ها قابل پیش‌بینی باشند. الگوی یکنواخت: یک جمله تله، یک نمونهٔ کوتاه در هر زبان، و یادآوری نتیجهٔ عملی.

### ۱. truthiness

> **تلهٔ C++:** در C++، `if (count)` تبدیل عدد به bool دارد؛ در Java باید `count != 0` یا predicate domain بنویسید.

```cpp
// C++: implicit numeric-to-bool
if (count) { /* ... */ }     // 0 → false، غیرصفر → true
```

```java
// Java: explicit boolean
if (count != 0) { /* ... */ }   // یا if (count > 0) اگر منظورتان این است
```

### ۲. overflow

> **تلهٔ C++:** در C++ signed overflow رفتار تعریف‌نشده است؛ Java int/long wrap دو مکمل تعریف‌شده دارد. تعریف‌شده بودن مجوز استفاده برای پول نیست.

```java
// Java: wrap دو مکمل تعریف‌شده
int x = Integer.MAX_VALUE;
int y = x + 1;            // -2147483648، قطعی و قابل پیش‌بینی
long z = 1L << 63;        // Long.MIN_VALUE
```

```cpp
// C++: signed overflow رفتار تعریف‌نشده (UBSan هشدار می‌دهد)
int x = std::numeric_limits<int>::max();
int y = x + 1;            // ممکن است -2147483648 باشد، یا هر چیز دیگر، یا optimization نامتعارف
```

Java در سطح language مشخص کرده که wrap می‌کند؛ C++ این کار را نکرده است و کامپایلر آزاد است هر رفتاری (از جمله حذف کامل عملیات) انتخاب کند. تعریف‌شده بودن، مجوز استفاده برای پول و capacity نیست.

### ۳. remainder

> **تلهٔ C++:** در Java remainder با truncation toward zero تعریف شده و علامت dividend را دارد. C++98/03 برای حالت منفی history implementation-defined دارد؛ C++ مدرن با Java همسو است.

```java
// Java
int r = -7 % 2;     // -1
int f = Math.floorMod(-7, 2);  // 1 (هم‌علامت divisor)
```

### ۴. unsigned shift

> **تلهٔ C++:** Java primitive unsigned عمومی مانند C++ ندارد؛ `>>>` ابزار zero-fill right shift است.

```cpp
// C++: `>>` روی unsigned zero-fill است
uint32_t x = 0x80000000;
uint32_t y = x >> 1;     // 0x40000000
```

```java
// Java: `>>>` برای zero-fill روی هر int
int x = 0x80000000;       // -2147483648
int y = x >>> 1;          // 1073741824 (positive)
int z = x >> 1;           // -1073743648 (sign-extend)
```

### ۵. switch و expression

> **تلهٔ C++:** C++ switch همیشه statement است و fall-through سنتی دارد؛ arrow switch Java راهی ساختاری برای حذف آن است.

```cpp
// C++17
int v = (cond ? a : b);   // ternary expression، value دارد
// switch در C++ نمی‌تواند expression باشد
```

```java
// Java 14+
int v = switch (x) {                // switch expression
    case 1 -> 10;
    case 2 -> 20;
    default -> 0;
};
```

### ۶. short-circuit در مقابل bitwise

> **تلهٔ C++:** در C++ `&&` و `||` short-circuit هستند ولی overload به شکل operator""  برای نوع‌های user-defined مجاز است. در Java، short-circuit فقط روی boolean primitive است.

```cpp
// C++: می‌توان یک operator&& overload کرد
struct S { bool operator&&(S) const; };
S a, b; if (a && b) { /* overload صدا زده می‌شود */ }
```

```java
// Java: && فقط روی boolean primitive
if (a && b) { /* همیشه short-circuit روی primitive */ }
```

### ۷. if-initializer (C++17)

> **تلهٔ C++:** در C++17 `if` می‌تواند initializer داشته باشد؛ Java این syntax را ندارد.

```cpp
if (auto it = m.find(k); it != m.end()) { /* use it */ }
```

```java
// Java: باید initializer قبل از if بنویسید
var it = m.find(k);
if (it != null) { /* use it */ }
```

### ۸. compound assignment narrowing

> **تلهٔ C++:** در C++ `b += 200;` با `b + 200` در سطح type رفتار یکسان دارد (هر دو نیاز به cast دارند). در Java، compound assignment implicit narrowing دارد و کامپایل می‌شود.

```java
byte b = 100;
b += 200;          // کامپایل می‌شود: b = (byte)(100+200) = 44
// b = b + 200;    // خطای کامپایل: int → byte narrowing implicit نیست
```

```cpp
// C++: هر دو نیاز به cast دارند
uint8_t b = 100;
b = b + 200;       // ⚠ int promotion قبل از جمع؛ cast لازم است
b = (uint8_t)(b + 200);
```

### ۹. for-scope

> **تلهٔ C++:** در C++ قبل از C++98 initializer for متغیر را در scope block for می‌گذاشت (و در C++98+ در scope خود for). در Java initializer for متغیر را در scope for قرار می‌دهد و پس از loop دیده نمی‌شود.

```cpp
// C++: متغیر i بعد از for در scope نیست (از C++98)
for (int i = 0; i < 3; i++) { /* i در اینجا */ }
// i اینجا در scope نیست
```

```java
// Java: همان رفتار — i بعد از for دیده نمی‌شود
for (int i = 0; i < 3; i++) { /* i در اینجا */ }
// i اینجا در scope نیست
```

### ۱۰. label بدون `:` و goto

> **تلهٔ C++:** در C++ label با `:` تمام می‌شود (`label:`) و `goto` می‌تواند به آن بپرد. در Java labelها فقط برای `break`/`continue` به کار می‌روند و `goto` وجود ندارد.

```cpp
// C++: goto آزاد است
goto end;
end: /* ... */
```

```java
// Java: label فقط برای break/continue
outer: for (...) { break outer; }
```

### ۱۱. ternary به عنوان lvalue

> **تلهٔ C++:** در C++ ternary می‌تواند lvalue باشد و در سمت چپ assignment بنشیند. در Java ternary همیشه rvalue است.

```cpp
// C++
(cond ? a : b) = 5;     // legal — یکی از a/b مقداردهی می‌شود
```

```java
// Java: خطای کامپایل — ternary rvalue است
// (cond ? a : b) = 5;   // ✗
```

### ۱۲. labeled continue

> **تلهٔ C++:** در C++ `continue` نمی‌تواند label بپذیرد (فقط break). در Java، `continue label` به loop labelدار می‌پرد.

```cpp
// C++: continue فقط loop جاری را ادامه می‌دهد
for (...) {
    for (...) {
        continue;    // فقط loop داخلی
    }
}
```

```java
// Java: continue label به outer می‌رود
outer: for (...) {
    for (...) {
        continue outer;    // iteration بعدی outer
    }
}
```
## واژه‌نامه

- **binary numeric promotion:** promotion operandهای عددی برای operation دودویی.
- **widening:** conversion به دامنه بزرگ‌تر.
- **narrowing:** conversion بالقوه lossy با cast.
- **truncation:** حذف fraction به سوی صفر.
- **overflow:** wrap شدن نتیجه خارج از دامنه integral.
- **dividend:** operand چپ تقسیم یا remainder.
- **short-circuit:** اجرا نشدن operand راست وقتی نتیجه معلوم است.
- **eager evaluation:** اجرا شدن همه operandها.
- **fall-through:** ادامه control از case colon به case بعدی.
- **yield:** تولید value در block arm switch expression.
- **exhaustiveness:** پوشش همه مسیرهای switch expression.
- **invariant:** گزاره برقرار در iterationهای loop.
- **definite assignment:** اثبات compiler برای assignment قبل از read.
- **label:** نام statement برای break یا continue.

## دام‌ها و اصلاح برداشت‌ها

**برداشت نادرست:** «دو int fraction می‌دهند.» خیر؛ `/` integral به سوی صفر truncate می‌کند.
**برداشت نادرست:** «علامت `%` همیشه مثبت است.» خیر؛ علامت remainder در Java از dividend است.
**برداشت نادرست:** «`>>>` همان `>>` است.» خیر؛ `>>>` zero-fill و `>>` sign-extend می‌کند.
**برداشت نادرست:** «`&` و `&&` یکی هستند.» روی boolean، `&` eager و `&&` short-circuit است.
**برداشت نادرست:** «arrow switch fall-through دارد.» خیر؛ fall-through ویژگی colon form است.
**برداشت نادرست:** «if عدد می‌پذیرد.» خیر؛ Java boolean صریح می‌خواهد.
**برداشت نادرست:** «`b+=1` با `b=b+1` یکسان compile می‌شود.» خیر؛ اولی narrowing ضمنی دارد.
**برداشت نادرست:** «var promotion را عوض می‌کند.» خیر؛ var نتیجه promotion را می‌گیرد.
**برداشت نادرست:** «floating equality همیشه دقیق است.» خیر؛ `0.1+0.2` مثال کلاسیک خطا است.
**برداشت نادرست:** «break label دو loop را جداگانه می‌شکند.» خیر؛ statement labelدار را تمام می‌کند.
**برداشت نادرست:** «do-while شاید body را اجرا نکند.» خیر؛ دست‌کم یک بار اجرا می‌شود.
**برداشت نادرست:** «for و while scope یکسان دارند.» initializer for بعد از loop دیده نمی‌شود.
**برداشت نادرست:** «continue for update را رد می‌کند.» خیر؛ سپس update اجرا می‌شود.
**برداشت نادرست:** «ternary هر دو branch را اجرا می‌کند.» خیر؛ فقط branch انتخاب‌شده اجرا می‌شود.
**برداشت نادرست:** «switch expression arm بدون value می‌پذیرد.» خیر؛ باید exhaustive باشد و value یا exception بدهد.
**برداشت نادرست:** «`i << 33` روی int صفر می‌دهد.» خیر؛ shift count روی int فقط پنج bit پایین دیده می‌شود، پس `i << 33` معادل `i << 1` است و `1 << 33` برابر 2.
**اصلاح:** برای long شش bit پایین ماسک می‌شود. در شهود، count را پیش از ارزیابی modulo کنید.
**برداشت نادرست:** «`x = x++;` یک واحد به x اضافه می‌کند.» خیر؛ expression `x++` مقدار قدیم را می‌دهد و سپس x یک واحد زیاد می‌شود، ولی assignment بعدی همان مقدار قدیم را دوباره می‌نویسد.
**اصلاح:** نتیجهٔ نهایی x بدون تغییر است. برای mutation واقعی، بنویسید `x++;` به‌تنهایی یا `x += 1;`.
**برداشت نادرست:** «در enhanced-for می‌توان با انتساب به متغیر حلقه، مقدار array را عوض کرد.» خیر؛ متغیر حلقه یک کپی per-iteration از المان فعلی است؛ mutation آن array اصلی را عوض نمی‌کند.
**اصلاح:** برای تغییر ساختاری، از iterator با `remove()`، از index-based for، یا از `List.replaceAll()` استفاده کنید.
**برداشت نادرست:** «اگر local در scope باشد، حتماً مقدار اولیه دارد.» خیر؛ scope با definite assignment یکی نیست. local تنها زمانی قابل خواندن است که در هر مسیر اجرا پیش از read مقدار گرفته باشد.
**اصلاح:** اگر شرط مقداردهی کامل نیست، default محلی بدهید یا initialization را به همهٔ branchها ببرید.
**برداشت نادرست:** «`==` روی Integer همیشه مقدار را مقایسه می‌کند.» خیر؛ `==` روی reference type هویت را مقایسه می‌کند، نه مقدار. عددهای کوچک به‌صورت cached shared هستند و این رفتار را به تصادف شبیه می‌کنند.
**اصلاح:** برای مقایسهٔ مقدار boxed، از `equals()` استفاده کنید: `a.equals(b)` یا `Integer.compare(a,b) == 0`.

**برداشت نادرست:** «`Integer a = 100; Integer b = 100; a == b` همیشه true است.» خیر؛ برای `Integer` (و بقیهٔ wrapperها)، مقادیر در بازهٔ `128-` تا `127` cache می‌شوند ولی خارج از آن شیء جدید ساخته می‌شود. این یک implementation detail است، نه language guarantee.
**اصلاح:** برای مقایسهٔ مقدار boxed، از `equals()` استفاده کنید یا auto-unbox را با `int` ساده انجام دهید.

**برداشت نادرست:** «`a == b` روی reference همیشه content را مقایسه می‌کند اگر `equals` override شده باشد.» خیر؛ `==` هیچ‌گاه متد صدا نمی‌زند. فقط `==` هویت (آدرس object) را مقایسه می‌کند. `equals` متد است و ممکن است content را مقایسه کند ولی ربطی به `==` ندارد.
**اصلاح:** برای مقایسهٔ محتوایی، `equals` (یا `Objects.equals` که null-safe است). برای مقایسهٔ هویتی، `==`.

**برداشت نادرست:** «`Math.floorMod(a, b)` همان `a % b` است.» خیر؛ برای علامت‌های مختلف نتیجه فرق می‌کند. `7 % -2 = 1` ولی `Math.floorMod(7, -2) = -1`. `Math.floorMod` هم‌علامت divisor است.
**اصلاح:** برای cyclic index که می‌خواهید در `[0, n)` بمانید، `Math.floorMod(i, n)` بنویسید.

**برداشت نادرست:** «`do-while` ممکن است صفر بار اجرا شود اگر شرط false باشد.» خیر؛ body دست‌کم یک بار اجرا می‌شود و condition پس از آن سنجیده می‌شود. برای zero-or-more execution باید `while` باشد.
**اصلاح:** از `while (cond) { ... }` برای zero-or-more، از `do { ... } while (cond);` برای at-least-once.

**برداشت نادرست:** «`NaN == NaN` برابر true است.» خیر؛ هیچ مقداری (حتی خود `NaN`) با `==` برابر `NaN` نیست. این از IEEE 754 آمده و رفتار تعریف‌شده است.
**اصلاح:** از `Float.isNaN(x)` یا `Double.isNaN(x)` استفاده کنید.

**برداشت نادرست:** «اگر `x` در همهٔ شاخه‌های `if-else` مقداردهی شود، قطعاً قبل از read مقدار دارد.» تقریباً درست، ولی اگر در یک شاخه `return`/`throw`/`break`/`continue` باشد، compiler شاخه‌های پس از آن را در نظر نمی‌گیرد. شرط definite assignment روی مسیرهای واقعی اجرا حساب می‌شود.
**اصلاح:** اگر شک دارید، مقدار default در ابتدا بدهید (`int x = 0;`) یا invariant را در کامنت روشن کنید.

**برداشت نادرست:** «در switch expression، `default` اختیاری است.» بستگی دارد: برای enum کامل و sealed type اگر همهٔ constantها/subtypeها case شده باشند، `default` اختیاری است. برای `int`/`String` تقریباً همیشه لازم است چون مقدار ممکن است هر چیزی باشد.
**اصلاح:** هر وقت exhaustiveness تضمین نمی‌شود، `default -> ...` بنویسید تا compiler راضی شود.

**برداشت نادرست:** «`continue` در for ابتدا condition را چک می‌کند و سپس update می‌کند.» خیر؛ `continue` در for ابتدا **update** و سپس **condition** را اجرا می‌کند. اگر update side-effect منفی داشته باشد، iteration بعدی ممکن است infinite شود یا skip شود.
**اصلاح:** invariant و progress را قبل از نوشتن `continue` روشن کنید. اگر update پیچیده است، `while` با explicit update بنویسید تا ترتیب روشن باشد.
## کارت‌های مرور تحلیلی

### کارت 1 — نوع literal و promotion

- برای `byte a = 40, b = 2` نوع عبارتٔ `a + b` و نوع متغیر `byte b` پس از `b += 5` را جدا بنویسید؛ یکی int است و دیگری همان byte باقی می‌ماند.
- نوع `char + int` و `int + long` را پیش‌بینی کنید؛ سپس توضیح دهید چرا char تنها در binary numeric promotion ارتقا می‌یابد.
- نوع `long + float` و `float + double` را بنویسید؛ بگویید promotion چرا به سمت بزرگ‌تر می‌رود و نه سمت int.
- یک سناریو انتخاب کنید که `byte x = (byte)(x + 1);` با `x += 1;` رفتار متفاوتی داشته باشد و بنویسید کدام جمع‌و‌جور و ایمن‌تر است.

### کارت 2 — cast، truncation و overflow

- `(int)3.99` و `(int)-3.99` را به ترتیب predict کنید و بگویید چرا floor نیست.
- `(byte)260` و `(byte)128` را محاسبه کنید و بگویید bitهای بالا چرا دور ریخته می‌شوند.
- `Integer.MAX_VALUE + 1` و `Integer.MAX_VALUE * 2` را حساب کنید و توضیح دهید wrap چرا قطعی است ولی قابل اعتماد برای پول نیست.
- یک input کوچک انتخاب کنید که در آن cast `double→int` و cast `long→int` هر دو غلط ظاهر می‌شوند ولی error متفاوت می‌دهند.

### کارت 3 — `/`، `%` و Math.floorMod

- مقادیر `7 / -2`، `7 % -2`، `-7 / 2` و `-7 % 2` را محاسبه کنید و نشان دهید علامت remainder از dividend می‌آید.
- `Math.floorMod(7, -2)` و `Math.floorMod(-7, 2)` را بنویسید و با `%` مقایسه کنید.
- سناریوی cyclic index با step منفی انتخاب کنید (مثلاً `arr[(i - 1 + n) % n]` در برابر `arr[Math.floorMod(i - 1, n)]`) و بگویید کدام برای `i=0` درست کار می‌کند.
- یک input مرزی مثل `n=0` در divisor بنویسید و توضیح دهید چه exception رخ می‌دهد.

### کارت 4 — shift count mask و `>>>`

- `1 << 33` و `1L << 63` و `1L << 64` را محاسبه کنید و mask پنج/شش bit را توضیح دهید.
- `-8 >> 1`، `-8 >>> 1`، `-8 >>> 29` و `-8 >> 29` را بنویسید و نشان دهید `>>>` چگونه zero-fill می‌کند.
- پیش‌بینی کنید `1 << 31` و `1 << 33` چه تفاوتی دارند و بگویید shift count منفی یا بزرگ چه خطایی می‌دهد.
- یک سناریو mask هشت‌بیتی انتخاب کنید و نشان دهید چرا `>>>` با int کافی است ولی برای long باید صریح long استفاده کرد.

### کارت 5 — short-circuit و order

- خروجی `p("L", false) && p("R", true)` و `p("L", true) || p("R", false)` را trace کنید و بگویید چرا side effect راست رخ نمی‌دهد.
- همان سناریو را با `&` و `|` تکرار کنید و نشان دهید eager evaluation چه چیزی را فعال می‌کند.
- بنویسید چرا `obj != null && obj.method()` امن‌تر از `obj.method() || true` است؛ یک ورودی که null باشد انتخاب کنید.
- یک سناریو بنویسید که short-circuit یک exception را کنترل می‌کند و eager بودن همان کد را می‌ترکاند.

### کارت 6 — precedence، cast و ternary

- `1 + 2 * 3`، `1 * 2 + 3` و `(1 + 2) * 3` را محاسبه کنید و precedence ضرب را بر جمع نشان دهید.
- نوع `(byte)(1 + 2)` و `(byte)(a + 1)` را بنویسید و توضیح دهید چرا literal جمع promotion ندارد ولی variable دارد.
- نوع `true ? 1 : 2.0` و `false ? 1 : 2.0` را predict کنید و بگویید ternary چگونه common type را انتخاب می‌کند.
- trace کنید `1 + 2 + "3"` و `"1" + 2 + 3` را، سپس نشان دهید چرا ترتیب ارزیابی چپ‌به‌راست نتیجه را عوض می‌کند.

### کارت 7 — if/else و range ordering

- برای grade با boundaryهای ۶۰ و ۹۰، ordering درست شرط‌ها (تخصصی پیش از عمومی) را بنویسید و دلیل overlap را توضیح دهید.
- برای ورودی‌های ۵۹، ۶۰، ۸۹، ۹۰، ۱۰۰ مقدار خروجی هر ordering را trace کنید.
- یک chain با `if (x >= 60)` قبل از `if (x >= 90)` بنویسید و نشان دهید چرا A هرگز چاپ نمی‌شود.
- بگویید compiler چرا overlap منطقی rangeها را تشخیص نمی‌دهد و چه تستی این regression را پیدا می‌کند.

### کارت 8 — switch statement در برابر switch expression

- برای switch colon form یک case بنویسید که fall-through عمدی دارد (مثلاً دو label با body مشترک) و نشان دهید break کجا لازم است.
- همان منطق را با arrow form بازنویسی کنید و توضیح دهید چرا fall-through حذف می‌شود.
- یک switch expression با block arm بنویسید که `yield` برمی‌گرداند و نشان دهید default چه نقشی دارد.
- دو selector، یکی enum کامل و یکی String، انتخاب کنید و بگویید کدام می‌تواند بدون default باشد و کدام نه.

### کارت 9 — loop invariant و enhanced-for

- یک loop بنویسید که invariant «`sum` برابر جمع عناصر دیده‌شده تا این iteration» دارد و نشان دهید initialization، maintenance و termination.
- trace کنید `for` با `continue` در ابتدای body در برابر `while` با `continue` در ابتدای body و بگویید کدام update را از دست می‌دهد.
- یک enhanced-for روی `int[]` بنویسید، داخل loop مقدار متغیر را عوض کنید، و نشان دهید array اصلی چرا تغییر نمی‌کند.
- نسخهٔ index-based همان enhanced-for را بنویسید که بتواند المان‌ها را در array جایگزین کند، و بگویید چه چیزی به دست آمد.

### کارت 10 — label، scope و definite assignment

- یک `break search` در loop تو در تو بنویسید، trace کنید چند iteration اجرا می‌شود، و نشان دهید label چگونه هر دو loop را پایان می‌دهد.
- یک متغیر در initializer for تعریف کنید، سپس خارج از loop به آن ارجاع دهید و توضیح دهید چرا compile نمی‌شود.
- یک local در دو شاخهٔ if/else مقدار بگیرد و در بیرون خوانده شود؛ سپس همان را با یک شاخهٔ بدون مقدار تکرار کنید و بگویید definite assignment چه نقشی دارد.
- یک سناریو با `continue label` بنویسید که فقط loop بیرونی advancement می‌کند، و نشان دهید loop داخلی چگونه دور انداخته می‌شود.

## چک‌لیست پایان فصل ۲

- [ ] می‌توانم type `byte + byte` را بدون اجرا بگویم.
- [ ] می‌توانم cast، truncation و overflow را جدا کنم.
- [ ] می‌توانم `%` منفی و `>>>` را محاسبه کنم.
- [ ] می‌دانم کجا && به جای & لازم است.
- [ ] rangeهای if را تخصصی به عمومی می‌چینم.
- [ ] switch expression و yield را توضیح می‌دهم.
- [ ] برای هر loop invariant و termination path دارم.
- [ ] label و definite assignment را با scope اشتباه نمی‌گیرم.

## تمرین پروژه‌ای پایان فصل ۲

یک `ScoreBoard` console بسازید که یک `int[]` score را تحلیل می‌کند.

1. با enhanced-for مجموع و میانگین floating-point را حساب کنید.
1. با `%` تعداد زوج/فرد را گزارش دهید و رفتار score منفی را مستند کنید.
1. با switch expression grade A تا F را تولید کنید و input نامعتبر را reject کنید.
1. با loop معمولی نخستین score مردود را پیدا کنید؛ اگر matrix ساختید، labeled break فقط برای پایان search باشد.
1. boundaryهای 59، 60 و 100 و یک input نامعتبر را دستی بررسی کنید.
1. در توضیح پروژه بگویید چرا validation با `&&` نوشته شده است.

