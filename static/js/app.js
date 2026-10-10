/**
 * KalaSetu (कला सेतु) - Main Application Controller
 * Orchestrates navigation, role-switching, theme management, voice accessibility, and global UI modals.
 */

class KalaSetuApp {
  constructor() {
    this.currentTab = 'scanner';
    this.isDarkTheme = true;
    this.isFullscreen = false;
  }

  async init() {
    console.log('[KalaSetu] Initializing Mobile App Platform...');

    // Initialize Subsystems
    window.authService.init();
    
    window.scannerController = new AIScannerController();
    window.scannerController.init();

    window.marketplaceController = new MarketplaceController();
    await window.marketplaceController.init();

    window.paymentGateway = new PaymentGatewayController();
    window.paymentGateway.init();

    window.deliveryTracker = new DeliveryTrackerController();
    await window.deliveryTracker.init();

    this.bindGlobalEvents();
    this.updateRoleUI();
    this.startClock();

    // Listen to user auth changes
    window.authService.onUserChange(() => {
      this.updateRoleUI();
    });
  }

  bindGlobalEvents() {
    // Bottom navigation items
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      item.addEventListener('click', () => {
        const targetTab = item.dataset.tab;
        if (targetTab) {
          this.switchTab(targetTab);
        }
      });
    });

    // Center Floating Scan Button
    const centerScanCta = document.getElementById('centerScanCta');
    if (centerScanCta) {
      centerScanCta.addEventListener('click', () => {
        this.switchTab('scanner');
      });
    }

    // Role switcher pill click
    const rolePill = document.getElementById('currentRolePill');
    if (rolePill) {
      rolePill.addEventListener('click', () => this.openRoleSwitcherModal());
    }

    // Theme Toggle
    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
      themeBtn.addEventListener('click', () => this.toggleTheme());
    }

    // Mobile / Desktop Viewport Switcher
    const viewSwitchBtn = document.getElementById('deviceViewSwitchBtn');
    if (viewSwitchBtn) {
      viewSwitchBtn.addEventListener('click', () => this.toggleDeviceView());
    }

    // MongoDB Telemetry Viewer Button
    const mongoBtn = document.getElementById('mongoVaultBtn');
    if (mongoBtn) {
      mongoBtn.addEventListener('click', () => this.openMongoVaultModal());
    }

    // Android Privacy Shield Modal
    const privacyBtn = document.getElementById('privacyShieldBtn');
    if (privacyBtn) {
      privacyBtn.addEventListener('click', () => this.openPrivacyShieldModal());
    }

    // Voice Assistant Welcome
    const voiceWelcomeBtn = document.getElementById('voiceWelcomeBtn');
    if (voiceWelcomeBtn) {
      voiceWelcomeBtn.addEventListener('click', () => this.playWelcomeAudio());
    }
  }

  switchTab(tabName) {
    this.currentTab = tabName;

    // Update Tab screens
    const screens = document.querySelectorAll('.app-tab-screen');
    screens.forEach(screen => {
      screen.classList.remove('active-tab');
      if (screen.id === `tabScreen_${tabName}`) {
        screen.classList.add('active-tab');
      }
    });

    // Update Bottom Nav active state
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      item.classList.remove('active');
      if (item.dataset.tab === tabName) {
        item.classList.add('active');
      }
    });

    // Special handlers per tab
    if (tabName === 'delivery') {
      window.deliveryTracker.fetchTracking();
    } else if (tabName === 'market') {
      window.marketplaceController.fetchProducts();
    }

    // Scroll to top of container
    const content = document.querySelector('.app-content-container');
    if (content) content.scrollTop = 0;
  }

  toggleTheme() {
    this.isDarkTheme = !this.isDarkTheme;
    document.documentElement.setAttribute('data-theme', this.isDarkTheme ? 'dark' : 'light');
    const icon = document.getElementById('themeToggleIcon');
    if (icon) icon.innerText = this.isDarkTheme ? '☀️' : '🌙';
    this.showToast(`Switched to ${this.isDarkTheme ? 'Dark' : 'Light'} Mode`, 'info');
  }

  toggleDeviceView() {
    this.isFullscreen = !this.isFullscreen;
    document.body.classList.toggle('fullscreen-mode', this.isFullscreen);
    const btn = document.getElementById('deviceViewSwitchBtn');
    if (btn) {
      btn.innerText = this.isFullscreen ? '📱 Mobile Frame' : '🖥️ Wide View';
    }
    this.showToast(this.isFullscreen ? 'Wide Web Mode' : 'Mobile Phone Frame Mode', 'info');
  }

  updateRoleUI() {
    const user = window.authService.currentUser;
    const rolePill = document.getElementById('currentRolePill');
    const roleText = document.getElementById('currentRoleLabel');
    const roleBadge = document.getElementById('userRoleProfileBadge');

    if (user && roleText) {
      const roleNames = {
        'ARTISAN': '🎨 Artisan Portal',
        'CLIENT_B2B': '🏢 B2B Wholesaler',
        'BUYER_USER': '🛍️ Consumer',
        'DELIVERY_AGENT': '🚚 Courier'
      };
      roleText.innerText = roleNames[user.role] || user.role;
    }

    // Update Artisan Studio Dashboard if on that tab
    const artisanName = document.getElementById('dashboardArtisanName');
    const artisanCraft = document.getElementById('dashboardArtisanCraft');
    if (artisanName && user) artisanName.innerText = user.full_name;
    if (artisanCraft && user) artisanCraft.innerText = user.city + ' Craft Guild';
  }

  openRoleSwitcherModal() {
    this.showModal(`
      <div style="padding:1.5rem;">
        <h3 style="margin-bottom:0.4rem; font-size:1.15rem;">Switch Authorized Persona</h3>
        <p style="font-size:0.75rem; color:var(--text-muted); margin-bottom:1rem;">
          Select a role to test role-based security, artisan voice studios, or B2B contracts.
        </p>

        <div style="display:flex; flex-direction:column; gap:0.6rem; margin-bottom:1.2rem;">
          <div class="role-select-item" onclick="window.app.selectPersona('ramesh_weaver')" style="background:var(--bg-surface-elevated); padding:0.75rem; border-radius:var(--radius-sm); border:1px solid var(--border-medium); cursor:pointer;">
            <div style="font-weight:700; font-size:0.85rem; color:var(--ochre-gold);">🎨 Ramesh Ansari (Marginalized Artisan)</div>
            <div style="font-size:0.72rem; color:var(--text-muted);">Banarasi Handloom Weaver • Escrow Balance: ₹38,400</div>
          </div>

          <div class="role-select-item" onclick="window.app.selectPersona('savitri_potter')" style="background:var(--bg-surface-elevated); padding:0.75rem; border-radius:var(--radius-sm); border:1px solid var(--border-medium); cursor:pointer;">
            <div style="font-weight:700; font-size:0.85rem; color:var(--terracotta);">🏺 Savitri Prajapati (Terracotta Potter)</div>
            <div style="font-size:0.72rem; color:var(--text-muted);">Gorakhpur Terracotta Cluster • GI Certified</div>
          </div>

          <div class="role-select-item" onclick="window.app.selectPersona('fabindia_procure')" style="background:var(--bg-surface-elevated); padding:0.75rem; border-radius:var(--radius-sm); border:1px solid var(--border-medium); cursor:pointer;">
            <div style="font-weight:700; font-size:0.85rem; color:#93C5FD;">🏢 Ananya Sengupta (B2B Client / NGO Lead)</div>
            <div style="font-size:0.72rem; color:var(--text-muted);">Bulk Procurement & Fair-Trade Compliance Audits</div>
          </div>

          <div class="role-select-item" onclick="window.app.selectPersona('arjun_buyer')" style="background:var(--bg-surface-elevated); padding:0.75rem; border-radius:var(--radius-sm); border:1px solid var(--border-medium); cursor:pointer;">
            <div style="font-weight:700; font-size:0.85rem; color:var(--emerald);">🛍️ Arjun Mehra (Consumer / Craft Enthusiast)</div>
            <div style="font-size:0.72rem; color:var(--text-muted);">Direct Artisan Buyer • UPI 1-Click Payments</div>
          </div>

          <div class="role-select-item" onclick="window.app.selectPersona('devendra_cargo')" style="background:var(--bg-surface-elevated); padding:0.75rem; border-radius:var(--radius-sm); border:1px solid var(--border-medium); cursor:pointer;">
            <div style="font-weight:700; font-size:0.85rem; color:#38BDF8;">🚚 Devendra Kumar (Logistics Courier)</div>
            <div style="font-size:0.72rem; color:var(--text-muted);">Clean Route EV Van • Proof-of-Delivery Agent</div>
          </div>
        </div>

        <button class="btn btn-secondary" style="width:100%;" onclick="window.app.closeModal()">Cancel</button>
      </div>
    `);
  }

  async selectPersona(presetKey) {
    await window.authService.loginAsPreset(presetKey);
    this.closeModal();
    this.showToast(`Logged in as ${window.authService.currentUser.full_name}`, 'success');
  }

  async  openPrivacyShieldModal() {
    this.showModal(`
      <div style="padding:1.5rem; max-height:85vh; overflow-y:auto;">
        <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.4rem;">
          <div style="width:36px; height:36px; border-radius:50%; background:var(--gradient-jade); color:#FFF; display:flex; align-items:center; justify-content:center; font-size:1.2rem;">
            🛡️
          </div>
          <div>
            <h3 style="font-size:1.15rem; font-weight:700;">Android Privacy & Security Shield</h3>
            <span class="badge badge-green" style="font-size:0.68rem;">Android 14/15 Compliant • SDK 34/35</span>
          </div>
        </div>

        <p style="font-size:0.75rem; color:var(--text-muted); margin-bottom:1rem; line-height:1.4;">
          KalaSetu adheres to the latest Android granular privacy protections to safeguard marginalized artisans and buyers.
        </p>

        <div style="display:flex; flex-direction:column; gap:0.6rem; margin-bottom:1.2rem;">
          <!-- Camera Privacy -->
          <div style="background:var(--bg-surface-elevated); border:1px solid var(--border-subtle); border-radius:var(--radius-sm); padding:0.75rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
              <strong style="font-size:0.82rem; color:var(--text-primary);">📷 Material Scanner (Camera)</strong>
              <span class="badge badge-green" style="font-size:0.64rem;">ON-DEMAND ONLY</span>
            </div>
            <p style="font-size:0.72rem; color:var(--text-muted);">
              Camera stream is processed locally on device for material texture analysis. No raw video feed is uploaded without explicit consent.
            </p>
          </div>

          <!-- Microphone Privacy -->
          <div style="background:var(--bg-surface-elevated); border:1px solid var(--border-subtle); border-radius:var(--radius-sm); padding:0.75rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
              <strong style="font-size:0.82rem; color:var(--text-primary);">🎙️ Voice Studio (Microphone)</strong>
              <span class="badge badge-green" style="font-size:0.64rem;">EPHEMERAL SPEECH</span>
            </div>
            <p style="font-size:0.72rem; color:var(--text-muted);">
              Audio dictation in Hindi/English is converted directly to text on the device. Audio recordings are immediately discarded.
            </p>
          </div>

          <!-- Location Privacy -->
          <div style="background:var(--bg-surface-elevated); border:1px solid var(--border-subtle); border-radius:var(--radius-sm); padding:0.75rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
              <strong style="font-size:0.82rem; color:var(--text-primary);">📍 Logistics ETA (Coarse Location)</strong>
              <span class="badge badge-green" style="font-size:0.64rem;">APPROXIMATE ONLY</span>
            </div>
            <p style="font-size:0.72rem; color:var(--text-muted);">
              Only city/regional hub coordinates are used for clean route calculation. Exact background tracking is disabled.
            </p>
          </div>

          <!-- Granular Storage & Media -->
          <div style="background:var(--bg-surface-elevated); border:1px solid var(--border-subtle); border-radius:var(--radius-sm); padding:0.75rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
              <strong style="font-size:0.82rem; color:var(--text-primary);">🗄️ Media Access (Photo Picker)</strong>
              <span class="badge badge-green" style="font-size:0.64rem;">ZERO BROAD STORAGE ACCESS</span>
            </div>
            <p style="font-size:0.72rem; color:var(--text-muted);">
              Complies with Android 14 Granular Photo Picker. KalaSetu only accesses individual craft photos selected by the user.
            </p>
          </div>

          <!-- Data Encryption & Escrow -->
          <div style="background:var(--bg-surface-elevated); border:1px solid var(--border-subtle); border-radius:var(--radius-sm); padding:0.75rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
              <strong style="font-size:0.82rem; color:var(--text-primary);">🔒 Cryptographic Escrow & Auth</strong>
              <span class="badge badge-green" style="font-size:0.64rem;">SHA-256 ENCRYPTED</span>
            </div>
            <p style="font-size:0.72rem; color:var(--text-muted);">
              All authentication tokens and escrow payout seals are protected with 256-bit encryption. Cloud backup extraction is blocked.
            </p>
          </div>
        </div>

        <div style="display:flex; gap:0.6rem;">
          <button class="btn btn-secondary" style="flex:1;" onclick="window.app.clearAppData()">
            🗑️ Clear Local App Data
          </button>
          <button class="btn btn-primary" style="flex:1;" onclick="window.app.closeModal()">
            Done
          </button>
        </div>
      </div>
    `);
  }

  clearAppData() {
    localStorage.clear();
    sessionStorage.clear();
    this.closeModal();
    this.showToast('Local application cache and credentials cleared securely.', 'success');
    setTimeout(() => window.location.reload(), 800);
  }

  async openMongoVaultModal() {
    try {
      const res = await ApiClient.request('/mongo/vault/');
      const scans = res.spectral_scans || [];
      const stories = res.artisan_stories || [];

      this.showModal(`
        <div style="padding:1.5rem; max-height:80vh; overflow-y:auto;">
          <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">
            <span style="font-size:1.5rem;">🍃</span>
            <h3 style="font-size:1.15rem;">MongoDB Document Vault & Telemetry</h3>
          </div>
          <p style="font-size:0.74rem; color:var(--text-muted); margin-bottom:1rem;">
            Document Engine: <strong>${res.database_engine}</strong> (${res.mongo_connected ? '🟢 Connected' : '🟡 Embedded High-Performance Vault'})
          </p>

          <h4 style="font-size:0.85rem; color:var(--ochre-gold); margin-bottom:0.5rem;">
            📊 Raw AI Spectral Scans Collection (${scans.length} documents)
          </h4>
          <div style="background:#06090E; border:1px solid var(--border-subtle); border-radius:var(--radius-sm); padding:0.75rem; font-family:var(--font-mono); font-size:0.68rem; color:#38BDF8; max-height:180px; overflow-y:auto; margin-bottom:1rem;">
            ${JSON.stringify(scans.slice(0, 3), null, 2)}
          </div>

          <h4 style="font-size:0.85rem; color:var(--emerald); margin-bottom:0.5rem;">
            📜 Heritage Craft Stories Collection (${stories.length} stories)
          </h4>
          <div style="background:#06090E; border:1px solid var(--border-subtle); border-radius:var(--radius-sm); padding:0.75rem; font-family:var(--font-mono); font-size:0.68rem; color:#A7F3D0; max-height:160px; overflow-y:auto; margin-bottom:1.2rem;">
            ${JSON.stringify(stories.slice(0, 2), null, 2)}
          </div>

          <button class="btn btn-primary" style="width:100%;" onclick="window.app.closeModal()">Close Vault</button>
        </div>
      `);
    } catch (err) {
      this.showToast('Error opening Mongo vault: ' + err.message, 'error');
    }
  }

  playWelcomeAudio() {
    const text = "कला सेतु में आपका स्वागत है। यह हाशिए पर मौजूद कारीगरों के लिए AI संचालित स्मार्ट कैटलॉगिंग और बाज़ार लिंकेज मोबाइल ऐप है। सामग्री स्कैन करने के लिए नीचे दिए गए बटन पर टैप करें।";
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'hi-IN';
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
      this.showToast('🔊 Playing Voice Guide in Hindi...', 'info');
    } else {
      this.showToast('Audio welcome not supported on this browser.', 'info');
    }
  }

  showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-message toast-${type} animate-slide-up`;
    toast.style.cssText = `
      background: ${type === 'success' ? '#065F46' : (type === 'error' ? '#991B1B' : '#1E293B')};
      color: #FFF;
      padding: 0.65rem 1.1rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 600;
      box-shadow: 0 8px 24px rgba(0,0,0,0.5);
      border: 1px solid rgba(255,255,255,0.15);
      margin-top: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    `;
    toast.innerHTML = `<span>${type === 'success' ? '✓' : (type === 'error' ? '⚠️' : 'ℹ️')}</span> ${message}`;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  showModal(htmlContent) {
    const container = document.getElementById('globalModalContainer');
    const contentBox = document.getElementById('globalModalContent');
    if (contentBox && container) {
      contentBox.innerHTML = htmlContent;
      container.style.display = 'flex';
      container.style.opacity = '1';
    }
  }

  closeModal() {
    const container = document.getElementById('globalModalContainer');
    if (container) {
      container.style.display = 'none';
      container.style.opacity = '0';
    }
  }

  startClock() {
    const clockEl = document.getElementById('phoneClockDisplay');
    const updateTime = () => {
      if (clockEl) {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const mins = now.getMinutes().toString().padStart(2, '0');
        clockEl.innerText = `${hours}:${mins}`;
      }
    };
    updateTime();
    setInterval(updateTime, 30000);
  }
}

window.app = new KalaSetuApp();
document.addEventListener('DOMContentLoaded', () => window.app.init());
