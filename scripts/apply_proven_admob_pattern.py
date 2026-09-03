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

# Home: navigation menu first, exactly one banner below it.
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

# Remove the accidental extra banner from inside the home content.
inline_home_ad = """        const SizedBox(height: 18),\n        const AcademyAdBanner(),\n        const SizedBox(height: 18),\n        const Text(\n          'اختر القسم',"""
plain_home = """        const SizedBox(height: 18),\n        const Text(\n          'اختر القسم',"""
if inline_home_ad in s:
    s = s.replace(inline_home_ad, plain_home, 1)

# Arabic RTL navigation: forward/enter points left and back points right.
s = s.replace("Icons.arrow_back_rounded", "Icons.chevron_left_rounded")
s = s.replace("وأختبار", "واختبار")

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
t = re.sub(r'^version:\s*.*$', 'version: 1.0.6+7', t, flags=re.M)
t = re.sub(r'^\s*google_mobile_ads:\s*.*$', '  google_mobile_ads: ^9.1.0', t, flags=re.M)
pub.write_text(t)
print('Preloaded AdMob safely; kept one bottom home banner, RTL fixes, and version 1.0.6+7')
