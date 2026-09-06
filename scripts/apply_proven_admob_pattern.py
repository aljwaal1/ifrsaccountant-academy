from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text()

# Start AdMob/UMP immediately after the first frame can render, without ever
# blocking application startup. The banner widgets reuse the same Future.
if "import 'dart:async';" not in s:
    s = s.replace("import 'dart:convert';\n", "import 'dart:async';\nimport 'dart:convert';\n", 1)

if "import 'ad_service.dart';" not in s:
    marker = "import 'package:url_launcher/url_launcher.dart';\n"
    if marker not in s:
        raise SystemExit('url_launcher import marker missing')
    s = s.replace(marker, marker + "\nimport 'ad_service.dart';\n", 1)

old_main = """void main() {\n  WidgetsFlutterBinding.ensureInitialized();\n  runApp(const AccountantAcademyApp());\n}"""
new_main = """void main() {\n  WidgetsFlutterBinding.ensureInitialized();\n  runApp(const AccountantAcademyApp());\n  unawaited(AdService.instance.initialize());\n}"""
if old_main in s:
    s = s.replace(old_main, new_main, 1)
elif "unawaited(AdService.instance.initialize());" not in s:
    raise SystemExit('main startup marker missing')

old_init = """    try {\n      await MobileAds.instance.initialize();\n      final size = await AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(width);"""
new_init = """    try {\n      if (!await AdService.instance.initialize()) return;\n      final size = await AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(width);"""
if old_init in s:
    s = s.replace(old_init, new_init, 1)
elif "if (!await AdService.instance.initialize()) return;" not in s:
    raise SystemExit('banner initialization marker missing')

old_banner = """    return Container(\n      color: Colors.white,\n      padding: const EdgeInsets.only(top: 6, bottom: 6),\n      alignment: Alignment.center,\n      child: SizedBox(\n        width: ad.size.width.toDouble(),\n        height: ad.size.height.toDouble(),\n        child: AdWidget(ad: ad),\n      ),\n    );"""
new_banner = """    return SizedBox(\n      width: double.infinity,\n      height: ad.size.height.toDouble() + 12,\n      child: ColoredBox(\n        color: Colors.white,\n        child: Center(\n          child: SizedBox(\n            width: ad.size.width.toDouble(),\n            height: ad.size.height.toDouble(),\n            child: AdWidget(ad: ad),\n          ),\n        ),\n      ),\n    );"""
if old_banner in s:
    s = s.replace(old_banner, new_banner, 1)
elif "height: ad.size.height.toDouble() + 12" not in s:
    raise SystemExit('banner layout marker missing')

old_home_order = """        children: [\n          const AcademyAdBanner(),\n          Divider(height: 1, color: Colors.grey.shade300),\n          NavigationBar("""
new_home_order = """        children: [\n          NavigationBar("""
if old_home_order in s:
    s = s.replace(old_home_order, new_home_order, 1)

old_nav_end = """            ],\n          ),\n        ],\n      ),"""
new_nav_end = """            ],\n          ),\n          Divider(height: 1, color: Colors.grey.shade300),\n          const SafeArea(\n            top: false,\n            child: AcademyAdBanner(),\n          ),\n        ],\n      ),"""
if "const SafeArea(\n            top: false,\n            child: AcademyAdBanner()," not in s:
    if old_nav_end not in s:
        raise SystemExit('home navigation end marker missing')
    s = s.replace(old_nav_end, new_nav_end, 1)

inline_home_ad = """        const SizedBox(height: 18),\n        const AcademyAdBanner(),\n        const SizedBox(height: 18),\n        const Text(\n          'اختر القسم',"""
plain_home = """        const SizedBox(height: 18),\n        const Text(\n          'اختر القسم',"""
if inline_home_ad in s:
    s = s.replace(inline_home_ad, plain_home, 1)

s = s.replace("وأختبار", "واختبار")

# Force Arabic RTL arrow semantics: forward/next points LEFT, back points RIGHT.
s = s.replace("Icons.arrow_back_rounded", "Icons.chevron_left_rounded")
s = s.replace("Icons.arrow_forward_rounded", "Icons.chevron_left_rounded")

# Add a clear contact/help onboarding card before the update card.
update_card = """      const _IntroCard(\n        icon: Icons.cloud_sync_rounded,\n        title: 'محتوى يتجدد باستمرار',\n        description:\n            'نضيف ونحسن الدروس والأسئلة باستمرار. راقب شارة التحديث وافحص المحتوى من فترة إلى أخرى حتى تبقى لديك أحدث نسخة تعليمية.',\n        accent: Color(0xFF176B87),\n      ),"""
contact_and_update = """      const _IntroCard(\n        icon: Icons.mark_email_read_rounded,\n        title: 'هل تحتاج شرحًا معينًا؟',\n        description:\n            'إذا رغبت بشرح موضوع محاسبي معين أو اقتراح درس جديد، افتح زر «المطور» أسفل التطبيق ثم اختر مراسلة المطور وأرسل طلبك مباشرة.',\n        accent: Color(0xFFE1A83A),\n      ),\n      const _IntroCard(\n        icon: Icons.cloud_sync_rounded,\n        title: 'محتوى يتجدد باستمرار',\n        description:\n            'نضيف ونحسن الدروس والأسئلة باستمرار. راقب شارة التحديث وافحص المحتوى من فترة إلى أخرى حتى تبقى لديك أحدث نسخة تعليمية.',\n        accent: Color(0xFF176B87),\n      ),"""
if update_card in s and "هل تحتاج شرحًا معينًا؟" not in s:
    s = s.replace(update_card, contact_and_update, 1)

# Replace the sections onboarding card with a full, scrollable list. It keeps
# dynamic tracks and supplements the known academy areas so the card never
# misleadingly shows only IFRS/CMA when cached content is partial.
new_sections_class = r'''class _SectionsIntroCard extends StatelessWidget {
  const _SectionsIntroCard({required this.tracks});
  final List<Map<String, dynamic>> tracks;

  @override
  Widget build(BuildContext context) {
    const knownSections = <String>[
      'IFRS / IAS',
      'CMA',
      'المحاسبة المالية',
      'المحاسبة الإدارية',
      'المحاسبة المتقدمة',
      'محاسبة البنوك',
    ];
    final dynamicTitles = tracks
        .map((track) => track['title']?.toString().trim() ?? '')
        .where((title) => title.isNotEmpty);
    final titles = <String>{...dynamicTitles, ...knownSections}.toList();

    return Container(
      width: double.infinity,
      constraints: const BoxConstraints(maxWidth: 680),
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(30),
        boxShadow: const [
          BoxShadow(color: Color(0x22000000), blurRadius: 30, offset: Offset(0, 12)),
        ],
      ),
      child: Column(
        children: [
          const Icon(Icons.grid_view_rounded, size: 48, color: Color(0xFF00A6A6)),
          const SizedBox(height: 12),
          const Text(
            'كل أقسام الأكاديمية أمامك',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 8),
          Text(
            'اختر المجال الذي تحتاجه وابدأ التعلم بالترتيب الذي يناسبك. الأقسام تتوسع مع تحديث المحتوى.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey.shade700, height: 1.5),
          ),
          const SizedBox(height: 18),
          Expanded(
            child: SingleChildScrollView(
              child: Wrap(
                alignment: WrapAlignment.center,
                spacing: 9,
                runSpacing: 9,
                children: [
                  for (final title in titles)
                    Chip(
                      avatar: const Icon(Icons.menu_book_rounded, size: 18, color: Color(0xFF0F3D56)),
                      label: Text(title),
                      backgroundColor: const Color(0xFF0F3D56).withOpacity(0.07),
                      side: BorderSide(color: const Color(0xFF00A6A6).withOpacity(0.22)),
                    ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
'''
s, section_count = re.subn(
    r'class _SectionsIntroCard extends StatelessWidget \{.*?\n\}\n\nclass AcademyAdBanner',
    new_sections_class + '\nclass AcademyAdBanner',
    s,
    count=1,
    flags=re.S,
)
if section_count != 1:
    raise SystemExit('Could not replace onboarding sections card')

# Use an explicit left-arrow glyph for "التالي" so RTL mirroring cannot flip it.
s = re.sub(
    r"icon: Icon\(page == pages\.length - 1\s*\? Icons\.rocket_launch_rounded\s*:\s*Icons\.chevron_left_rounded\),",
    "icon: page == pages.length - 1\n                        ? const Icon(Icons.rocket_launch_rounded)\n                        : const Text('←', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900)),",
    s,
    count=1,
    flags=re.S,
)

track_appbar = """      appBar: AppBar(\n        title: Text(track['title']?.toString() ?? ''),\n        centerTitle: true,"""
track_appbar_new = """      appBar: AppBar(\n        leading: IconButton(\n          icon: const Icon(Icons.chevron_right_rounded),\n          tooltip: 'رجوع',\n          onPressed: () => Navigator.maybePop(context),\n        ),\n        title: Text(track['title']?.toString() ?? ''),\n        centerTitle: true,"""
if track_appbar in s:
    s = s.replace(track_appbar, track_appbar_new, 1)

lesson_appbar = """      appBar: AppBar(\n        title: Text(lessonCode(lesson)),\n        backgroundColor: const Color(0xFF0F3D56),"""
lesson_appbar_new = """      appBar: AppBar(\n        leading: IconButton(\n          icon: const Icon(Icons.chevron_right_rounded),\n          tooltip: 'رجوع',\n          onPressed: () => Navigator.maybePop(context),\n        ),\n        title: Text(lessonCode(lesson)),\n        backgroundColor: const Color(0xFF0F3D56),"""
if lesson_appbar in s:
    s = s.replace(lesson_appbar, lesson_appbar_new, 1)

p.write_text(s)

pub = Path('pubspec.yaml')
t = pub.read_text()
t = re.sub(r'^version:\s*.*$', 'version: 1.0.9+10', t, flags=re.M)
t = re.sub(r'^\s*google_mobile_ads:\s*.*$', '  google_mobile_ads: ^9.1.0', t, flags=re.M)
pub.write_text(t)
print('Applied onboarding/contact/RTL fixes and version 1.0.9+10')
