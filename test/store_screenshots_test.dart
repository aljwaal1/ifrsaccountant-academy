import 'dart:convert';
import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:accountant_academy_dynamic/main.dart';

late Map<String, dynamic> storeContent;
final screenshotKey = GlobalKey();

Future<void> launchApp(
  WidgetTester tester, {
  required Size logicalSize,
}) async {
  tester.view.physicalSize = logicalSize;
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);

  SharedPreferences.setMockInitialValues({
    'academy_content_json': jsonEncode(storeContent),
    'academy_last_update': '2026-08-17 18:00',
  });

  await tester.pumpWidget(
    RepaintBoundary(
      key: screenshotKey,
      child: const AccountantAcademyApp(),
    ),
  );
  await tester.pumpAndSettle();
}

Future<void> capture(String relativePath, double outputScale) async {
  final boundary = screenshotKey.currentContext!.findRenderObject()
      as RenderRepaintBoundary;
  final image = await boundary.toImage(pixelRatio: outputScale);
  final data = await image.toByteData(format: ui.ImageByteFormat.png);
  if (data == null) throw StateError('Could not encode screenshot');

  final file = File('test/goldens/$relativePath');
  await file.parent.create(recursive: true);
  await file.writeAsBytes(data.buffer.asUint8List(), flush: true);
  image.dispose();
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
    const logicalSize = Size(360, 640);
    const scale = 3.0;

    testWidgets('01 home', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await capture('phone/01_home.png', scale);
    });

    testWidgets('02 lessons', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await openFirstTrack(tester);
      await capture('phone/02_lessons.png', scale);
    });

    testWidgets('03 lesson summary', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await openFirstLesson(tester);
      await capture('phone/03_lesson_summary.png', scale);
    });

    testWidgets('04 quiz', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await openFirstLesson(tester);
      await tester.tap(find.text('اختبار'));
      await tester.pumpAndSettle();
      await capture('phone/04_quiz.png', scale);
    });

    testWidgets('05 updates', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await tester.tap(find.text('تحديث').last);
      await tester.pumpAndSettle();
      await capture('phone/05_updates.png', scale);
    });

    testWidgets('06 developer', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await tester.tap(find.text('المطور').last);
      await tester.pumpAndSettle();
      await capture('phone/06_developer.png', scale);
    });
  });

  group('Tablet 7-inch 1440x2560', () {
    const logicalSize = Size(720, 1280);
    const scale = 2.0;

    testWidgets('01 home', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await capture('tablet_7/01_home.png', scale);
    });

    testWidgets('02 lessons', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await openFirstTrack(tester);
      await capture('tablet_7/02_lessons.png', scale);
    });

    testWidgets('03 lesson summary', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await openFirstLesson(tester);
      await capture('tablet_7/03_lesson_summary.png', scale);
    });

    testWidgets('04 quiz', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await openFirstLesson(tester);
      await tester.tap(find.text('اختبار'));
      await tester.pumpAndSettle();
      await capture('tablet_7/04_quiz.png', scale);
    });
  });

  group('Tablet 10-inch 1800x3200', () {
    const logicalSize = Size(900, 1600);
    const scale = 2.0;

    testWidgets('01 home', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await capture('tablet_10/01_home.png', scale);
    });

    testWidgets('02 lessons', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await openFirstTrack(tester);
      await capture('tablet_10/02_lessons.png', scale);
    });

    testWidgets('03 lesson summary', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await openFirstLesson(tester);
      await capture('tablet_10/03_lesson_summary.png', scale);
    });

    testWidgets('04 quiz', (tester) async {
      await launchApp(tester, logicalSize: logicalSize);
      await openFirstLesson(tester);
      await tester.tap(find.text('اختبار'));
      await tester.pumpAndSettle();
      await capture('tablet_10/04_quiz.png', scale);
    });
  });
}
