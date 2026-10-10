/**
 * Unified API Client for KalaSetu Mobile Application
 * Handles both REST API endpoints and Graphene GraphQL queries & mutations.
 */

const API_BASE_URL = '/api/v1';
const GRAPHQL_ENDPOINT = '/graphql';

class ApiClient {
  static getToken() {
    return localStorage.getItem('kalasetu_jwt_token') || '';
  }

  static setToken(token) {
    if (token) {
      localStorage.setItem('kalasetu_jwt_token', token);
    } else {
      localStorage.removeItem('kalasetu_jwt_token');
    }
  }

  static getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  // --- REST API Request Handler ---
  static async request(endpoint, method = 'GET', data = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const options = {
      method,
      headers: this.getHeaders(),
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      const json = await response.json();
      if (!response.ok) {
        throw new Error(json.error || json.message || `HTTP Error ${response.status}`);
      }
      return json;
    } catch (err) {
      console.error(`[REST API Error] ${method} ${endpoint}:`, err);
      throw err;
    }
  }

  // --- GraphQL Query & Mutation Handler ---
  static async graphql(query, variables = {}) {
    try {
      const response = await fetch(GRAPHQL_ENDPOINT, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ query, variables })
      });
      const json = await response.json();
      if (json.errors && json.errors.length > 0) {
        throw new Error(json.errors[0].message);
      }
      return json.data;
    } catch (err) {
      console.error('[GraphQL Error]:', err);
      throw err;
    }
  }

  // Convenient GraphQL Material Scan Query
  static async scanMaterialGraphQL(materialHint) {
    const query = `
      query ScanMaterial($hint: String!) {
        scanMaterial(materialHint: $hint) {
          materialKey
          materialCode
          materialName
          category
          originRegion
          giCertified
          confidenceScore
          tensileStrength
          durabilityYears
          carbonFootprintScore
          textureSpec
          propertiesJson
          suggestedCrafts
          sampleImage
          pricing {
            rawMaterialBaseCost
            standardCraftWeightKg
            standardLaborHours
            fairHourlyWage
            fairArtisanWage
            toolingAndFiring
            ecoPackagingAndTax
            recommendedFairRetailPrice
            conventionalMiddlemanPrice
            artisanDirectSharePercent
            currency
          }
          assignedDelivery {
            id
            name
            phone
            vehicleType
            vehicleNumber
            hubCity
            rating
            estimatedDispatchMins
          }
        }
      }
    `;
    const data = await this.graphql(query, { hint: materialHint });
    return data.scanMaterial;
  }
}

window.ApiClient = ApiClient;
