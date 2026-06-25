# Google Gemini API Setup Guide

## Critical Update: Backend is Now Using Google Gemini API

The backend has been updated to use **Google's official Gemini API endpoint** instead of a placeholder. All answers from now on will come directly from Google's Gemini API.

### What Changed
1. **API Endpoint**: Now uses `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent`
2. **Request Format**: Updated to match Google's official API specification
3. **Response Parsing**: Updated to handle Google's response format with `candidates` and `content.parts`

---

## Step 1: Get Your Google Gemini API Key

1. Go to **[https://ai.google.dev/](https://ai.google.dev/)**
2. Click on **"Get API Key"** button
3. Sign in with your Google account (or create one)
4. Click **"Create API key"**
5. Copy the generated API key (it will look something like: `AIzaSy...`)

> **Important**: Keep this key private! Never commit it to version control.

---

## Step 2: Update Your Backend Environment

Open the file: `backend/backendpart/.env`

Find this line:
```
GEMINI_API_KEY=your_google_gemini_api_key_here
```

Replace it with your actual API key:
```
GEMINI_API_KEY=AIzaSy_YOUR_ACTUAL_KEY_HERE
```

**Save the file.**

---

## Step 3: Restart Your Backend

Stop the running Django server (Ctrl+C) and start it again:

```bash
cd Chat-with-pdf/backend/backendpart
python manage.py runserver
```

---

## Step 4: Test the Integration

1. **Open the frontend** at `http://localhost:3000`
2. **Upload a PDF** with clear questions/answers in it
3. **Ask a specific question** from the PDF
4. **Check the response**:
   - ✅ **Good**: Answer comes from Gemini API (will be AI-generated based on the document)
   - ❌ **Bad**: Answer is just copied text from the PDF (that means it's using the local fallback)

### How to Tell if Gemini is Working
- Upload a PDF with the text: "The capital of France is Paris"
- Ask: "What is the capital of France?"
- **Gemini will respond**: "The capital of France is Paris" (or similar AI-generated response)
- **Local fallback would return**: "The capital of France is Paris" (exact text extraction)

---

## Step 5: Monitor for Errors

If something goes wrong, you'll see a **warning message** below the answer:
```
⚠️ Third-party Gemini API error: [error details] — returning a local fallback answer.
```

**Common issues**:
1. **Invalid API Key**: Check that you copied it correctly from https://ai.google.dev/
2. **API Key not in .env**: Make sure you edited `.env` and saved it
3. **API Rate Limit**: Google has rate limits; wait a few seconds and try again
4. **Network Issues**: Check your internet connection

---

## API Configuration

Current settings (in `backend/backendpart/app_api/views.py`):
- **Model**: `gemini-1.5-flash` (change to `gemini-pro` if needed)
- **Temperature**: 0.2 (lower = more factual, higher = more creative)
- **Max Output Tokens**: 256 (max response length)

To change these, edit the `call_gemini_api()` function.

---

## How It Works Now

### Upload Flow
1. User uploads PDF/image/text
2. Backend extracts content
3. Backend sends to Gemini API (for ingestion tracking)
4. PDF stored in database with extracted text
5. ✅ Upload complete

### Question Flow
1. User asks a question
2. Backend retrieves uploaded document from database
3. Backend sends question + document context to **Gemini API** ← **ALL ANSWERS COME FROM HERE**
4. Gemini AI generates answer based on the document
5. Response returned to frontend
6. ⚠️ If Gemini fails, local matching is used as fallback (with warning)

---

## Troubleshooting

### Problem: "No exact answer found for that question"
- **Cause**: Either the Gemini API isn't working, or the question isn't in the document
- **Solution**: Check the error message. If it says "API error", verify your API key

### Problem: All answers are exact text from PDF
- **Cause**: Gemini API is failing, using local fallback
- **Solution**: Check `.env` file has correct API key. Check backend console for errors.

### Problem: Backend errors in console
- **Cause**: Various possible issues
- **Solution**: 
  1. Check .env has `GEMINI_API_KEY` with valid Google key
  2. Check internet connection
  3. Check Google Gemini API status at https://status.cloud.google.com/

---

## Files Modified

1. `backend/backendpart/app_api/views.py`
   - Updated `call_gemini_api()` with Google endpoint
   - Updated `push_document_to_third_party()` with Google endpoint
   - Updated `parse_gemini_response()` to handle Google format

2. `backend/backendpart/backendpart/settings.py`
   - Removed old GEMINI_API_URL setting

3. `backend/backendpart/.env`
   - Placeholder API key (needs to be replaced with real Google key)

4. `front-end/src/components/Search/QuestionForm.jsx`
   - Added warning display for API errors

5. `front-end/src/components/Upload/FileUploader.jsx`
   - Added warning display for API errors

---

## Need Help?

If the API isn't working:
1. Verify your API key at https://ai.google.dev/
2. Check backend console for error messages
3. Test locally with curl (example provided on request)
4. Check Google's API documentation: https://ai.google.dev/tutorials/python_quickstart
