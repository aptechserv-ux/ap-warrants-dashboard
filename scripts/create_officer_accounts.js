#!/usr/bin/env node
/**
 * create_officer_accounts.js
 * --------------------------------------------------------------------
 * One-time (or re-run-anytime) provisioning script: creates one Firebase
 * Authentication account per Police Unit (plus one State HQ Admin
 * account), and sets a custom claim on each so Firestore Security Rules
 * can enforce unit-level access server-side -- not just in the browser.
 *
 * This script needs Admin SDK privileges, so it must be run locally by
 * you, never pasted into chat or committed: it reads a Firebase service
 * account key you download yourself.
 *
 * Setup:
 *   npm install firebase-admin
 *   (written against firebase-admin's modular API, v12+ / v14 confirmed)
 *
 * Get a service account key:
 *   Firebase Console -> Project Settings -> Service Accounts
 *   -> "Generate new private key" -> save as service-account.json
 *   (keep this file OUT of git -- it's already covered by .gitignore)
 *
 * Run:
 *   node scripts/create_officer_accounts.js ./service-account.json
 *
 * The script prints each account's login email and a freshly generated
 * password ONCE. Save that output somewhere safe (a password manager,
 * not this repo) and distribute each unit's credential to that unit's
 * officers through your normal secure channel -- it is never written to
 * disk or to Firestore.
 *
 * Re-running is safe: existing accounts are left alone (claims are
 * refreshed, password is NOT reset) unless you pass --reset-passwords.
 * --------------------------------------------------------------------
 */
const crypto = require("crypto");
const path = require("path");
const { initializeApp, cert } = require("firebase-admin/app");
const { getAuth } = require("firebase-admin/auth");

const POLICE_UNITS = [
  "Chittoor","Tirupathi","YSR Kadapa","NTR Commissionerate","Annamayya","GRP Vijayawada",
  "Eluru","Sri Potti Sriramulu Nellore","Anakapalli","Kakinada","East Godavari","West Godavari",
  "Vizianagaram","Srikakulam","Kurnool","Polavaram","Alluri Sitharama Raju","Sri Sathya Sai",
  "Ananthapuram","Visakhapatnam Commissionerate","Palnadu","Prakasam","Dr. B R Ambedkar Konaseema",
  "Nandyal","Bapatla","Parvathipuram Manyam","GRP Guntakal","Guntur","Markapuram","Krishna"
];
const HQ_UNIT_NAME = "IGP Technical Services HQ";

function slugUnit(u) {
  return String(u).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}
function emailFor(unit) {
  return unit === HQ_UNIT_NAME ? "hq-admin@ap-warrants.local" : `${slugUnit(unit)}@ap-warrants.local`;
}
function genPassword() {
  // 16-char password from a URL-safe alphabet -- meets Firebase's 6-char
  // minimum many times over.
  return crypto.randomBytes(12).toString("base64").replace(/[+/=]/g, "x");
}

async function main() {
  const keyPath = process.argv[2];
  const resetPasswords = process.argv.includes("--reset-passwords");
  if (!keyPath) {
    console.error("Usage: node scripts/create_officer_accounts.js <service-account.json> [--reset-passwords]");
    process.exit(1);
  }

  initializeApp({ credential: cert(require(path.resolve(keyPath))) });
  const auth = getAuth();

  const accounts = [
    { unit: HQ_UNIT_NAME, role: "hq_admin" },
    ...POLICE_UNITS.map((unit) => ({ unit, role: "field" })),
  ];

  const results = [];

  for (const { unit, role } of accounts) {
    const email = emailFor(unit);
    let user;
    let password = null;
    try {
      user = await auth.getUserByEmail(email);
      if (resetPasswords) {
        password = genPassword();
        await auth.updateUser(user.uid, { password });
      }
    } catch (e) {
      if (e.code !== "auth/user-not-found") throw e;
      password = genPassword();
      user = await auth.createUser({ email, password, emailVerified: true, disabled: false });
    }

    const claims = role === "hq_admin" ? { role: "hq_admin" } : { role: "field", unit };
    await auth.setCustomUserClaims(user.uid, claims);

    results.push({ unit, email, password, status: password ? "created/reset" : "already existed (claims refreshed)" });
  }

  console.log("\nAccount provisioning complete.\n");
  console.log("Unit".padEnd(32), "Login Email".padEnd(40), "Password".padEnd(18), "Status");
  console.log("-".repeat(110));
  for (const r of results) {
    console.log(
      r.unit.padEnd(32),
      r.email.padEnd(40),
      (r.password || "(unchanged)").padEnd(18),
      r.status
    );
  }
  console.log("\nSave the passwords above somewhere safe now -- they are not shown again and are not stored anywhere by this script.");
  console.log("Distribute each unit's credential to that unit's officers through your normal secure channel.\n");
}

main().catch((e) => {
  console.error("Provisioning failed:", e);
  process.exit(1);
});
