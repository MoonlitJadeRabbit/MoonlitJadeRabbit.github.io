# Junye Zhou — portfolio site

Static portfolio published with **GitHub Pages**.

## Live URL (no `/website/` in the path)

**https://moonlitjaderabbit.github.io/**

That URL works when this repo is named **`MoonlitJadeRabbit.github.io`** (see setup below).

## One-time GitHub setup (required)

### 1. Rename the repository (removes `/website/` from the URL)

1. Open [github.com/MoonlitJadeRabbit/website/settings](https://github.com/MoonlitJadeRabbit/website/settings)
2. Under **Repository name**, change `website` → **`MoonlitJadeRabbit.github.io`**
3. Click **Rename**

Then update your local clone:

```powershell
git -c safe.directory="D:/Junye Website" remote set-url origin https://github.com/MoonlitJadeRabbit/MoonlitJadeRabbit.github.io.git
```

### 2. Turn on GitHub Pages

1. Open **Settings → Pages** on the renamed repo
2. **Build and deployment → Source:** choose **Deploy from a branch**
3. **Branch:** `gh-pages` · **Folder:** `/ (root)` · **Save**
4. Wait 1–3 minutes, then open **https://moonlitjaderabbit.github.io/**

The workflow `.github/workflows/pages.yml` updates the `gh-pages` branch whenever you push to `main`.

### Custom domain (`junyezhou.com`)

In **Settings → Pages**, add your domain, then set DNS at your registrar to the records GitHub shows.

## Local preview

```bash
npx --yes serve .
```

## Deploy updates

```powershell
cd C:\junye-website\website-main
.\scripts\sync-github.ps1 -Action Push -Message "Describe your change"
```

Or with plain git:

```powershell
cd C:\junye-website\website-main
git add -A
git commit -m "Describe your change"
git push
```

## Sync between two computers

GitHub holds the shared copy. **Push** when you finish on one PC; **pull** before you start on the other.

| On this computer… | Run |
|-------------------|-----|
| After editing (send changes to GitHub) | `.\scripts\sync-github.ps1 -Action Push -Message "what you changed"` |
| Before editing (get changes from the other PC) | `.\scripts\sync-github.ps1 -Action Pull` |
| Check if you are ahead/behind | `.\scripts\sync-github.ps1 -Action Status` |

**Cursor auto-pull (optional):** With `.cursor/hooks.json` enabled, Cursor pulls from GitHub before you message the agent. Restart Cursor after pulling hook updates. Commit and push manually (or ask the agent) when you are ready.

### One-time setup on each computer

1. Install [Git for Windows](https://git-scm.com/download/win) (or `winget install Git.Git`).
2. Clone the repo once (pick a folder you will always use):

   ```powershell
   git clone https://github.com/MoonlitJadeRabbit/MoonlitJadeRabbit.github.io.git C:\junye-website\website-main
   ```

3. Set your name and email once (needed for commits):

   ```powershell
   git config --global user.name "Junye Zhou"
   git config --global user.email "junye.zhou@mail.utoronto.ca"
   ```

4. The first time you **push**, sign in to GitHub (browser or personal access token).

Open the **same clone** in Cursor on each computer. Do not maintain two unrelated copies of the folder; always pull/push through GitHub.

### If this PC already has files but no git history yet

On this computer, Git was initialized in `C:\junye-website\website-main`. Link it to GitHub once:

```powershell
cd C:\junye-website\website-main
git pull origin main --allow-unrelated-histories
```

If Git reports conflicts, open the listed files, keep the parts you want, then:

```powershell
git add -A
git commit -m "Merge local work with GitHub"
git push -u origin main
```

After that, use **Push** / **Pull** only.

### Cursor auto-pull hook

Project hooks in `.cursor/hooks/` pull from GitHub when you use the agent:

| When | What runs |
|------|-----------|
| Chat starts / you send a message | **Pull** from `origin` (throttled to once per 60s) |

**Push and commit are always manual:**

```powershell
git add -A
git commit -m "Describe your change"
git push origin main
```

**Safeguards:** fails open (Git errors do not block chat); merge conflicts are logged and left for you to fix.

Logs: `.cursor/hooks/git-sync.log` (not committed). **Restart Cursor** after pulling hook files on a new PC.

> **Note:** The Desktop shortcut `Junye Website` on this PC only links to the local folder here. It does not sync to your other computer by itself; GitHub does.
