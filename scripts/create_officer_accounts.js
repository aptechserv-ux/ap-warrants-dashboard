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
 *
 * To add a login for a unit that doesn't have one yet, or to reset just
 * ONE unit's password without touching anyone else's, pass --unit:
 *   node scripts/create_officer_accounts.js ./service-account.json --unit="Chittoor"
 *   node scripts/create_officer_accounts.js ./service-account.json --unit="Chittoor" --reset-passwords
 *   node scripts/create_officer_accounts.js ./service-account.json --unit="HQ" --reset-passwords
 * (--unit="HQ" targets the State HQ Admin account.) Match is
 * case-insensitive; the script lists valid unit names if it doesn't
 * recognize what you typed.
 *
 * A unit that isn't in the POLICE_UNITS list below (a brand-new unit,
 * not one that already has a login) can't be targeted with --unit until
 * it's added to that list in this file AND to the POLICE_UNITS array in
 * index.html (which drives the login dropdown and jurisdiction scoping)
 * -- ask your developer/this assistant to add it, then re-run.
 *
 * To give a SECOND (or third, etc.) officer in the same unit their own
 * separate login instead of sharing the unit's one password, add
 * --login-id to a --unit command -- this creates an ADDITIONAL account
 * for that unit with the same jurisdiction (same custom claims), under
 * its own password, leaving the unit's original/primary login untouched:
 *   node scripts/create_officer_accounts.js ./service-account.json --unit="Chittoor" --login-id="2"
 * That officer then signs in picking Unit = Chittoor, Login ID = "2",
 * plus the password this prints. Leaving Login ID blank at sign-in (the
 * default for everyone) always means the unit's original account, so
 * nobody who already has credentials is affected by adding more.
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
function emailFor(unit, loginId) {
  const base = unit === HQ_UNIT_NAME ? "hq-admin" : slugUnit(unit);
  const suffix = loginId ? "-" + slugUnit(loginId) : "";
  return `${base}${suffix}@ap-warrants.local`;
}
function genPassword() {
  // 16-char password from a URL-safe alphabet -- meets Firebase's 6-char
  // minimum many times over.
  return crypto.randomBytes(12).toString("base64").replace(/[+/=]/g, "x");
}

async function main() {
  const keyPath = process.argv[2];
  const resetPasswords = process.argv.includes("--reset-passwords");
  const unitArg = process.argv.find((a) => a.startsWith("--unit="));
  const targetUnit = unitArg ? unitArg.slice("--unit=".length).trim() : null;
  const loginIdArg = process.argv.find((a) => a.startsWith("--login-id="));
  const loginId = loginIdArg ? loginIdArg.slice("--login-id=".length).trim() : null;
  if (!keyPath) {
    console.error('Usage: node scripts/create_officer_accounts.js <service-account.json> [--reset-passwords] [--unit="Unit Name"] [--login-id="id"]');
    process.exit(1);
  }
  if (loginId && !targetUnit) {
    console.error('--login-id requires --unit="<Unit Name>" (or --unit="HQ") to say which unit this extra login belongs to.');
    process.exit(1);
  }

  initializeApp({ credential: cert(require(path.resolve(keyPath))) });
  const auth = getAuth();

  let accounts = [
    { unit: HQ_UNIT_NAME, role: "hq_admin" },
    ...POLICE_UNITS.map((unit) => ({ unit, role: "field" })),
  ];

  if (targetUnit) {
    const wanted = targetUnit.toLowerCase();
    const match = accounts.find(
      (a) => a.unit.toLowerCase() === wanted || (wanted === "hq" && a.unit === HQ_UNIT_NAME)
    );
    if (!match) {
      console.error(`No unit matching "${targetUnit}".\nValid values: HQ, ${POLICE_UNITS.join(", ")}`);
      process.exit(1);
    }
    accounts = [match];
  }

  const results = [];

  for (const { unit, role } of accounts) {
    const email = emailFor(unit, loginId);
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

    results.push({
      unit: unit + (loginId ? ` (Login ID: ${loginId})` : ""),
      email, password,
      status: password ? "created/reset" : "already existed (claims refreshed)"
    });
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
