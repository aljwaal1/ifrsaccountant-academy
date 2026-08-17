# Google Play release

This project keeps the existing direct APK workflow and adds a separate manual workflow for the Google Play Android App Bundle (AAB).

## App identity

- App name: `أكاديمية المحاسب`
- Application ID: `com.explapp.accountantacademy`
- Minimum Android API: 23
- Google Play target API: 36
- Flutter: 3.44.7

## Required GitHub Actions secrets

Add these repository secrets before running the Google Play workflow:

- `ANDROID_KEYSTORE_BASE64`
- `ANDROID_KEYSTORE_PASSWORD`
- `ANDROID_KEY_ALIAS`
- `ANDROID_KEY_PASSWORD`

Never commit the keystore or any of these secret values to the repository.

## Build the Play bundle

1. Open the repository on GitHub.
2. Open **Actions**.
3. Choose **Build Google Play AAB**.
4. Choose **Run workflow**.
5. Download the artifact named `accountant-academy-google-play-aab`.
6. Upload `app-release.aab` to Google Play Console.

The workflow verifies the AAB signature before uploading the artifact.

## Versioning

The current Flutter version is read from `pubspec.yaml` (`version: 1.0.0+1`). Before every later Google Play update, increase the build number after `+` so every uploaded bundle has a higher `versionCode`.

## Signing

The workflow uses a private upload key stored only through GitHub Actions secrets. Google Play App Signing can then manage the final app-signing key used for APKs delivered to users.
