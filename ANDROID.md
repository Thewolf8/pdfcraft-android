# PdfCraft لأندرويد (Capacitor + GitHub Actions)

نفس أسلوب مشروع HomeMed Cabinet: نسخة الويب من PdfCraft (WebAssembly) تُغلَّف بـ **Capacitor**، ومشروع الأندرويد **يُولَّد داخل GitHub Actions** في كل بناء، فلا توجد نسخ Gradle أو ملفات أندرويد تتعارض. كل شيء يعمل محلياً داخل الهاتف دون إنترنت.

> هذه النسخة **تستبدل** نسخة الغلاف اليدوي (Kotlin) السابقة: احذف مجلد `android/` القديم من المستودع إن كنت أضفته.

## الملفات

| المسار | الوظيفة |
|---|---|
| `.github/workflows/android.yml` | يبني الويب ثم Capacitor ثم APK |
| `mobile/package.json`, `capacitor.config.json` | إعداد Capacitor (نفس إصدارات HomeMed) |
| `mobile/scripts/patch_android.py` | يعدّل المشروع المُولَّد: فتح PDF، الأيقونة، التوقيع |
| `mobile/mobile-ui.patch` | تعديل واجهة Rust للهاتف (يُطبَّق أثناء البناء) |
| `apps/pdfcraft-web/index.html` | معدّل: لمس، حفظ ومشاركة، فتح الملفات، زر الرجوع |

## الاستخدام

1. انسخ المحتويات إلى جذر المستودع (استبدل `apps/pdfcraft-web/index.html` والـ workflow القديم)، ثم `commit` و`push`.
2. يعمل الـ workflow تلقائياً عند الدفع إلى `main` أو يدوياً من **Actions ▸ Android APK ▸ Run workflow**.
3. نزّل الملف من **Artifacts** (أول بناء 20–35 دقيقة). وبوسم `android-v0.9.0` يُنشأ **Release**.

## توقيع ثابت (مهم للتحديثات)

`assembleRelease` وحده ينتج APK **غير موقّع لا يمكن تثبيته**؛ لذلك يوقّعه هذا الـ workflow بمفتاح تجريبي إن لم تضف مفتاحك. لمفتاح ثابت:

```bash
keytool -genkeypair -v -keystore release.jks -alias pdfcraft -keyalg RSA -keysize 2048 -validity 10000
base64 -w0 release.jks
```

أضف في **Settings ▸ Secrets and variables ▸ Actions**: `ANDROID_KEYSTORE_BASE64` و`ANDROID_KEYSTORE_PASSWORD` و`ANDROID_KEY_ALIAS` و`ANDROID_KEY_PASSWORD`. احتفظ بنسخة من `release.jks`.

## كيف يعمل على الهاتف

- **الحفظ/التصدير:** يُكتب الملف في الكاش ثم تُفتح شاشة المشاركة (احفظ في «الملفات» أو Drive...)، كما في HomeMed.
- **فتح PDF من تطبيق آخر:** «فتح بواسطة PdfCraft». إن كان التطبيق مفتوحاً يسأل قبل إعادة التشغيل لأن التغييرات غير المحفوظة تضيع.
- **الواجهة:** عند ضيق العرض تصبح لوحتا الأدوات والمفتش ورقة سفلية تحت المستند، وتكبر عناصر التحكم 15%. إن لم يُبنَ هذا التعديل يبني الـ workflow الواجهة الأصلية ويعرض تحذيراً.
- **الرجوع:** ضغطتان للخروج حتى لا يضيع العمل.

## ما لم أستطع اختباره

لا إنترنت لدي، فلم أبنِ شيئاً هنا. اختبرت فقط سكربت التعديل على مشروع وهمي وكود الجسر في Node. احتمالات المراجعة بعد أول بناء: هوامش الشاشة (شريط الحالة) وسلوك لوحة المفاتيح، وحجم الملفات الكبيرة جداً عند المرور عبر Capacitor. الصق لي سجل الخطأ أو وصف المشكلة وأعدّلها.

الطباعة غير مدعومة في نسخة الويب أصلاً. الأيقونة من المشروع (MIT/Apache-2.0)؛ استبدل ما يلزم قبل النشر على متجر.
