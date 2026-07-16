from pathlib import Path

MAIN_FILE = Path('lib/main.dart')


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        if new in text:
            return text
        raise SystemExit(f'Expected text not found: {old}')
    return text.replace(old, new, 1)


def main() -> None:
    text = MAIN_FILE.read_text(encoding='utf-8')
    text = replace_once(
        text,
        "const Text('تعلم IFRS و CMA بالعربي', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold))",
        "const Text('تعلّم المحاسبة من الأساس إلى الاحتراف', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold))",
    )
    text = replace_once(
        text,
        "Text('عدد الدروس الحالية: $count. يمكنك تحديث المحتوى من الإنترنت بدون إصدار APK جديد.', style: const TextStyle(color: Colors.white, height: 1.5))",
        "Text('عدد الدروس الحالية: $count. أقسام محاسبية متخصصة تتوسع باستمرار ويمكن تحديثها دون إصدار APK جديد.', style: const TextStyle(color: Colors.white, height: 1.5))",
    )
    MAIN_FILE.write_text(text, encoding='utf-8')
    print('Updated academy home text for expanded accounting tracks.')


if __name__ == '__main__':
    main()
