#!/usr/bin/env python3
"""
Simple APK builder for web apps using python-for-android
This script creates a basic Android APK that wraps the web app
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def create_android_webview_app():
    """Create a simple Android webview APK"""
    
    # Create android project structure
    android_dir = Path("android_project")
    if android_dir.exists():
        shutil.rmtree(android_dir)
    
    android_dir.mkdir()
    
    # Create basic Android manifest
    manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.sai.squiz"
    android:versionCode="1"
    android:versionName="1.0">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="S Quiz"
        android:theme="@style/AppTheme"
        android:usesCleartextTraffic="true">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="portrait">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>"""
    
    # Create MainActivity.java
    main_activity_content = """package com.sai.squiz;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebSettings;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        webView = findViewById(R.id.webview);
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setAllowFileAccess(true);
        webSettings.setAllowContentAccess(true);
        
        webView.setWebViewClient(new WebViewClient());
        
        // Load the web app - for development, you can change this to your local server
        webView.loadUrl("file:///android_asset/index.html");
    }
    
    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}"""
    
    # Create activity_main.xml layout
    layout_content = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

</LinearLayout>"""
    
    # Write files
    (android_dir / "AndroidManifest.xml").write_text(manifest_content)
    
    src_dir = android_dir / "src" / "main" / "java" / "com" / "sai" / "squiz"
    src_dir.mkdir(parents=True)
    (src_dir / "MainActivity.java").write_text(main_activity_content)
    
    res_dir = android_dir / "src" / "main" / "res" / "layout"
    res_dir.mkdir(parents=True)
    (res_dir / "activity_main.xml").write_text(layout_content)
    
    # Copy static files to assets
    assets_dir = android_dir / "src" / "main" / "assets"
    assets_dir.mkdir(parents=True)
    
    if Path("static").exists():
        shutil.copytree("static", assets_dir / "static", dirs_exist_ok=True)
    
    # Copy index.html to assets root
    if Path("static/index.html").exists():
        shutil.copy2("static/index.html", assets_dir / "index.html")
    
    print("Android project structure created!")
    print(f"Project location: {android_dir.absolute()}")
    print("\nTo build the APK, you need to:")
    print("1. Install Android Studio")
    print("2. Open the project in Android Studio")
    print("3. Build APK using Build > Build Bundle(s) / APK(s) > Build APK(s)")
    
    return android_dir

if __name__ == "__main__":
    try:
        project_dir = create_android_webview_app()
        print(f"\n✅ Android project created successfully!")
        print(f"📁 Location: {project_dir}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
