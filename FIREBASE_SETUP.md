# 🔥 Firebase Service Account Setup Guide

## Step 1: Get Service Account Credentials

1. **Go to Firebase Console**: https://console.firebase.google.com/
2. **Select your project**: `kisanconnect-402db`
3. **Click the gear icon** ⚙️ → **Project Settings**
4. **Go to "Service Accounts" tab**
5. **Click "Generate new private key"** button
6. **Download the JSON file** (keep it secure!)

## Step 2: Extract Required Information

From the downloaded JSON file, you need these values:

```json
{
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@kisanconnect-402db.iam.gserviceaccount.com",
  "client_id": "123456789..."
}
```

## Step 3: Update .env File

### Option A: Use the Setup Script (Recommended)
```bash
python setup_firebase.py
```

### Option B: Manual Update
Edit `news-backend/.env` and replace:

- `your-private-key-id` → your actual `private_key_id`
- `YOUR_PRIVATE_KEY_HERE` → your actual `private_key` (keep the \n characters)
- `firebase-adminsdk-fbsvc@kisanconnect-402db.iam.gserviceaccount.com` → your actual `client_email`
- `your-client-id` → your actual `client_id`

## Step 4: Test Connection

```bash
python test_connection.py
```

## Step 5: Start Backend

```bash
python start.py
```

## 🔒 Security Notes

- **Never commit** the service account JSON file to version control
- **Keep the .env file secure** and don't share it
- **Add .env to .gitignore** if not already there

## ❓ Troubleshooting

### "Permission denied" errors:
- Make sure your service account has the right permissions
- In Firebase Console → IAM & Admin, ensure your service account has "Firebase Admin SDK Administrator Service Agent" role

### "Project not found" errors:
- Double-check the project ID is `kisanconnect-402db`
- Make sure you're using the correct Firebase project

### "Invalid credentials" errors:
- Verify the private key format (should include `-----BEGIN PRIVATE KEY-----`)
- Check that all \n characters are preserved in the private key