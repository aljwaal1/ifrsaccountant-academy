from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

replacement = r'''class TracksView extends StatelessWidget {
  const TracksView({super.key, required this.content});
  final Map<String, dynamic> content;

  @override
  Widget build(BuildContext context) {
    final tracks = (content['tracks'] as List? ?? [])
        .cast<Map<String, dynamic>>();
    final lessonCount = tracks.fold<int>(
      0,
      (total, track) => total + ((track['lessons'] as List?)?.length ?? 0),
    );

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _HeroCard(count: lessonCount, sectionCount: tracks.length),
        const SizedBox(height: 18),
        const Text(
          'اختر القسم',
          style: TextStyle(fontSize: 21, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(
          'ادخل إلى القسم لعرض دروسه وابدأ التعلم بالترتيب الذي يناسبك.',
          style: TextStyle(color: Colors.grey.shade700, height: 1.5),
        ),
        const SizedBox(height: 14),
        for (final track in tracks) SectionCard(track: track),
      ],
    );
  }
}

class _HeroCard extends StatelessWidget {
  const _HeroCard({required this.count, required this.sectionCount});
  final int count;
  final int sectionCount;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF0F3D56), Color(0xFF00A6A6)],
        ),
        borderRadius: BorderRadius.circular(26),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(
            Icons.workspace_premium,
            color: Color(0xFFE1A83A),
            size: 42,
          ),
          const SizedBox(height: 10),
          const Text(
            'تعلّم المحاسبة من الأساس إلى الاحتراف',
            style: TextStyle(
              color: Colors.white,
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '$sectionCount أقسام محاسبية و$count درسًا، مع تحديث مستمر للمحتوى عبر الإنترنت.',
            style: const TextStyle(color: Colors.white, height: 1.5),
          ),
        ],
      ),
    );
  }
}

class _TrackStyle {
  const _TrackStyle(this.icon, this.color);
  final IconData icon;
  final Color color;
}

_TrackStyle _trackStyle(Map<String, dynamic> track) {
  final id = (track['id'] ?? '').toString().toLowerCase();
  final title = (track['title'] ?? '').toString();

  if (id.contains('ifrs') || title.contains('IFRS')) {
    return const _TrackStyle(Icons.public, Color(0xFF176B87));
  }
  if (id.contains('cma') || title.contains('CMA')) {
    return const _TrackStyle(Icons.workspace_premium, Color(0xFF7B4BB7));
  }
  if (id.contains('bank') || title.contains('البنوك')) {
    return const _TrackStyle(Icons.account_balance, Color(0xFF167D6D));
  }
  if (id.contains('cost') || title.contains('التكاليف')) {
    return const _TrackStyle(Icons.calculate, Color(0xFFE07A2D));
  }
  if (id.contains('manager') || title.contains('الإدارية')) {
    return const _TrackStyle(Icons.analytics, Color(0xFFB54555));
  }
  if (id.contains('advanced') || title.contains('المتقدمة')) {
    return const _TrackStyle(Icons.auto_graph, Color(0xFF5C6578));
  }
  if (id.contains('intermediate') || title.contains('المتوسطة')) {
    return const _TrackStyle(Icons.stacked_line_chart, Color(0xFF4F67B1));
  }
  if (id.contains('financial') || title.contains('المالية')) {
    return const _TrackStyle(Icons.receipt_long, Color(0xFF2E7D5B));
  }
  if (id.contains('princip') || title.contains('مبادئ')) {
    return const _TrackStyle(Icons.menu_book, Color(0xFF0097A7));
  }
  return const _TrackStyle(Icons.school, Color(0xFF0F3D56));
}

class SectionCard extends StatelessWidget {
  const SectionCard({super.key, required this.track});
  final Map<String, dynamic> track;

  @override
  Widget build(BuildContext context) {
    final lessons = (track['lessons'] as List? ?? [])
        .cast<Map<String, dynamic>>();
    final style = _trackStyle(track);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 0,
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: InkWell(
        onTap: () {
          SystemSound.play(SystemSoundType.click);
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => Directionality(
                textDirection: TextDirection.rtl,
                child: TrackLessonsPage(track: track),
              ),
            ),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 54,
                height: 54,
                decoration: BoxDecoration(
                  color: style.color.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Icon(style.icon, color: style.color, size: 29),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      track['title']?.toString() ?? '',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      track['subtitle']?.toString() ?? '',
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(color: Colors.grey.shade700, height: 1.35),
                    ),
                    const SizedBox(height: 9),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(
                        color: style.color.withOpacity(0.10),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        '${lessons.length} درس',
                        style: TextStyle(
                          color: style.color,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Icon(Icons.chevron_left, color: style.color, size: 30),
            ],
          ),
        ),
      ),
    );
  }
}

class TrackLessonsPage extends StatelessWidget {
  const TrackLessonsPage({super.key, required this.track});
  final Map<String, dynamic> track;

  @override
  Widget build(BuildContext context) {
    final lessons = (track['lessons'] as List? ?? [])
        .cast<Map<String, dynamic>>();
    final style = _trackStyle(track);

    return Scaffold(
      appBar: AppBar(
        title: Text(track['title']?.toString() ?? ''),
        centerTitle: true,
        backgroundColor: style.color,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: style.color.withOpacity(0.10),
              borderRadius: BorderRadius.circular(22),
            ),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 27,
                  backgroundColor: style.color,
                  child: Icon(style.icon, color: Colors.white, size: 28),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        track['title']?.toString() ?? '',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        track['subtitle']?.toString() ?? '',
                        style: TextStyle(color: Colors.grey.shade700, height: 1.4),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '${lessons.length} درس',
                        style: TextStyle(
                          color: style.color,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          if (lessons.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 50),
              child: Center(child: Text('ستتم إضافة دروس هذا القسم قريبًا.')),
            )
          else
            for (var index = 0; index < lessons.length; index++)
              Card(
                margin: const EdgeInsets.only(bottom: 10),
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
                child: ListTile(
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 14,
                    vertical: 7,
                  ),
                  leading: CircleAvatar(
                    backgroundColor: style.color.withOpacity(0.12),
                    foregroundColor: style.color,
                    child: Text('${index + 1}'),
                  ),
                  title: Text(
                    _lessonTitle(lessons[index]),
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  subtitle: Text(
                    'أسئلة: ${((lessons[index]['questions'] as List?) ?? []).length}',
                  ),
                  trailing: const Icon(Icons.chevron_left),
                  onTap: () {
                    SystemSound.play(SystemSoundType.click);
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => Directionality(
                          textDirection: TextDirection.rtl,
                          child: LessonPage(lesson: lessons[index]),
                        ),
                      ),
                    );
                  },
                ),
              ),
        ],
      ),
    );
  }

  String _lessonTitle(Map<String, dynamic> lesson) {
    final code = lessonCode(lesson).trim();
    final title = (lesson['title'] ?? '').toString();
    return code.isEmpty ? title : '$code - $title';
  }
}

'''

pattern = r'class TracksView extends StatelessWidget \{.*?(?=class LessonPage extends StatefulWidget)'
updated, count = re.subn(pattern, replacement, text, flags=re.S)
if count != 1:
    raise SystemExit(f'Expected one navigation block, found {count}')

path.write_text(updated, encoding='utf-8')
print('Section navigation v2 applied successfully')
