# درجهٔ ۲ — عملگرها و جریان کنترل

> **مسیر:** Java 21 / Operators and Control Flow  
> **مخاطب:** برنامه‌نویس C++ که می‌خواهد مقدار، نوع و مسیر اجرای Java را پیش از اجرا پیش‌بینی کند.

این فصل متن آموزشی مستقل است: توضیح‌ها، مثال‌ها و تمرین‌ها برای همین مسیر نوشته شده‌اند و بازتولید متن تجاری نیستند.
نحو Java به C++ نزدیک دیده می‌شود، اما در عملگرها و کنترل جریان، شباهت نشانه‌ها جایگزین قواعد type، promotion، evaluation order و scope نمی‌شود.

## نقشهٔ یادگیری و خروجی مورد انتظار

پس از این درجه باید بتوانید:

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

پیش از arithmetic دودویی، Java operandهای `byte`، `short` و `char` را دست‌کم به `int` promotion می‌دهد. این قاعده به مقدار فعلی variable نگاه نمی‌کند؛ به type آن نگاه می‌کند.
برای خواندن code، ابتدا type و valueها را جدا کنید؛ سپس مسیر control را روی کاغذ trace کنید. Output تنها تأیید است، نه جایگزین reasoning.

- `byte + byte` یک `int` می‌دهد.
- وجود `long` نتیجه را دست‌کم `long` می‌کند.
- وجود `float` یا `double` نتیجه را به آن نوع می‌برد.
- unary `+`، `-` و `~` نیز نوع‌های کوچک را به int می‌برند.

```text
byte ─┐
short ─┼── binary numeric promotion ──> int
char ──┘
int  ────────────────────────────────> int
long  ───────────────────────────────> long
float ───────────────────────────────> float
double ──────────────────────────────> double
```

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

## 3. arithmetic، division و modulo

برای integralها، `/` تقسیم صحیح با truncation به سوی صفر است. برای داشتن fraction باید پیش از operation یک operand floating-point باشد.
برای خواندن code، ابتدا type و valueها را جدا کنید؛ سپس مسیر control را روی کاغذ trace کنید. Output تنها تأیید است، نه جایگزین reasoning.

- `7 / 2` برابر 3 است.
- `7 / 2.0` برابر 3.5 است.
- علامت `%` از dividend، یعنی سمت چپ، می‌آید.
- overflow int و long در Java wrap دو مکمل دارد.

## 4. bitwise و shift

`&`، `|`، `^` و `~` روی bitهای integral کار می‌کنند. برای flagها literal باینری یا hexadecimal معمولاً خواناتر از decimal است.
برای خواندن code، ابتدا type و valueها را جدا کنید؛ سپس مسیر control را روی کاغذ trace کنید. Output تنها تأیید است، نه جایگزین reasoning.

- `<<` bitها را به چپ می‌برد.
- `>>` bit علامت را از چپ تکرار می‌کند.
- `>>>` از چپ صفر وارد می‌کند.
- در int فقط پنج bit پایین shift count مؤثر است.

| موضوع | Java | C++ رایج |
|---|---|---|
| shift راست zero-fill | `>>>` | `>>` روی unsigned type |
| integer unsigned عمومی | primitive جدا ندارد | `unsigned int` و هم‌خانواده‌ها |
| signed overflow | wrap تعریف‌شده | رفتار تعریف‌نشده |

## 5. comparison و logical

عملگرهای relational یک boolean تولید می‌کنند. Java numeric truthiness ندارد: شرط `if`، `while` و for باید دقیقاً boolean باشد.
برای خواندن code، ابتدا type و valueها را جدا کنید؛ سپس مسیر control را روی کاغذ trace کنید. Output تنها تأیید است، نه جایگزین reasoning.

- `==` روی primitive value را مقایسه می‌کند.
- `==` روی reference identity را مقایسه می‌کند.
- `&&` و `||` short-circuit هستند.
- `&` و `|` روی boolean قانونی اما eager هستند.

| expression | ارزیابی راست؟ | کاربرد پیش‌فرض |
|---|---:|---|
| `a && b` با `a=false` | خیر | guard |
| `a || b` با `a=true` | خیر | fallback |
| `a & b` | بله | bitwise/eager آگاهانه |
| `a | b` | بله | bitwise/eager آگاهانه |

## 6. assignment، precedence و ternary

Precedence syntax را تعیین می‌کند، نه intention را. هر جا خواننده ممکن است ترتیب را اشتباه بگیرد، parentheses یا statementهای کوچک‌تر راه‌حل‌اند.
برای خواندن code، ابتدا type و valueها را جدا کنید؛ سپس مسیر control را روی کاغذ trace کنید. Output تنها تأیید است، نه جایگزین reasoning.

- `x++` مقدار قدیم و سپس افزایش می‌دهد.
- `++x` ابتدا افزایش و سپس مقدار جدید تولید می‌کند.
- compound assignment LHS را فقط یک بار evaluate می‌کند.
- ternary فقط branch انتخاب‌شده را evaluate می‌کند.

## 7. if و if/else

`if` یک statement یا block را در صورت true بودن condition انتخاب می‌کند. در زنجیره if/else-if نخستین condition true برنده است.
برای خواندن code، ابتدا type و valueها را جدا کنید؛ سپس مسیر control را روی کاغذ trace کنید. Output تنها تأیید است، نه جایگزین reasoning.

- brace را حتی برای یک statement نگه دارید.
- range تخصصی‌تر را پیش از range عمومی‌تر بنویسید.
- compiler overlap منطقی rangeها را لزوماً تشخیص نمی‌دهد.
- boundaryها را جداگانه بررسی کنید.

## 8. switch statement

switch برای انتخاب valueهای گسسته است، نه rangeهای باز. colon form fall-through دارد مگر break، return، throw یا پایان statement کنترل را قطع کند.
برای خواندن code، ابتدا type و valueها را جدا کنید؛ سپس مسیر control را روی کاغذ trace کنید. Output تنها تأیید است، نه جایگزین reasoning.

- case label باید constant مناسب و یکتا باشد.
- چند case می‌توانند body مشترک داشته باشند.
- default مسیر valueهای پوشش‌نداده است.
- selectorهای مفید شامل char، String و enum هستند.

| شکل | fall-through | value تولید می‌کند |
|---|---:|---:|
| `case x:` statement | ممکن است | خیر |
| `case x ->` statement | خیر | خیر |
| switch expression | خیر | بله |

## 9. switch expression و yield

switch expression value تولید می‌کند و arrow form fall-through ندارد. هر مسیر باید value یا exception بدهد.
برای خواندن code، ابتدا type و valueها را جدا کنید؛ سپس مسیر control را روی کاغذ trace کنید. Output تنها تأیید است، نه جایگزین reasoning.

- block arm با `yield` value می‌دهد.
- yield از method return نمی‌کند.
- enum کامل می‌تواند بدون default exhaustive باشد.
- برای String و int default معمولاً لازم است.

## 10. for و enhanced-for

for initializer، condition و update را کنار هم قرار می‌دهد. enhanced-for برای پیمایش ساده collection یا array مناسب است.
برای خواندن code، ابتدا type و valueها را جدا کنید؛ سپس مسیر control را روی کاغذ trace کنید. Output تنها تأیید است، نه جایگزین reasoning.

- continue در for ابتدا update و سپس condition را می‌بیند.
- `for (;;)` بی‌شرط است و exit path لازم دارد.
- loop variable enhanced-for copy value/reference است.
- برای index یا حذف ساختاری شکل دیگری از loop لازم می‌شود.

## 11. while، do-while و loop بی‌نهایت

while condition را پیش از body می‌سنجد؛ do-while پس از body می‌سنجد. هر loop باید invariant و پیشرفت قابل بیان داشته باشد.
برای خواندن code، ابتدا type و valueها را جدا کنید؛ سپس مسیر control را روی کاغذ trace کنید. Output تنها تأیید است، نه جایگزین reasoning.

- while می‌تواند صفر بار اجرا شود.
- do-while body را دست‌کم یک بار اجرا می‌کند.
- event loop مشروع است اما ownership توقف می‌خواهد.
- mutation شرط پایان را پنهان نکنید.

## 12. labels، scope و definite assignment

Label نام statement است، نه goto عمومی. Scope از declaration آغاز می‌شود و با block تمام می‌شود. definite assignment proof کامپایلر برای read امن local است.
برای خواندن code، ابتدا type و valueها را جدا کنید؛ سپس مسیر control را روی کاغذ trace کنید. Output تنها تأیید است، نه جایگزین reasoning.

- break label statement نام‌دار را تمام می‌کند.
- continue label فقط loop نام‌دار را می‌پذیرد.
- initializer for بعد از loop در scope نیست.
- local باید در همه مسیرها پیش از read مقدار گرفته باشد.

```text
{
  for (int index = 0; index < 3; index++) {
      int inside = index;
  }
  // index و inside اینجا در scope نیستند
}
```

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

### truthiness

> **تلهٔ C++:** در C++، `if (count)` تبدیل عدد به bool دارد؛ در Java باید `count != 0` یا predicate domain را بنویسید.

### overflow

> **تلهٔ C++:** در C++ signed overflow رفتار تعریف‌نشده است؛ Java int/long wrap دو مکمل تعریف‌شده دارد. تعریف‌شده بودن مجوز استفاده برای پول نیست.

### مقایسهٔ رفتار overflow در دو زبان

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

### remainder

> **تلهٔ C++:** در Java remainder با truncation toward zero تعریف شده و علامت dividend را دارد. C++98/03 برای حالت منفی history implementation-defined دارد؛ C++ مدرن با Java همسو است.

### unsigned shift

> **تلهٔ C++:** Java primitive unsigned عمومی مانند C++ ندارد؛ `>>>` ابزار zero-fill right shift است.

### switch

> **تلهٔ C++:** C++ switch fall-through سنتی دارد؛ arrow switch Java راهی ساختاری برای حذف آن است.

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

## چک‌لیست پایان درجهٔ ۲

- [ ] می‌توانم type `byte + byte` را بدون اجرا بگویم.
- [ ] می‌توانم cast، truncation و overflow را جدا کنم.
- [ ] می‌توانم `%` منفی و `>>>` را محاسبه کنم.
- [ ] می‌دانم کجا && به جای & لازم است.
- [ ] rangeهای if را تخصصی به عمومی می‌چینم.
- [ ] switch expression و yield را توضیح می‌دهم.
- [ ] برای هر loop invariant و termination path دارم.
- [ ] label و definite assignment را با scope اشتباه نمی‌گیرم.

## تمرین پروژه‌ای پایان درجهٔ ۲

یک `ScoreBoard` console بسازید که یک `int[]` score را تحلیل می‌کند.

1. با enhanced-for مجموع و میانگین floating-point را حساب کنید.
1. با `%` تعداد زوج/فرد را گزارش دهید و رفتار score منفی را مستند کنید.
1. با switch expression grade A تا F را تولید کنید و input نامعتبر را reject کنید.
1. با loop معمولی نخستین score مردود را پیدا کنید؛ اگر matrix ساختید، labeled break فقط برای پایان search باشد.
1. boundaryهای 59، 60 و 100 و یک input نامعتبر را دستی بررسی کنید.
1. در توضیح پروژه بگویید چرا validation با `&&` نوشته شده است.

