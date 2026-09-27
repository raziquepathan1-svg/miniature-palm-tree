# Instagram and Facebook: automatic Reels

Every day the agent makes a ~45-second vertical **Short** on the same topic as the YouTube video. It's fact-checked with the same script. After the YouTube video goes public (12 PM New York, 7 PM Saudi), the workflow **Post Short to Instagram and Facebook** posts it as a **Reel** on both. If you set the YouTube video to Private during your review, the Short is **not** posted.

Everything is free. There are no extra costs, apart from a few extra cents of Claude usage for writing the Short.

---

## Part 1: Create the Facebook Page (5 min, phone or laptop)
1. Log in to **facebook.com** with your personal Facebook account. A Page must belong to a personal profile, but the Page is shown under its own name.
2. Go to **facebook.com/pages/create**.
3. **Page name:** `Health Support Studio`
4. **Category:** `Health & Wellness Website` (or `Education`)
5. **Bio:**
   ```
   Health & medical topics, made simple. New health videos every day. Educational only, not medical advice. In an emergency, call 911.
   ```
6. Click **Create Page**.
7. **Profile picture:** `branding/logo.png`. **Cover photo:** `branding/facebook_cover.png`.
8. In **Edit details**:
   - **Email:** healthsupportstudio@gmail.com
   - **Website:** your YouTube channel link

## Part 2: Create the Instagram account (5 min, on your phone)
1. In the Instagram app, go to **Add account** and **Create new account**.
2. **Email:** healthsupportstudio@gmail.com. **Username:** `healthsupportstudio`, or `healthsupport.studio` if that's taken.
3. **Name:** `Health Support Studio`. **Profile picture:** `logo.png`.
4. **Bio** (up to 150 characters):
   ```
   🩺 Health & medical topics, made simple
   🎬 New health video every day
   ⚠️ Educational only, not medical advice
   ```
5. **Link:** your YouTube channel.
6. **Switch to a professional account:** go to **Settings → Account type and tools → Switch to professional account**, then choose **Creator** (or Business) and the category **Health/Beauty** or **Education**.
7. **Connect it to the Facebook Page:** go to **Settings → Accounts Center → Accounts → Add accounts** and add your Facebook profile. Then, on the Facebook Page, open **Settings → Linked accounts → Instagram → Connect**.

Automatic posting only works with an Instagram **professional** account that's **linked to the Facebook Page**.

## Part 3: Allow automatic posting (15 min, on the laptop)
### A. Create a Meta developer app
1. Go to **developers.facebook.com** and log in with the same Facebook account. Click **Get started** and verify your account if asked.
2. Go to **My Apps → Create app**.
   - **App name:** `Health Support Studio Poster`
   - **Contact email:** healthsupportstudio@gmail.com
   - **Use cases:** choose **"Manage everything on your Page"**, and also **"Manage messaging & content on Instagram"** (sometimes called "Instagram API with Facebook login").
   - **Business portfolio:** skip, or pick "I don't want to connect a business portfolio yet".
3. Open **App settings → Basic** and note the **App ID** and **App secret** privately.

The app can stay in **Development mode**. As the app's admin, you can post to your own Page and Instagram without Meta's app review.

### B. Get a Page access token that doesn't expire
1. Open **developers.facebook.com/tools/explorer**.
2. **Meta App:** choose `Health Support Studio Poster`. **User or Page:** **User Token**.
3. Under **Permissions**, add:
   `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`, `business_management`
4. Click **Generate Access Token**, log in, and allow access to **Health Support Studio** (the Page and the Instagram account).
5. Copy the token. It's short-lived for now.
6. Make it long-lived. Paste this into your browser address bar, replacing the three CAPITAL words:
   ```
   https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN
   ```
   Copy the `access_token` value from the page. This is the **long user token**.
7. Get the **Page token**, which never expires:
   ```
   https://graph.facebook.com/me/accounts?access_token=LONG_USER_TOKEN
   ```
   Under your Health Support Studio page, copy:
   - `id` → this is the **Page ID**
   - `access_token` → this is the **Page token**
8. Get the **Instagram ID**:
   ```
   https://graph.facebook.com/PAGE_ID?fields=instagram_business_account&access_token=PAGE_TOKEN
   ```
   Copy the `id` inside `instagram_business_account`. This is the **Instagram user ID**.
9. Optional check: paste the Page token into **developers.facebook.com/tools/debug/accesstoken**. It should say **Expires: Never**.

### C. Add 3 secrets in GitHub
Go to **Settings → Secrets and variables → Actions → New repository secret**:

| Name | Value |
|---|---|
| `META_PAGE_ID` | Page ID (step B7) |
| `META_PAGE_TOKEN` | Page token (step B7) |
| `IG_USER_ID` | Instagram user ID (step B8) |

⚠️ Never paste these tokens in a chat or anywhere public. Anyone with the Page token can post to your Page.

### D. Test
In the GitHub repo, go to **Actions → Post Short to Instagram and Facebook → Run workflow**. It posts the latest Short, but only if its YouTube video is already public.

---

## How it works each day
| Time (Saudi) | What happens |
|---|---|
| ~6 AM | Video + Short are made; the YouTube video is scheduled |
| 7 PM | YouTube video goes public (8 PM in winter) |
| ~8:25 PM | The Short is posted as a Reel on Instagram and Facebook, if the YouTube video is public |

If you set the YouTube video to Private, or delete it, the Short is skipped automatically.
