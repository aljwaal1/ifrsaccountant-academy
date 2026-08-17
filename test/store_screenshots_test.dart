import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:accountant_academy_dynamic/main.dart';

late Map<String, dynamic> storeContent;

Future<void> launchApp(
  WidgetTester tester, {
  required Size physicalSize,
  required double devicePixelRatio,
}) async {
  tester.view.physicalSize = physicalSize;
  tester.view.devicePixelRatio = devicePixelRatio;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);

  SharedPreferences.setMockInitialValues({
    'academy_content_json': jsonEncode(storeContent),
    'academy_last_update': '2026-08-17 18:00',
  });

  await tester.pumpWidget(const AccountantAcademyApp());
  await tester.pumpAndSettle();
}

Future<void> capture(WidgetTester tester, String path) async {
  await expectLater(
    find.byType(Scaffold).last,
    matchesGoldenFile(path),
  );
}

Future<void> openFirstTrack(WidgetTester tester) async {
  await tester.tap(find.byType(SectionCard).first);
  await tester.pumpAndSettle();
}

Future<void> openFirstLesson(WidgetTester tester) async {
  await openFirstTrack(tester);
  await tester.tap(find.byType(ListTile).first);
  await tester.pumpAndSettle();
}

void main() {
  setUpAll(() {
    storeContent = jsonDecode(
      File('store_assets/academy_content.json').readAsStringSync(),
    ) as Map<String, dynamic>;
  });

  group('Phone 1080x1920', () {
    const size = Size(1080, 1920);
    const dpr = 3.0;

    testWidgets('01 home', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await capture(tester, 'goldens/phone/01_home.png');
    });

    testWidgets('02 lessons', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await openFirstTrack(tester);
      await capture(tester, 'goldens/phone/02_lessons.png');
    });

    testWidgets('03 lesson summary', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await openFirstLesson(tester);
      await capture(tester, 'goldens/phone/03_lesson_summary.png');
    });

    testWidgets('04 quiz', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await openFirstLesson(tester);
      await tester.tap(find.text('اختبار'));
      await tester.pumpAndSettle();
      await capture(tester, 'goldens/phone/04_quiz.png');
    });

    testWidgets('05 updates', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await tester.tap(find.text('تحديث').last);
      await tester.pumpAndSettle();
      await capture(tester, 'goldens/phone/05_updates.png');
    });

    testWidgets('06 developer', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await tester.tap(find.text('المطور').last);
      await tester.pumpAndSettle();
      await capture(tester, 'goldens/phone/06_developer.png');
    });
  });

  group('Tablet 7-inch 1440x2560', () {
    const size = Size(1440, 2560);
    const dpr = 2.0;

    testWidgets('01 home', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await capture(tester, 'goldens/tablet_7/01_home.png');
    });

    testWidgets('02 lessons', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await openFirstTrack(tester);
      await capture(tester, 'goldens/tablet_7/02_lessons.png');
    });

    testWidgets('03 lesson summary', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await openFirstLesson(tester);
      await capture(tester, 'goldens/tablet_7/03_lesson_summary.png');
    });

    testWidgets('04 quiz', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await openFirstLesson(tester);
      await tester.tap(find.text('اختبار'));
      await tester.pumpAndSettle();
      await capture(tester, 'goldens/tablet_7/04_quiz.png');
    });
  });

  group('Tablet 10-inch 1800x3200', () {
    const size = Size(1800, 3200);
    const dpr = 2.0;

    testWidgets('01 home', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await capture(tester, 'goldens/tablet_10/01_home.png');
    });

    testWidgets('02 lessons', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await openFirstTrack(tester);
      await capture(tester, 'goldens/tablet_10/02_lessons.png');
    });

    testWidgets('03 lesson summary', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await openFirstLesson(tester);
      await capture(tester, 'goldens/tablet_10/03_lesson_summary.png');
    });

    testWidgets('04 quiz', (tester) async {
      await launchApp(tester, physicalSize: size, devicePixelRatio: dpr);
      await openFirstLesson(tester);
      await tester.tap(find.text('اختبار'));
      await tester.pumpAndSettle();
      await capture(tester, 'goldens/tablet_10/04_quiz.png');
    });
  });
}
