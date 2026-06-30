import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AccountantAcademyApp());
}

const developerEmail = 'fastunlocked2017@gmail.com';
const defaultContentUrl = 'https://raw.githubusercontent.com/aljwaal1/accountant-academy-content/main/academy_content.json';
const fallbackContentUrls = [
  defaultContentUrl,
  'https://raw.githubusercontent.com/aljwaal1/accountant-academy-content/refs/heads/main/academy_content.json',
  'https://cdn.jsdelivr.net/gh/aljwaal1/accountant-academy-content@main/academy_content.json',
];

String lessonCode(Map<String, dynamic> lesson) {
  return (lesson['code'] ?? lesson['standardCode'] ?? '').toString();
}

class AccountantAcademyApp extends StatelessWidget {
  const AccountantAcademyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'أكاديمية المحاسب الدولي',
      theme: ThemeData(
        useMaterial3: true,
        fontFamily: 'Arial',
        colorScheme: const ColorScheme.light(
          primary: Color(0xFF0F3D56),
          secondary: Color(0xFF00A6A6),
          tertiary: Color(0xFFE1A83A),
          surface: Color(0xFFF4F7F8),
        ),
        scaffoldBackgroundColor: const Color(0xFFF4F7F8),
      ),
      home: const Directionality(
        textDirection: TextDirection.rtl,
        child: AcademyHomePage(),
      ),
    );
  }
}

class AcademyHomePage extends StatefulWidget {
  const AcademyHomePage({super.key});

  @override
  State<AcademyHomePage> createState() => _AcademyHomePageState();
}

class _AcademyHomePageState extends State<AcademyHomePage> {
  Map<String, dynamic> content = jsonDecode(fallbackContentJson) as Map<String, dynamic>;
  int page = 0;
  String contentUrl = defaultContentUrl;
  String lastUpdate = 'المحتوى الداخلي';
  String updateStatus = 'لم يتم الفحص بعد';
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _loadSavedContent();
  }

  Future<void> _loadSavedContent() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString('academy_content_json');
    final savedUrl = prefs.getString('academy_content_url');
    contentUrl = _isValidContentUrl(savedUrl) ? savedUrl!.trim() : defaultContentUrl;
    lastUpdate = prefs.getString('academy_last_update') ?? 'المحتوى الداخلي';
    if (saved != null && saved.trim().isNotEmpty) {
      try {
        final parsed = jsonDecode(saved) as Map<String, dynamic>;
        content = parsed;
      } catch (_) {
        content = jsonDecode(fallbackContentJson) as Map<String, dynamic>;
      }
    }
    if (mounted) setState(() => loading = false);
  }

  Future<void> _saveContentUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('academy_content_url', url.trim());
    setState(() => contentUrl = url.trim());
  }

  bool _isValidContentUrl(String? url) {
    final value = url?.trim() ?? '';
    return value.startsWith('http') &&
        !value.contains('USERNAME') &&
        !value.contains('accounting-academy-content');
  }

  Uri _contentRequestUri() {
    final base = Uri.parse(contentUrl);
    return _cacheBustedUri(base);
  }

  Uri _cacheBustedUri(Uri base) {
    return base.replace(
      queryParameters: {
        ...base.queryParameters,
        'v': DateTime.now().millisecondsSinceEpoch.toString(),
      },
    );
  }

  Future<void> _updateContent() async {
    if (!_isValidContentUrl(contentUrl)) {
      contentUrl = defaultContentUrl;
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('academy_content_url', defaultContentUrl);
    }
    if (!_isValidContentUrl(contentUrl)) {
      _message('تعذر تحديد رابط تحديث المحتوى');
      return;
    }
    setState(() {
      loading = true;
      updateStatus = 'جاري الاتصال بخادم المحتوى...';
    });
    try {
      final body = await _downloadContent();
      final parsed = jsonDecode(body) as Map<String, dynamic>;
      if (parsed['tracks'] is! List) throw Exception('ملف غير صالح');
      final lessonCount = _lessonCount(parsed);
      final prefs = await SharedPreferences.getInstance();
      final now = DateTime.now();
      final updateText = '${now.year}-${_two(now.month)}-${_two(now.day)} ${_two(now.hour)}:${_two(now.minute)}';
      await prefs.setString('academy_content_json', body);
      await prefs.setString('academy_last_update', updateText);
      setState(() {
        content = parsed;
        lastUpdate = updateText;
        updateStatus = 'تم جلب المحتوى بنجاح. عدد الدروس: $lessonCount';
      });
      SystemSound.play(SystemSoundType.alert);
      _message('تم تحديث المحتوى بنجاح');
    } catch (e) {
      final errorText = e.toString().replaceFirst('Exception: ', '');
      setState(() => updateStatus = 'فشل التحديث: $errorText');
      _message('تعذر التحديث: $errorText');
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<String> _downloadContent() async {
    final urls = <String>[
      contentUrl,
      ...fallbackContentUrls.where((url) => url != contentUrl),
    ];
    final errors = <String>[];
    for (final url in urls) {
      if (!_isValidContentUrl(url)) continue;
      final client = HttpClient();
      try {
        final request = await client.getUrl(_cacheBustedUri(Uri.parse(url)));
        request.headers.set(HttpHeaders.acceptHeader, 'application/json,text/plain,*/*');
        request.headers.set(HttpHeaders.userAgentHeader, 'AccountantAcademy/1.0');
        final response = await request.close().timeout(const Duration(seconds: 20));
        final body = await response.transform(utf8.decoder).join();
        client.close(force: true);
        if (response.statusCode < 200 || response.statusCode >= 300) {
          errors.add('${Uri.parse(url).host}: HTTP ${response.statusCode}');
          continue;
        }
        jsonDecode(body);
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('academy_content_url', url);
        contentUrl = url;
        return body;
      } catch (e) {
        client.close(force: true);
        errors.add('${Uri.parse(url).host}: ${e.toString()}');
      }
    }
    throw Exception(errors.isEmpty ? 'لا يوجد رابط صالح' : errors.join(' | '));
  }

  int _lessonCount(Map<String, dynamic> data) {
    final tracks = (data['tracks'] as List? ?? []);
    return tracks.fold<int>(0, (count, track) {
      if (track is! Map) return count;
      return count + ((track['lessons'] as List?)?.length ?? 0);
    });
  }

  Future<void> _resetContent() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('academy_content_json');
    await prefs.setString('academy_last_update', 'المحتوى الداخلي');
    setState(() {
      content = jsonDecode(fallbackContentJson) as Map<String, dynamic>;
      lastUpdate = 'المحتوى الداخلي';
    });
    _message('تم الرجوع للمحتوى الداخلي');
  }

  String _two(int n) => n.toString().padLeft(2, '0');

  void _message(String text) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text), behavior: SnackBarBehavior.floating));
  }

  @override
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
        title: Text(content['appTitle']?.toString() ?? 'أكاديمية المحاسب الدولي'),
        centerTitle: true,
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: loading ? const Center(child: CircularProgressIndicator()) : pages[page],
      bottomNavigationBar: NavigationBar(
        selectedIndex: page,
        onDestinationSelected: (v) {
          SystemSound.play(SystemSoundType.click);
          setState(() => page = v);
        },
        destinations: const [
          NavigationDestination(icon: Icon(Icons.school_outlined), selectedIcon: Icon(Icons.school), label: 'الدروس'),
          NavigationDestination(icon: Icon(Icons.cloud_sync_outlined), selectedIcon: Icon(Icons.cloud_done), label: 'تحديث'),
          NavigationDestination(icon: Icon(Icons.mail_outline), selectedIcon: Icon(Icons.mail), label: 'المطور'),
        ],
      ),
    );
  }
}

class TracksView extends StatelessWidget {
  const TracksView({super.key, required this.content});
  final Map<String, dynamic> content;

  @override
  Widget build(BuildContext context) {
    final tracks = (content['tracks'] as List? ?? []).cast<Map<String, dynamic>>();
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _HeroCard(count: tracks.fold<int>(0, (p, t) => p + ((t['lessons'] as List?)?.length ?? 0))),
        const SizedBox(height: 14),
        for (final track in tracks) TrackCard(track: track),
      ],
    );
  }
}

class _HeroCard extends StatelessWidget {
  const _HeroCard({required this.count});
  final int count;
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [Color(0xFF0F3D56), Color(0xFF00A6A6)]),
        borderRadius: BorderRadius.circular(26),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.workspace_premium, color: Color(0xFFE1A83A), size: 42),
          const SizedBox(height: 10),
          const Text('تعلم IFRS و CMA بالعربي', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text('عدد الدروس الحالية: $count. يمكنك تحديث المحتوى من الإنترنت بدون إصدار APK جديد.', style: const TextStyle(color: Colors.white, height: 1.5)),
        ],
      ),
    );
  }
}

class TrackCard extends StatelessWidget {
  const TrackCard({super.key, required this.track});
  final Map<String, dynamic> track;
  @override
  Widget build(BuildContext context) {
    final lessons = (track['lessons'] as List? ?? []).cast<Map<String, dynamic>>();
    return Card(
      margin: const EdgeInsets.only(bottom: 14),
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              CircleAvatar(backgroundColor: const Color(0xFFE1A83A), child: Text('${lessons.length}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold))),
              const SizedBox(width: 10),
              Expanded(child: Text(track['title']?.toString() ?? '', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold))),
            ]),
            const SizedBox(height: 6),
            Text(track['subtitle']?.toString() ?? '', style: TextStyle(color: Colors.grey.shade700)),
            const Divider(height: 26),
            for (final lesson in lessons)
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.menu_book, color: Color(0xFF00A6A6)),
                title: Text('${lessonCode(lesson)} - ${lesson['title'] ?? ''}', style: const TextStyle(fontWeight: FontWeight.w700)),
                subtitle: Text('أسئلة: ${((lesson['questions'] as List?) ?? []).length}'),
                trailing: const Icon(Icons.chevron_left),
                onTap: () {
                  SystemSound.play(SystemSoundType.click);
                  Navigator.push(context, MaterialPageRoute(builder: (_) => Directionality(textDirection: TextDirection.rtl, child: LessonPage(lesson: lesson))));
                },
              ),
          ],
        ),
      ),
    );
  }
}

class LessonPage extends StatefulWidget {
  const LessonPage({super.key, required this.lesson});
  final Map<String, dynamic> lesson;
  @override
  State<LessonPage> createState() => _LessonPageState();
}

class _LessonPageState extends State<LessonPage> {
  int tab = 0;
  @override
  Widget build(BuildContext context) {
    final lesson = widget.lesson;
    final views = [SummaryView(lesson: lesson), LongView(lesson: lesson), QuizView(lesson: lesson)];
    return Scaffold(
      appBar: AppBar(title: Text(lessonCode(lesson)), backgroundColor: const Color(0xFF0F3D56), foregroundColor: Colors.white),
      body: Column(children: [
        Padding(
          padding: const EdgeInsets.all(12),
          child: SegmentedButton<int>(
            segments: const [
              ButtonSegment(value: 0, label: Text('ملخص'), icon: Icon(Icons.short_text)),
              ButtonSegment(value: 1, label: Text('شرح'), icon: Icon(Icons.article_outlined)),
              ButtonSegment(value: 2, label: Text('اختبار'), icon: Icon(Icons.quiz_outlined)),
            ],
            selected: {tab},
            onSelectionChanged: (s) {
              SystemSound.play(SystemSoundType.click);
              setState(() => tab = s.first);
            },
          ),
        ),
        Expanded(child: views[tab]),
      ]),
    );
  }
}

class SummaryView extends StatelessWidget {
  const SummaryView({super.key, required this.lesson});
  final Map<String, dynamic> lesson;
  @override
  Widget build(BuildContext context) {
    final summary = (lesson['summary'] as List? ?? []).map((e) => e.toString()).toList();
    return ListView(padding: const EdgeInsets.all(16), children: [
      Text(lesson['title']?.toString() ?? '', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
      const SizedBox(height: 12),
      for (final item in summary) _Bullet(text: item),
    ]);
  }
}

class LongView extends StatelessWidget {
  const LongView({super.key, required this.lesson});
  final Map<String, dynamic> lesson;
  @override
  Widget build(BuildContext context) {
    final paragraphs = (lesson['longExplanation'] as List? ?? []).map((e) => e.toString()).toList();
    return ListView(padding: const EdgeInsets.all(16), children: [
      for (final p in paragraphs)
        Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18)),
          child: Text(p, style: const TextStyle(fontSize: 16, height: 1.7)),
        ),
    ]);
  }
}

class QuizView extends StatefulWidget {
  const QuizView({super.key, required this.lesson});
  final Map<String, dynamic> lesson;
  @override
  State<QuizView> createState() => _QuizViewState();
}

class _QuizViewState extends State<QuizView> {
  final Map<int, int> selected = {};
  bool finished = false;

  @override
  Widget build(BuildContext context) {
    final questions = (widget.lesson['questions'] as List? ?? []).cast<Map<String, dynamic>>();
    if (questions.isEmpty) return const Center(child: Text('لا توجد أسئلة بعد.'));
    final score = selected.entries.where((e) => questions[e.key]['answer'] == e.value).length;
    return ListView(padding: const EdgeInsets.all(16), children: [
      if (finished)
        Container(
          padding: const EdgeInsets.all(16),
          margin: const EdgeInsets.only(bottom: 14),
          decoration: BoxDecoration(color: const Color(0xFFE1A83A), borderRadius: BorderRadius.circular(18)),
          child: Text('نتيجتك: $score من ${questions.length}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white)),
        ),
      for (int i = 0; i < questions.length; i++) _QuestionCard(index: i, data: questions[i], selected: selected[i], finished: finished, onSelect: (v) {
        SystemSound.play(SystemSoundType.click);
        setState(() => selected[i] = v);
      }),
      FilledButton.icon(
        onPressed: selected.length == questions.length ? () { SystemSound.play(SystemSoundType.alert); setState(() => finished = true); } : null,
        icon: const Icon(Icons.check_circle_outline),
        label: const Text('إنهاء الاختبار وعرض الشرح'),
      ),
    ]);
  }
}

class _QuestionCard extends StatelessWidget {
  const _QuestionCard({required this.index, required this.data, required this.selected, required this.finished, required this.onSelect});
  final int index;
  final Map<String, dynamic> data;
  final int? selected;
  final bool finished;
  final ValueChanged<int> onSelect;
  @override
  Widget build(BuildContext context) {
    final options = (data['options'] as List? ?? []).map((e) => e.toString()).toList();
    final answer = data['answer'] as int? ?? -1;
    return Card(
      elevation: 0,
      margin: const EdgeInsets.only(bottom: 14),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('س${index + 1}: ${data['q'] ?? ''}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 8),
          for (int i = 0; i < options.length; i++)
            RadioListTile<int>(
              value: i,
              groupValue: selected,
              onChanged: finished ? null : (v) => onSelect(v ?? i),
              title: Text(options[i]),
              activeColor: const Color(0xFF00A6A6),
            ),
          if (finished)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: selected == answer ? const Color(0xFFE9F8F4) : const Color(0xFFFFF1F0),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Text('الإجابة الصحيحة: ${answer >= 0 && answer < options.length ? options[answer] : ''}\n${data['explanation'] ?? ''}', style: const TextStyle(height: 1.5)),
            ),
        ]),
      ),
    );
  }
}

class _Bullet extends StatelessWidget {
  const _Bullet({required this.text});
  final String text;
  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Icon(Icons.check_circle, color: Color(0xFF00A6A6)),
        const SizedBox(width: 10),
        Expanded(child: Text(text, style: const TextStyle(height: 1.5))),
      ]),
    );
  }
}

class UpdateContentView extends StatelessWidget {
  const UpdateContentView({
    super.key,
    required this.contentUrl,
    required this.lastUpdate,
    required this.updateStatus,
    required this.onSaveUrl,
    required this.onUpdate,
    required this.onReset,
  });
  final String contentUrl;
  final String lastUpdate;
  final String updateStatus;
  final Future<void> Function(String) onSaveUrl;
  final Future<void> Function() onUpdate;
  final Future<void> Function() onReset;

  @override
  Widget build(BuildContext context) {
    final isInternal = lastUpdate == 'المحتوى الداخلي';
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: const LinearGradient(colors: [Color(0xFF0F3D56), Color(0xFF00A6A6)]),
            borderRadius: BorderRadius.circular(26),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.auto_stories, color: Color(0xFFE1A83A), size: 44),
              SizedBox(height: 12),
              Text('تحديث الدروس والأسئلة', style: TextStyle(color: Colors.white, fontSize: 23, fontWeight: FontWeight.bold)),
              SizedBox(height: 8),
              Text('يتم تحديث التطبيق بالمعلومات والشروحات والأسئلة بشكل دوري، ويمكنك التحقق من وجود محتوى جديد من هنا.', style: TextStyle(color: Colors.white, height: 1.6)),
            ],
          ),
        ),
        const SizedBox(height: 16),
        _UpdateStatusCard(lastUpdate: lastUpdate, isInternal: isInternal),
        const SizedBox(height: 14),
        _LastCheckCard(updateStatus: updateStatus),
        const SizedBox(height: 14),
        FilledButton.icon(
          onPressed: onUpdate,
          icon: const Icon(Icons.cloud_download),
          label: const Text('التحقق من التحديثات الآن'),
        ),
        const SizedBox(height: 8),
        OutlinedButton.icon(
          onPressed: onReset,
          icon: const Icon(Icons.restore),
          label: const Text('الرجوع للمحتوى الأساسي'),
        ),
        const SizedBox(height: 14),
        const _HelpBox(),
      ],
    );
  }
}

class _LastCheckCard extends StatelessWidget {
  const _LastCheckCard({required this.updateStatus});
  final String updateStatus;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20)),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const CircleAvatar(
            backgroundColor: Color(0xFFEFF6FF),
            child: Icon(Icons.info_outline, color: Color(0xFF0F3D56)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('آخر محاولة تحديث', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 4),
                Text(updateStatus, style: TextStyle(color: Colors.grey.shade700, height: 1.4)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _UpdateStatusCard extends StatelessWidget {
  const _UpdateStatusCard({required this.lastUpdate, required this.isInternal});
  final String lastUpdate;
  final bool isInternal;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20)),
      child: Row(
        children: [
          CircleAvatar(
            backgroundColor: isInternal ? const Color(0xFFE1A83A) : const Color(0xFF00A6A6),
            child: Icon(isInternal ? Icons.menu_book : Icons.verified, color: Colors.white),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('حالة المحتوى', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 4),
                Text(isInternal ? 'أنت تستخدم المحتوى الأساسي المرفق مع التطبيق.' : 'آخر تحديث للمحتوى: $lastUpdate', style: TextStyle(color: Colors.grey.shade700, height: 1.4)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _HelpBox extends StatelessWidget {
  const _HelpBox();
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18)),
      child: const Text('ملاحظة: يتم إضافة شروحات وأسئلة جديدة بشكل دوري. عند الضغط على زر التحديث سيحاول التطبيق جلب أحدث محتوى متاح، وإذا لم يتوفر اتصال بالإنترنت سيبقى المحتوى الموجود محفوظًا على جهازك.', style: TextStyle(height: 1.6)),
    );
  }
}

class DeveloperView extends StatefulWidget {
  const DeveloperView({super.key});
  @override
  State<DeveloperView> createState() => _DeveloperViewState();
}

class _DeveloperViewState extends State<DeveloperView> {
  final controller = TextEditingController();
  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }
  @override
  Widget build(BuildContext context) {
    return ListView(padding: const EdgeInsets.all(16), children: [
      const Icon(Icons.support_agent, size: 72, color: Color(0xFF0F3D56)),
      const SizedBox(height: 10),
      const Text('مراسلة المطور', textAlign: TextAlign.center, style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
      const SizedBox(height: 8),
      const Text(developerEmail, textAlign: TextAlign.center),
      const SizedBox(height: 16),
      TextField(
        controller: controller,
        minLines: 5,
        maxLines: 8,
        decoration: InputDecoration(hintText: 'اكتب ملاحظتك هنا...', border: OutlineInputBorder(borderRadius: BorderRadius.circular(18))),
      ),
      const SizedBox(height: 12),
      FilledButton.icon(
        onPressed: () {
          final msg = 'إلى: $developerEmail\n\nملاحظة على تطبيق أكاديمية المحاسب الدولي:\n${controller.text}';
          Clipboard.setData(ClipboardData(text: msg));
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('تم نسخ الرسالة والبريد')));
        },
        icon: const Icon(Icons.copy),
        label: const Text('نسخ الرسالة'),
      ),
    ]);
  }
}

const fallbackContentJson = r'''
{
  "version": 3,
  "updatedAt": "2026-06-16",
  "appTitle": "أكاديمية المحاسب الدولي",
  "tracks": [
    {
      "id": "ifrs",
      "title": "IFRS / IAS",
      "subtitle": "معايير المحاسبة الدولية والتقارير المالية",
      "lessons": [
        {
          "id": "ifrs_15",
          "code": "IFRS 15",
          "title": "الإيرادات من العقود مع العملاء",
          "summary": [
            "يركز المعيار على الاعتراف بالإيراد عندما تنتقل السيطرة على السلعة أو الخدمة إلى العميل.",
            "الفكرة العملية هي تحليل العقد، تحديد التزامات الأداء، قياس سعر المعاملة، ثم توزيع السعر والاعتراف بالإيراد عند الوفاء.",
            "المعيار مهم لأنه يجعل معالجة الإيرادات أكثر اتساقًا بين القطاعات المختلفة."
          ],
          "longExplanation": [
            "يعالج IFRS 15 واحدة من أكثر القضايا حساسية في التقارير المالية: متى نعترف بالإيراد وبأي مبلغ. في الواقع العملي لا يكفي أن تصدر المنشأة فاتورة أو تقبض نقدًا حتى تقول إن الإيراد تحقق. السؤال المحاسبي الأهم هو: هل قدمت المنشأة ما وعدت به في العقد؟ وهل حصل العميل على السيطرة على السلعة أو الخدمة؟",
            "يبدأ التفكير من تحديد وجود عقد قابل للتنفيذ بين المنشأة والعميل. يجب أن تكون الحقوق والالتزامات واضحة، وأن يكون للمقابل أساس يمكن قياسه. بعد ذلك نبحث عن التزامات الأداء، وهي الوعود الجوهرية التي تعهدت المنشأة بتقديمها للعميل. قد يكون العقد بسيطًا مثل بيع سلعة واحدة، وقد يكون مركبًا مثل بيع جهاز مع تدريب وصيانة وترخيص استخدام.",
            "بعد تحديد التزامات الأداء، يتم تحديد سعر المعاملة. هذا السعر ليس دائمًا المبلغ المكتوب في الفاتورة فقط؛ فقد يتأثر بخصومات، حوافز، مكافآت أداء، غرامات تأخير، حق إرجاع، أو مقابل متغير. لذلك يحتاج المحاسب إلى فهم طبيعة العقد وليس مجرد تسجيل رقم جاهز.",
            "عند وجود أكثر من التزام أداء، يجب توزيع سعر المعاملة على هذه الالتزامات بطريقة تعكس القيمة النسبية لكل جزء. فمثلًا إذا باعت الشركة برنامجًا مع خدمة دعم لمدة سنة، فقد يتم الاعتراف بجزء من الإيراد عند تسليم البرنامج وجزء آخر على مدى فترة الدعم.",
            "الاعتراف بالإيراد قد يكون في نقطة زمنية معينة أو على مدى فترة زمنية. يحدث الاعتراف في نقطة زمنية عندما تنتقل السيطرة دفعة واحدة، مثل تسليم سلعة جاهزة. أما الاعتراف على مدى فترة فيظهر في الخدمات المستمرة أو عقود الإنشاء أو الحالات التي يستفيد فيها العميل من الخدمة أثناء تقديمها.",
            "تطبيق المعيار يحتاج حكمًا مهنيًا، خصوصًا في العقود المركبة. لذلك من الخطأ حفظ الخطوات فقط دون فهم أثرها على القوائم المالية. الاعتراف المبكر قد يضخم الأرباح، والاعتراف المتأخر قد يخفي الأداء الحقيقي، ولهذا يهتم المدققون والمحللون بهذا المعيار كثيرًا."
          ],
          "questions": [
            {"q":"ما الفكرة الأساسية في IFRS 15؟","options":["الاعتراف بالإيراد عند إصدار الفاتورة فقط","الاعتراف بالإيراد عند انتقال السيطرة للعميل","الاعتراف بالإيراد عند القبض النقدي فقط","تسجيل كل العقود كمصاريف"],"answer":1,"explanation":"المعيار يركز على الوفاء بالتزام الأداء وانتقال السيطرة على السلعة أو الخدمة إلى العميل."},
            {"q":"ماذا نفعل إذا تضمن العقد سلعة وخدمة صيانة مستقبلية؟","options":["نعترف بكل الإيراد فورًا دائمًا","نبحث هل توجد التزامات أداء متعددة","نتجاهل الصيانة","نسجل المبلغ كله كمصروف"],"answer":1,"explanation":"قد تكون السلعة والصيانة التزامين مختلفين ويجب توزيع سعر المعاملة عليهما."},
            {"q":"أي مما يلي قد يجعل المقابل متغيرًا؟","options":["خصم أو حافز أداء","لون الفاتورة","اسم المحاسب","رقم الهاتف"],"answer":0,"explanation":"الخصومات والحوافز وحقوق الإرجاع قد تؤثر على قيمة الإيراد المعترف به."},
            {"q":"متى يكون الاعتراف بالإيراد على مدى فترة؟","options":["عندما يستفيد العميل من الخدمة أثناء تقديمها","عند تغيير شعار الشركة","عند شراء أثاث للمكتب","عند دفع رواتب الموظفين"],"answer":0,"explanation":"الخدمات المستمرة قد تحقق شروط الاعتراف بالإيراد على مدى فترة زمنية."}
          ]
        },
        {
          "id": "ias_1",
          "code": "IAS 1",
          "title": "عرض القوائم المالية",
          "summary": [
            "ينظم IAS 1 عرض القوائم المالية العامة.",
            "يركز على العرض العادل، الاستمرارية، الاتساق، الأهمية النسبية، والمقارنة.",
            "يساعد المستخدمين على فهم المركز المالي والأداء والتدفقات النقدية."
          ],
          "longExplanation": [
            "IAS 1 ليس معيارًا لحساب بند واحد، بل هو إطار عام لكيفية عرض القوائم المالية. الهدف أن تكون القوائم مفهومة وقابلة للمقارنة وتعطي صورة عادلة عن المركز المالي والأداء المالي والتدفقات النقدية.",
            "من المبادئ المهمة في هذا المعيار مبدأ الاستمرارية. عندما تعد الإدارة القوائم، فهي تفترض أن المنشأة ستستمر في نشاطها في المستقبل المنظور ما لم توجد مؤشرات قوية على غير ذلك. إذا وُجد شك جوهري حول الاستمرارية، يجب الإفصاح عنه بوضوح.",
            "يهتم المعيار أيضًا بالاتساق في العرض. لا يجوز تغيير طريقة عرض البنود من سنة لأخرى دون سبب مناسب، لأن التغيير المستمر يضعف قدرة المستخدم على المقارنة. ومع ذلك، يمكن تغيير العرض إذا أصبح الأسلوب الجديد أكثر ملاءمة ووضوحًا.",
            "الأهمية النسبية عنصر جوهري في IAS 1. ليست كل التفاصيل تستحق العرض المنفصل، لكن البنود المهمة التي قد تؤثر على قرارات المستخدمين يجب عرضها أو الإفصاح عنها. لذلك يحتاج المحاسب إلى موازنة بين الإفصاح الكافي وعدم إغراق القارئ بتفاصيل غير مفيدة.",
            "يفرق المعيار عادة بين الأصول والالتزامات المتداولة وغير المتداولة، ويحدد القوائم الرئيسية مثل قائمة المركز المالي، قائمة الربح أو الخسارة والدخل الشامل الآخر، قائمة التغيرات في حقوق الملكية، قائمة التدفقات النقدية، والإيضاحات."
          ],
          "questions": [
            {"q":"ما الغرض الرئيسي من IAS 1؟","options":["تنظيم عرض القوائم المالية","حساب ضريبة الدخل فقط","تحديد سعر البيع","حساب تكلفة المخزون فقط"],"answer":0,"explanation":"IAS 1 يهتم بعرض القوائم المالية العامة ومبادئ الإفصاح والعرض."},
            {"q":"ما المقصود بالاستمرارية؟","options":["إعداد القوائم يوميًا","افتراض استمرار المنشأة ما لم يوجد دليل عكس ذلك","إغلاق المنشأة فورًا","تغيير السياسة كل شهر"],"answer":1,"explanation":"الاستمرارية تعني إعداد القوائم على أساس استمرار نشاط المنشأة في المستقبل المنظور."},
            {"q":"لماذا الاتساق مهم؟","options":["لتحسين قابلية المقارنة بين الفترات","لزيادة عدد الصفحات فقط","لمنع قراءة القوائم","لتغيير الأرقام"],"answer":0,"explanation":"الاتساق يساعد المستخدمين على مقارنة القوائم بين سنة وأخرى."}
          ]
        }
      ]
    },
    {
      "id": "cma",
      "title": "CMA",
      "subtitle": "المحاسبة الإدارية والإدارة المالية",
      "lessons": [
        {
          "id": "cma_cost",
          "code": "CMA Part 1",
          "title": "إدارة التكلفة",
          "summary": [
            "إدارة التكلفة تساعد الإدارة على فهم تكلفة المنتجات والخدمات.",
            "تركز على التكلفة المتغيرة، الثابتة، هامش المساهمة، ونقطة التعادل.",
            "الهدف هو دعم القرار وليس التسجيل فقط."
          ],
          "longExplanation": [
            "في CMA لا يتم النظر إلى التكلفة كرقم تاريخي فقط، بل كأداة لفهم النشاط واتخاذ القرار. الإدارة تحتاج معرفة كيف تتغير التكاليف مع حجم الإنتاج أو البيع، وما أثر ذلك على الربح والتسعير وقبول الطلبات الخاصة.",
            "التكاليف المتغيرة تتغير عادة مع حجم النشاط، مثل المواد المباشرة في كثير من الصناعات. أما التكاليف الثابتة فتبقى ثابتة ضمن نطاق ملائم، مثل الإيجار أو بعض الرواتب الإدارية. هذا التصنيف يساعد في تحليل الربحية لكنه يحتاج فهمًا لطبيعة النشاط.",
            "هامش المساهمة يساوي المبيعات ناقص التكاليف المتغيرة. هذا الهامش يستخدم لتغطية التكاليف الثابتة، وما يزيد بعد ذلك يمثل ربحًا. لذلك يعد هامش المساهمة مفهومًا رئيسيًا في قرارات التسعير وتحليل المنتجات.",
            "نقطة التعادل هي مستوى المبيعات الذي لا تحقق عنده المنشأة ربحًا ولا خسارة. فهم نقطة التعادل يساعد الإدارة على معرفة الحد الأدنى من النشاط المطلوب لتغطية التكاليف، كما يساعد في تقييم أثر تغيير السعر أو التكلفة أو حجم الإنتاج.",
            "إدارة التكلفة لا تعني تخفيض كل المصاريف بشكل عشوائي؛ فقد يؤدي التخفيض غير المدروس إلى تراجع الجودة أو رضا العملاء. الإدارة الجيدة تبحث عن التكلفة التي لا تضيف قيمة وتحاول تحسين العمليات مع الحفاظ على جودة المنتج أو الخدمة."
          ],
          "questions": [
            {"q":"ما هو هامش المساهمة؟","options":["المبيعات ناقص التكاليف المتغيرة","الأصول ناقص الالتزامات","صافي الربح ناقص رأس المال","النقد ناقص البنك"],"answer":0,"explanation":"هامش المساهمة يوضح الجزء المتاح لتغطية التكاليف الثابتة ثم تحقيق الربح."},
            {"q":"ما فائدة نقطة التعادل؟","options":["معرفة مستوى المبيعات الذي يغطي التكاليف","تحديد لون المنتج","اختيار اسم الشركة","حساب رقم الهاتف"],"answer":0,"explanation":"نقطة التعادل تحدد حجم النشاط الذي تكون عنده الإيرادات مساوية للتكاليف."},
            {"q":"أي تكلفة غالبًا تتغير مع حجم الإنتاج؟","options":["المواد المباشرة","الإيجار السنوي","رخصة البرنامج الثابتة","راتب المدير العام غالبًا"],"answer":0,"explanation":"المواد المباشرة ترتبط عادة بحجم الإنتاج لذلك تعد مثالًا شائعًا على التكلفة المتغيرة."},
            {"q":"هل تخفيض التكلفة يعني دائمًا قرارًا جيدًا؟","options":["نعم دائمًا","لا، يجب دراسة أثره على الجودة والقيمة","نعم إذا كان سريعًا","لا علاقة له بالإدارة"],"answer":1,"explanation":"تخفيض التكلفة دون دراسة قد يضر الجودة أو رضا العملاء."}
          ]
        }
      ]
    }
  ]
}

''';
