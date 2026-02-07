package com.quiz.ai;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.view.KeyEvent;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {

    private WebView webView;
    // URL to load
    private static final String TARGET_URL = "https://quiz-ai-app-1.onrender.com";

    @Override
    @SuppressLint("SetJavaScriptEnabled")
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webView);
        
        // Configure WebView Settings
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setDatabaseEnabled(true);
        webSettings.setAllowFileAccess(true);
        webSettings.setAllowContentAccess(true);
        
        // Cache settings for performance
        webSettings.setCacheMode(WebSettings.LOAD_DEFAULT);

        // Set WebViewClient to handle page navigation within the WebView
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                // Keep navigation inside the WebView if it matches our domain
                if (url.contains("quiz-ai-app-1.onrender.com")) {
                    return false;
                }
                // Determine if we want to open external links in browser, 
                // typically returning false loads in webview, true hands off to OS.
                // For a wrapper app, we usually want to keep everything in app if possible,
                // or open external links (like social media) in browser.
                // Here we keep everything in WebView for simplicity unless logic dictates otherwise.
                return false; 
            }
        });

        // Load the URL
        if (savedInstanceState == null) {
            webView.loadUrl(TARGET_URL);
        }
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        // Handle Back button to go back in WebView history
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
    
    // For newer Android versions, onBackPressed is separate, but onKeyDown covers most bases for simple Activities.
    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
