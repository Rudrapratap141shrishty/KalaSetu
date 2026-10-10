/**
 * Authentication & Role Authorization Service
 * Manages JWT tokens, multi-role personas (Artisan, B2B Client, Buyer, Courier),
 * and role-based interface gating.
 */

class AuthService {
  constructor() {
    this.currentUser = null;
    this.currentRole = 'ARTISAN';
    this.onUserChangedCallbacks = [];
  }

  init() {
    const savedUser = localStorage.getItem('kalasetu_user');
    if (savedUser) {
      try {
        this.currentUser = JSON.parse(savedUser);
        this.currentRole = this.currentUser.role;
      } catch (e) {
        this.currentUser = null;
      }
    }
    
    // Default fallback persona if none logged in
    if (!this.currentUser) {
      this.loginAsPreset('ramesh_weaver');
    }
  }

  onUserChange(cb) {
    this.onUserChangedCallbacks.push(cb);
  }

  notifyChange() {
    localStorage.setItem('kalasetu_user', JSON.stringify(this.currentUser));
    this.onUserChangedCallbacks.forEach(cb => cb(this.currentUser));
  }

  async login(username, role = 'ARTISAN') {
    try {
      const res = await ApiClient.request('/auth/login/', 'POST', { username, role });
      ApiClient.setToken(res.token);
      this.currentUser = res.user;
      this.currentRole = res.user.role;
      this.notifyChange();
      return res;
    } catch (err) {
      console.warn('Backend login fallback:', err);
      // Mock local fallback
      this.currentUser = {
        username: username || 'artisan_demo',
        full_name: (username || 'artisan').replace('_', ' ').toUpperCase(),
        role: role,
        email: `${username || 'user'}@kalasetu.org`,
        city: 'Varanasi',
        is_verified: true
      };
      this.currentRole = role;
      this.notifyChange();
      return { success: true, user: this.currentUser };
    }
  }

  async register(formData) {
    try {
      const res = await ApiClient.request('/auth/register/', 'POST', formData);
      ApiClient.setToken(res.token);
      this.currentUser = res.user;
      this.currentRole = res.user.role;
      this.notifyChange();
      return res;
    } catch (err) {
      throw err;
    }
  }

  async loginAsPreset(presetKey) {
    const presets = {
      'ramesh_weaver': { username: 'ramesh_weaver', role: 'ARTISAN', label: 'Ramesh Ansari (Banarasi Silk Artisan)' },
      'savitri_potter': { username: 'savitri_potter', role: 'ARTISAN', label: 'Savitri Devi (Terracotta Potter)' },
      'fabindia_procure': { username: 'fabindia_procure', role: 'CLIENT_B2B', label: 'Ananya Sengupta (B2B Wholesaler / NGO Lead)' },
      'arjun_buyer': { username: 'arjun_buyer', role: 'BUYER_USER', label: 'Arjun Mehra (Consumer / Enthusiast)' },
      'devendra_cargo': { username: 'devendra_cargo', role: 'DELIVERY_AGENT', label: 'Devendra Kumar (EV Green Logistics)' }
    };

    const target = presets[presetKey] || presets['ramesh_weaver'];
    return await this.login(target.username, target.role);
  }

  logout() {
    ApiClient.setToken('');
    localStorage.removeItem('kalasetu_user');
    this.currentUser = null;
    this.notifyChange();
  }

  isArtisan() { return this.currentRole === 'ARTISAN'; }
  isClientB2B() { return this.currentRole === 'CLIENT_B2B'; }
  isBuyer() { return this.currentRole === 'BUYER_USER'; }
  isDelivery() { return this.currentRole === 'DELIVERY_AGENT'; }
}

window.authService = new AuthService();
