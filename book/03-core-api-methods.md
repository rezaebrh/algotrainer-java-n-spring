# فصل ۳ — Core API و متدها در Java 21

> **مسیر:** Java 21 / OCP Core API
> **مخاطب:** برنامه‌نویس C++ که می‌خواهد method declaration، String API، آرایه، Math و parsing عددی را به‌عنوان ابزار روزانه به‌کار بگیرد.

این فصل متن آموزشی مستقل است: از اصطلاحات استاندارد Java استفاده می‌کند، اما توضیح‌ها، مثال‌ها، دیاگرام‌ها و تمرین‌ها برای همین مسیر یادگیری نوشته شده‌اند. مقایسه با C++ برای کشف تفاوت قراردادها است، نه برای یکی‌گرفتن دو مدل.

## نقشهٔ یادگیری و خروجی مورد انتظار

پس از این فصل باید بتوانید:

1. یک method با return type دلخواه، overload، و `void` بنویسید بدون اینکه compiler در مورد signature شکایت کند؛
2. تشخیص دهید چه چیزی overload می‌شود و چه چیزی نمی‌شود (return type، parameter name، access modifier هیچ‌کدام overload نیستند)؛
3. early `return` را به‌عنوان guard بنویسید و درک کنید چه زمانی `return` از method `void` لازم است؛
4. String API، immutability، literal pool، و `StringBuilder` را درست به‌کار ببرید و از `==` به‌جای `equals` اجتناب کنید؛
5. آرایهٔ ۱بعدی و ۲بعدی بسازید و با `Arrays` (sort، toString، copyOf، equals) کار کنید؛
6. متدهای static `Math` را به‌کار ببرید و `Integer.parseInt`/`valueOf` را با مدیریت `NumberFormatException` بنویسید.

### قرارداد خواندن این فصل

- **قاعدهٔ زبان:** نتیجه‌ای که Java Language Specification برای برنامهٔ قابل مشاهده تعیین می‌کند.
- **جزئیات runtime:** رفتاری که ممکن است در HotSpot یا JVM دیگری رخ دهد؛ برای correctness هرگز به آن تکیه نکنید.
- **ترمیم:** هر جا یک برداشت رایج احتمال دارد مدل ذهنی را منحرف کند، برچسب مفهومِ مناسب برای مرور تطبیقی آمده است.

---

## بخش ۱: متدها، ساخت و فراخوانی در Java 21

> **مسیر:** Java 21 / OCP Core API  
> **مخاطب:** برنامه‌نویس C++ که می‌خواهد قرارداد method declaration، overload و lifecycle یک method ساده Java را از توابع/متدهای C++ جدا کند.

method در Java واحد اصلی سازمان‌دهی رفتار است. هر method یک signature دارد (نام + پارامترها)، یک return type (یا `void`)، یک access modifier، و یک body. method در داخل یک `class` یا `interface` تعریف می‌شود و فراخوانی آن تنها از طریق reference به object (instance method) یا از طریق نام کلاس (static method) ممکن است. این فصل تصمیم‌های روزمره‌ای را پوشش می‌دهد که در نوشتن method اشتباه می‌شوند: overload در برابر override، return زودهنگام، scope پارامترها، varargs و `this`.

مقایسه با C++ برای کشف تفاوت‌های قراردادی است، نه برای هم‌ارز دانستن دو زبان.

## نقشهٔ یادگیری و خروجی مورد انتظار

پس از این فصل باید بتوانید:

1. یک method با return type دلخواه، چندین overload، و `void` بنویسید بدون اینکه compiler در مورد signature شکایت کند؛
2. تشخیص دهید چه چیزی overload می‌شود و چه چیزی نمی‌شود (return type، parameter name، access modifier هیچ‌کدام overload نیستند)؛
3. early `return` را به‌عنوان guard بنویسید و درک کنید چه زمانی `return` از method `void` لازم است؛
4. پارامترها را به‌عنوان local variable بشناسید و از shadowing فیلد با parameter پرهیز کنید؛
5. varargs را درست تعریف و فراخوانی کنید و با overload کردن آن به آرایه دچار ambiguity نشوید؛
6. در یک زنجیرهٔ فراخوانی، رد `this` و reference به فیلدها را بدون سردرگمی دنبال کنید.

### قرارداد خواندن این فصل

- **قاعدهٔ زبان:** نتیجه‌ای که Java Language Specification برای برنامهٔ قابل مشاهده تعیین می‌کند.
- **جزئیات runtime:** رفتاری که ممکن است در HotSpot یا JVM دیگری رخ دهد؛ برای correctness هرگز به آن تکیه نکنید.
- **ترمیم:** هر جا یک برداشت رایج احتمال دارد مدل ذهنی را منحرف کند، برچسب مفهومِ مناسب برای مرور تطبیقی آمده است.

---

## ۱. signature و return type

هر method declaration چهار بخش دارد: **access modifier** (`public`/`protected`/`private` یا default)، **نوع بازگشت** (یک نوع primitive، reference، یا `void`)، **نام**، و **پارامترها** (به ترتیب type و نام). بدنهٔ method در `{ ... }` می‌آید و اگر return type غیر `void` باشد، باید در همهٔ مسیرهای execution مقداری از آن نوع برگرداند.

```java
public int sum(int a, int b) {
    return a + b;                  // return int — با نوع بازگشت سازگار
}

public void log(String msg) {
    if (msg == null) return;       // return; بدون مقدار در void مجاز است
    System.out.println(msg);
}
```

اگر method non-void باشد، compiler **هر مسیر قابل اجرا** را بررسی می‌کند: اگر در شاخه‌ای `return` نباشد، خطای کامپایل است. این همان definite assignment در سطح statement است. اگر method هیچ statement قابل اجرایی نداشته باشد (مثلاً فقط `throw` کند)، باز هم return لازم نیست چون compiler exception را به‌عنوان termination می‌شناسد:

```java
public int parse(String s) {
    if (s == null) {
        throw new IllegalArgumentException("null");
    }
    return Integer.parseInt(s);
    // اگر return را حذف کنید، خطای کامپایل می‌گیرید چون s ممکن است non-null باشد
}
```

> **تلهٔ C++:** در C++ تابع non-void می‌تواند بدون `return` باشد و خواندن مقدار بازگشتی UB است. در Java، compiler این را در سطح type system اجرا می‌کند و اصلاً کامپایل نمی‌شود. این یک ایمنی بنیادی است: متد non-void همیشه یا return دارد یا throw می‌کند.

## ۲. overload در برابر override

**overload**: چند method با **نام یکسان** ولی **signature متفاوت** (تعداد یا نوع پارامترها) در یک کلاس. در زمان فراخوانی، compiler بر اساس نوع آرگومان‌های ایستا (compile-time) یکی را انتخاب می‌کند. این تصمیم به نوع runtime object بستگی ندارد.

**override**: method در subclass با **signature و return type یکسان** (یا covariant) دوباره تعریف می‌شود. در runtime، dispatch بر اساس نوع واقعی object است (virtual dispatch). در این فصل override کمتر مطرح است (subclass در فصل ۴ می‌آید) ولی تشخیص تفاوت overload/override در تصمیم‌گیری روزانه ضروری است.

```java
void print(int x)         { /* ... */ }   // overload 1
void print(String s)      { /* ... */ }   // overload 2
void print(double d)      { /* ... */ }   // overload 3
```

### چه چیزی overload **نمی‌شود**

- **فقط return type متفاوت:** `int get()` و `String get()` در یک کلاس خطای کامپایل هستند. signature شامل return type نمی‌شود.
- **فقط نام پارامتر متفاوت:** `void f(int a)` و `void f(int b)` یک method هستند (duplicate declaration).
- **فقط access modifier متفاوت:** overload نیست (و در بسیاری موارد خطا).
- **varargs و آرایه به‌عنوان امضای متفاوت؟** بسته به context — `void f(int... a)` و `void f(int[] a)` در سطح source code یکسان‌اند و duplicate محسوب می‌شوند.

### قوانین انتخاب overload

compiler در زمان فراخوانی **بهترین match** را با استفاده از ترتیب زیر پیدا می‌کند:

1. exact match (نوع دقیق)
2. widening primitive (مثل `int → long`)
3. widening reference (مثل `Integer → Number` یا `String → Object`)
4. autoboxing یا unboxing
5. varargs (آخرین گزینه)

اگر در هیچ مرحله‌ای unique نباشد، **ambiguous** است و خطای کامپایل می‌دهد. این یکی از رایج‌ترین خطاهای overload است: `null` که می‌تواند هم `String` باشد هم `Integer` و انتخاب compiler مبهم است.

```java
void f(String s) { /* ... */ }
void f(Integer i) { /* ... */ }
f(null);   // ⚠ reference to f is ambiguous
```

> **تلهٔ C++:** در C++ overload می‌تواند شامل const/volatile، pointer، reference، و template باشد و قوانین پیچیده‌تری دارد. در Java، overload ساده‌تر است: فقط تعداد و نوع پارامترها. اگر از C++ عادت به «overload با reference type» دارید، در Java باید با signature primitive/reference صریح کار کنید.

## ۳. early return و guard clause

early return یعنی از method در همان ابتدا خارج شوید اگر precondition برقرار نیست. این الگو nesting را کم می‌کند و خوانایی را بالا می‌برد:

```java
// ✗ deep nesting
String describe(int score) {
    String result;
    if (score >= 0) {
        if (score <= 100) {
            if (score >= 60) {
                result = "pass";
            } else {
                result = "fail";
            }
        } else {
            result = "out of range";
        }
    } else {
        result = "out of range";
    }
    return result;
}

// ✓ guards
String describe(int score) {
    if (score < 0 || score > 100) return "out of range";
    return score >= 60 ? "pass" : "fail";
}
```

guard clause در method‌های validation، parsing، و initialization بسیار رایج است. اگر method چندین precondition دارد، بهتر است guardها در ابتدا باشند و منطق اصلی در انتها — به این ترتیب depth of nesting حداکثر ۲ باقی می‌ماند.

> **تلهٔ C++:** در C++ گاهی early return با RAII و destructor conflict دارد (مثلاً اگر منابعی در ابتدا allocate شده باشند). در Java با try-with-resources این مشکل وجود ندارد چون resource در پایان try بسته می‌شود.

## ۴. پارامترها local variable هستند

پارامترهای method در scope method قابل دسترسی‌اند و **بعد از پایان method از بین می‌روند**. آن‌ها از نظر رفتاری با local variable معمولی یکسان‌اند: definite assignment لازم نیست (پارامتر همیشه مقدار دارد)، final می‌توانند باشند، و می‌توان آن‌ها را shadow کرد (که معمولاً warning می‌دهد).

```java
void f(int x) {                 // x یک local است
    int y = x + 1;              // x در این scope قابل خواندن
    // x و y بعد از return از بین می‌روند
}

void shadowExample(int value) {
    int value = 5;              // ⚠ variable value is already defined in method
}
```

**shadowing** وقتی رخ می‌دهد که local variable (یا پارامتر) همان نام field کلاس را داشته باشد. در آن صورت، در scope local، field با `this.fieldName` قابل دسترسی است:

```java
class Box {
    private int value;
    void setValue(int value) {        // پارامتر value، field value را shadow می‌کند
        this.value = value;           // this.value فیلد، value پارامتر
    }
}
```

بدون `this`، عبارت `value = value` در مثال بالا، پارامتر را به خودش انتساب می‌دهد (no-op) و فیلد تغییر نمی‌کند. این یکی از رایج‌ترین bugهای method نویسی است.

> **تلهٔ C++:** در C++ پارامترها در ابتدای scope method قرار می‌گیرند ولی shadowing فیلد به‌صراحت `this->field` لازم دارد. رفتار یکسان است ولی Java از نظر نوشتاری ساده‌تر است.

## ۵. `this` و زنجیرهٔ فراخوانی

`this` یک reference ضمنی به object فعلی است. در instance method قابل استفاده است؛ در static method **وجود ندارد** (static method به instance تعلق ندارد). کاربردهای `this`:

1. رفع ambiguity بین فیلد و پارامتر: `this.value = value`
2. ارسال object فعلی به method دیگر: `helper.process(this)`
3. فراخوانی یک constructor از constructor دیگر: `this(...)` فقط در اولین خط constructor

```java
class Counter {
    private int count;
    Counter increment() {
        count++;
        return this;        // برای زنجیره‌سازی برمی‌گرداند
    }
}

// زنجیره: c.increment().increment().increment();
```

`this` در lambda expression به capture rule مربوط می‌شود (در فصل ۶)، ولی در method معمولی ساده است: `this` همیشه به receiver فعلی اشاره دارد.

## ۶. varargs

varargs (variable-length arguments) اجازه می‌دهد method با **تعداد متغیر** آرگومان از یک نوع فراخوانی شود. syntax: `Type... name` (سه نقطه). در داخل method، name یک آرایه از آن نوع است.

```java
int sum(int... values) {
    int total = 0;
    for (int v : values) total += v;
    return total;
}

sum();                  // values = [] → total = 0
sum(1);                 // values = [1] → total = 1
sum(1, 2, 3, 4, 5);     // values = [1, 2, 3, 4, 5] → total = 15
```

### قواعد varargs

- **فقط یک varargs** در هر method می‌تواند باشد.
- varargs **باید آخرین پارامتر** باشد.
- method با `int... values` و method با `int[] values` در سطح JVM یکسان‌اند، ولی در source code duplicate محسوب می‌شوند.
- **فراخوانی با آرایهٔ موجود** مجاز است: `sum(new int[]{1, 2, 3})` معادل `sum(1, 2, 3)` است.

### ابهام رایج

```java
void f(int... values) { /* ... */ }
void f(int first, int... rest) { /* ... */ }
f(1, 2, 3);   // به f(int, int...) می‌رود — unambiguous
f(1);         // به f(int...) می‌رود — تنها گزینه
```

اگر overloadی بنویسید که انتخاب بین varargs و آرایه مبهم شود (مثل `f(int...)` و `f(int[])` که duplicate هستند)، compiler خطا می‌دهد. در overload با چند پارامتر، ممکن است فراخوانی `f(1, 2)` هم به `(int, int...)` برود هم به `(int[], int)` (اگر signature دوم مجاز باشد) — در آن صورت ambiguous.

> **تلهٔ C++:** در C++ varargs به شکل `...` (C-style) یا initializer_list/vector وجود دارد. در Java varargs type-safe است و در سطح JVM به آرایه compile می‌شود، بنابراین overhead runtime ندارد.

## ۷. static method و instance method

**static method** متعلق به کلاس است، نه به instance. فراخوانی آن از طریق `ClassName.method()` یا از داخل method static/instance همان کلاس (بدون پیشوند) ممکن است. در static method:

- `this` در دسترس **نیست**.
- فقط static field قابل دسترسی است (نه instance field).
- method instance قابل فراخوانی **نیست** (مگر از طریق reference صریح).

**instance method** متعلق به object است. در آن:

- `this` در دسترس است.
- هم static و هم instance field قابل دسترسی است.
- می‌تواند static method فراخوانی کند.

```java
class MathHelper {
    static final double PI = 3.14159;       // static field
    int instanceCount = 0;                   // instance field

    static double circleArea(double r) {     // static method
        return PI * r * r;                   // فقط static field
        // return instanceCount;            // ⚠ غیرقابل دسترس
    }

    int incrementCount() {                   // instance method
        instanceCount++;
        return instanceCount;
    }
}

// فراخوانی
double a = MathHelper.circleArea(2.0);      // از طریق کلاس
MathHelper h = new MathHelper();
int c = h.incrementCount();                 // از طریق instance
```

> **تلهٔ C++:** در C++ تابع static در کلاس معنی متفاوتی دارد (internal linkage در translation unit). در Java static method صرفاً متد بدون `this` است. اگر از C++ عادت به «static = helper» دارید، در Java هم هست، ولی دلیلش متفاوت است.

## ۸. recursion

method می‌تواند خودش را فراخوانی کند. هر فراخوانی یک **stack frame** جدید ایجاد می‌کند و پارامترها و local variableهای آن frame مستقل هستند. recursion باید:

1. **base case** داشته باشد (شرطی که در آن بازگشت متوقف می‌شود).
2. به سمت base case **پیشرفت** کند (پارامتر کوچک‌تر شود، accumulator جمع شود).

```java
int factorial(int n) {
    if (n <= 1) return 1;            // base case
    return n * factorial(n - 1);     // پیشرفت به سمت n=1
}
```

اگر base case نداشته باشید یا پیشرفت نکنید، `StackOverflowError` رخ می‌دهد — JVM stack پر می‌شود. این یکی از معدود خطاهایی است که در Java recoverable نیست: thread می‌میرد و thread‌های دیگر معمولاً آسیب نمی‌بینند (مگر اینکه به اشتراک گذاشته شده باشند).

> **تلهٔ C++:** در C++ recursion می‌تواند با `tail call optimization` در بعضی کامپایلرها بهینه شود. در Java، JVM استاندارد tail call optimization ندارد و هر فراخوانی frame جدید می‌گیرد. برای الگوریتم‌های بازگشتی عمیق (مثل DFS روی گراف بزرگ) باید به iterative تبدیل شود.

## مثال‌های اجرایی و تحلیل

### مثال 1 — run id=g3-overload-pick

<!-- verify: run id=g3-overload-pick -->
```java
class OverloadPick {
    static void f(int x) { System.out.println("int " + x); }
    static void f(long x) { System.out.println("long " + x); }
    static void f(Integer x) { System.out.println("Integer " + x); }
    public static void main(String[] args) {
        f(5);
        f(5L);
        f((Integer) 5);
    }
}
```

خروجی:
```text
int 5
long 5
Integer 5
```

exact match `int`، سپس exact match `long`، سپس boxing. widening قبل از boxing ترجیح داده می‌شود.

### مثال 2 — compile-fail id=g3-same-erasure

<!-- verify: compile-fail id=g3-same-erasure -->
```java
class SameErasure {
    static int get() { return 1; }
    static String get() { return "x"; }   // ⚠ duplicate method, only return type differs
    public static void main(String[] args) { System.out.println(get()); }
}
```

کامپایل نمی‌شود اگر خط دوم را از حالت comment خارج کنید: return type در signature نیست، پس دو method با نام و پارامتر یکسان duplicate محسوب می‌شوند.

### مثال 3 — run id=g3-varargs-empty

<!-- verify: run id=g3-varargs-empty -->
```java
class VarargsEmpty {
    static int sum(int... values) {
        int total = 0;
        for (int v : values) total += v;
        return total;
    }
    public static void main(String[] args) {
        System.out.println(sum());
        System.out.println(sum(1, 2, 3));
    }
}
```

خروجی:
```text
0
6
```

فراخوانی `sum()` آرایهٔ خالی به method می‌فرستد.

### مثال 4 — run id=g3-guard-return

<!-- verify: run id=g3-guard-return -->
```java
class GuardReturn {
    static String describe(int score) {
        if (score < 0 || score > 100) return "out of range";
        return score >= 60 ? "pass" : "fail";
    }
    public static void main(String[] args) {
        System.out.println(describe(85));
        System.out.println(describe(45));
        System.out.println(describe(150));
    }
}
```

خروجی:
```text
pass
fail
out of range
```

guard clause در ابتدا، منطق اصلی در انتها.

### مثال 5 — run id=g3-this-shadow

<!-- verify: run id=g3-this-shadow -->
```java
class ThisShadow {
    private int value;
    void setValue(int value) {
        this.value = value;
    }
    int getValue() { return value; }
    public static void main(String[] args) {
        ThisShadow t = new ThisShadow();
        t.setValue(42);
        System.out.println(t.getValue());
    }
}
```

خروجی:
```text
42
```

بدون `this`، انتساب به خود پارامتر می‌شد و فیلد تغییر نمی‌کرد.

### مثال 6 — compile-fail id=g3-this-in-static

<!-- verify: compile-fail id=g3-this-in-static -->
```java
class ThisInStatic {
    static void f() {
        System.out.println(this);    // ⚠ cannot use this in a static context
    }
    public static void main(String[] args) { f(); }
}
```

کامپایل نمی‌شود: `this` در static method در دسترس نیست.

### مثال 7 — run id=g3-recursion-factorial

<!-- verify: run id=g3-recursion-factorial -->
```java
class RecursionFactorial {
    static int factorial(int n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }
    public static void main(String[] args) {
        for (int i = 0; i <= 5; i++) {
            System.out.println(i + "! = " + factorial(i));
        }
    }
}
```

خروجی:
```text
0! = 1
1! = 1
2! = 2
3! = 6
4! = 24
5! = 120
```

base case در n≤1، پیشرفت به سمت n=1.

### مثال 8 — run id=g3-stack-overflow

<!-- verify: skip id=g3-stack-overflow reason=would-throw-StackOverflowError -->
```java
class StackOverflow {
    static int rec(int n) { return rec(n + 1); }
    public static void main(String[] args) {
        try {
            System.out.println(rec(0));
        } catch (StackOverflowError e) {
            System.out.println("caught");
        }
    }
}
```

این کد در runtime به `StackOverflowError` می‌خورد (base case ندارد). skip شده چون نمی‌تواند بدون خطا اجرا شود. در عمل، stack size در JVM محدود است (~512KB default در main thread) و recursion بیش از چند هزار فراخوانی معمولاً crash می‌کند.


---

## بخش ۲: String، immutability و API آن در Java 21

> **مسیر:** Java 21 / OCP Core API  
> **مخاطب:** برنامه‌نویس C++ که می‌خواهد `String` و `StringBuilder` را به‌عنوان API روزمره (نه نوع ابتدایی) بفهمد و از دام‌های معروف آن (== ، interning، concat در loop) دوری کند.

`String` در Java یک **reference type** است که نشان‌دهندهٔ دنباله‌ای از کاراکترهای UTF-16 است. سه ویژگی آن در استفادهٔ روزمره تعیین‌کننده‌اند: **immutability** (هر String قابل تغییر نیست)، **literal pool** (literal های یکسان به یک reference اشاره می‌کنند)، و **API غنی** (متدهایی مثل `substring`، `indexOf`، `split`، `replace`). این فصل هر سه را با دقت بررسی می‌کند و به `StringBuilder` و `String.format` نیز می‌پردازد.

مقایسه با C++: `std::string` در C++ قابل تغییر است و مقایسه با `==` محتوا را می‌سنجد. در Java، `==` روی reference **هویت** را مقایسه می‌کند؛ برای محتوا از `.equals()` استفاده کنید. این تفاوت منبع اصلی bug در کدهای منتقل‌شده است.

## نقشهٔ یادگیری و خروجی مورد انتظار

پس از این فصل باید بتوانید:

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


---

## بخش ۳: آرایه، Math و parsing در Java 21

> **مسیر:** Java 21 / OCP Core API  
> **مخاطب:** برنامه‌نویس C++ که می‌خواهد آرایه‌های primitive/reference، محدودیت‌های length، و متدهای static کلاس‌های `java.lang.Math` و `java.util.Arrays` را به‌عنوان ابزار روزانه به‌کار بگیرد.

آرایه در Java یک **object** است (حتی آرایهٔ primitive)، با طول ثابت که در ساخت تعیین می‌شود. `length` فیلد است نه متد (برخلاف `String.length()`). این فصل آرایهٔ ۱بعدی و ۲بعدی، خطاهای bounds، کلاس `Arrays` (sort، toString، copyOf، equals)، متدهای static `Math`، و parsing عددی را پوشش می‌دهد.

مقایسه با C++: آرایه در C++ اشاره‌گر به حافظهٔ contiguous است؛ `a[i]` بدون bounds check است. در Java هر `arr[i]` bounds check می‌شود (هزینهٔ اندک ولی ایمنی بالا).

## نقشهٔ یادگیری و خروجی مورد انتظار

پس از این فصل باید بتوانید:

1. آرایهٔ ۱بعدی و ۲بعدی بسازید و با initializer literal مقداردهی کنید؛
2. `ArrayIndexOutOfBoundsException` و `NullPointerException` را از هم تشخیص دهید و دام‌های آن‌ها را بشناسید؛
3. از `Arrays.sort`/`toString`/`copyOf`/`equals` برای کار روزمره استفاده کنید؛
4. متدهای static `Math` را برای min/max/abs/round/pow/random به‌کار ببرید؛
5. `Integer.parseInt` و `Integer.valueOf` را به‌درستی استفاده کنید و `NumberFormatException` را catch کنید.

### قرارداد خواندن این فصل

- **قاعدهٔ زبان:** نتیجه‌ای که JLS برای برنامهٔ قابل مشاهده تعیین می‌کند.
- **جزئیات runtime:** bounds check در هر `arr[i]`، overhead ناچیز در JIT.
- **ترمیم:** هر جا یک برداشت رایج مدل ذهنی را منحرف می‌کند، برچسب مفهوم آمده است.

---

## ۱. آرایهٔ ۱بعدی

سه روش اصلی ساخت آرایه در Java:

```java
int[] a = new int[5];             // طول ۵، مقدار پیش‌فرض 0
int[] b = {1, 2, 3, 4, 5};          // initializer literal
int[] c = new int[]{1, 2, 3};       // anonymous array — می‌توان به‌عنوان آرگومان فرستاد
```

**طول ثابت است.** پس از `new int[5]`, نمی‌توانید طول را عوض کنید. اگر نیاز به resize دارید، از `Arrays.copyOf` استفاده کنید (یک آرایهٔ جدید می‌سازد). برای dynamic size، `ArrayList` (در فصل ۶) مناسب‌تر است.

### دسترسی و bounds

```java
int[] a = {10, 20, 30};
a[0];          // 10
a[2];          // 30
a[3];          // ⚠ ArrayIndexOutOfBoundsException — index معتبر نیست
a[-1];         // ⚠ ArrayIndexOutOfBoundsException
a.length;      // 3 (فیلد، نه متد)
```

هر `arr[i]` در runtime چک می‌شود: اگر `i` خارج از `[0, length)` باشد، exception. این bounds check توسط JIT در بسیاری از موارد حذف می‌شود (escape analysis و hoisting)، ولی در سطح source code باید فرض کنید هست.

### `length` فیلد است، `length()` متد است

| ساختار | دسترسی به طول | نوع |
|---|---|---|
| آرایه | `arr.length` | فیلد (بدون پرانتز) |
| String | `s.length()` | متد (با پرانتز) |
| `List<T>` | `list.size()` | متد (با پرانتز) |
| `Collection<T>` | `c.size()` | متد (با پرانتز) |

این تفاوت syntax یکی از رایج‌ترین خطاهای syntax در Java است.

### مقدار پیش‌فرض

آرایه‌ای که با `new` ساخته می‌شود، مقادیر پیش‌فرض دارد:

- `int[]` → همه ۰
- `boolean[]` → همه `false`
- `String[]` → همه `null` (reference)
- `double[]` → همه ۰٫۰

این با local variable متفاوت است (که مقدار پیش‌فرض ندارد و definite assignment لازم دارد).

## ۲. آرایهٔ ۲بعدی و jagged array

آرایهٔ ۲بعدی در Java **آرایه‌ای از آرایه‌ها** است:

```java
int[][] grid = new int[3][4];           // 3 سطر، 4 ستون
int[][] triangle = new int[3][];        // jagged: هر سطر طول متفاوت
triangle[0] = new int[1];
triangle[1] = new int[2];
triangle[2] = new int[3];
```

**jagged array** به شما اجازه می‌دهد سطرهای با طول متفاوت داشته باشید. این در الگوریتم‌های مثلثی (مثل dynamic programming روی مثلث پاسکال) و sparse data رایج است. در C++ شما باید با pointer-to-pointer این کار را دستی انجام دهید.

```java
int[][] grid = {{1, 2}, {3, 4}, {5, 6}};
grid.length;       // 3 (تعداد سطر)
grid[0].length;    // 2 (طول سطر اول)
```

> **تلهٔ C++:** در C++ آرایهٔ ۲بعدی contiguous است (`int grid[3][4]`). در Java آرایهٔ ۲بعدی contiguous نیست: هر سطر یک object جداگانه است. اگر به memory layout وابسته‌اید، باید ۱بعدی با `index = row * cols + col` بسازید.

## ۳. `java.util.Arrays` — متدهای static

`Arrays` کلاسی با متدهای static برای کار با آرایه است. مهم‌ترین آن‌ها:

### `toString` و `deepToString`

```java
int[] a = {1, 2, 3};
System.out.println(Arrays.toString(a));        // [1, 2, 3]

int[][] g = {{1, 2}, {3, 4}};
System.out.println(Arrays.toString(g));        // [[I@..., [I@...] — hash codes
System.out.println(Arrays.deepToString(g));    // [[1, 2], [3, 4]] — بازگشتی
```

`toString` روی آرایه ۲بعدی hash code چاپ می‌کند. برای nested، `deepToString` لازم است.

### `sort`

```java
int[] a = {3, 1, 4, 1, 5};
Arrays.sort(a);          // [1, 1, 3, 4, 5] — Dual-Pivot Quicksort برای primitive
```

برای آرایهٔ reference، `sort` از `Comparable` (natural order) یا `Comparator` (custom) استفاده می‌کند. primitive بدون boxing sort می‌شود (سریع).

### `copyOf` و `copyOfRange`

```java
int[] a = {1, 2, 3, 4, 5};
int[] b = Arrays.copyOf(a, 3);       // [1, 2, 3] — کوتاه‌شده
int[] c = Arrays.copyOf(a, 7);       // [1, 2, 3, 4, 5, 0, 0] — extended با default
int[] d = Arrays.copyOfRange(a, 1, 4);  // [2, 3, 4] — از 1 تا 4 (exclusive)
```

برای آرایهٔ ۲بعدی، `copyOf` shallow است (فقط reference سطرها کپی می‌شود). برای deep copy باید سطر به سطر کپی کنید یا از stream استفاده کنید.

### `equals` و `deepEquals`

```java
int[] a = {1, 2, 3};
int[] b = {1, 2, 3};
System.out.println(a.equals(b));             // false — == reference
System.out.println(Arrays.equals(a, b));     // true — مقایسهٔ محتوا
```

### `fill` و `setAll`

```java
int[] a = new int[5];
Arrays.fill(a, 7);             // [7, 7, 7, 7, 7]

int[] b = new int[5];
Arrays.setAll(b, i -> i * i);  // [0, 1, 4, 9, 16] — i برای هر index
```

`setAll(IntFunction)` یک `IntUnaryOperator` می‌گیرد (در Java 8+).

### `stream` و `parallelSort`

```java
int[] a = {3, 1, 4, 1, 5};
int sum = Arrays.stream(a).sum();    // 14
```

از Java 8، `Arrays.stream(T[])` یک `Stream<T>` می‌سازد که می‌تواند `.sum()`، `.average()`، `.max()` و غیره داشته باشد. `parallelSort` نسخهٔ موازی `sort` است (multi-thread).

> **تلهٔ C++:** در C++ `std::sort` از introsort استفاده می‌کند. در Java `Arrays.sort` برای primitive Dual-Pivot Quicksort و برای reference TimSort است. اگر به algorithm خاصی نیاز دارید، باید خودتان بنویسید.

## ۴. Enhanced-for روی آرایه

enhanced-for (for-each) ساده‌ترین راه پیمایش آرایه است:

```java
int[] a = {1, 2, 3, 4, 5};
for (int x : a) {
    System.out.println(x);
}
```

تفاوت با for کلاسیک: **index ندارید.** اگر به index نیاز دارید (مثلاً برای mutation شرطی)، باید `for (int i = 0; i < a.length; i++)` بنویسید. متغیر loop (`x`) کپی element است (در آرایهٔ primitive، کپی value؛ در آرایهٔ reference، کپی reference).

```java
int[] a = {1, 2, 3};
for (int x : a) x = 0;       // تغییر x آرایه را عوض نمی‌کند
System.out.println(a[0]);    // 1

int[][] g = {{1, 2}, {3, 4}};
for (int[] row : g) row[0] = 0;   // row کپی reference است؛ تغییر از طریق آن قابل مشاهده
System.out.println(g[0][0]);      // 0
```

> **تلهٔ C++:** در C++ range-based for با `auto&` قابل mutate است، `auto` (by value) نه. در Java enhanced-for **همیشه** کپی است.

## ۵. `java.lang.Math` — متدهای static

`Math` تمام متدهایش static است. مهم‌ترین‌ها:

```java
int a = Math.max(3, 7);          // 7
int b = Math.min(3, 7);          // 3
int c = Math.abs(-5);            // 5
long d = Math.round(3.7);        // 4 (long round)
double e = Math.floor(3.7);       // 3.0
double f = Math.ceil(3.2);       // 4.0
double g = Math.pow(2, 10);      // 1024.0
double h = Math.sqrt(2);         // 1.414...
double i = Math.random();         // [0.0, 1.0)
```

### `Math.random` و `Random`

`Math.random()` یک `double` در `[0.0, 1.0)` برمی‌گرداند. برای عدد صحیح در بازه:

```java
int dice = (int) (Math.random() * 6) + 1;     // 1..6
```

برای کاربرد جدی‌تر، `java.util.Random` یا `ThreadLocalRandom.current()` مناسب‌تر است:

```java
Random r = new Random(42);                     // seed ثابت → reproducible
int x = r.nextInt(100);                        // 0..99

int y = ThreadLocalRandom.current().nextInt(100);  // thread-safe، بدون contention
```

> **تلهٔ C++:** در C++ `rand()` global state است و thread-unsafe. در Java `ThreadLocalRandom` thread-local است و در محیط multi-thread سریع‌تر است.

### `Math.addExact` و overflow detection

برای عملیاتی که نمی‌خواهید wrap شوند، `Math.addExact(a, b)` و `Math.multiplyExact(a, b)` در overflow `ArithmeticException` پرتاب می‌کنند (از Java 8):

```java
int a = Math.addExact(Integer.MAX_VALUE, 1);    // ArithmeticException
```

این در codeی که عدد دقیق می‌خواهد (مثل financial بدون BigDecimal) مفید است.

## ۶. `Integer.parseInt` و `valueOf`

دو راه اصلی برای تبدیل `String` به `int`:

```java
int a = Integer.parseInt("42");         // primitive
Integer b = Integer.valueOf("42");      // wrapper
```

تفاوت‌ها:

- `parseInt` **همیشه** primitive جدید می‌سازد.
- `valueOf` از cache داخلی استفاده می‌کند: برای مقادیر `-128..127` (و قابل تنظیم با `-XX:AutoBoxCacheMax`) یک instance مشترک برمی‌گرداند. برای مقادیر بزرگ‌تر، instance جدید می‌سازد ولی باز هم به اندازهٔ `new Integer(...)` کارایی دارد (و deprecated نیست).
- برای اکثر استفاده‌ها، **autoboxing** کافی است: `Integer x = 42;` کامپایلر `valueOf` را صدا می‌زند.

### `NumberFormatException`

اگر String قابل parse نباشد، هر دو متد `NumberFormatException` (زیرکلاس `IllegalArgumentException`) پرتاب می‌کنند:

```java
try {
    int n = Integer.parseInt("3.14");    // ⚠ NumberFormatException
} catch (NumberFormatException e) {
    System.out.println("not an int");
}
```

متدهای مرتبط:

- `Integer.parseUnsignedInt(s)` — بدون علامت، `s` نمی‌تواند منفی باشد
- `Long.parseLong(s, radix)` — radix مشخص (مثل ۱۶ برای hex)
- `Double.parseDouble(s)` — double، `"3.14"` و `"Infinity"` و `"NaN"` مجاز

> **تلهٔ C++:** در C++ `std::stoi` اگر parse نشود `std::invalid_argument` یا `std::out_of_range` می‌دهد. در Java `NumberFormatException` هر دو حالت را پوشش می‌دهد (out of range نیز NFE است).

## ۷. `String` به عدد — مسیر امن

```java
String input = "42";
try {
    int n = Integer.parseInt(input.trim());
    System.out.println("parsed: " + n);
} catch (NumberFormatException e) {
    System.out.println("invalid input: " + input);
}
```

الگوی استاندارد:

1. `input.trim()` — حذف whitespace (مهم: leading/trailing space می‌تواند parse را بشکند)
2. `parseInt` — در try/catch
3. اگر نیاز به validation بیشتر (مثلاً فقط digit)، از regex استفاده کنید قبل از parse

```java
if (input.matches("-?\\d+")) {     // فقط digit و یک علامت منفی اختیاری
    int n = Integer.parseInt(input);
    // ...
}
```

## مثال‌های اجرایی و تحلیل

### مثال 1 — run id=g3-array-defaults

<!-- verify: run id=g3-array-defaults -->
```java
class ArrayDefaults {
    public static void main(String[] args) {
        int[] a = new int[3];
        String[] s = new String[3];
        System.out.println("a[0]=" + a[0]);
        System.out.println("s[0]=" + s[0]);
        System.out.println("a.length=" + a.length);
    }
}
```

خروجی:
```text
a[0]=0
s[0]=null
a.length=3
```

primitive default 0، reference default null، length فیلد.

### مثال 2 — run id=g3-array-oob

<!-- verify: run id=g3-array-oob -->
```java
class ArrayOob {
    public static void main(String[] args) {
        int[] a = {1, 2, 3};
        try {
            System.out.println(a[3]);
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("caught oob");
        }
        int[] n = null;
        try {
            System.out.println(n[0]);
        } catch (NullPointerException e) {
            System.out.println("caught npe");
        }
    }
}
```

خروجی:
```text
caught oob
caught npe
```

out-of-bounds و null array دو exception متفاوت می‌دهند.

### مثال 3 — run id=g3-jagged

<!-- verify: run id=g3-jagged -->
```java
class Jagged {
    public static void main(String[] args) {
        int[][] t = new int[3][];
        t[0] = new int[]{1};
        t[1] = new int[]{2, 3};
        t[2] = new int[]{4, 5, 6};
        for (int[] row : t) {
            for (int v : row) System.out.print(v + " ");
            System.out.println();
        }
    }
}
```

خروجی:
```text
1
2 3
4 5 6
```

هر سطر می‌تواند طول مستقل داشته باشد.

### مثال 4 — run id=g3-arrays-sort

<!-- verify: run id=g3-arrays-sort -->
```java
import java.util.Arrays;
class ArraysSort {
    public static void main(String[] args) {
        int[] a = {5, 2, 8, 1, 9};
        Arrays.sort(a);
        System.out.println(Arrays.toString(a));

        int[] b = {1, 2, 3};
        int[] c = {1, 2, 3};
        System.out.println("==: " + (b == c));
        System.out.println("equals: " + Arrays.equals(b, c));
    }
}
```

خروجی:
```text
[1, 2, 5, 8, 9]
==: false
equals: true
```

`==` روی reference مقایسه می‌کند، `Arrays.equals` محتوا را.

### مثال 5 — run id=g3-deep-tostring

<!-- verify: run id=g3-deep-tostring -->
```java
import java.util.Arrays;
class DeepToString {
    public static void main(String[] args) {
        int[][] g = {{1, 2}, {3, 4}};
        System.out.println(Arrays.deepToString(g));
    }
}
```

خروجی:
```text
[[1, 2], [3, 4]]
```

`deepToString` محتوای nested را بازگشتی چاپ می‌کند. `toString` روی آرایهٔ ۲بعدی فقط hash code هر سطر را چاپ می‌کند و برای دیدن محتوا قابل استفاده نیست.

### مثال 6 — run id=g3-math-basic

<!-- verify: run id=g3-math-basic -->
```java
class MathBasic {
    public static void main(String[] args) {
        System.out.println(Math.max(3, 7));
        System.out.println(Math.abs(-42));
        System.out.println(Math.round(3.7));
        System.out.println(Math.floor(3.7));
        System.out.println(Math.ceil(3.2));
        System.out.println(Math.pow(2, 10));
    }
}
```

خروجی:
```text
7
42
4
3.0
4.0
1024.0
```

`round` long برمی‌گرداند، `floor`/`ceil` double.

### مثال 7 — run id=g3-random-bounded

<!-- verify: run id=g3-random-bounded -->
```java
import java.util.Random;
class RandomBounded {
    public static void main(String[] args) {
        Random r = new Random(42);
        for (int i = 0; i < 5; i++) {
            System.out.println(r.nextInt(10));     // 0..9
        }
    }
}
```

خروجی:
```text
0
3
8
4
0
```

seed ثابت → sequence قابل بازتولید. (مقادیر دقیق به الگوریتم JDK وابسته{Z}اند؛ در OpenJDK 17+ با LXM این sequence تولید می{Z}شود.)

### مثال 8 — run id=g3-parseint-nfe

<!-- verify: run id=g3-parseint-nfe -->
```java
class ParseIntNfe {
    public static void main(String[] args) {
        for (String s : new String[]{"42", "  7 ", "3.14", "abc", ""}) {
            try {
                int n = Integer.parseInt(s.trim());
                System.out.println(s + " -> " + n);
            } catch (NumberFormatException e) {
                System.out.println(s + " -> NFE");
            }
        }
    }
}
```

خروجی:
```text
42 -> 42
  7  -> 7
3.14 -> NFE
abc -> NFE
 -> NFE
```

`"  7 "` پس از trim می‌شود `"7"` و قابل parse. `""` و حروف و نقطه NFE می‌دهند.

### مثال 9 — run id=g3-add-exact

<!-- verify: run id=g3-add-exact -->
```java
class AddExact {
    public static void main(String[] args) {
        try {
            int x = Math.addExact(Integer.MAX_VALUE, 1);
            System.out.println("ok: " + x);
        } catch (ArithmeticException e) {
            System.out.println("overflow detected");
        }
    }
}
```

خروجی:
```text
overflow detected
```

`Math.addExact` در overflow exception می‌دهد، برخلاف `+` که wrap می‌کند.

### مثال 10 — run id=g3-copyof-extend

<!-- verify: run id=g3-copyof-extend -->
```java
import java.util.Arrays;
class CopyOfExtend {
    public static void main(String[] args) {
        int[] a = {1, 2, 3};
        int[] b = Arrays.copyOf(a, 5);
        System.out.println(Arrays.toString(b));
    }
}
```

خروجی:
```text
[1, 2, 3, 0, 0]
```

extend با default value (0 برای int).



## مقایسه‌های لازم با C++

### method declaration

> **تلهٔ C++:** در C++ تابع می‌تواند بدون `return` در non-void باشد و خواندن مقدار بازگشتی UB است. در Java، compiler در سطح type system این را اجرا می‌کند و اصلاً کامپایل نمی‌شود.

### overload

> **تلهٔ C++:** در C++ overload می‌تواند شامل const/volatile، pointer، reference و template باشد و قوانین پیچیده‌تری دارد. در Java فقط تعداد و نوع پارامترها.

### early return

> **تلهٔ C++:** در C++ گاهی early return با RAII و destructor conflict دارد (مثلاً اگر منابعی در ابتدا allocate شده باشند). در Java با try-with-resources این مشکل وجود ندارد.

### shadowing

> **تلهٔ C++:** در C++ پارامترها در ابتدای scope method قرار می‌گیرند ولی shadowing فیلد به‌صراحت `this->field` لازم دارد. در Java `this.field` کافی است.

### `==` در برابر `equals` روی String

> **تلهٔ C++:** در C++ `==` روی `std::string` محتوا را مقایسه می‌کند. در Java `==` هویت را می‌سنجد. این تفاوت بزرگ‌ترین منبع bug در port از C++ به Java است.

### `String` immutable

> **تلهٔ C++:** در C++ `std::string` قابل تغییر است. `s.toUpperCase()` در بعضی implementationها درجا تغییر می‌کند، در بعضی دیگر new می‌سازد. در Java رفتار کاملاً مشخص است: **همیشه** String جدید.

### String literal pool

> **تلهٔ C++:** در C++ چیزی به نام string literal pool وجود ندارد. در Java این رفتار **مشخص** است و بیشتر برنامه‌نویس‌ها انتظارش را ندارند.

### concat در حلقه

> **تلهٔ C++:** در C++ `s += piece` در همان `std::string` تغییر ایجاد می‌کند (in-place). در Java `s = s + piece` **همیشه** String جدید می‌سازد. در حلقهٔ بزرگ باید StringBuilder بنویسید.

### varargs

> **تلهٔ C++:** در C++ varargs به شکل `...` (C-style) یا initializer_list/vector وجود دارد. در Java varargs type-safe است و در سطح JVM به آرایه compile می‌شود.

### آرایه contiguous در برابر آرایه آرایه

> **تلهٔ C++:** در C++ آرایهٔ ۲بعدی contiguous است. در Java آرایهٔ ۲بعدی contiguous نیست: هر سطر یک object جداگانه است.

### bounds check

> **تلهٔ C++:** در C++ `a[i]` بدون bounds check است. در Java هر `arr[i]` bounds check می‌شود (هزینهٔ اندک ولی ایمنی بالا).

### `length` فیلد در برابر متد

> **تلهٔ C++:** در C++ آرایه length را با `sizeof(a)/sizeof(a[0])` یا `std::size(a)` می‌گیرید. در Java آرایه `.length` فیلد دارد، String `.length()` متد، و List `.size()` متد. تفاوت syntax منبع رایج bug است.

### enhanced-for mutate

> **تلهٔ C++:** در C++ range-based for با `auto&` قابل mutate است. در Java enhanced-for **همیشه** کپی است.

### `String.format` type-safe

> **تلهٔ C++:** در C++ `printf` varargs و type-unsafe است. در Java `String.format` type-safe است و در ناسازگاری type، `IllegalFormatConversionException` می‌دهد.

## واژه‌نامه

- **method:** واحد رفتار در کلاس، با signature، return type، و body.
- **signature:** نام method به‌همراه تعداد و نوع پارامترها (return type و parameter name جزو signature نیست).
- **overload:** چند method با نام یکسان ولی signature متفاوت در یک کلاس.
- **override:** بازتعریف method در subclass با signature و return type یکسان (در فصل ۴).
- **varargs:** پارامتری که تعداد متغیر آرگومان از یک نوع می‌پذیرد، در source `Type...`، در JVM آرایه.
- **guard clause:** early return در ابتدای method برای رد کردن precondition نامعتبر.
- **immutability:** ویژگی‌ای که object پس از ساخت تغییر نمی‌کند.
- **literal pool:** منطقه‌ای در heap که String literalهای یکسان به یک reference اشاره می‌کنند.
- **intern:** فراخوانی `String.intern()` برای اضافه کردن یک String به pool.
- **enhanced-for (for-each):** سینتکس پیمایش collection یا array بدون index.
- **text block:** literal چندخطی که با `"""` شروع و تمام می‌شود.
- **jagged array:** آرایه‌ای که سطرهای آن طول متفاوت دارند.
- **bounds check:** بررسی runtime برای اطمینان از معتبر بودن index آرایه.
- **definite assignment:** الزام compiler برای مقداردهی local variable پیش از read.

## دام‌ها و اصلاح برداشت‌ها

**برداشت نادرست:** «return type متفاوت overload می‌شود.» خیر؛ فقط signature (تعداد و نوع پارامترها) overload است.
**اصلاح:** اگر دو method فقط return type متفاوت دارند، duplicate هستند و خطای کامپایل می‌دهند.

**برداشت نادرست:** «`f(null)` بین overload `String` و `Integer` قابل تشخیص است.» خیر؛ compiler بدون type cast نمی‌تواند انتخاب کند و ambiguous می‌شود.
**اصلاح:** اگر overload `String`/`Integer` دارید، `f((String) null)` یا `f((Integer) null)` بنویسید.

**برداشت نادرست:** «`this` در static method با `this == null` قابل استفاده است.» خیر؛ static method به instance تعلق ندارد و `this` کامپایل نمی‌شود.
**اصلاح:** اگر نیاز به state دارید، method را instance کنید یا state را به‌عنوان پارامتر بفرستید.

**برداشت نادرست:** «`s.toUpperCase()` رشتهٔ اصلی را تغییر می‌دهد.» خیر؛ String immutable است و یک String جدید برمی‌گرداند.
**اصلاح:** اگر می‌خواهید تغییر کنید، `s = s.toUpperCase();` بنویسید.

**برداشت نادرست:** «`==` روی String همیشه محتوا را مقایسه می‌کند.» خیر؛ `==` هویت (reference) را می‌سنجد. literalهای یکسان به یک object اشاره می‌کنند ولی `new String(...)` نه.
**اصلاح:** همیشه از `.equals()` استفاده کنید، یا از `Objects.equals(a, b)` برای null-safe.

**برداشت نادرست:** «String concat در حلقه با `+` به‌اندازهٔ StringBuilder سریع است.» خیر؛ `+` در حلقهٔ N-مرحله‌ای N-1 object موقت می‌سازد.
**اصلاح:** در حلقهٔ concat از `StringBuilder` استفاده کنید.

**برداشت نادرست:** «trim و strip یکی هستند.» خیر؛ `trim` فقط whitespace ASCII (≤ U+0020) را حذف می‌کند، `strip` Unicode-aware است.
**اصلاح:** در code جدید از `strip` استفاده کنید.

**برداشت نادرست:** «`replace` و `replaceAll` فقط در نام فرق دارند.» خیر؛ `replace` literal است، `replaceAll` regex.
**اصلاح:** برای جایگزینی literal از `replace` استفاده کنید، برای pattern از `replaceAll`.

**برداشت نادرست:** «`arr.length` و `s.length()` یکی هستند.» خیر؛ آرایه `.length` فیلد دارد (بدون پرانتز)، String `.length()` متد.
**اصلاح:** آرایه: `arr.length`؛ String: `s.length()`؛ List: `list.size()`.

**برداشت نادرست:** «enhanced-for می‌تواند element آرایه را mutate کند.» خیر؛ متغیر loop کپی element است. برای primitive کپی value، برای reference کپی reference (ولی object مشترک است).
**اصلاح:** برای mutate از for کلاسیک با index یا از `Arrays.setAll` استفاده کنید.

**برداشت نادرست:** «آرایهٔ ۲بعدی contiguous است.» خیر؛ آرایهٔ ۲بعدی آرایه‌ای از آرایه است و سطرها object جداگانه‌اند.
**اصلاح:** اگر contiguous لازم دارید، آرایهٔ ۱بعدی با `index = row * cols + col` بسازید.

**برداشت نادرست:** «`Integer.parseInt` فقط digit می‌پذیرد.» تقریباً؛ leading/trailing whitespace پس از `trim` قابل قبول است، ولی متن غیرعددی (حتی `"3.14"`) `NumberFormatException` می‌دهد.
**اصلاح:** اگر ورودی ممکن است اعشاری یا خالی باشد، قبل از parse با regex یا manual check validation کنید.

**برداشت نادرست:** «`Math.addExact` همان `+` است با سینتکس بلندتر.» خیر؛ `+` در overflow wrap می‌کند، `addExact` exception پرتاب می‌کند.
**اصلاح:** در codeی که نمی‌خواهید wrap شود (مثل financial بدون BigDecimal)، از `addExact`/`multiplyExact` استفاده کنید.

**برداشت نادرست:** «`Math.random()` عدد صحیح تصادفی می‌دهد.» خیر؛ `double` در `[0.0, 1.0)` برمی‌گرداند.
**اصلاح:** برای int در بازه `[0, n)` از `ThreadLocalRandom.current().nextInt(n)` استفاده کنید.

## کارت‌های مرور تحلیلی

### کارت ۱ — overload selection

- بین `f(int)`، `f(long)`، `f(Integer)`، `f(int...)`، فراخوانی `f(5)` به کدام می‌رود؟ ترتیب ترجیح compiler را بنویسید.
- `f(5L)` و `f((Integer) 5)` در همین overload set کجا می‌روند؟
- سناریویی بنویسید که `f(null)` بین دو overload reference (مثل `f(String)` و `f(Integer)`) مبهم شود.

### کارت ۲ — early return

- یک method `validate(int age, String role)` با سه guard clause بنویسید: null role، age منفی، age خارج از بازه.
- توضیح دهید چرا nesting بیش از ۳ را با early return می‌شکنیم نه با if-else عمیق.
- نشان دهید چگونه یک return زودهنگام در method `void` بدون return در انتها ممکن است.

### کارت ۳ — `==` در برابر `equals`

- سه سناریو بنویسید که در آن `==` روی String درست کار می‌کند (literal، intern، final compile-time constant).
- سه سناریو بنویسید که در آن `==` غلط است (`new String`، runtime concat، `valueOf` خارج از cache).
- توضیح دهید چرا `Objects.equals(a, b)` بهتر از `a.equals(b)` است وقتی یکی null باشد.

### کارت ۴ — String API

- تفاوت `trim` و `strip` را با یک مثال از کاراکتر Unicode نشان دهید.
- `s.split(",")` و `s.split(",", -1)` را با `"a,b,,c,"` مقایسه کنید.
- توضیح دهید چرا `s.replace(".", "!")` و `s.replaceAll(".", "!")` نتیجهٔ متفاوت می‌دهند.

### کارت ۵ — StringBuilder

- یک حلقهٔ ۱۰۰۰ تایی concat بنویسید و نشان دهید چرا StringBuilder بهتر است.
- تفاوت `StringBuffer` و `StringBuilder` را توضیح دهید و بگویید چرا در code تک‌نخی `StringBuilder` ترجیح دارد.
- سناریویی بنویسید که `+` در compile-time constant به‌صورت خودکار به StringBuilder تبدیل می‌شود (string literal + literal).

### کارت ۶ — array bounds

- یک حلقه بنویسید که `ArrayIndexOutOfBoundsException` بدهد (off-by-one).
- همان حلقه را با enhanced-for بنویسید و نشان دهید چرا exception ندارد.
- یک jagged array ۳×? بسازید و `deepToString` آن را چاپ کنید.

### کارت ۷ — Math utilities

- یک method بنویسید که ۶ تاس می‌اندازد و مجموع را برمی‌گرداند (از `ThreadLocalRandom`).
- `Math.floor` و `Math.round` را با ۳ عدد اعشاری (مثبت، منفی، صفر) مقایسه کنید.
- `Math.addExact` و `+` را در دو سناریو (نزدیک `MAX_VALUE`، عادی) نشان دهید.

### کارت ۸ — parsing

- یک method `parsePositiveInt(String s)` بنویسید که whitespace را trim کند، NFE را catch کند، و در null یا منفی -1 برگرداند.
- `parseInt` و `valueOf` را با ۵ مقدار تست کنید (digit، space+number، hex، "3.14"، null).
- توضیح دهید چرا regex `"-?\d+"` قبل از parse امن‌تر است.

## چک‌لیست پایان فصل ۳

- [ ] می‌توانم method با return type، overload، و `void` بنویسم و compiler را راضی کنم.
- [ ] می‌دانم چه چیزی overload می‌شود (فقط signature) و چه نمی‌شود (return type، parameter name).
- [ ] می‌توانم early return را به‌عنوان guard بنویسم و nesting را کم کنم.
- [ ] می‌دانم پارامترها local variable هستند و برای رفع shadowing فیلد از `this` استفاده می‌کنم.
- [ ] می‌توانم varargs را تعریف و فراخوانی کنم بدون اینکه با array overload دچار ambiguity شوم.
- [ ] می‌دانم String immutable است و concat در حلقه با StringBuilder بهتر است.
- [ ] می‌توانم `==` و `equals` را درست تشخیص دهم و از `intern` در موارد مناسب استفاده کنم.
- [ ] می‌توانم String API اصلی (length، charAt، substring، indexOf، split، replace، trim/strip، format) را به‌کار ببرم.
- [ ] می‌توانم آرایه بسازم، با initializer literal مقداردهی کنم، و bounds را رعایت کنم.
- [ ] می‌دانم `Arrays.sort`/`toString`/`copyOf`/`equals`/`deepToString` چه‌کار می‌کنند.
- [ ] می‌توانم آرایهٔ ۲بعدی و jagged array بسازم و تفاوت‌شان را توضیح دهم.
- [ ] می‌توانم متدهای `Math` (max/min/abs/round/floor/ceil/pow/random) را به‌کار ببرم.
- [ ] می‌توانم `Integer.parseInt`/`valueOf` را با مدیریت `NumberFormatException` بنویسم.

## تمرین پروژه‌ای پایان فصل ۳

یک برنامهٔ کنسولی بنویسید که:

1. خط فرمان را می‌خواند (`args[0]` نام فایل، یا از `System.in` prompt می‌گیرد).
2. فایل متنی را خط به خط می‌خواند.
3. هر خط را parse می‌کند: اگر با `##` شروع شود comment است و رد شود؛ اگر خالی است skip شود.
4. هر خط عددی (مثل `42` یا `-7`) را به `int` تبدیل می‌کند و در آرایهٔ dynamic اضافه می‌کند (از `ArrayList<Integer>`).
5. در انتها: min، max، sum، mean، و median را با `Math` و `Arrays` محاسبه و چاپ کند.
6. اگر خط غیرعددی بود، با `NumberFormatException` پیام خطا چاپ کند (با شمارهٔ خط) و ادامه دهد.

نکته: از `String.split` برای جدا کردن فیلدها (اگر خط comma-separated است) و از `String.format` برای خروجی استفاده کنید.
