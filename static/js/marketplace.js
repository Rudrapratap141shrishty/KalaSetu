/**
 * Marketplace & Smart Cataloging Studio Controller
 * Displays artisanal products, craft heritage stories, AR previews,
 * and voice-assisted product listing forms.
 */

class MarketplaceController {
  constructor() {
    this.products = [];
    this.activeCategory = 'all';
    this.searchQuery = '';
    this.isListening = false;
  }

  async init() {
    this.bindEvents();
    await this.fetchProducts();
  }

  bindEvents() {
    // Category pill filters
    const catPills = document.querySelectorAll('.cat-filter-pill');
    catPills.forEach(pill => {
      pill.addEventListener('click', () => {
        catPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        this.activeCategory = pill.dataset.cat;
        this.filterAndRender();
      });
    });

    // Search input
    const searchInput = document.getElementById('marketSearchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value.toLowerCase();
        this.filterAndRender();
      });
    }

    // Voice Cataloging Dictation Button
    const micBtn = document.getElementById('voiceDictationBtn');
    if (micBtn) {
      micBtn.addEventListener('click', () => this.toggleVoiceDictation());
    }

    // New Listing Form Submission
    const listingForm = document.getElementById('createListingForm');
    if (listingForm) {
      listingForm.addEventListener('submit', (e) => this.handleCreateListing(e));
    }
  }

  async fetchProducts() {
    try {
      const res = await ApiClient.request('/products/');
      this.products = res.products || [];
      this.filterAndRender();
    } catch (err) {
      console.warn('Failed to fetch products from API:', err);
    }
  }

  filterAndRender() {
    const grid = document.getElementById('marketProductsGrid');
    if (!grid) return;

    let filtered = this.products;
    if (this.activeCategory !== 'all') {
      filtered = filtered.filter(p => p.category.toLowerCase().includes(this.activeCategory.toLowerCase()));
    }
    if (this.searchQuery) {
      filtered = filtered.filter(p =>
        p.title.toLowerCase().includes(this.searchQuery) ||
        p.description.toLowerCase().includes(this.searchQuery) ||
        (p.artisan_name && p.artisan_name.toLowerCase().includes(this.searchQuery))
      );
    }

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1/-1; text-align:center; padding: 2.5rem 1rem; color:var(--text-muted);">
          <div style="font-size:2.5rem; margin-bottom:0.5rem;">🔍</div>
          <h4>No authentic crafts match your search</h4>
          <p style="font-size:0.8rem;">Try adjusting the category or search keywords.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = filtered.map(prod => `
      <div class="product-item-card animate-slide-up" style="
        background: var(--bg-surface-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        transition: transform var(--transition-normal);
      ">
        <div style="position:relative; height:160px; overflow:hidden;">
          <img src="${prod.image_url || 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=600'}" 
               alt="${prod.title}" 
               style="width:100%; height:100%; object-fit:cover; transition:transform 0.4s ease;"
               onerror="this.src='https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=600'" />
          <span class="badge badge-gi" style="position:absolute; top:8px; left:8px; font-size:0.65rem; background:rgba(0,0,0,0.7); backdrop-filter:blur(6px);">
            ${prod.badge || 'GI Certified'}
          </span>
          <button onclick="window.marketplaceController.open3DPreview('${prod.id}')" 
                  style="position:absolute; bottom:8px; right:8px; background:rgba(0,0,0,0.75); color:#FFF; font-size:0.7rem; padding:3px 8px; border-radius:var(--radius-pill); border:1px solid rgba(255,255,255,0.2); backdrop-filter:blur(6px);">
            🕶️ 3D AR
          </button>
        </div>

        <div style="padding: 0.9rem; flex:1; display:flex; flex-direction:column; justify-content:space-between;">
          <div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px;">
              <span style="font-size:0.72rem; color:var(--ochre-gold); font-weight:600; text-transform:uppercase;">
                ${prod.category}
              </span>
              <span style="font-size:0.72rem; color:var(--emerald); font-weight:700;">
                🌱 Fair Trade
              </span>
            </div>
            <h4 style="font-size:0.92rem; font-weight:700; margin-bottom:4px; line-height:1.3;">
              ${prod.title}
            </h4>
            <p style="font-size:0.74rem; color:var(--text-muted); margin-bottom:8px; line-height:1.4;">
              By <strong>${prod.artisan_name || 'Master Artisan'}</strong> • ${prod.artisan_city || 'Varanasi'}
            </p>
          </div>

          <div>
            <div style="background:rgba(244, 162, 40, 0.08); border-radius:var(--radius-xs); padding:5px 8px; margin-bottom:8px; display:flex; justify-content:space-between; font-size:0.72rem;">
              <span style="color:var(--text-secondary)">Artisan Fair Wage:</span>
              <strong style="color:var(--ochre-gold)">₹${prod.fair_artisan_wage}</strong>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span style="font-size:1.15rem; font-weight:800; color:var(--text-primary); font-family:var(--font-mono);">
                ₹${prod.price}
              </span>
              <button class="voice-guide-btn" style="padding:2px 7px; font-size:0.7rem;" onclick="window.marketplaceController.playProductStory('${prod.id}')">
                📖 Story
              </button>
            </div>

            <button class="btn btn-primary btn-sm" style="width:100%; border-radius:var(--radius-pill);" onclick="window.marketplaceController.buyProduct('${prod.id}')">
              ⚡ Buy with Escrow
            </button>
          </div>
        </div>
      </div>
    `).join('');
  }

  buyProduct(productId) {
    const prod = this.products.find(p => p.id === productId);
    if (!prod) return;
    window.paymentGateway.openCheckout(prod);
  }

  playProductStory(productId) {
    const prod = this.products.find(p => p.id === productId);
    if (!prod) return;

    const story = prod.artisan_story || `${prod.title} is handcrafted with pure authentic materials following traditional techniques by artisan ${prod.artisan_name || 'Master Weaver'}.`;
    
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(story);
      utterance.lang = 'hi-IN';
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    }
    
    window.app.showModal(`
      <div style="padding:1.5rem; text-align:center;">
        <div style="font-size:2.2rem; margin-bottom:0.5rem;">📜</div>
        <h3 style="margin-bottom:0.4rem;">Artisan Craft Heritage</h3>
        <h5 style="color:var(--ochre-gold); margin-bottom:1rem;">${prod.title}</h5>
        <div style="background:var(--bg-surface-elevated); padding:1rem; border-radius:var(--radius-md); text-align:left; font-size:0.82rem; line-height:1.6; color:var(--text-secondary); margin-bottom:1.2rem;">
          "${story}"
        </div>
        <button class="btn btn-primary" style="width:100%;" onclick="window.app.closeModal()">Close</button>
      </div>
    `);
  }

  open3DPreview(productId) {
    const prod = this.products.find(p => p.id === productId);
    if (!prod) return;

    window.app.showModal(`
      <div style="padding:1.5rem; text-align:center;">
        <div style="position:relative; width:100%; height:220px; background:#000; border-radius:var(--radius-md); overflow:hidden; margin-bottom:1rem; display:flex; align-items:center; justify-content:center;">
          <img src="${prod.image_url}" style="max-height:85%; transform:perspective(500px) rotateY(25deg); filter:drop-shadow(0 15px 25px rgba(0,0,0,0.8));" />
          <div style="position:absolute; bottom:8px; left:8px; background:rgba(0,0,0,0.7); font-size:0.7rem; padding:3px 8px; border-radius:var(--radius-pill); border:1px solid rgba(255,255,255,0.2);">
            📐 3D Spatial Hologram (Simulated)
          </div>
        </div>
        <h3 style="font-size:1.1rem; margin-bottom:0.3rem;">${prod.title}</h3>
        <p style="font-size:0.75rem; color:var(--text-muted); margin-bottom:1.2rem;">Rotate or place in your living space with WebXR</p>
        <div style="display:flex; gap:0.5rem;">
          <button class="btn btn-secondary" style="flex:1;" onclick="window.app.closeModal()">Close</button>
          <button class="btn btn-gold" style="flex:1;" onclick="window.app.closeModal(); window.marketplaceController.buyProduct('${prod.id}')">⚡ Buy Now</button>
        </div>
      </div>
    `);
  }

  toggleVoiceDictation() {
    const micBtn = document.getElementById('voiceDictationBtn');
    const descField = document.getElementById('listingDescriptionInput');

    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      window.app.showToast('Speech Recognition not supported in this browser. Please type.', 'info');
      return;
    }

    if (this.isListening) {
      if (this.recognition) this.recognition.stop();
      this.isListening = false;
      micBtn.classList.remove('active');
      return;
    }

    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRec();
    this.recognition.lang = 'hi-IN';
    this.recognition.continuous = false;
    this.recognition.interimResults = false;

    this.recognition.onstart = () => {
      this.isListening = true;
      if (micBtn) micBtn.classList.add('active');
      window.app.showToast('🎙️ Bolye! Listening in Hindi/English...', 'info');
    };

    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (descField) {
        descField.value += (descField.value ? ' ' : '') + transcript;
      }
      window.app.showToast(`Recorded: "${transcript}"`, 'success');
    };

    this.recognition.onerror = (e) => {
      console.warn('Speech error:', e);
      this.isListening = false;
      if (micBtn) micBtn.classList.remove('active');
    };

    this.recognition.onend = () => {
      this.isListening = false;
      if (micBtn) micBtn.classList.remove('active');
    };

    this.recognition.start();
  }

  async handleCreateListing(e) {
    e.preventDefault();
    const user = window.authService.currentUser;
    if (!user) {
      window.app.showToast('Please log in as an artisan to catalog a product.', 'error');
      return;
    }

    const title = document.getElementById('listingTitleInput').value;
    const category = document.getElementById('listingCategorySelect').value;
    const price = parseFloat(document.getElementById('listingPriceInput').value);
    const fairWage = parseFloat(document.getElementById('listingWageInput').value);
    const description = document.getElementById('listingDescriptionInput').value;
    const story = document.getElementById('listingStoryInput').value;

    try {
      const res = await ApiClient.request('/products/', 'POST', {
        artisan_id: user.id,
        title,
        category,
        price,
        fair_artisan_wage: fairWage,
        description,
        artisan_story: story,
        image_url: 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=600'
      });

      window.app.showToast('🎉 Craft listed successfully on the global artisan marketplace!', 'success');
      e.target.reset();
      await this.fetchProducts();
      window.app.switchTab('market');
    } catch (err) {
      window.app.showToast('Error cataloging craft: ' + err.message, 'error');
    }
  }
}

window.MarketplaceController = MarketplaceController;
