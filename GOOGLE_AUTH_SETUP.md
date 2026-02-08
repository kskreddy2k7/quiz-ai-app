# Google Sign-In Setup Guide

This guide explains how to configure Google Sign-In for the S Quiz AI application.

## Prerequisites

- A Google Account
- Access to Google Cloud Console

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter project name: "S Quiz AI" (or your preferred name)
5. Click "Create"

## Step 2: Enable Google Sign-In API

1. In the Google Cloud Console, navigate to "APIs & Services" > "Library"
2. Search for "Google Identity Services"
3. Click on it and press "Enable"

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (unless you have a workspace)
3. Click "Create"
4. Fill in the required fields:
   - **App name**: S Quiz AI
   - **User support email**: Your email
   - **Developer contact email**: Your email
5. Click "Save and Continue"
6. Skip the "Scopes" section (click "Save and Continue")
7. Add test users if needed (for development)
8. Click "Save and Continue"

## Step 4: Create OAuth Client ID

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose application type: "Web application"
4. Enter name: "S Quiz Web Client"
5. Add authorized JavaScript origins:
   - For local development: `http://localhost:8000`
   - For production: `https://your-domain.com`
6. Add authorized redirect URIs (same as above)
7. Click "Create"
8. **IMPORTANT**: Copy the Client ID that appears - you'll need this!

## Step 5: Configure Environment Variables

### For Local Development

Create a `.env` file in the project root:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com

# JWT Secret (generate a secure random string)
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Other existing environment variables
GEMINI_API_KEY=your-gemini-api-key
```

### For Production (Render/Railway/Heroku)

Add these environment variables in your hosting platform's dashboard:

1. **Render.com**:
   - Go to your service dashboard
   - Click "Environment"
   - Add new environment variable:
     - Key: `GOOGLE_CLIENT_ID`
     - Value: Your Google Client ID

2. **Railway.app**:
   - Go to your project
   - Click "Variables"
   - Add: `GOOGLE_CLIENT_ID=your-client-id`

3. **Heroku**:
   - Go to Settings > Config Vars
   - Add: `GOOGLE_CLIENT_ID` with your client ID

## Step 6: Test the Integration

1. Start your application:
   ```bash
   python main_web.py
   ```

2. Open your browser to `http://localhost:8000`

3. You should see a "Continue with Google" button on the login screen

4. Click it and sign in with your Google account

5. You should be logged in automatically!

## Security Best Practices

### ✅ DO:
- Use HTTPS in production (required by Google)
- Keep your Google Client ID safe (it's not as sensitive as a secret, but still)
- Never commit secrets to Git
- Use environment variables for all sensitive config
- Enable Google's security features (2FA, etc.)

### ❌ DON'T:
- Don't hardcode the Client ID in your frontend code
- Don't share your OAuth Client Secret (we don't use it, but if you do)
- Don't use the same OAuth client for multiple environments
- Don't skip HTTPS in production

## Troubleshooting

### "Google Sign-In is not configured"
- Check that `GOOGLE_CLIENT_ID` is set in your environment
- Restart your application after setting the environment variable

### "Invalid token" or "401 Unauthorized"
- Verify the Client ID matches exactly
- Check that your domain is in the authorized JavaScript origins
- Clear browser cache and cookies

### "This app hasn't been verified"
- This is normal for apps in development/testing
- Click "Advanced" > "Go to S Quiz (unsafe)" to continue
- For production, submit your app for Google verification

### Button doesn't appear
- Check browser console for JavaScript errors
- Verify the Google Sign-In script is loading
- Check network tab for failed requests

## Play Store Requirements

If publishing to Google Play Store:

1. Add your app's package name to authorized redirect URIs
2. Use SHA-1 fingerprint of your signing key
3. Create an OAuth client ID for Android
4. Follow Google's Play Store OAuth requirements
5. Implement proper token refresh logic

## Support

For issues with Google Sign-In:
- [Google Identity Services Documentation](https://developers.google.com/identity)
- [OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server)

## Summary

After setup, users can:
- ✅ Sign in with one click using their Google account
- ✅ No need to remember passwords
- ✅ Secure authentication with Google's infrastructure
- ✅ Profile photos automatically imported
- ✅ Seamless user experience

The authentication is production-ready and follows Google's best practices!
