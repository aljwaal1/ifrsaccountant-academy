import 'dart:async';

import 'package:google_mobile_ads/google_mobile_ads.dart';

/// Ad initialization copied from the proven pattern used by the Matching app.
/// Ads are never allowed to block or crash application startup.
class AdService {
  AdService._();

  static final AdService instance = AdService._();

  Future<bool>? _initialization;

  Future<bool> initialize() => _initialization ??= _initialize();

  Future<bool> _initialize() async {
    try {
      final consentUpdated = Completer<void>();
      ConsentInformation.instance.requestConsentInfoUpdate(
        ConsentRequestParameters(),
        () {
          ConsentForm.loadAndShowConsentFormIfRequired((_) {
            if (!consentUpdated.isCompleted) consentUpdated.complete();
          });
        },
        (_) {
          if (!consentUpdated.isCompleted) consentUpdated.complete();
        },
      );

      await consentUpdated.future.timeout(
        const Duration(seconds: 8),
        onTimeout: () {},
      );

      final canRequestAds = await ConsentInformation.instance.canRequestAds();
      if (!canRequestAds) return false;

      await MobileAds.instance.initialize();
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> get privacyOptionsRequired async {
    try {
      return await ConsentInformation.instance
              .getPrivacyOptionsRequirementStatus() ==
          PrivacyOptionsRequirementStatus.required;
    } catch (_) {
      return false;
    }
  }

  void showPrivacyOptions(void Function(FormError?) onDismissed) {
    ConsentForm.showPrivacyOptionsForm(onDismissed);
  }
}
