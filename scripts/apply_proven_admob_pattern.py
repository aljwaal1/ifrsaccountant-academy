from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text()

if "import 'ad_service.dart';" not in s:
    marker = "import 'package:url_launcher/url_launcher.dart';\n"
    if marker not in s:
        raise SystemExit('url_launcher import marker missing')
    s = s.replace(marker, marker + "\nimport 'ad_service.dart';\n", 1)

old_init = """    try {\n      await MobileAds.instance.initialize();\n      final size = await AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(width);"""
new_init = """    try {\n      if (!await AdService.instance.initialize()) return;\n      final size = await AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(width);"""
if old_init in s:
    s = s.replace(old_init, new_init, 1)
elif "if (!await AdService.instance.initialize()) return;" not in s:
    raise SystemExit('banner initialization marker missing')

# Keep banner compact inside Scaffold.bottomNavigationBar. Without an explicit
# outer height, Container(alignment: ...) can expand vertically on inner pages.
old_banner = """    return Container(\n      color: Colors.white,\n      padding: const EdgeInsets.only(top: 6, bottom: 6),\n      alignment: Alignment.center,\n      child: SizedBox(\n        width: ad.size.width.toDouble(),\n        height: ad.size.height.toDouble(),\n        child: AdWidget(ad: ad),\n      ),\n    );"""
new_banner = """    return SizedBox(\n      width: double.infinity,\n      height: ad.size.height.toDouble() + 12,\n      child: ColoredBox(\n        color: Colors.white,\n        child: Center(\n          child: SizedBox(\n            width: ad.size.width.toDouble(),\n            height: ad.size.height.toDouble(),\n            child: AdWidget(ad: ad),\n          ),\n        ),\n      ),\n    );"""
if old_banner in s:
    s = s.replace(old_banner, new_banner, 1)
elif "height: ad.size.height.toDouble() + 12" not in s:
    raise SystemExit('banner layout marker missing')

# Arabic RTL navigation: forward/enter arrows point left; back points right.
s = s.replace("Icons.arrow_back_rounded", "Icons.chevron_left_rounded")
s = s.replace("'وأختبار يساعدك", "'واختبار يساعدك")

# Explicit right-pointing back arrows for nested pages.
track_appbar = """      appBar: AppBar(\n        title: Text(track['title']?.toString() ?? ''),\n        centerTitle: true,"""
track_appbar_new = """      appBar: AppBar(\n        leading: IconButton(\n          icon: const Icon(Icons.chevron_right_rounded),\n          tooltip: 'رجوع',\n          onPressed: () => Navigator.maybePop(context),\n        ),\n        title: Text(track['title']?.toString() ?? ''),\n        centerTitle: true,"""
if track_appbar in s:
    s = s.replace(track_appbar, track_appbar_new, 1)
elif "tooltip: 'رجوع'" not in s:
    raise SystemExit('track appbar marker missing')

lesson_appbar = """      appBar: AppBar(\n        title: Text(lessonCode(lesson)),\n        backgroundColor: const Color(0xFF0F3D56),"""
lesson_appbar_new = """      appBar: AppBar(\n        leading: IconButton(\n          icon: const Icon(Icons.chevron_right_rounded),\n          tooltip: 'رجوع',\n          onPressed: () => Navigator.maybePop(context),\n        ),\n        title: Text(lessonCode(lesson)),\n        backgroundColor: const Color(0xFF0F3D56),"""
if lesson_appbar in s:
    s = s.replace(lesson_appbar, lesson_appbar_new, 1)

p.write_text(s)

pub = Path('pubspec.yaml')
t = pub.read_text()
t = re.sub(r'^version:\s*.*$', 'version: 1.0.2+3', t, flags=re.M)
t = re.sub(r'^\s*google_mobile_ads:\s*.*$', '  google_mobile_ads: ^9.1.0', t, flags=re.M)
pub.write_text(t)
print('AdMob banner sizing and RTL navigation fixes applied')
