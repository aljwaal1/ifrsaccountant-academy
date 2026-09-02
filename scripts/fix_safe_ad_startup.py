from pathlib import Path
p=Path('lib/main.dart')
s=p.read_text()
old="""Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await MobileAds.instance.initialize();
  runApp(const AccountantAcademyApp());
}
"""
new="""void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AccountantAcademyApp());
}
"""
if old not in s:
    raise SystemExit('main startup block not found')
s=s.replace(old,new,1)
old2="""  Future<void> _load(int width) async {
    final size = await AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(width);
    if (!mounted || size == null) return;
"""
new2="""  Future<void> _load(int width) async {
    try {
      await MobileAds.instance.initialize();
    } catch (_) {
      return;
    }
    AdSize? size;
    try {
      size = await AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(width);
    } catch (_) {
      return;
    }
    if (!mounted || size == null) return;
"""
if old2 not in s:
    raise SystemExit('ad load block not found')
s=s.replace(old2,new2,1)
p.write_text(s)
print('safe ad startup patch applied')
