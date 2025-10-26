# 🔐 OAuth Configuration Guide - Vectort.io

## ⚠️ SECURITY NOTE
This guide does NOT contain any actual secrets. All credentials are stored securely in environment variables.

---

## ✅ Google OAuth Configuration

### Backend Configuration
The Google OAuth credentials are configured in `/app/backend/.env`:
- `GOOGLE_CLIENT_ID`: Your Google OAuth Client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth Client Secret
- `GOOGLE_REDIRECT_URI`: Callback URL for OAuth flow

### Required URIs in Google Cloud Console

**JavaScript Origins**:
```
https://oauth-debug-2.preview.emergentagent.com
```

**Redirect URIs**:
```
https://oauth-debug-2.preview.emergentagent.com/api/auth/google/callback
```

### How to Configure

1. Go to: https://console.cloud.google.com/apis/credentials
2. Select your OAuth Client ID
3. Add the JavaScript Origin (see above)
4. Add the Redirect URI (see above)
5. Click "SAVE"
6. Wait 1-2 minutes for propagation

---

## 🐙 GitHub OAuth Configuration

### Backend Configuration
The GitHub OAuth credentials are configured in `/app/backend/.env`:
- `GITHUB_CLIENT_ID`: Your GitHub OAuth Client ID
- `GITHUB_CLIENT_SECRET`: Your GitHub OAuth Client Secret
- `GITHUB_REDIRECT_URI`: Callback URL for OAuth flow

### Required URIs in GitHub OAuth App

**Authorization callback URL**:
```
https://oauth-debug-2.preview.emergentagent.com/api/auth/github/callback
```

### How to Configure

1. Go to: https://github.com/settings/developers
2. Select your OAuth App
3. Update "Authorization callback URL" (see above)
4. Click "Update application"

---

## 🧪 Testing OAuth

1. Visit: https://oauth-debug-2.preview.emergentagent.com
2. Click "Continue with Google" or "GitHub"
3. Authorize access
4. You should be redirected to the dashboard

---

## 🔒 Security Best Practices

- ✅ All secrets are stored in `.env` files (git-ignored)
- ✅ Never commit credentials to git
- ✅ Use environment variables in code
- ✅ Rotate credentials regularly
