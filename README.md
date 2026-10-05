# AP Police — Statewide Pending Warrants Monitoring & Execution System

DGP Desk No. 85 · Single-file app (`index.html`) · Free to host on **GitHub Pages** + **Firebase Firestore** (free Spark tier), with an automatic **Demo Mode** fallback to `localStorage` if no Firebase project is configured.

## What's in this repo

- `index.html` — the entire application (Tailwind CSS, Lucide icons, Chart.js, Firebase Firestore compat SDK). Single file, no build step.
- `warrants_data.json` — the full seed dataset: **6,435 real warrant records**, converted directly from `Out of State Warrants_CCTNS.xlsx` (every row in that export, not a sample), matching the CCTNS Uniform Proforma schema. Used by the in-app "Seed Database" button and auto-seed-if-empty on first load.
- `Out of State Warrants_CCTNS.xlsx` — the original source export this seed data was derived from.
- `exceltojsonconvertor.py` — the real conversion script (`python3 exceltojsonconvertor.py "Out of State Warrants_CCTNS.xlsx" warrants_data.json`) used to produce `warrants_data.json`. Re-run it whenever the source Excel is refreshed with new or updated records — it handles the DD/MM/YYYY date formats, strips the stray quote characters Excel adds to numeric-looking IDs, and recomputes ageing from each warrant's actual date.
- `.github/workflows/deploy-pages.yml` — GitHub Actions workflow that deploys this repo to GitHub Pages on every push to `main`.

## One-time setup: enable GitHub Pages

The workflow above deploys automatically, but GitHub requires one manual, one-time toggle per repo before it will accept that deployment:

1. On GitHub, open **Settings → Pages** for this repository.
2. Under **Build and deployment → Source**, choose **GitHub Actions** (not "Deploy from a branch").
3. Push to `main` (or re-run the workflow from the **Actions** tab) — the site will publish to `https://<your-username>.github.io/ap-warrants-dashboard/`.

## Going live on Firebase (optional — Demo Mode works without this)

By default `index.html` runs in **Demo Mode**: all data lives in the browser's `localStorage`, which is enough to try out every feature but is per-browser/per-device, not shared across officers.

To make it a real shared, live database:

1. Create a free Firebase project at https://console.firebase.google.com (Spark/free tier is enough).
2. Enable **Firestore Database** (production mode is fine — see security notes below).
3. In Firebase Console → Project Settings → General → "Your apps", register a Web App and copy its config object.
4. Paste those values into the `firebaseConfig` object near the top of the `<script>` block in `index.html` (search for `YOUR_API_KEY`).
5. Commit and push — `DEMO_MODE` auto-detects a real config and switches to Firestore automatically.

### Security notes

Login in this app is a **client-side access gate** (per-unit PINs defined in `UNIT_PINS` in `index.html`) — good for day-to-day accidental-cross-unit-edit prevention and for driving the audit trail, but it is not server-enforced: anyone who can view the page source can see the PIN list, and Firestore itself has no rules keyed to login yet. Before using this with real, sensitive warrant data:

- **Change every PIN** in `UNIT_PINS` and `HQ_ADMIN_PIN`.
- Add **Firebase Authentication** (email/password or phone OTP per officer).
- Write **Firestore Security Rules** that check a custom claim (e.g. `request.auth.token.unit`) against `resource.data.policeUnit`, so access is enforced by the server, not just the UI.

## Data model

All 66 fields of the DGP Desk No. 85 Uniform Proforma are defined in the `FIELDS` array in `index.html`, in proforma order, and are included in CSV exports. Editable "field unit update" fields are grouped by section in the Update modal (Address Verification, NATGRID/CCTNS checks, Location & Execution Planning, Team Deployment, Court Compliance, Next Action). Every save automatically stamps `lastUpdatedByUnit`, `lastUpdatedByOfficer`, and `lastUpdatedAt` for the audit trail.

Several verification/tracing fields (Address Verification Status, Priority, Inter-State Team Required, NATGRID Verification Required/Status, Report Filed Before Court) come through **blank** from the real CCTNS export — those are exactly the fields field units are expected to fill in via the Update modal, not facts CCTNS already records. The KPI cards that depend on them will read 0 until officers start updating records; that's expected, not a bug.

Execution Status uses the department's own real wording as found in the export — `NBWs yet to Entrust`, `NBWs Execution Pending`, `NBWs Return to court`, `NBWs Recalled`, `NBWs Executed` — rather than a generic Pending/In Progress/Executed scheme.

Police Unit values match the **current (post-2022 reorganization)** CCTNS unit list actually present in the data (e.g. `NTR Commissionerate`, `YSR Kadapa`, `Tirupathi`, `Dr. B R Ambedkar Konaseema`, `Alluri Sitharama Raju`, two GRP (railway) units, etc.) — 30 units in total, each with its own login PIN in `UNIT_PINS`, plus `IGP Technical Services HQ` for statewide oversight.

## Using the app

- **Dashboard** — 10 KPI cards matching the official Excel "State Dashboard" proforma (Total Warrants, Inter-State Team Required, Executed, Pending/In Progress, Address Not Traceable, NATGRID Requested/Pending, >3/>5/>10 Years, Court Report Filed), plus state-wise distribution, ageing-bucket, and execution-funnel charts.
- **Warrant Master Data** — searchable, filterable, paginated (25/page) register. Field units see only their own unit's warrants; **IGP Technical Services HQ** (or the "State HQ Admin" login role) sees and can seed the full statewide dataset.
- **State Deployment & Clustering** — inter-state warrants auto-grouped by destination State/UT, to help stand up dedicated execution teams.
- **Export CSV** — exports the currently filtered rows in the full proforma column order, plus the audit-trail columns.
- **Add Warrant** — any signed-in unit can log a warrant that isn't in the CCTNS export yet (e.g. a case the unit knows about before CCTNS has issued a record for it). Field units can only add for their own unit; the police-unit field is auto-filled and locked. A warrant added this way gets a short stand-in ID (e.g. `NEW-CHIT-7K2PQ1`) instead of a CCTNS ID until one is filled in, and is marked with a blue "New" badge in the Sl. No. column until then.

## Authentication & server-enforced access (recommended before real deployment)

Login in this app has two modes:

- **Demo Mode** (no real Firebase configured, or Firebase not yet set up): a client-side PIN check against `UNIT_PINS` in `index.html`. Fine for trying the app out, but anyone viewing the page source can see the PIN list, and nothing stops a determined user from bypassing the UI check in their browser.
- **Live Mode** (a real `firebaseConfig` is set): real **Firebase Authentication** (email/password), with a **custom claim** (`unit` or `role: "hq_admin"`) set per account. Firestore Security Rules then check that claim server-side on every read/write — this is enforced by Firebase itself, not just by this page's JavaScript.

### One-time setup for Live Mode

1. **Enable Email/Password sign-in.** Firebase Console → **Build → Authentication → Sign-in method → Email/Password → Enable**.
2. **Download a service account key** (admin credential — keep this off GitHub and off chat, it grants full admin access to your Firebase project): Console → **Project Settings → Service Accounts → Generate new private key**. Save it locally, e.g. as `service-account.json` (already covered by `.gitignore`).
3. **Provision one account per unit**, each with the right custom claim:
   ```
   npm install firebase-admin
   node scripts/create_officer_accounts.js ./service-account.json
   ```
   This creates (or, on re-run, just refreshes the claims on) one Firebase Auth account per Police Unit plus one for `IGP Technical Services HQ`, each with a freshly generated 16-character password, and prints a table of unit → login email → password **once**. Save that output somewhere safe (a password manager — not this repo) and distribute each unit's credential to that unit's officers through your normal secure channel.
   - Re-run anytime to add units or refresh claims; existing passwords are left alone unless you pass `--reset-passwords`.
   - **To reset just one unit's password** (e.g. an SP forgot it) without touching anyone else's: `node scripts/create_officer_accounts.js ./service-account.json --unit="Chittoor" --reset-passwords` (use `--unit="HQ"` for the State HQ Admin account). Drop `--reset-passwords` and the same `--unit=` command creates that one login if it doesn't exist yet, without affecting any other unit.
4. **Replace the Firestore rules** (Console → Firestore Database → Rules) with:
   ```
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /warrants/{warrantId} {
         allow read: if request.auth != null &&
           (request.auth.token.role == 'hq_admin' || request.auth.token.unit == resource.data.policeUnit);
         allow create: if request.auth != null &&
           (request.auth.token.role == 'hq_admin' || request.auth.token.unit == request.resource.data.policeUnit);
         allow update: if request.auth != null &&
           (request.auth.token.role == 'hq_admin' || request.auth.token.unit == resource.data.policeUnit);
         allow delete: if request.auth != null && request.auth.token.role == 'hq_admin';
       }
     }
   }
   ```
   This is what actually closes the gap: a field officer's requests are rejected by Firestore itself if `request.auth.token.unit` doesn't match the record's `policeUnit`, regardless of what the browser UI does or doesn't show. The `create` rule uses `request.resource.data.policeUnit` (the document *being written*) rather than `resource.data` (which doesn't exist yet on a brand-new document) -- this is what lets a field unit use "Add Warrant" in the app to log a new warrant for its own jurisdiction, while still blocking it from creating one tagged to a different unit.

   **If you already pasted the original version of these rules in before this update**, go back to Console → Firestore Database → Rules and replace the `allow create` line with the one above -- otherwise "Add Warrant" will fail with a permission-denied error for every field-unit login (HQ Admin is unaffected either way, since its rule never depended on `policeUnit`).
5. **Log in** on the login screen as usual — pick your unit, enter your officer name, and use the password from step 3 instead of a PIN. `index.html` auto-detects Live Mode from `firebaseConfig.apiKey` and switches the login flow (and the password-field label) accordingly; no further code changes are needed.

Once Live Mode + real rules are in place, the "this is a client-side gate only" caveat in the rest of this README no longer applies.

### Changing a unit's password

The 16-character generated passwords from `create_officer_accounts.js` are secure but not meant to be memorized day-to-day. Once signed in, click **Change Password** in the header to set a memorable one for your unit (at least 8 characters, with an uppercase letter, a lowercase letter, a number, and a symbol — a passphrase like `Chittoor@Warrants2026` is fine). This changes the real Firebase Auth password for that unit's shared account; re-share the new password with your unit's officers the same way you shared the original one. "Username" (the login email, e.g. `chittoor@ap-warrants.local`) is fixed per unit by design, since that's what Firestore's rules match against — only the password is changeable.

If a unit ever forgets its password entirely, re-run the provisioning script with `--reset-passwords` to generate (and print) a fresh one for every unit.
