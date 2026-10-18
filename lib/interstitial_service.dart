import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';
import 'ad_service.dart';

/// Only show at natural navigation breaks; never interrupt reading or quizzes.
class AcademyInterstitialObserver extends NavigatorObserver {
  static final DateTime _sessionStart = DateTime.now();
  static DateTime? _lastShown;
  static InterstitialAd? _ready;
  static bool _loading = false;
  static bool _showing = false;
  static const _productionId = 'ca-app-pub-3082968903080396/4317744798';
  static const _testId = 'ca-app-pub-3940256099942544/1033173712';

  static Future<void> _load() async {
    if (_loading || _ready != null || _showing) return;
    _loading = true;
    try {
      if (!await AdService.instance.initialize()) return;
      await InterstitialAd.load(
        adUnitId: kReleaseMode ? _productionId : _testId,
        request: const AdRequest(),
        adLoadCallback: InterstitialAdLoadCallback(
          onAdLoaded: (ad) { _ready = ad; _loading = false; },
          onAdFailedToLoad: (error) {
            debugPrint('Interstitial load failed: $error');
            _loading = false;
          },
        ),
      );
    } catch (error) {
      debugPrint('Interstitial setup failed: $error');
    } finally {
      if (_ready == null) _loading = false;
    }
  }

  static void _tryShow() {
    final now = DateTime.now();
    if (now.difference(_sessionStart) < const Duration(seconds: 40)) return;
    if (_lastShown != null &&
        now.difference(_lastShown!) < const Duration(minutes: 3)) return;
    if (_showing) return;
    final ad = _ready;
    if (ad == null) { unawaited(_load()); return; }
    _ready = null;
    _showing = true;
    ad.fullScreenContentCallback = FullScreenContentCallback(
      onAdShowedFullScreenContent: (_) => _lastShown = DateTime.now(),
      onAdDismissedFullScreenContent: (ad) {
        ad.dispose();
        _showing = false;
        unawaited(_load());
      },
      onAdFailedToShowFullScreenContent: (ad, error) {
        ad.dispose();
        _showing = false;
        unawaited(_load());
      },
    );
    ad.show();
  }

  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    unawaited(_load());
    super.didPush(route, previousRoute);
  }

  @override
  void didPop(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPop(route, previousRoute);
    if (route is PageRoute && previousRoute is PageRoute) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _tryShow());
    }
  }
}
