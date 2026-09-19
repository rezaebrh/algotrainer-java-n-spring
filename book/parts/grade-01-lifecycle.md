# درجهٔ ۱: چرخهٔ عمر شیء و مدیریت منابع در Java

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
