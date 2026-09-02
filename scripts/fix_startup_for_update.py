from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()
s = s.replace("Future<void> main() async {\n  WidgetsFlutterBinding.ensureInitialized();\n  await MobileAds.instance.initialize();\n  runApp(const AccountantAcademyApp());\n}", "void main() {\n  WidgetsFlutterBinding.ensureInitialized();\n  runApp(const AccountantAcademyApp());\n}", 1)
s = s.replace("  Future<void> _load(int width) async {\n    final size = await AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(width);", "  Future<void> _load(int width) async {\n    try {\n      await MobileAds.instance.initialize();\n      final size = await AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(width);", 1)
s = s.replace("    _banner = ad;\n    _loaded = false;\n    await ad.load();\n  }\n\n  @override\n  void dispose()", "      _banner = ad;\n      _loaded = false;\n      await ad.load();\n    } catch (_) {\n      if (mounted) {\n        setState(() {\n          _loaded = false;\n          _banner = null;\n        });\n      }\n    }\n  }\n\n  @override\n  void dispose()", 1)
p.write_text(s)

pub = Path('pubspec.yaml')
t = pub.read_text().replace('version: 1.0.0+1', 'version: 1.0.1+2', 1)
pub.write_text(t)
