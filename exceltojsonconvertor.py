<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>AP Police — Statewide Pending Warrants Monitoring &amp; Execution System</title>
<meta name="description" content="DGP Desk No. 85 — Statewide Pending Warrants Monitoring and Execution Dashboard" />

<!-- Tailwind CSS -->
<script src="https://cdn.tailwindcss.com"></script>
<!-- Lucide Icons -->
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<!-- Firebase (compat SDK) -->
<script src="https://www.gstatic.com/firebasejs/10.12.5/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.5/firebase-firestore-compat.js"></script>

<script>
  tailwind.config = {
    darkMode: 'class',
    theme: {
      extend: {
        colors: {
          navy: { 950:'#050a14', 900:'#0a1428', 800:'#0f1d38', 700:'#15284a', 600:'#1c3560', 500:'#254478' },
          brass: { 500:'#c9a84c', 400:'#d8bc6e', 300:'#e6d49a' },
        },
        fontFamily: { sans: ['Inter','ui-sans-serif','system-ui','sans-serif'] }
      }
    }
  }
</script>

<style>
  :root{
    --bg:#f3f5f9; --surface:#ffffff; --surface-2:#f8fafc; --border:#e2e8f0;
    --text:#0f172a; --text-dim:#475569; --accent:#1c3560; --accent-2:#c9a84c;
  }
  html[data-theme="dark"]{
    --bg:#070c18; --surface:#0f1a2e; --surface-2:#122039; --border:#1e2d4a;
    --text:#e8edf7; --text-dim:#93a3c2; --accent:#4d79c9; --accent-2:#d8bc6e;
  }
  *{ box-sizing:border-box; }
  body{ background:var(--bg); color:var(--text); transition:background .2s,color .2s; }
  .surface{ background:var(--surface); border:1px solid var(--border); }
  .surface-2{ background:var(--surface-2); border:1px solid var(--border); }
  .text-dim{ color:var(--text-dim); }
  .border-c{ border-color:var(--border); }
  ::-webkit-scrollbar{ width:10px; height:10px; }
  ::-webkit-scrollbar-track{ background:transparent; }
  ::-webkit-scrollbar-thumb{ background:var(--border); border-radius:8px; }
  .tab-btn.active{ background:var(--accent); color:#fff; }
  .tab-btn{ color:var(--text-dim); }
  .badge{ display:inline-flex; align-items:center; gap:4px; padding:2px 10px; border-radius:999px; font-size:11px; font-weight:600; letter-spacing:.02em; }
  .modal-backdrop{ background:rgba(2,6,16,.6); backdrop-filter: blur(2px); }
  table thead th{ position:sticky; top:0; background:var(--surface-2); z-index:10; }
  .chip-row::-webkit-scrollbar{ height:6px; }
  input,select,textarea{ background:var(--surface-2); border:1px solid var(--border); color:var(--text); }
  input:focus,select:focus,textarea:focus{ outline:2px solid var(--accent); outline-offset:1px; }
  .fade-in{ animation: fadeIn .18s ease-out; }
  @keyframes fadeIn{ from{opacity:0; transform:translateY(4px);} to{opacity:1; transform:translateY(0);} }
</style>
</head>
<body class="min-h-screen font-sans text-sm">

<!-- ===================== LOGIN MODAL ===================== -->
<div id="loginModal" class="fixed inset-0 modal-backdrop z-50 flex items-center justify-center p-3">
  <div class="surface rounded-2xl w-full max-w-md p-6 shadow-2xl">
    <div class="text-center mb-6">
      <div class="w-12 h-12 rounded-xl mx-auto flex items-center justify-center mb-3" style="background:var(--accent)">
        <i data-lucide="shield-alert" class="text-white w-7 h-7"></i>
      </div>
      <h2 class="font-bold text-lg">AP Police Warrant Monitoring System</h2>
      <p class="text-dim text-xs mt-1">DGP Desk No. 85 · Secure Unit Authentication</p>
    </div>
    
    <form id="loginForm" class="space-y-4">
      <div>
        <label class="text-xs font-semibold text-dim block mb-1">Select Police Unit / Command</label>
        <select id="loginUnit" required class="w-full px-3 py-2.5 rounded-lg text-sm">
          <option value="">-- Choose Unit / Commissionerate --</option>
          <option value="IGP TECHNICAL SERVICES HQ">IGP Technical Services HQ (State Nodal)</option>
          <option value="Visakhapatnam City">Visakhapatnam City Commissionerate</option>
          <option value="Vijayawada City">Vijayawada City Commissionerate</option>
          <option value="Tirupati Urban">Tirupati Urban District</option>
          <option value="Srikakulam">Srikakulam District</option>
          <option value="Vizianagaram">Vizianagaram District</option>
          <option value="East Godavari">East Godavari District</option>
          <option value="West Godavari">West Godavari District</option>
          <option value="Krishna">Krishna District</option>
          <option value="Guntur Urban">Guntur Urban District</option>
          <option value="Prakasam">Prakasam District</option>
          <option value="Nellore">Nellore District</option>
          <option value="Kadapa">Kadapa District</option>
          <option value="Kurnool">Kurnool District</option>
          <option value="Anantapur">Anantapur District</option>
          <option value="Chittoor">Chittoor District</option>
        </select>
      </div>
      <div>
        <label class="text-xs font-semibold text-dim block mb-1">Officer / Investigator ID &amp; Name</label>
        <input id="loginOfficer" type="text" required placeholder="e.g., CI K. Ramesh (ID: AP-1892)" class="w-full px-3 py-2.5 rounded-lg text-sm" />
      </div>
      <div>
        <label class="text-xs font-semibold text-dim block mb-1">Secure Access PIN</label>
        <input id="loginPin" type="password" required placeholder="Enter unit authorization PIN" class="w-full px-3 py-2.5 rounded-lg text-sm" />
      </div>
      <button type="submit" class="w-full py-2.5 rounded-lg text-white font-semibold flex items-center justify-center gap-2 mt-2" style="background:var(--accent)">
        <i data-lucide="log-in" class="w-4 h-4"></i> Authenticate &amp; Access Dashboard
      </button>
    </form>
  </div>
</div>

<div id="app" class="min-h-screen flex flex-col hidden">

  <!-- ===================== HEADER ===================== -->
  <header class="surface border-b border-c sticky top-0 z-40">
    <div class="max-w-[1600px] mx-auto px-4 py-3 flex flex-wrap items-center gap-3 justify-between">
      <div class="flex items-center gap-3">
        <div class="w-11 h-11 rounded-lg flex items-center justify-center" style="background:var(--accent)">
          <i data-lucide="shield-check" class="text-white w-6 h-6"></i>
        </div>
        <div>
          <h1 class="font-bold text-base sm:text-lg leading-tight">AP Police Statewide Pending Warrants</h1>
          <p class="text-dim text-xs leading-tight">Monitoring &amp; Execution System · DGP Desk No. 85</p>
        </div>
      </div>

      <div class="flex items-center gap-2 flex-wrap">
        <span id="userBadge" class="badge surface-2 font-medium"></span>
        <span id="connStatus" class="badge surface-2"><i data-lucide="circle" class="w-2.5 h-2.5"></i> Connecting…</span>
        <button id="seedBtn" class="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold border border-c surface-2 hover:opacity-80 transition">
          <i data-lucide="database" class="w-4 h-4"></i> Seed DB
        </button>
        <button id="exportBtn" class="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold border border-c surface-2 hover:opacity-80 transition">
          <i data-lucide="file-down" class="w-4 h-4"></i> Export CSV
        </button>
        <button id="themeBtn" class="w-9 h-9 flex items-center justify-center rounded-lg border border-c surface-2 hover:opacity-80 transition">
          <i data-lucide="moon" class="w-4 h-4"></i>
        </button>
        <button id="logoutBtn" title="Switch Unit / Logout" class="w-9 h-9 flex items-center justify-center rounded-lg border border-c surface-2 hover:opacity-80 transition text-rose-500">
          <i data-lucide="log-out" class="w-4 h-4"></i>
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <nav class="max-w-[1600px] mx-auto px-4 flex gap-1 overflow-x-auto chip-row">
      <button data-tab="dashboard" class="tab-btn active px-4 py-2.5 rounded-t-lg text-sm font-semibold whitespace-nowrap transition">
        <i data-lucide="layout-dashboard" class="w-4 h-4 inline -mt-0.5 mr-1"></i>Executive Dashboard
      </button>
      <button data-tab="master" class="tab-btn px-4 py-2.5 rounded-t-lg text-sm font-semibold whitespace-nowrap transition">
        <i data-lucide="table" class="w-4 h-4 inline -mt-0.5 mr-1"></i>Warrant Master Data
      </button>
      <button data-tab="deployment" class="tab-btn px-4 py-2.5 rounded-t-lg text-sm font-semibold whitespace-nowrap transition">
        <i data-lucide="map" class="w-4 h-4 inline -mt-0.5 mr-1"></i>State Deployment &amp; Clustering
      </button>
    </nav>
  </header>

  <!-- ===================== MAIN ===================== -->
  <main class="max-w-[1600px] w-full mx-auto px-4 py-5 flex-1">

    <!-- ---------- DASHBOARD TAB ---------- -->
    <section id="view-dashboard" class="fade-in">
      <div id="kpiGrid" class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3 mb-5"></div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-5">
        <div class="surface rounded-xl p-4 lg:col-span-1">
          <h3 class="font-semibold mb-3 flex items-center gap-2"><i data-lucide="bar-chart-3" class="w-4 h-4"></i>State-wise Distribution</h3>
          <canvas id="stateChart" height="220"></canvas>
        </div>
        <div class="surface rounded-xl p-4 lg:col-span-1">
          <h3 class="font-semibold mb-3 flex items-center gap-2"><i data-lucide="hourglass" class="w-4 h-4"></i>Ageing Buckets</h3>
          <canvas id="ageingChart" height="220"></canvas>
        </div>
        <div class="surface rounded-xl p-4 lg:col-span-1">
          <h3 class="font-semibold mb-3 flex items-center gap-2"><i data-lucide="filter" class="w-4 h-4"></i>Execution Funnel</h3>
          <canvas id="funnelChart" height="220"></canvas>
        </div>
      </div>

      <div class="surface rounded-xl p-4">
        <h3 class="font-semibold mb-3 flex items-center gap-2"><i data-lucide="alert-triangle" class="w-4 h-4 text-amber-500"></i>Priority Attention — Critical &amp; High Ageing Warrants</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-xs" id="priorityTable">
            <thead><tr class="text-left text-dim">
              <th class="py-2 pr-3">Sl.No</th><th class="py-2 pr-3">Name</th><th class="py-2 pr-3">Unit</th>
              <th class="py-2 pr-3">Probable State</th><th class="py-2 pr-3">Ageing</th><th class="py-2 pr-3">Priority</th>
              <th class="py-2 pr-3">Execution Status</th>
            </tr></thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ---------- MASTER DATA TAB ---------- -->
    <section id="view-master" class="hidden fade-in">
      <div class="surface rounded-xl p-3 mb-3 flex flex-wrap gap-2 items-center">
        <div class="relative flex-1 min-w-[220px]">
          <i data-lucide="search" class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-dim"></i>
          <input id="searchInput" type="text" placeholder="Search by name, CCTNS ID, crime no, unit…" class="w-full pl-9 pr-3 py-2 rounded-lg text-sm" />
        </div>
        <select id="filterUnit" class="px-2 py-2 rounded-lg text-sm"><option value="">All Police Units</option></select>
        <select id="filterState" class="px-2 py-2 rounded-lg text-sm"><option value="">All Probable States</option></select>
        <select id="filterAddrStatus" class="px-2 py-2 rounded-lg text-sm"><option value="">All Address Status</option></select>
        <select id="filterExecStatus" class="px-2 py-2 rounded-lg text-sm"><option value="">All Execution Status</option></select>
        <select id="filterPriority" class="px-2 py-2 rounded-lg text-sm"><option value="">All Priority</option></select>
        <select id="filterAgeing" class="px-2 py-2 rounded-lg text-sm"><option value="">All Ageing</option></select>
        <button id="clearFilters" class="px-3 py-2 rounded-lg text-xs font-semibold border border-c surface-2 hover:opacity-80">Clear</button>
      </div>

      <div class="surface rounded-xl overflow-hidden">
        <div class="overflow-x-auto max-h-[65vh]">
          <table class="w-full text-xs whitespace-nowrap" id="masterTable">
            <thead><tr class="text-left text-dim border-b border-c">
              <th class="py-2.5 px-3">Sl.No</th>
              <th class="py-2.5 px-3">Police Unit</th>
              <th class="py-2.5 px-3">Police Station</th>
              <th class="py-2.5 px-3">Crime No/Year</th>
              <th class="py-2.5 px-3">Accused Name</th>
              <th class="py-2.5 px-3">Probable State/UT</th>
              <th class="py-2.5 px-3">Address Verification</th>
              <th class="py-2.5 px-3">Ageing</th>
              <th class="py-2.5 px-3">Execution Status</th>
              <th class="py-2.5 px-3">Last Modified By</th>
              <th class="py-2.5 px-3">Action</th>
            </tr></thead>
            <tbody id="masterTbody"></tbody>
          </table>
        </div>
        <div class="flex items-center justify-between px-3 py-2.5 border-t border-c text-xs text-dim">
          <span id="rowCountLabel">0 records</span>
          <div class="flex items-center gap-2">
            <button id="prevPage" class="px-2 py-1 rounded border border-c surface-2">Prev</button>
            <span id="pageLabel">Page 1</span>
            <button id="nextPage" class="px-2 py-1 rounded border border-c surface-2">Next</button>
          </div>
        </div>
      </div>
    </section>

    <!-- ---------- STATE DEPLOYMENT TAB ---------- -->
    <section id="view-deployment" class="hidden fade-in">
      <div class="surface rounded-xl p-4 mb-4">
        <h3 class="font-semibold mb-1 flex items-center gap-2"><i data-lucide="users" class="w-4 h-4"></i>Inter-State Execution Team Clusters</h3>
        <p class="text-dim text-xs">Warrants are grouped automatically by <strong>Current Probable State / UT</strong> to assist forming dedicated inter-state execution teams.</p>
      </div>
      <div id="clusterGrid" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4"></div>
    </section>

  </main>

  <footer class="text-center text-dim text-xs py-4 border-t border-c">
    AP Police Statewide Pending Warrants System · DGP Desk No. 85 · Built for internal law-enforcement use
  </footer>
</div>

<!-- ===================== EDIT MODAL ===================== -->
<div id="editModal" class="fixed inset-0 modal-backdrop hidden z-50 flex items-center justify-center p-3">
  <div class="surface rounded-xl w-full max-w-4xl max-h-[92vh] overflow-y-auto">
    <div class="flex items-center justify-between px-5 py-4 border-b border-c sticky top-0 surface z-10">
      <div>
        <h3 class="font-bold text-base" id="modalTitle">Update Warrant Record</h3>
        <p class="text-dim text-xs" id="modalSubtitle"></p>
      </div>
      <button id="closeModal" class="w-8 h-8 rounded-lg surface-2 border border-c flex items-center justify-center"><i data-lucide="x" class="w-4 h-4"></i></button>
    </div>

    <div class="p-5">
      <div class="surface-2 rounded-lg p-4 mb-5 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs" id="modalSnapshot"></div>

      <form id="editForm" class="space-y-6">
        <div>
          <h4 class="font-semibold text-sm mb-3 flex items-center gap-2 text-amber-500"><i data-lucide="map-pin" class="w-4 h-4"></i>Address Verification &amp; Tracing</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" id="grp-address"></div>
        </div>
        <div>
          <h4 class="font-semibold text-sm mb-3 flex items-center gap-2 text-blue-500"><i data-lucide="satellite-dish" class="w-4 h-4"></i>Technology &amp; Database Checks (NATGRID / CCTNS)</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" id="grp-tech"></div>
        </div>
        <div>
          <h4 class="font-semibold text-sm mb-3 flex items-center gap-2 text-purple-500"><i data-lucide="crosshair" class="w-4 h-4"></i>Current Location &amp; Execution Planning</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" id="grp-location"></div>
        </div>
        <div>
          <h4 class="font-semibold text-sm mb-3 flex items-center gap-2 text-emerald-500"><i data-lucide="users-round" class="w-4 h-4"></i>Team Deployment &amp; Execution Status</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" id="grp-exec"></div>
        </div>
        <div>
          <h4 class="font-semibold text-sm mb-3 flex items-center gap-2 text-rose-500"><i data-lucide="gavel" class="w-4 h-4"></i>Court Compliance Log</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" id="grp-court"></div>
        </div>
        <div>
          <h4 class="font-semibold text-sm mb-3 flex items-center gap-2"><i data-lucide="clipboard-list" class="w-4 h-4"></i>Next Action &amp; Accountability</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" id="grp-action"></div>
        </div>
        <div>
          <label class="text-xs font-semibold text-dim">Remarks</label>
          <textarea id="f_remarks" rows="2" class="w-full mt-1 px-3 py-2 rounded-lg text-sm"></textarea>
        </div>
      </form>
    </div>

    <div class="flex items-center justify-end gap-2 px-5 py-4 border-t border-c sticky bottom-0 surface">
      <button id="cancelEdit" class="px-4 py-2 rounded-lg text-sm font-semibold border border-c surface-2">Cancel</button>
      <button id="saveEdit" class="px-4 py-2 rounded-lg text-sm font-semibold text-white flex items-center gap-2" style="background:var(--accent)">
        <i data-lucide="save" class="w-4 h-4"></i> Save to Database
      </button>
    </div>
  </div>
</div>

<!-- Toast -->
<div id="toast" class="fixed bottom-5 right-5 z-[60] hidden"></div>

<script>
/* =====================================================================
   AP POLICE STATEWIDE PENDING WARRANTS SYSTEM — DGP DESK NO. 85
   ===================================================================== */
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

const COLLECTION_NAME = "warrants";
const DEMO_MODE = !firebaseConfig.apiKey || firebaseConfig.apiKey === "YOUR_API_KEY";

let db = null;
if (!DEMO_MODE) {
  try {
    firebase.initializeApp(firebaseConfig);
    db = firebase.firestore();
  } catch (e) {
    console.error("Firebase init failed, falling back to demo mode.", e);
  }
}

// Current logged-in session state
let CURRENT_USER = null;

function checkLoginSession(){
  const saved = localStorage.getItem("ap_police_warrant_user");
  if (saved) {
    try {
      CURRENT_USER = JSON.parse(saved);
      document.getElementById("loginModal").classList.add("hidden");
      document.getElementById("app").classList.remove("hidden");
      document.getElementById("userBadge").innerHTML = `<i data-lucide="user-check" class="w-3 h-3"></i> ${escapeHtml(CURRENT_USER.unit)} (${escapeHtml(CURRENT_USER.officer)})`;
      lucide.createIcons();
      bootApp();
      return;
    } catch(e){}
  }
  document.getElementById("loginModal").classList.remove("hidden");
  document.getElementById("app").classList.add("hidden");
}

document.getElementById("loginForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const unit = document.getElementById("loginUnit").value;
  const officer = document.getElementById("loginOfficer").value.trim();
  const pin = document.getElementById("loginPin").value.trim();

  if (!unit || !officer || !pin) return;
  
  CURRENT_USER = { unit, officer, loggedInAt: new Date().toISOString() };
  localStorage.setItem("ap_police_warrant_user", JSON.stringify(CURRENT_USER));
  
  document.getElementById("loginModal").classList.add("hidden");
  document.getElementById("app").classList.remove("hidden");
  document.getElementById("userBadge").innerHTML = `<i data-lucide="user-check" class="w-3 h-3"></i> ${escapeHtml(CURRENT_USER.unit)} (${escapeHtml(CURRENT_USER.officer)})`;
  lucide.createIcons();
  bootApp();
});

document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("ap_police_warrant_user");
  location.reload();
});

const FIELDS = [
  ["slNo","Sl. No."],["range","Range"],["policeUnit","Police Unit"],["policeStation","Police Station"],
  ["crimeNoYear","Crime No. / Year"],["cctnsId","CCTNS ID"],["court","Court"],["courtCaseNo","Court Case No."],
  ["warrantType","Warrant Type"],["warrantNo","Warrant No."],["warrantDate","Warrant Date"],
  ["sectionsOfLaw","Sections of Law"],["categoryOfCase","Category of Case"],["nameOfPerson","Name of Person"],
  ["alias","Alias"],["fatherSpouseName","Father / Spouse Name"],["dobAge","DOB / Age"],["gender","Gender"],
  ["mobileNo","Mobile No."],["photographAvailable","Photograph Available"],["idParticularsAvailable","ID Particulars Available"],
  ["originalAddress","Original Address"],["addressStateUT","Address State / UT"],["addressDistrict","Address District"],
  ["addressPS","Address PS"],["latestKnownAddress","Latest Known Address"],["addressVerificationStatus","Address Verification Status"],
  ["dateLastVerified","Date Last Verified"],["cctnsSearchConducted","CCTNS Search Conducted"],["cctnsSearchDate","CCTNS Search Date"],
  ["natgridVerificationRequired","NATGRID Verification Required"],["natgridVerificationStatus","NATGRID Verification Status"],
  ["otherDatabaseChecks","Other Database Checks"],["interStatePoliceVerification","Inter-State Police Verification"],
  ["currentProbableStateUT","Current Probable State / UT"],["currentProbableDistrict","Current Probable District"],
  ["currentProbablePS","Current Probable PS"],["locationConfidence","Location Confidence"],
  ["previousExecutionAttempts","Previous Execution Attempts"],["lastAttemptDate","Last Attempt Date"],
  ["resultOfLastAttempt","Result of Last Attempt"],["reasonsForNonExecution","Reasons for Non-Execution"],
  ["warrantPendingSince","Warrant Pending Since"],["ageingDays","Ageing (Days)"],["ageingBucket","Ageing Bucket"],
  ["priority","Priority"],["interStateTeamRequired","Inter-State Team Required"],["proposedStateCluster","Proposed State Cluster"],
  ["proposedDistrictCluster","Proposed District Cluster"],["localPoliceCoordination","Local Police Coordination"],
  ["teamAssigned","Team Assigned"],["dateTeamDeployed","Date Team Deployed"],["executionStatus","Execution Status"],
  ["dateOfExecution","Date of Execution"],["productionTransitStatus","Production / Transit Status"],
  ["courtIntimated","Court Intimated"],["dateCourtIntimated","Date Court Intimated"],
  ["untraceableEffortsRecorded","Untraceable - Efforts Recorded"],["reportFiledBeforeCourt","Report Filed Before Court"],
  ["reportDate","Report Date"],["nextAction","Next Action"],["targetDate","Target Date"],
  ["responsibleOfficer","Responsible Officer"],["shoVerification","SHO Verification"],
  ["unitNodalOfficerVerification","Unit Nodal Officer Verification"],["remarks","Remarks"]
];

const OPTS = {
  addressVerificationStatus: ["Verified - Correct & Traceable","Incomplete","Incorrect","False","Shifted","Obsolete","Not Verified"],
  natgridVerificationRequired: ["Yes","No"],
  natgridVerificationStatus: ["Not Required","Pending","Verified - Match Found","Verified - No Match","N/A"],
  interStatePoliceVerification: ["Yes","No","N/A"],
  locationConfidence: ["High","Medium","Low","Unknown"],
  priority: ["Critical","High","Normal"],
  interStateTeamRequired: ["Yes","No"],
  localPoliceCoordination: ["Requested","Confirmed","Not Initiated","N/A"],
  executionStatus: ["Pending","In Progress","Team Deployed","Executed","Untraceable","Returned Unexecuted","Stayed / Withdrawn"],
  productionTransitStatus: ["N/A","Produced Before Court","In Transit","Remanded"],
  courtIntimated: ["Yes","No"],
  untraceableEffortsRecorded: ["Yes","No"],
  reportFiledBeforeCourt: ["Yes","No"],
  shoVerification: ["Yes","No"],
  unitNodalOfficerVerification: ["Yes","No"],
  cctnsSearchConducted: ["Yes","No"]
};

const EDIT_GROUPS = {
  address: ["addressVerificationStatus","dateLastVerified","latestKnownAddress","reasonsForNonExecution"],
  tech: ["cctnsSearchConducted","cctnsSearchDate","natgridVerificationRequired","natgridVerificationStatus","otherDatabaseChecks","interStatePoliceVerification"],
  location: ["currentProbableStateUT","currentProbableDistrict","currentProbablePS","locationConfidence","previousExecutionAttempts","lastAttemptDate","resultOfLastAttempt","priority"],
  exec: ["interStateTeamRequired","proposedStateCluster","proposedDistrictCluster","localPoliceCoordination","teamAssigned","dateTeamDeployed","executionStatus","dateOfExecution","productionTransitStatus"],
  court: ["courtIntimated","dateCourtIntimated","untraceableEffortsRecorded","reportFiledBeforeCourt","reportDate"],
  action: ["nextAction","targetDate","responsibleOfficer","shoVerification","unitNodalOfficerVerification"]
};
const FIELD_LABEL = Object.fromEntries(FIELDS);
const INDIAN_STATES_UTS = ["Andhra Pradesh","Telangana","Karnataka","Tamil Nadu","Maharashtra","Odisha","Chhattisgarh","Delhi","Madhya Pradesh","West Bengal","Uttar Pradesh","Bihar","Kerala","Gujarat","Rajasthan","Punjab","Haryana","Jharkhand","Assam","Other"];

let WARRANTS = [];
let unsubscribeFn = null;

const LocalStore = {
  key: "ap_warrants_demo_v2",
  all(){ try { return JSON.parse(localStorage.getItem(this.key)) || []; } catch(e){ return []; } },
  save(arr){ localStorage.setItem(this.key, JSON.stringify(arr)); }
};

function computeAgeing(w){
  if (!w.warrantDate) return { days: Number(w.ageingDays)||0, bucket: w.ageingBucket || "Unknown" };
  const start = new Date(w.warrantDate);
  if (isNaN(start)) return { days: Number(w.ageingDays)||0, bucket: w.ageingBucket || "Unknown" };
  const days = Math.max(0, Math.round((Date.now() - start.getTime()) / 86400000));
  const yrs = days/365;
  let bucket = "<1 Year";
  if (yrs >= 10) bucket = ">10 Years";
  else if (yrs >= 5) bucket = "5-10 Years";
  else if (yrs >= 1) bucket = "1-5 Years";
  return { days, bucket };
}

function normalizeRecord(id, data){
  const w = Object.assign({ id }, data);
  const ag = computeAgeing(w);
  w.ageingDays = ag.days;
  w.ageingBucket = ag.bucket;
  return w;
}

function startRealtimeSync(onChange){
  if (DEMO_MODE || !db) {
    WARRANTS = LocalStore.all().map(r => normalizeRecord(r.id, r));
    onChange(WARRANTS);
    return;
  }
  unsubscribeFn = db.collection(COLLECTION_NAME).onSnapshot(snap => {
    WARRANTS = snap.docs.map(d => normalizeRecord(d.id, d.data()));
    onChange(WARRANTS);
  }, err => {
    console.error("Firestore sync error:", err);
    setConnStatus("error", "Firestore error");
  });
}

async function isCollectionEmpty(){
  if (DEMO_MODE || !db) return LocalStore.all().length === 0;
  const snap = await db.collection(COLLECTION_NAME).limit(1).get();
  return snap.empty;
}

async function seedDatabase(records){
  if (DEMO_MODE || !db) {
    const withIds = records.map((r,i) => Object.assign({}, r, { id: r.id || ("local_" + (r.slNo || i+1)) }));
    LocalStore.save(withIds);
    WARRANTS = withIds.map(r => normalizeRecord(r.id, r));
    renderAll();
    return records.length;
  }
  const batchSize = 400;
  let count = 0;
  for (let i=0; i<records.length; i+=batchSize) {
    const batch = db.batch();
    const chunk = records.slice(i, i+batchSize);
    chunk.forEach(rec => {
      const docId = rec.cctnsId || rec.warrantNo || String(rec.slNo) || db.collection(COLLECTION_NAME).doc().id;
      const ref = db.collection(COLLECTION_NAME).doc(String(docId));
      batch.set(ref, rec, { merge: true });
      count++;
    });
    await batch.commit();
  }
  return count;
}

async function updateWarrantFields(id, fields){
  if (DEMO_MODE || !db) {
    const all = LocalStore.all();
    const idx = all.findIndex(r => r.id === id);
    if (idx >= 0) { all[idx] = Object.assign({}, all[idx], fields); LocalStore.save(all); }
    WARRANTS = all.map(r => normalizeRecord(r.id, r));
    renderAll();
    return;
  }
  await db.collection(COLLECTION_NAME).doc(id).set(fields, { merge: true });
}

let currentTab = "dashboard";
let filters = { q:"", unit:"", state:"", addrStatus:"", execStatus:"", priority:"", ageing:"" };
let page = 1;
const PAGE_SIZE = 25;
let charts = {};
let activeEditId = null;

function setConnStatus(mode, label){
  const el = document.getElementById("connStatus");
  const colors = { connecting: "text-amber-500", live: "text-emerald-500", demo: "text-blue-500", error: "text-rose-500" };
  el.className = "badge surface-2 " + (colors[mode]||"");
  el.innerHTML = `<i data-lucide="circle" class="w-2.5 h-2.5 fill-current"></i> ${label}`;
  lucide.createIcons();
}

function toast(msg, kind="success"){
  const el = document.getElementById("toast");
  const bg = kind==="success" ? "#15803d" : kind==="error" ? "#be123c" : "#1c3560";
  el.innerHTML = `<div class="px-4 py-3 rounded-lg text-white text-sm shadow-lg fade-in flex items-center gap-2" style="background:${bg}">
    <i data-lucide="${kind==='success'?'check-circle':'alert-circle'}" class="w-4 h-4"></i>${msg}</div>`;
  el.classList.remove("hidden");
  lucide.createIcons();
  clearTimeout(el._t);
  el._t = setTimeout(()=> el.classList.add("hidden"), 3200);
}

function escapeHtml(s){ return String(s ?? "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function isInterState(w){ return w.currentProbableStateUT && w.currentProbableStateUT !== "Andhra Pradesh"; }
function isVerified(w){ return (w.addressVerificationStatus||"").startsWith("Verified"); }

function uniqueValues(key){
  return Array.from(new Set(WARRANTS.map(w => w[key]).filter(Boolean))).sort();
}

function filteredWarrants(){
  const q = filters.q.trim().toLowerCase();
  // Enforce unit-level restriction if not IGP HQ
  const unitRestriction = (CURRENT_USER && CURRENT_USER.unit !== "IGP TECHNICAL SERVICES HQ") ? CURRENT_USER.unit : null;

  return WARRANTS.filter(w => {
    if (unitRestriction && w.policeUnit !== unitRestriction) return false;
    if (q) {
      const hay = [w.nameOfPerson, w.cctnsId, w.crimeNoYear, w.policeUnit, w.policeStation, w.courtCaseNo, w.warrantNo].join(" ").toLowerCase();
      if (!hay.includes(q)) return false;
    }
    if (filters.unit && w.policeUnit !== filters.unit) return false;
    if (filters.state && w.currentProbableStateUT !== filters.state) return false;
    if (filters.addrStatus && w.addressVerificationStatus !== filters.addrStatus) return false;
    if (filters.execStatus && w.executionStatus !== filters.execStatus) return false;
    if (filters.priority && w.priority !== filters.priority) return false;
    if (filters.ageing && w.ageingBucket !== filters.ageing) return false;
    return true;
  });
}

function renderKPIs(){
  const rows = filteredWarrants();
  const total = rows.length;
  const inter = rows.filter(isInterState).length;
  const intra = total - inter;
  const verified = rows.filter(isVerified).length;
  const defective = rows.filter(w => w.addressVerificationStatus && !isVerified(w)).length;
  const over5 = rows.filter(w => w.ageingBucket === "5-10 Years" || w.ageingBucket === ">10 Years").length;
  const over10 = rows.filter(w => w.ageingBucket === ">10 Years").length;

  const cards = [
    { label:"Total Warrants", value:total, icon:"file-text", color:"var(--accent)" },
    { label:"Inter-State Pendency", value:inter, icon:"map-pinned", color:"#b45309" },
    { label:"Intra-State Pendency", value:intra, icon:"map-pin", color:"#0e7490" },
    { label:"Verified Addresses", value:verified, icon:"badge-check", color:"#15803d" },
    { label:"Defective Addresses", value:defective, icon:"triangle-alert", color:"#be123c" },
    { label:"Ageing >5 / >10 Yrs", value:`${over5} / ${over10}`, icon:"hourglass", color:"#7c3aed" },
  ];
  document.getElementById("kpiGrid").innerHTML = cards.map(c => `
    <div class="surface rounded-xl p-4 flex items-center gap-3">
      <div class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0" style="background:${c.color}22">
        <i data-lucide="${c.icon}" class="w-5 h-5" style="color:${c.color}"></i>
      </div>
      <div class="min-w-0">
        <div class="text-xl font-bold leading-tight">${c.value}</div>
        <div class="text-dim text-[11px] leading-tight">${c.label}</div>
      </div>
    </div>`).join("");
  lucide.createIcons();

  const priorityRows = rows
    .filter(w => w.priority === "Critical" || w.priority === "High")
    .sort((a,b) => b.ageingDays - a.ageingDays)
    .slice(0, 10);
  document.querySelector("#priorityTable tbody").innerHTML = priorityRows.map(w => `
    <tr class="border-t border-c">
      <td class="py-2 pr-3">${escapeHtml(w.slNo)}</td>
      <td class="py-2 pr-3 font-medium">${escapeHtml(w.nameOfPerson)}</td>
      <td class="py-2 pr-3 text-dim">${escapeHtml(w.policeUnit)}</td>
      <td class="py-2 pr-3">${escapeHtml(w.currentProbableStateUT)}</td>
      <td class="py-2 pr-3">${w.ageingDays}d · ${escapeHtml(w.ageingBucket)}</td>
      <td class="py-2 pr-3">${priorityBadge(w.priority)}</td>
      <td class="py-2 pr-3">${statusBadge(w.executionStatus)}</td>
    </tr>`).join("") || `<tr><td colspan="7" class="py-4 text-center text-dim">No critical/high priority warrants</td></tr>`;
}

function chartColors(){
  const dark = document.documentElement.getAttribute("data-theme") === "dark";
  return {
    text: dark ? "#93a3c2" : "#475569",
    grid: dark ? "#1e2d4a" : "#e2e8f0",
    palette: ["#1c3560","#c9a84c","#0e7490","#be123c","#7c3aed","#15803d","#b45309","#4d79c9","#db2777","#64748b"]
  };
}

function renderCharts(){
  const rows = filteredWarrants();
  const cc = chartColors();
  Chart.defaults.color = cc.text;
  Chart.defaults.borderColor = cc.grid;

  const stateCounts = {};
  rows.forEach(w => { const s = w.currentProbableStateUT || "Unknown"; stateCounts[s] = (stateCounts[s]||0)+1; });
  const stateEntries = Object.entries(stateCounts).sort((a,b)=>b[1]-a[1]).slice(0,8);

  if (charts.state) charts.state.destroy();
  charts.state = new Chart(document.getElementById("stateChart"), {
    type: "bar",
    data: { labels: stateEntries.map(e=>e[0]), datasets: [{ data: stateEntries.map(e=>e[1]), backgroundColor: cc.palette, borderRadius:6 }] },
    options: { plugins:{ legend:{ display:false } }, scales:{ y:{ beginAtZero:true, grid:{color:cc.grid} }, x:{ grid:{display:false} } } }
  });

  const buckets = ["<1 Year","1-5 Years","5-10 Years",">10 Years"];
  const bucketCounts = buckets.map(b => rows.filter(w=>w.ageingBucket===b).length);
  if (charts.ageing) charts.ageing.destroy();
  charts.ageing = new Chart(document.getElementById("ageingChart"), {
    type: "doughnut",
    data: { labels: buckets, datasets: [{ data: bucketCounts, backgroundColor: [cc.palette[5],cc.palette[1],cc.palette[6],cc.palette[3]] }] },
    options: { plugins:{ legend:{ position:"bottom", labels:{ boxWidth:10, font:{size:10} } } } }
  });

  const funnelStages = ["Pending","In Progress","Team Deployed","Executed"];
  const funnelCounts = funnelStages.map(s => rows.filter(w=>w.executionStatus===s).length);
  if (charts.funnel) charts.funnel.destroy();
  charts.funnel = new Chart(document.getElementById("funnelChart"), {
    type: "bar",
    data: { labels: funnelStages, datasets: [{ data: funnelCounts, backgroundColor: cc.palette[0], borderRadius:6 }] },
    options: { indexAxis:"y", plugins:{ legend:{ display:false } }, scales:{ x:{ beginAtZero:true, grid:{color:cc.grid} }, y:{ grid:{display:false} } } }
  });
}

function statusBadge(status){
  const map = {
    "Executed":"bg-emerald-500/15 text-emerald-500",
    "Pending":"bg-slate-500/15 text-slate-400",
    "In Progress":"bg-amber-500/15 text-amber-500",
    "Team Deployed":"bg-blue-500/15 text-blue-400",
    "Untraceable":"bg-rose-500/15 text-rose-500",
    "Returned Unexecuted":"bg-rose-500/15 text-rose-500",
    "Stayed / Withdrawn":"bg-purple-500/15 text-purple-400"
  };
  return `<span class="badge ${map[status]||'bg-slate-500/15 text-slate-400'}">${escapeHtml(status||"—")}</span>`;
}
function addrBadge(status){
  const ok = (status||"").startsWith("Verified");
  const cls = ok ? "bg-emerald-500/15 text-emerald-500" : status ? "bg-rose-500/15 text-rose-500" : "bg-slate-500/15 text-slate-400";
  return `<span class="badge ${cls}">${escapeHtml(status||"Not Verified")}</span>`;
}
function priorityBadge(p){
  const map = { Critical:"bg-rose-500/15 text-rose-500", High:"bg-amber-500/15 text-amber-500", Normal:"bg-slate-500/15 text-slate-400" };
  return `<span class="badge ${map[p]||map.Normal}">${escapeHtml(p||"Normal")}</span>`;
}

function populateFilterOptions(){
  const sel = (id, values) => {
    const el = document.getElementById(id);
    const current = el.value;
    el.innerHTML = el.firstElementChild.outerHTML + values.map(v => `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`).join("");
    el.value = current;
  };
  sel("filterUnit", uniqueValues("policeUnit"));
  sel("filterState", uniqueValues("currentProbableStateUT"));
  sel("filterAddrStatus", OPTS.addressVerificationStatus);
  sel("filterExecStatus", OPTS.executionStatus);
  sel("filterPriority", OPTS.priority);
  sel("filterAgeing", ["<1 Year","1-5 Years","5-10 Years",">10 Years"]);
}

function renderMasterTable(){
  const rows = filteredWarrants();
  const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  page = Math.min(page, totalPages);
  const start = (page-1)*PAGE_SIZE;
  const pageRows = rows.slice(start, start+PAGE_SIZE);

  document.getElementById("masterTbody").innerHTML = pageRows.map(w => `
    <tr class="border-t border-c hover:bg-black/5 dark:hover:bg-white/5">
      <td class="py-2 px-3">${escapeHtml(w.slNo)}</td>
      <td class="py-2 px-3">${escapeHtml(w.policeUnit)}</td>
      <td class="py-2 px-3">${escapeHtml(w.policeStation)}</td>
      <td class="py-2 px-3">${escapeHtml(w.crimeNoYear)}</td>
      <td class="py-2 px-3 font-medium">${escapeHtml(w.nameOfPerson)}</td>
      <td class="py-2 px-3">${escapeHtml(w.currentProbableStateUT)}${isInterState(w) ? ' <span class="text-[10px] text-dim">(Inter-State)</span>' : ''}</td>
      <td class="py-2 px-3">${addrBadge(w.addressVerificationStatus)}</td>
      <td class="py-2 px-3">${w.ageingDays}d<br/><span class="text-dim text-[10px]">${escapeHtml(w.ageingBucket)}</span></td>
      <td class="py-2 px-3">${statusBadge(w.executionStatus)}</td>
      <td class="py-2 px-3 text-dim text-[11px]">${escapeHtml(w.lastUpdatedByUnit || "CCTNS Import")}<br/>${escapeHtml(w.lastUpdatedByOfficer || "")}</td>
      <td class="py-2 px-3">
        <button class="editBtn px-2.5 py-1.5 rounded-lg text-xs font-semibold text-white flex items-center gap-1" style="background:var(--accent)" data-id="${w.id}">
          <i data-lucide="pencil" class="w-3 h-3"></i>Update
        </button>
      </td>
    </tr>`).join("") || `<tr><td colspan="11" class="py-8 text-center text-dim">No records match the current filters.</td></tr>`;

  document.getElementById("rowCountLabel").textContent = `${rows.length} record${rows.length!==1?'s':''} (filtered)`;
  document.getElementById("pageLabel").textContent = `Page ${page} of ${totalPages}`;
  lucide.createIcons();

  document.querySelectorAll(".editBtn").forEach(btn => btn.addEventListener("click", () => openEditModal(btn.dataset.id)));
}

function renderClusters(){
  const rows = filteredWarrants();
  const interWarrants = rows.filter(isInterState);
  const groups = {};
  interWarrants.forEach(w => {
    const key = w.currentProbableStateUT || "Unspecified";
    (groups[key] = groups[key] || []).push(w);
  });
  const entries = Object.entries(groups).sort((a,b) => b[1].length - a[1].length);

  if (!entries.length) {
    document.getElementById("clusterGrid").innerHTML = `<div class="surface rounded-xl p-8 text-center text-dim col-span-full">No inter-state warrants found for the selected unit/filters.</div>`;
    return;
  }

  document.getElementById("clusterGrid").innerHTML = entries.map(([state, list]) => {
    const verified = list.filter(isVerified).length;
    const ready = list.filter(w => isVerified(w) && w.executionStatus !== "Executed").length;
    const executed = list.filter(w => w.executionStatus === "Executed").length;
    const districts = Array.from(new Set(list.map(w=>w.currentProbableDistrict).filter(Boolean)));
    return `
    <div class="surface rounded-xl p-4">
      <div class="flex items-center justify-between mb-3">
        <h4 class="font-bold flex items-center gap-2"><i data-lucide="flag" class="w-4 h-4" style="color:var(--accent-2)"></i>${escapeHtml(state)}</h4>
        <span class="badge surface-2">${list.length} warrants</span>
      </div>
      <div class="grid grid-cols-3 gap-2 text-xs mb-3">
        <div class="surface-2 rounded-lg p-2"><div class="text-dim">Verified</div><div class="font-bold">${verified}</div></div>
        <div class="surface-2 rounded-lg p-2"><div class="text-dim">Ready</div><div class="font-bold text-emerald-500">${ready}</div></div>
        <div class="surface-2 rounded-lg p-2"><div class="text-dim">Executed</div><div class="font-bold">${executed}</div></div>
      </div>
      <div class="text-xs text-dim mb-2">Districts: ${districts.slice(0,5).map(escapeHtml).join(", ") || "—"}</div>
      <button class="viewClusterBtn w-full text-xs font-semibold py-2 rounded-lg border border-c surface-2 hover:opacity-80" data-state="${escapeHtml(state)}">
        View Warrants &rarr;
      </button>
    </div>`;
  }).join("");
  lucide.createIcons();

  document.querySelectorAll(".viewClusterBtn").forEach(btn => btn.addEventListener("click", () => {
    filters.state = btn.dataset.state;
    document.getElementById("filterState").value = filters.state;
    switchTab("master");
    renderMasterTable();
  }));
}

function fieldInputHTML(key){
  const label = FIELD_LABEL[key] || key;
  if (OPTS[key]) {
    return `<div>
      <label class="text-xs font-semibold text-dim">${label}</label>
      <select id="f_${key}" class="w-full mt-1 px-3 py-2 rounded-lg text-sm">
        ${OPTS[key].map(o => `<option value="${escapeHtml(o)}">${escapeHtml(o)}</option>`).join("")}
      </select>
    </div>`;
  }
  if (key === "currentProbableStateUT") {
    return `<div>
      <label class="text-xs font-semibold text-dim">${label}</label>
      <select id="f_${key}" class="w-full mt-1 px-3 py-2 rounded-lg text-sm">
        ${INDIAN_STATES_UTS.map(o => `<option value="${escapeHtml(o)}">${escapeHtml(o)}</option>`).join("")}
      </select>
    </div>`;
  }
  const isDate = /date|since/i.test(key) && key !== "warrantPendingSince";
  return `<div>
    <label class="text-xs font-semibold text-dim">${label}</label>
    <input id="f_${key}" type="${isDate ? 'date' : 'text'}" class="w-full mt-1 px-3 py-2 rounded-lg text-sm" />
  </div>`;
}

function buildEditFormOnce(){
  Object.entries(EDIT_GROUPS).forEach(([grp, keys]) => {
    document.getElementById("grp-" + grp).innerHTML = keys.map(fieldInputHTML).join("");
  });
}

function openEditModal(id){
  const w = WARRANTS.find(r => r.id === id);
  if (!w) return;
  activeEditId = id;

  document.getElementById("modalTitle").textContent = `Update Warrant — ${w.nameOfPerson || ""}`;
  document.getElementById("modalSubtitle").textContent = `CCTNS ID: ${w.cctnsId || "—"} · Crime No: ${w.crimeNoYear || "—"} · Unit: ${w.policeUnit || ""}`;

  const snapshotFields = ["policeUnit","policeStation","court","courtCaseNo","warrantType","warrantDate","sectionsOfLaw","categoryOfCase","fatherSpouseName","originalAddress"];
  document.getElementById("modalSnapshot").innerHTML = snapshotFields.map(k => `
    <div><div class="text-dim text-[10px] uppercase tracking-wide">${FIELD_LABEL[k]}</div><div class="font-medium">${escapeHtml(w[k]) || "—"}</div></div>
  `).join("");

  Object.values(EDIT_GROUPS).flat().forEach(key => {
    const el = document.getElementById("f_" + key);
    if (el) el.value = w[key] || "";
  });
  document.getElementById("f_remarks").value = w.remarks || "";
  document.getElementById("editModal").classList.remove("hidden");
}

function closeEditModal(){
  document.getElementById("editModal").classList.add("hidden");
  activeEditId = null;
}

async function saveEdit(){
  if (!activeEditId) return;
  const fields = {};
  Object.values(EDIT_GROUPS).flat().forEach(key => {
    const el = document.getElementById("f_" + key);
    if (el) fields[key] = el.value;
  });
  fields.remarks = document.getElementById("f_remarks").value;
  // Audit trail stamp
  fields.lastUpdatedAt = new Date().toISOString();
  fields.lastUpdatedByUnit = CURRENT_USER.unit;
  fields.lastUpdatedByOfficer = CURRENT_USER.officer;

  const btn = document.getElementById("saveEdit");
  btn.disabled = true; btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Saving…`; lucide.createIcons();
  try {
    await updateWarrantFields(activeEditId, fields);
    toast("Record updated & audited successfully.");
    closeEditModal();
  } catch (e) {
    console.error(e);
    toast("Failed to save: " + e.message, "error");
  } finally {
    btn.disabled = false; btn.innerHTML = `<i data-lucide="save" class="w-4 h-4"></i> Save to Database`; lucide.createIcons();
  }
}

function exportCSV(){
  const rows = filteredWarrants();
  const header = FIELDS.map(f => f[1]);
  const lines = [header.map(toCSVValue).join(",")];
  rows.forEach(w => {
    lines.push(FIELDS.map(([k]) => toCSVValue(w[k])).join(","));
  });
  const csv = lines.join("\r\n");
  const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = `AP_Police_Pending_Warrants_${CURRENT_USER.unit.replace(/\s+/g,'_')}.csv`;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
  toast(`Exported ${rows.length} record(s).`);
}
function toCSVValue(v){
  const s = String(v ?? "");
  if (/[",\n]/.test(s)) return '"' + s.replace(/"/g,'""') + '"';
  return s;
}

async function handleSeed(){
  try {
    const empty = await isCollectionEmpty();
    if (!empty && confirm("Database already has records. Overwrite/merge with seed data?") === false) return;
    const res = await fetch("./warrants_data.json");
    if (!res.ok) throw new Error("warrants_data.json not found");
    const data = await res.json();
    const count = await seedDatabase(data);
    toast(`Seeded ${count} warrant records.`);
  } catch (e) {
    toast("Seed failed: " + e.message, "error");
  }
}

function switchTab(tab){
  currentTab = tab;
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.toggle("active", b.dataset.tab === tab));
  ["dashboard","master","deployment"].forEach(t => {
    document.getElementById("view-" + t).classList.toggle("hidden", t !== tab);
  });
  if (tab === "dashboard") renderCharts();
}

function initTheme(){
  const saved = localStorage.getItem("ap_warrants_theme") || "light";
  document.documentElement.setAttribute("data-theme", saved);
  updateThemeIcon();
}
function toggleTheme(){
  const cur = document.documentElement.getAttribute("data-theme");
  const next = cur === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("ap_warrants_theme", next);
  updateThemeIcon();
  renderCharts();
}
function updateThemeIcon(){
  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  document.getElementById("themeBtn").innerHTML = `<i data-lucide="${isDark?'sun':'moon'}" class="w-4 h-4"></i>`;
  lucide.createIcons();
}

function renderAll(){
  populateFilterOptions();
  renderKPIs();
  if (currentTab === "dashboard") renderCharts();
  renderMasterTable();
  renderClusters();
}

function wireEvents(){
  document.querySelectorAll(".tab-btn").forEach(b => b.addEventListener("click", () => switchTab(b.dataset.tab)));
  document.getElementById("themeBtn").addEventListener("click", toggleTheme);
  document.getElementById("seedBtn").addEventListener("click", handleSeed);
  document.getElementById("exportBtn").addEventListener("click", exportCSV);

  let searchTimer;
  document.getElementById("searchInput").addEventListener("input", (e) => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => { filters.q = e.target.value; page = 1; renderMasterTable(); }, 220);
  });
  [["filterUnit","unit"],["filterState","state"],["filterAddrStatus","addrStatus"],
   ["filterExecStatus","execStatus"],["filterPriority","priority"],["filterAgeing","ageing"]
  ].forEach(([id,key]) => {
    document.getElementById(id).addEventListener("change", (e) => { filters[key] = e.target.value; page = 1; renderMasterTable(); });
  });
  document.getElementById("clearFilters").addEventListener("click", () => {
    filters = { q:"", unit:"", state:"", addrStatus:"", execStatus:"", priority:"", ageing:"" };
    document.getElementById("searchInput").value = "";
    ["filterUnit","filterState","filterAddrStatus","filterExecStatus","filterPriority","filterAgeing"].forEach(id => document.getElementById(id).value = "");
    page = 1; renderMasterTable();
  });
  document.getElementById("prevPage").addEventListener("click", () => { if (page>1){ page--; renderMasterTable(); } });
  document.getElementById("nextPage").addEventListener("click", () => { page++; renderMasterTable(); });

  document.getElementById("closeModal").addEventListener("click", closeEditModal);
  document.getElementById("cancelEdit").addEventListener("click", closeEditModal);
  document.getElementById("saveEdit").addEventListener("click", saveEdit);
}

function bootApp(){
  lucide.createIcons();
  initTheme();
  buildEditFormOnce();
  wireEvents();

  if (DEMO_MODE) {
    setConnStatus("demo", "Demo Mode (Local Storage)");
  } else {
    setConnStatus("connecting", "Connecting to Firestore…");
  }

  startRealtimeSync((data) => {
    if (!DEMO_MODE) setConnStatus("live", `Live · ${data.length} records`);
    renderAll();
  });
}

(function(){
  checkLoginSession();
})();
</script>
</body>
</html>