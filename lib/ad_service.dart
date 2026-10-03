import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

/// Reliable AdMob startup:
/// 1) initialize the Mobile Ads SDK immediately, as in Dioon Plus,
/// 2) complete UMP consent before sending a real ad request,
/// 3) do not permanently cache a temporary consent failure.
class AdService {
  AdService._();

  static final AdService instance = AdService._();

  Future<InitializationStatus>? _sdkInitialization;
  Future<bool>? _consentInitialization;

  Future<InitializationStatus> _initializeSdk() {
    return _sdkInitialization ??= MobileAds.instance.initialize();
  }

  Future<bool> initialize() async {
    // Dioon Plus initializes the SDK as soon as the app starts. Doing the same
    // here removes SDK startup from the critical banner-load path.
    try {
      await _initializeSdk();
    } catch (error) {
      debugPrint('AdMob: SDK initialization failed: $error');
      _sdkInitialization = null;
      return false;
    }

    final existing = _consentInitialization;
    if (existing != null) return existing;

    final attempt = _updateConsentAndCheck();
    _consentInitialization = attempt;
    final success = await attempt;

    // A false result can be temporary (network/UMP state). Allow the banner
    // widget to retry instead of caching false for the whole app session.
    if (!success) {
      _consentInitialization = null;
    }
    return success;
  }

  Future<bool> _updateConsentAndCheck() async {
    final completer = Completer<void>();

    void completeOnce() {
      if (!completer.isCompleted) completer.complete();
    }

    try {
      ConsentInformation.instance.requestConsentInfoUpdate(
        ConsentRequestParameters(),
        () {
          ConsentForm.loadAndShowConsentFormIfRequired((formError) {
            if (formError != null) {
              debugPrint(
                'AdMob UMP: consent form error '
                'code=${formError.errorCode}, message=${formError.message}',
              );
            }
            completeOnce();
          });
        },
        (formError) {
          debugPrint(
            'AdMob UMP: consent info update failed '
            'code=${formError.errorCode}, message=${formError.message}',
          );
          completeOnce();
        },
      );

      // Avoid hanging forever if a device/SDK callback is unexpectedly lost.
      await completer.future.timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          debugPrint('AdMob UMP: consent callback timed out.');
        },
      );

      final canRequestAds = await ConsentInformation.instance.canRequestAds();
      debugPrint('AdMob UMP: canRequestAds=$canRequestAds');
      return canRequestAds;
    } catch (error) {
      debugPrint('AdMob UMP: consent flow exception: $error');
      try {
        return await ConsentInformation.instance.canRequestAds();
      } catch (_) {
        return false;
      }
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
