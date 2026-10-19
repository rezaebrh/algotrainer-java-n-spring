# بخش ۳: آرایه، Math و parsing در Java 21

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
