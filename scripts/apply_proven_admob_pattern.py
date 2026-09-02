from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

if "import 'ad_service.dart';" not in s:
    marker = "import 'package:url_launcher/url_launcher.dart';\n"
    if marker not in s:
        raise SystemExit('url_launcher import marker missing')
    s = s.replace(marker, marker + "\nimport 'ad_service.dart';\n", 1)

old = """    try {\n      await MobileAds.instance.initialize();\n      final size = await AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(width);"""
new = """    try {\n      if (!await AdService.instance.initialize()) return;\n      final size = await AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(width);"""
if old in s:
    s = s.replace(old, new, 1)
elif "if (!await AdService.instance.initialize()) return;" not in s:
    raise SystemExit('banner initialization marker missing')

p.write_text(s)

pub = Path('pubspec.yaml')
t = pub.read_text()
import re
t = re.sub(r'^version:\s*.*$', 'version: 1.0.1+2', t, flags=re.M)
t = re.sub(r'^\s*google_mobile_ads:\s*.*$', '  google_mobile_ads: ^9.1.0', t, flags=re.M)
pub.write_text(t)
print('Proven Matching AdMob pattern applied')
