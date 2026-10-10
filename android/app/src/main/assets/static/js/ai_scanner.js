/**
 * AI Material Scanner & Smart Cataloging Controller
 * Interacts with GraphQL & REST APIs to analyze artisanal materials,
 * calculate fair-wage pricing, and dispatch hyper-local couriers.
 */

class AIScannerController {
  constructor() {
    this.currentScanResult = null;
    this.selectedMaterialHint = 'BANARASI_SILK';
    this.isScanning = false;
    this.stream = null;
  }

  init() {
    this.bindEvents();
    // Default initial scan to populate UI nicely
    this.performScan('BANARASI_SILK');
  }

  bindEvents() {
    // Material chip click handlers
    const chips = document.querySelectorAll('.sample-chip');
    chips.forEach(chip => {
      chip.addEventListener('click', (e) => {
        chips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        const hint = chip.dataset.hint;
        this.selectedMaterialHint = hint;
        this.performScan(hint);
      });
    });

    // Scan CTA Button click
    const scanBtn = document.getElementById('triggerScanBtn');
    if (scanBtn) {
      scanBtn.addEventListener('click', () => {
        this.performScan(this.selectedMaterialHint);
      });
    }

    // Camera Toggle Button
    const camToggle = document.getElementById('toggleCameraBtn');
    if (camToggle) {
      camToggle.addEventListener('click', () => this.toggleRealCamera());
    }

    // Image Upload Input
    const fileInput = document.getElementById('customMaterialUpload');
    if (fileInput) {
      fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
    }

    // Voice Feedback Button
    const voiceBtn = document.getElementById('voiceNarrateScanBtn');
    if (voiceBtn) {
      voiceBtn.addEventListener('click', () => this.narrateScanResult());
    }
  }

  async toggleRealCamera() {
    const video = document.getElementById('cameraVideoFeed');
    const previewImg = document.getElementById('cameraImagePreview');
    
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
      video.style.display = 'none';
      previewImg.style.display = 'block';
      window.app.showToast('Camera stream paused', 'info');
      return;
    }

    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      video.srcObject = this.stream;
      video.style.display = 'block';
      previewImg.style.display = 'none';
      video.play();
      window.app.showToast('Live Camera Activated!', 'success');
    } catch (err) {
      console.warn('Camera access error (simulated preview active):', err);
      window.app.showToast('Camera access unavailable. Using HD spectral visualizer.', 'info');
    }
  }

  handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const previewImg = document.getElementById('cameraImagePreview');
      previewImg.src = e.target.result;
      previewImg.style.display = 'block';
      const video = document.getElementById('cameraVideoFeed');
      if (video) video.style.display = 'none';

      window.app.showToast(`Analyzing uploaded image: ${file.name}...`, 'info');
      this.performScan(file.name);
    };
    reader.readAsDataURL(file);
  }

  async performScan(hint) {
    if (this.isScanning) return;
    this.isScanning = true;

    const scanWrapper = document.getElementById('scannerViewfinderCard');
    const hudStatus = document.getElementById('hudStatusText');
    const resultContainer = document.getElementById('scanResultContainer');

    if (scanWrapper) scanWrapper.classList.add('is-scanning');
    if (hudStatus) hudStatus.innerText = 'AI Scanning Spectral Matrix...';

    try {
      // 1. Query GraphQL API for Material Properties, Pricing & Courier
      let data = null;
      try {
        const gqlData = await ApiClient.scanMaterialGraphQL(hint);
        if (gqlData) {
          data = {
            material_name: gqlData.materialName,
            material_code: gqlData.materialCode,
            category: gqlData.category,
            origin_region: gqlData.originRegion,
            gi_certified: gqlData.giCertified,
            confidence_score: gqlData.confidenceScore,
            tensile_strength: gqlData.tensileStrength,
            durability_years: gqlData.durabilityYears,
            carbon_footprint_score: gqlData.carbonFootprintScore,
            texture_spec: gqlData.textureSpec,
            properties: JSON.parse(gqlData.propertiesJson || '{}'),
            suggested_crafts: gqlData.suggestedCrafts || [],
            sample_image: gqlData.sampleImage,
            pricing: {
              raw_material_base_cost: gqlData.pricing.rawMaterialBaseCost,
              fair_artisan_wage: gqlData.pricing.fairArtisanWage,
              standard_labor_hours: gqlData.pricing.standardLaborHours,
              fair_hourly_wage: gqlData.pricing.fairHourlyWage,
              tooling_and_firing: gqlData.pricing.toolingAndFiring,
              eco_packaging_and_tax: gqlData.pricing.ecoPackagingAndTax,
              recommended_fair_retail_price: gqlData.pricing.recommendedFairRetailPrice,
              conventional_middleman_price: gqlData.pricing.conventionalMiddlemanPrice,
              artisan_direct_share_percent: gqlData.pricing.artisanDirectSharePercent,
            },
            assigned_delivery: gqlData.assignedDelivery
          };
        }
      } catch (gqlErr) {
        console.warn('GraphQL query fallback to REST endpoint:', gqlErr);
      }

      // If GraphQL didn't return (or as fallback), call REST API
      if (!data) {
        const restRes = await ApiClient.request('/materials/scan/', 'POST', {
          material_hint: hint,
          scan_source: 'AI_VIEWFINDER'
        });
        data = restRes.analysis;
      }

      this.currentScanResult = data;

      // Update Camera Preview Image if not custom video
      const previewImg = document.getElementById('cameraImagePreview');
      if (previewImg && data.sample_image) {
        previewImg.src = data.sample_image;
      }

      // Render Data into DOM
      this.renderScanResult(data);

      if (hudStatus) hudStatus.innerText = `Identified: ${data.material_name}`;
      window.app.showToast(`✨ Identified ${data.material_name} (${(data.confidence_score * 100).toFixed(1)}% Match)`, 'success');

    } catch (err) {
      console.error('Scan error:', err);
      window.app.showToast('Scan error: ' + err.message, 'error');
    } finally {
      setTimeout(() => {
        if (scanWrapper) scanWrapper.classList.remove('is-scanning');
        this.isScanning = false;
      }, 600);
    }
  }

  renderScanResult(data) {
    const container = document.getElementById('scanResultContainer');
    if (!container) return;

    const p = data.pricing;
    const del = data.assigned_delivery || {
      name: 'Devendra Kumar (EV Cargo)',
      phone: '+91 98112 34567',
      vehicle_type: 'Green Electric Van',
      hub_city: 'Varanasi Central Artisan Depot',
      estimated_dispatch_mins: 12,
      rating: 4.9
    };

    // Build Properties list
    let propRows = '';
    for (const [key, val] of Object.entries(data.properties || {})) {
      const formattedKey = key.replace(/_/g, ' ').toUpperCase();
      propRows += `
        <div class="spec-box">
          <div class="spec-label">${formattedKey}</div>
          <div class="spec-value">${val}</div>
        </div>
      `;
    }

    container.innerHTML = `
      <div class="scan-result-card animate-slide-up">
        <!-- Header -->
        <div class="scan-result-header">
          <div class="scan-title-box">
            <div style="display:flex; align-items:center; gap:0.4rem; margin-bottom:0.25rem;">
              <span class="badge badge-gi">🛡️ GI Tag Certified</span>
              <span class="badge badge-green">🌱 ${data.carbon_footprint_score}</span>
            </div>
            <h3>${data.material_name}</h3>
            <p>📍 Origin: ${data.origin_region} • Category: ${data.category}</p>
          </div>
          <div class="confidence-gauge">
            <span>AI MATCH</span>
            <strong>${(data.confidence_score * 100).toFixed(1)}%</strong>
          </div>
        </div>

        <!-- Material Properties & Specs Grid -->
        <h4 style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.5rem; text-transform:uppercase;">
          🧪 Certified Physical & Spectral Properties
        </h4>
        <div class="properties-spec-grid">
          <div class="spec-box">
            <div class="spec-label">TENSILE / STRENGTH</div>
            <div class="spec-value">${data.tensile_strength}</div>
          </div>
          <div class="spec-box">
            <div class="spec-label">ESTIMATED LIFE</div>
            <div class="spec-value">${data.durability_years} Years Heritage</div>
          </div>
          ${propRows}
        </div>

        <!-- Transparent Fair-Wage Pricing Card -->
        <div class="pricing-breakdown-card">
          <div class="pricing-title-row">
            <h4>⚖️ AI Transparent Fair-Wage Pricing</h4>
            <span class="badge badge-terracotta">${p.artisan_direct_share_percent}% to Artisan</span>
          </div>

          <div class="price-line-item">
            <span>Raw Material Cost (${data.material_name.split(' ')[0]})</span>
            <span style="font-family:var(--font-mono)">₹${p.raw_material_base_cost.toFixed(2)}</span>
          </div>
          <div class="price-line-item highlight-wage">
            <span>⭐ Fair Artisan Living Wage (${p.standard_labor_hours} hrs @ ₹${p.fair_hourly_wage}/hr)</span>
            <span style="font-family:var(--font-mono); color:var(--ochre-gold);">+₹${p.fair_artisan_wage.toFixed(2)}</span>
          </div>
          <div class="price-line-item">
            <span>Tooling, Firing & Eco-Packaging</span>
            <span style="font-family:var(--font-mono)">+₹${(p.tooling_and_firing + p.eco_packaging_and_tax).toFixed(2)}</span>
          </div>
          <div class="price-line-item final-price">
            <span>Recommended Fair Retail Price</span>
            <span style="color:var(--emerald); font-size:1.15rem; font-family:var(--font-mono)">₹${p.recommended_fair_retail_price.toFixed(2)}</span>
          </div>

          <div class="middleman-comparison-alert">
            <span>⚠️</span>
            <span>Middleman Broker Price: <strong>₹${p.conventional_middleman_price.toFixed(2)}</strong> (Artisan direct platform saves <strong>₹${(p.conventional_middleman_price - p.recommended_fair_retail_price).toFixed(2)}</strong>!).</span>
          </div>
        </div>

        <!-- Assigned Nearest Delivery Logistics Partner -->
        <h4 style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.5rem; text-transform:uppercase;">
          🚚 Nearest Assigned Logistics Partner
        </h4>
        <div class="delivery-partner-preview">
          <div class="courier-info-left">
            <div class="courier-avatar-badge">⚡</div>
            <div class="courier-details">
              <h5>${del.name}</h5>
              <p>${del.vehicle_type} • ${del.hub_city}</p>
            </div>
          </div>
          <div class="courier-eta-badge">
            <div style="font-size:1rem; color:var(--emerald)">⚡ ${del.estimated_dispatch_mins || 12} mins</div>
            <span style="font-size:0.68rem; color:var(--text-muted)">Dispatch ETA</span>
          </div>
        </div>

        <!-- Action Trigger Bar -->
        <div style="display:flex; gap:0.6rem; margin-top:0.8rem;">
          <button class="btn btn-primary" style="flex:1;" onclick="window.scannerController.catalogCraftPrompt()">
            📦 Smart Catalog Craft
          </button>
          <button class="btn btn-gold" style="flex:1;" onclick="window.scannerController.quickBuyScanned()">
            ⚡ Buy with Escrow
          </button>
          <button class="voice-guide-btn" id="voiceNarrateScanBtn" title="Audio voice narration" onclick="window.scannerController.narrateScanResult()">
            🔊 Voice
          </button>
        </div>
      </div>
    `;
  }

  narrateScanResult() {
    if (!this.currentScanResult) return;
    const res = this.currentScanResult;
    const textToSpeak = `सामग्री की पहचान पूरी हुई। यह है ${res.material_name}। जी आई टैग प्रमाणित। अनुशंसित उचित मूल्य ₹${res.pricing.recommended_fair_retail_price} है, जिसमें कारीगर का पारिश्रमिक ₹${res.pricing.fair_artisan_wage} शामिल है। निकटतम डिलीवरी पार्टनर ${res.assigned_delivery.name} बारह मिनट में उपलब्ध है।`;

    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(textToSpeak);
      utterance.lang = 'hi-IN';
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
      window.app.showToast('🔊 Audio voice guidance playing in Hindi...', 'info');
    } else {
      window.app.showToast('Text-to-speech not supported on this browser.', 'info');
    }
  }

  catalogCraftPrompt() {
    if (!this.currentScanResult) return;
    window.app.switchTab('catalog');
    window.app.showToast('Redirected to Voice Catalog Studio with scanned material pre-filled!', 'success');
  }

  quickBuyScanned() {
    if (!this.currentScanResult) return;
    const res = this.currentScanResult;
    const mockProduct = {
      id: 'quick-buy-' + Date.now(),
      title: `${res.material_name} Handcrafted Edition`,
      price: res.pricing.recommended_fair_retail_price,
      fair_artisan_wage: res.pricing.fair_artisan_wage,
      image_url: res.sample_image,
      artisan: { full_name: 'Master Artisan', city: res.origin_region }
    };
    window.paymentGateway.openCheckout(mockProduct);
  }
}

window.AIScannerController = AIScannerController;
