import 'package:flutter_test/flutter_test.dart';
import 'package:accountant_academy_dynamic/main.dart';

void main() {
  testWidgets('Accountant Academy starts', (tester) async {
    await tester.pumpWidget(const AccountantAcademyApp());
    expect(find.text('أكاديمية المحاسب الدولي'), findsOneWidget);
  });
}
