# بخش ۱: متدها، ساخت و فراخوانی در Java 21

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
