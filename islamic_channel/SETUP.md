# Hidaya (Islamic channel): connect YouTube (one time, about 10 minutes, browser only)

This is the same as Restore Remake Studio's Step 1: reuse the Google Cloud app you made for Health Support
Studio and only make a **new login** for the Islamic channel.

1. Make sure the Health Support Studio Google Cloud app is **In production** (Google Cloud Console →
   **Google Auth Platform → Audience**). If it still says *Testing*, add the Islamic channel's Google
   account as a **test user** there.
2. Open **developers.google.com/oauthplayground**.
3. Click the ⚙️ gear (top right) → tick **Use your own OAuth credentials** → paste the **same** Client ID and
   Client secret you used for Health Support Studio → close.
4. In "Input your own scopes" paste:
   `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.force-ssl`
   and click **Authorize APIs**.
5. Sign in with the Google account that owns **Hidaya** and **pick the Hidaya channel** (not Health
   Support Studio or The Anatomy Unfolded). On "Google hasn't verified this app" click
   **Advanced → Go to …**, then allow.
6. Click **Exchange authorization code for tokens** and copy the **Refresh token**.
7. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**:
   - Name: `ISL_YOUTUBE_REFRESH_TOKEN`, Value: the refresh token.
8. Verify the channel's phone number at **youtube.com/verify** (needed for custom thumbnails).
9. **Required:** copy the channel ID (YouTube Studio → **Settings → Channel → Advanced settings**, starts
   with `UC`) into `islamic_channel/config.json` as `channel_id`. Then nothing is ever uploaded to the
   wrong channel.

⚠️ Never paste the refresh token in a chat or anywhere public. Only in the GitHub secret.

## How uploads work
- Claude edits your clips into a finished video and puts it in `islamic_channel/upload_queue/<name>/`.
- The **Islamic channel - upload videos** workflow uploads it automatically, **scheduled** for the next
  5 PM India time that is at least 2 hours away, in the playlist "Ali aur Dadu".
- Check it in the **YouTube Studio app** before then. If something is wrong, set it to **Private**.
- Videos are marked **Made for kids** (cartoons for children must be, by YouTube's rules) and
  **Altered or synthetic content** (AI-made).
