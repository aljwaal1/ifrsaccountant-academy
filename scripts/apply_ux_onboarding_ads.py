from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Missing pattern: {label}')
    s = s.replace(old, new, 1)

replace_once(
"import 'package:flutter/services.dart';\nimport 'package:shared_preferences/shared_preferences.dart';",
"import 'package:flutter/services.dart';\nimport 'package:google_mobile_ads/google_mobile_ads.dart';\nimport 'package:shared_preferences/shared_preferences.dart';\nimport 'package:url_launcher/url_launcher.dart';",
'import dependencies',
)

replace_once(
"void main() {\n  WidgetsFlutterBinding.ensureInitialized();\n  runApp(const AccountantAcademyApp());\n}",
"Future<void> main() async {\n  WidgetsFlutterBinding.ensureInitialized();\n  await MobileAds.instance.initialize();\n  runApp(const AccountantAcademyApp());\n}",
'initialize ads',
)

replace_once(
"  bool loading = true;",
"  bool loading = true;\n  bool showOnboarding = false;\n  bool updateDue = false;",
'state flags',
)

replace_once(
"    lastUpdate = prefs.getString('academy_last_update') ?? 'المحتوى الداخلي';",
"    lastUpdate = prefs.getString('academy_last_update') ?? 'المحتوى الداخلي';\n    showOnboarding = !(prefs.getBool('academy_onboarding_seen') ?? false);\n    final lastCheckMs = prefs.getInt('academy_last_check_ms');\n    updateDue = lastCheckMs == null ||\n        DateTime.now().millisecondsSinceEpoch - lastCheckMs >=\n            const Duration(days: 3).inMilliseconds;",
'load onboarding and update reminder',
)

replace_once(
"  Future<void> _saveContentUrl(String url) async {",
"  Future<void> _finishOnboarding() async {\n    final prefs = await SharedPreferences.getInstance();\n    await prefs.setBool('academy_onboarding_seen', true);\n    if (mounted) setState(() => showOnboarding = false);\n  }\n\n  Future<void> _saveContentUrl(String url) async {",
'finish onboarding',
)

replace_once(
"      await prefs.setString('academy_content_json', body);\n      await prefs.setString('academy_last_update', updateText);\n      setState(() {\n        content = parsed;\n        lastUpdate = updateText;\n        updateStatus = 'تم جلب المحتوى بنجاح. عدد الدروس: $lessonCount';\n      });",
"      await prefs.setString('academy_content_json', body);\n      await prefs.setString('academy_last_update', updateText);\n      await prefs.setInt('academy_last_check_ms', now.millisecondsSinceEpoch);\n      setState(() {\n        content = parsed;\n        lastUpdate = updateText;\n        updateDue = false;\n        updateStatus = 'تم جلب المحتوى بنجاح. عدد الدروس: $lessonCount';\n      });",
'save update check',
)

old_build = """  @override
  Widget build(BuildContext context) {
    final pages = [
      TracksView(content: content),
      UpdateContentView(
        contentUrl: contentUrl,
        lastUpdate: lastUpdate,
        updateStatus: updateStatus,
        onSaveUrl: _saveContentUrl,
        onUpdate: _updateContent,
        onReset: _resetContent,
      ),
      const DeveloperView(),
    ];
    return Scaffold(
      appBar: AppBar(
        title: Text(
          content['appTitle']?.toString() ?? 'أكاديمية المحاسب الدولي',
        ),
        centerTitle: true,
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : pages[page],
      bottomNavigationBar: NavigationBar(
        selectedIndex: page,
        onDestinationSelected: (v) {
          SystemSound.play(SystemSoundType.click);
          setState(() => page = v);
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.school_outlined),
            selectedIcon: Icon(Icons.school),
            label: 'الدروس',
          ),
          NavigationDestination(
            icon: Icon(Icons.cloud_sync_outlined),
            selectedIcon: Icon(Icons.cloud_done),
            label: 'تحديث',
          ),
          NavigationDestination(
            icon: Icon(Icons.mail_outline),
            selectedIcon: Icon(Icons.mail),
            label: 'المطور',
          ),
        ],
      ),
    );
  }
}"""

new_build = """  @override
  Widget build(BuildContext context) {
    if (showOnboarding && !loading) {
      return OnboardingPage(content: content, onDone: _finishOnboarding);
    }

    final pages = [
      TracksView(
        content: content,
        updateDue: updateDue,
        onOpenUpdate: () => setState(() => page = 1),
      ),
      UpdateContentView(
        contentUrl: contentUrl,
        lastUpdate: lastUpdate,
        updateStatus: updateStatus,
        onSaveUrl: _saveContentUrl,
        onUpdate: _updateContent,
        onReset: _resetContent,
      ),
      const DeveloperView(),
    ];
    return Scaffold(
      appBar: AppBar(
        title: Text(
          content['appTitle']?.toString() ?? 'أكاديمية المحاسب الدولي',
        ),
        centerTitle: true,
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : pages[page],
      bottomNavigationBar: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const AcademyAdBanner(),
          Divider(height: 1, color: Colors.grey.shade300),
          NavigationBar(
            selectedIndex: page,
            onDestinationSelected: (v) {
              SystemSound.play(SystemSoundType.click);
              setState(() => page = v);
            },
            destinations: [
              const NavigationDestination(
                icon: Icon(Icons.school_outlined),
                selectedIcon: Icon(Icons.school),
                label: 'الدروس',
              ),
              NavigationDestination(
                icon: Badge(
                  isLabelVisible: updateDue,
                  child: const Icon(Icons.cloud_sync_outlined),
                ),
                selectedIcon: Badge(
                  isLabelVisible: updateDue,
                  child: const Icon(Icons.cloud_done),
                ),
                label: 'تحديث',
              ),
              const NavigationDestination(
                icon: Icon(Icons.mail_outline),
                selectedIcon: Icon(Icons.mail),
                label: 'المطور',
              ),
            ],
          ),
        ],
      ),
    );
  }
}"""
replace_once(old_build, new_build, 'home build')

insert_before_tracks = r'''
class OnboardingPage extends StatefulWidget {
  const OnboardingPage({super.key, required this.content, required this.onDone});
  final Map<String, dynamic> content;
  final Future<void> Function() onDone;

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  final controller = PageController();
  int page = 0;

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final tracks = (widget.content['tracks'] as List? ?? [])
        .whereType<Map>()
        .map((e) => Map<String, dynamic>.from(e))
        .toList();
    final pages = <Widget>[
      const _IntroCard(
        icon: Icons.account_balance_wallet_rounded,
        title: 'أكاديمية المحاسب الدولي',
        description:
            'مساحتك التعليمية للمحاسبة، مصممة للمحاسبين وطلاب المحاسبة وكل من يريد بناء معرفة عملية ومنظمة من الأساس إلى المستوى المتقدم.',
        accent: Color(0xFFE1A83A),
      ),
      _SectionsIntroCard(tracks: tracks),
      const _IntroCard(
        icon: Icons.school_rounded,
        title: 'تعلّم ثم اختبر نفسك',
        description:
            'كل درس يجمع بين ملخص مركز، شرح تفصيلي، وأختبار يساعدك على تثبيت المعلومة وقياس فهمك خطوة بخطوة.',
        accent: Color(0xFF00A6A6),
      ),
      const _IntroCard(
        icon: Icons.cloud_sync_rounded,
        title: 'محتوى يتجدد باستمرار',
        description:
            'نضيف ونحسن الدروس والأسئلة باستمرار. راقب شارة التحديث وافحص المحتوى من فترة إلى أخرى حتى تبقى لديك أحدث نسخة تعليمية.',
        accent: Color(0xFF176B87),
      ),
    ];

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF0F3D56), Color(0xFF0B5969), Color(0xFFF4F7F8)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 14, 20, 8),
                child: Row(
                  children: [
                    const Expanded(
                      child: Text(
                        'مرحبًا بك',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                    TextButton(
                      onPressed: widget.onDone,
                      child: const Text('تخطي', style: TextStyle(color: Colors.white)),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: PageView.builder(
                  controller: controller,
                  itemCount: pages.length,
                  onPageChanged: (value) => setState(() => page = value),
                  itemBuilder: (_, index) => Padding(
                    padding: const EdgeInsets.fromLTRB(18, 12, 18, 18),
                    child: pages[index],
                  ),
                ),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(
                  pages.length,
                  (index) => AnimatedContainer(
                    duration: const Duration(milliseconds: 220),
                    width: page == index ? 24 : 8,
                    height: 8,
                    margin: const EdgeInsets.symmetric(horizontal: 4),
                    decoration: BoxDecoration(
                      color: page == index
                          ? const Color(0xFF00A6A6)
                          : Colors.grey.shade400,
                      borderRadius: BorderRadius.circular(20),
                    ),
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(18),
                child: SizedBox(
                  width: double.infinity,
                  height: 54,
                  child: FilledButton.icon(
                    onPressed: () async {
                      if (page == pages.length - 1) {
                        await widget.onDone();
                      } else {
                        await controller.nextPage(
                          duration: const Duration(milliseconds: 300),
                          curve: Curves.easeOutCubic,
                        );
                      }
                    },
                    icon: Icon(page == pages.length - 1
                        ? Icons.rocket_launch_rounded
                        : Icons.arrow_back_rounded),
                    label: Text(page == pages.length - 1 ? 'ابدأ التعلم' : 'التالي'),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _IntroCard extends StatelessWidget {
  const _IntroCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.accent,
  });
  final IconData icon;
  final String title;
  final String description;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        width: double.infinity,
        constraints: const BoxConstraints(maxWidth: 680),
        padding: const EdgeInsets.all(26),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(30),
          boxShadow: const [
            BoxShadow(color: Color(0x22000000), blurRadius: 30, offset: Offset(0, 12)),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 92,
              height: 92,
              decoration: BoxDecoration(
                color: accent.withOpacity(0.12),
                borderRadius: BorderRadius.circular(28),
              ),
              child: Icon(icon, size: 48, color: accent),
            ),
            const SizedBox(height: 24),
            Text(
              title,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 25, fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 14),
            Text(
              description,
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 17, height: 1.75, color: Colors.grey.shade700),
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionsIntroCard extends StatelessWidget {
  const _SectionsIntroCard({required this.tracks});
  final List<Map<String, dynamic>> tracks;

  @override
  Widget build(BuildContext context) {
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
            'اختر المجال الذي تحتاجه وابدأ التعلم بالترتيب الذي يناسبك.',
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
                  for (final track in tracks)
                    Chip(
                      avatar: Icon(_trackStyle(track).icon, size: 18, color: _trackStyle(track).color),
                      label: Text(track['title']?.toString() ?? ''),
                      backgroundColor: _trackStyle(track).color.withOpacity(0.09),
                      side: BorderSide(color: _trackStyle(track).color.withOpacity(0.20)),
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

class AcademyAdBanner extends StatefulWidget {
  const AcademyAdBanner({super.key});

  @override
  State<AcademyAdBanner> createState() => _AcademyAdBannerState();
}

class _AcademyAdBannerState extends State<AcademyAdBanner> {
  BannerAd? _banner;
  int? _width;
  bool _loaded = false;

  String get _testUnitId => Platform.isAndroid
      ? 'ca-app-pub-3940256099942544/6300978111'
      : 'ca-app-pub-3940256099942544/2934735716';

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final width = MediaQuery.sizeOf(context).width.truncate();
    if (_width == width && _banner != null) return;
    _width = width;
    _load(width);
  }

  Future<void> _load(int width) async {
    final size = await AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(width);
    if (!mounted || size == null) return;
    await _banner?.dispose();
    final ad = BannerAd(
      adUnitId: _testUnitId,
      request: const AdRequest(),
      size: size,
      listener: BannerAdListener(
        onAdLoaded: (_) {
          if (mounted) setState(() => _loaded = true);
        },
        onAdFailedToLoad: (ad, _) {
          ad.dispose();
          if (mounted) setState(() {
            _loaded = false;
            _banner = null;
          });
        },
      ),
    );
    _banner = ad;
    _loaded = false;
    await ad.load();
  }

  @override
  void dispose() {
    _banner?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final ad = _banner;
    if (!_loaded || ad == null) return const SizedBox.shrink();
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.only(top: 6, bottom: 6),
      alignment: Alignment.center,
      child: SizedBox(
        width: ad.size.width.toDouble(),
        height: ad.size.height.toDouble(),
        child: AdWidget(ad: ad),
      ),
    );
  }
}

'''
replace_once('class TracksView extends StatelessWidget {', insert_before_tracks + 'class TracksView extends StatelessWidget {', 'insert onboarding and ads')

replace_once(
"class TracksView extends StatelessWidget {\n  const TracksView({super.key, required this.content});\n  final Map<String, dynamic> content;",
"class TracksView extends StatelessWidget {\n  const TracksView({\n    super.key,\n    required this.content,\n    required this.updateDue,\n    required this.onOpenUpdate,\n  });\n  final Map<String, dynamic> content;\n  final bool updateDue;\n  final VoidCallback onOpenUpdate;",
'home view params',
)

replace_once(
"        _HeroCard(count: lessonCount, sectionCount: tracks.length),\n        const SizedBox(height: 18),",
"        _HeroCard(count: lessonCount, sectionCount: tracks.length),\n        if (updateDue) ...[\n          const SizedBox(height: 14),\n          Card(\n            elevation: 0,\n            color: const Color(0xFFFFF7E6),\n            child: ListTile(\n              leading: const CircleAvatar(\n                backgroundColor: Color(0xFFE1A83A),\n                child: Icon(Icons.new_releases_rounded, color: Colors.white),\n              ),\n              title: const Text('حان وقت فحص المحتوى', style: TextStyle(fontWeight: FontWeight.bold)),\n              subtitle: const Text('مرّ بعض الوقت منذ آخر فحص. تحقق من وجود دروس أو أسئلة جديدة.'),\n              trailing: const Icon(Icons.chevron_left),\n              onTap: onOpenUpdate,\n            ),\n          ),\n        ],\n        const SizedBox(height: 18),",
'update reminder card',
)

# Add the banner to secondary screens without covering content.
track_marker = "class TrackLessonsPage extends StatelessWidget {"
track_start = s.index(track_marker)
lesson_marker = "class LessonPage extends StatefulWidget {"
lesson_start = s.index(lesson_marker)
track_part = s[track_start:lesson_start]
if "bottomNavigationBar: const SafeArea" not in track_part:
    track_part = track_part.replace(
        "    return Scaffold(\n      appBar:",
        "    return Scaffold(\n      bottomNavigationBar: const SafeArea(top: false, child: AcademyAdBanner()),\n      appBar:",
        1,
    )
    s = s[:track_start] + track_part + s[lesson_start:]

lesson_start = s.index(lesson_marker)
summary_marker = "class SummaryView extends StatelessWidget {"
summary_start = s.index(summary_marker)
lesson_part = s[lesson_start:summary_start]
if "bottomNavigationBar: const SafeArea" not in lesson_part:
    lesson_part = lesson_part.replace(
        "    return Scaffold(\n      appBar:",
        "    return Scaffold(\n      bottomNavigationBar: const SafeArea(top: false, child: AcademyAdBanner()),\n      appBar:",
        1,
    )
    s = s[:lesson_start] + lesson_part + s[summary_start:]

# Replace the primitive developer screen with direct email composition.
dev_start = s.index('class DeveloperView extends StatefulWidget {')
dev_end = s.index('const fallbackContentJson =', dev_start)
new_dev = r'''class DeveloperView extends StatefulWidget {
  const DeveloperView({super.key});
  @override
  State<DeveloperView> createState() => _DeveloperViewState();
}

class _DeveloperViewState extends State<DeveloperView> {
  final controller = TextEditingController();
  bool openingMail = false;

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    FocusScope.of(context).unfocus();
    setState(() => openingMail = true);
    final uri = Uri(
      scheme: 'mailto',
      path: developerEmail,
      queryParameters: {
        'subject': 'ملاحظة من تطبيق أكاديمية المحاسب الدولي',
        'body': controller.text.trim(),
      },
    );
    final opened = await launchUrl(uri, mode: LaunchMode.externalApplication);
    if (!mounted) return;
    setState(() => openingMail = false);
    if (!opened) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('تعذر فتح تطبيق البريد على هذا الجهاز')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(22),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF0F3D56), Color(0xFF00A6A6)],
            ),
            borderRadius: BorderRadius.circular(28),
          ),
          child: const Column(
            children: [
              CircleAvatar(
                radius: 34,
                backgroundColor: Color(0x22FFFFFF),
                child: Icon(Icons.support_agent_rounded, size: 38, color: Color(0xFFE1A83A)),
              ),
              SizedBox(height: 14),
              Text(
                'تواصل مع المطور',
                style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.w900),
              ),
              SizedBox(height: 8),
              Text(
                'اقتراحك أو ملاحظتك تساعدنا على تحسين الأكاديمية. اكتب رسالتك وسنفتحها لك مباشرة في تطبيق البريد.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white, height: 1.6),
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Row(
            children: [
              const CircleAvatar(
                backgroundColor: Color(0xFFE8F7F7),
                child: Icon(Icons.email_outlined, color: Color(0xFF00A6A6)),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('البريد المخصص للدعم', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 3),
                    Text(developerEmail, style: TextStyle(color: Colors.grey.shade700)),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        TextField(
          controller: controller,
          minLines: 6,
          maxLines: 10,
          textInputAction: TextInputAction.newline,
          decoration: InputDecoration(
            labelText: 'رسالتك',
            hintText: 'اكتب اقتراحك أو المشكلة التي واجهتك...',
            alignLabelWithHint: true,
            filled: true,
            fillColor: Colors.white,
            prefixIcon: const Padding(
              padding: EdgeInsets.only(bottom: 100),
              child: Icon(Icons.edit_note_rounded),
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(20),
              borderSide: BorderSide.none,
            ),
          ),
        ),
        const SizedBox(height: 14),
        SizedBox(
          height: 52,
          child: FilledButton.icon(
            onPressed: openingMail ? null : _send,
            icon: openingMail
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.send_rounded),
            label: const Text('إرسال إلى المطور'),
          ),
        ),
        const SizedBox(height: 10),
        Text(
          'سيتم فتح تطبيق البريد على جهازك لتراجع الرسالة ثم ترسلها.',
          textAlign: TextAlign.center,
          style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
        ),
      ],
    );
  }
}

'''
s = s[:dev_start] + new_dev + s[dev_end:]

p.write_text(s, encoding='utf-8')

pub = Path('pubspec.yaml')
ps = pub.read_text(encoding='utf-8')
if 'google_mobile_ads:' not in ps:
    ps = ps.replace(
        '  shared_preferences: ^2.3.3\n',
        '  shared_preferences: ^2.3.3\n  google_mobile_ads: ^6.0.0\n  url_launcher: ^6.3.2\n',
        1,
    )
pub.write_text(ps, encoding='utf-8')
print('UX patch applied')
