# Android Studio Project for Quiz AI

This folder contains a native Android Studio project for the Quiz AI app.

## Project Details
- **Package Name**: `com.quiz.ai`
- **Language**: Java
- **Min SDK**: API 21
- **Target SDK**: Latest

## How to Build

1.  **Open Android Studio**.
2.  Select **Open** and navigate to this `android_studio_project` folder.
    *   *Note*: Since this is a raw source export, you may need to "Import Project" or create a new project and copy the `app/src` folder content if Gradle files are missing.
    *   **Recommended**: Create a new "Empty Views Activity" project in Android Studio, then replace its `app/src` folder with the one provided here.
3.  **Sync Gradle**: Allow Android Studio to download necessary dependencies.
4.  **Build APK**:
    *   Go to **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
    *   The APK will be generated in `app/build/outputs/apk/debug/`.
5.  **Build AAB (Play Store)**:
    *   Go to **Build > Generate Signed Bundle / APK**.
    *   Choose **Android App Bundle**.
    *   Create a keystore key and follow the wizard.

## Structure
- `app/src/main/AndroidManifest.xml`: Permissions and configuration.
- `app/src/main/java/com/quiz/ai/MainActivity.java`: WebView logic.
- `app/src/main/res/layout/activity_main.xml`: UI Layout.
