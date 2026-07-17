from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')
old_title = "const Text('تعلم IFRS و CMA بالعربي', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),"
new_title = "const Text('تعلّم المحاسبة من الأساس إلى الاحتراف', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),"
old_desc = "Text('عدد الدروس الحالية: $count. يمكنك تحديث المحتوى من الإنترنت بدون إصدار APK جديد.', style: const TextStyle(color: Colors.white, height: 1.5)),"
new_desc = "Text('يضم التطبيق $count درسًا، ويتم تحديث المحتوى باستمرار عبر الإنترنت دون الحاجة إلى تثبيت إصدار جديد.', style: const TextStyle(color: Colors.white, height: 1.5)),"

if old_title not in text:
    raise SystemExit('Old title text not found')
if old_desc not in text:
    raise SystemExit('Old description text not found')

text = text.replace(old_title, new_title, 1).replace(old_desc, new_desc, 1)
path.write_text(text, encoding='utf-8')
print('Home text updated successfully')
