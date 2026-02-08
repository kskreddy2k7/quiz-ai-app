# APK Storage

This directory is used to host the Android APK file for direct download from the website.

## How to add the APK

1. Download the latest APK from GitHub Actions artifacts or Releases
2. Rename it to `S-Quiz.apk`
3. Place it in this directory
4. Commit and deploy

The website will automatically detect Android devices and offer the APK download.

## Automatic Build

The APK is automatically built by GitHub Actions on every push to main branch.
Download it from: https://github.com/kskreddy2k7/quiz-ai-app/releases

## Note

For Play Store distribution, use the AAB (Android App Bundle) format instead of APK.
