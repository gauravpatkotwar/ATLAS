const BASE_URL = window.location.hostname.includes('loca.lt')
  ? 'https://mighty-seals-judge.loca.lt/api/v1'
  : 'http://localhost:8000/api/v1';

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('atlas_token');
  const headers = new Headers(options.headers || {});
  
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers
  });
  
  if (response.status === 204) {
    return null as unknown as T;
  }
  
  const data = await response.json();
  
  if (!response.ok) {
    const errorMsg = data.detail || 'An error occurred during the API transaction.';
    throw new Error(Array.isArray(errorMsg) ? JSON.stringify(errorMsg) : errorMsg);
  }
  
  return data as T;
}

export const api = {
  auth: {
    async register(
      email: string,
      password: string,
      role: string = 'recruiter',
      orgName?: string,
      inviteCode?: string
    ): Promise<any> {
      return apiRequest('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          role,
          org_name: orgName || undefined,
          invite_code: inviteCode || undefined
        })
      });
    },
    
    async login(email: string, password: string): Promise<{ access_token: string; token_type: string }> {
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);
      
      const res = await apiRequest<{ access_token: string; token_type: string }>('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params.toString()
      });
      
      localStorage.setItem('atlas_token', res.access_token);
      return res;
    },
    
    async google(email: string, token: string): Promise<{ access_token: string; token_type: string }> {
      const res = await apiRequest<{ access_token: string; token_type: string }>('/auth/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, token })
      });
      localStorage.setItem('atlas_token', res.access_token);
      return res;
    },
    
    async me(): Promise<{ id: number; email: string; role: string; is_active: boolean }> {
      return apiRequest('/auth/me');
    },
    
    logout(): void {
      localStorage.removeItem('atlas_token');
    }
  },
  
  candidates: {
    async list(): Promise<any[]> {
      return apiRequest('/candidates');
    },
    
    async get(id: number): Promise<any> {
      return apiRequest(`/candidates/${id}`);
    },
    
    async upload(file: File): Promise<any> {
      const formData = new FormData();
      formData.append('file', file);
      
      return apiRequest('/candidates/upload', {
        method: 'POST',
        body: formData
      });
    },
    
    async update(id: number, payload: any): Promise<any> {
      return apiRequest(`/candidates/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    },
    
    async delete(id: number): Promise<void> {
      return apiRequest(`/candidates/${id}`, {
        method: 'DELETE'
      });
    },

    async initiateCall(candidateId: number, sdpOffer?: string): Promise<any> {
      return apiRequest('/candidates/call/initiate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_id: candidateId, sdp_offer: sdpOffer })
      });
    },
    
    async respondCall(candidateId: number, status: string, sdpAnswer?: string): Promise<any> {
      return apiRequest(`/candidates/call/respond/${candidateId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status, sdp_answer: sdpAnswer })
      });
    },
    
    async getCallStatus(candidateId: number): Promise<any> {
      return apiRequest(`/candidates/call/status/${candidateId}`);
    }
  },
  
  jobs: {
    async list(): Promise<any[]> {
      return apiRequest('/jobs');
    },
    
    async get(id: number): Promise<any> {
      return apiRequest(`/jobs/${id}`);
    },
    
    async create(payload: any): Promise<any> {
      return apiRequest('/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    },
    
    async update(id: number, payload: any): Promise<any> {
      return apiRequest(`/jobs/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    },
    
    async delete(id: number): Promise<void> {
      return apiRequest(`/jobs/${id}`, {
        method: 'DELETE'
      });
    },
    
    async recommendations(id: number): Promise<any[]> {
      return apiRequest(`/jobs/${id}/recommendations`);
    },

    async getPublic(id: number): Promise<any> {
      return apiRequest(`/jobs/${id}/public`);
    },

    async applyPublic(id: number, name: string, email: string, phone: string, file: File): Promise<any> {
      const formData = new FormData();
      formData.append('name', name);
      formData.append('email', email);
      if (phone) {
        formData.append('phone', phone);
      }
      formData.append('file', file);
      
      return apiRequest(`/jobs/${id}/apply`, {
        method: 'POST',
        body: formData
      });
    }
  },
  
  search: {
    async candidates(query: string, topK: number = 5): Promise<any[]> {
      return apiRequest('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: topK })
      });
    }
  },
  
  copilot: {
    async chat(query: string): Promise<{ reply: string }> {
      return apiRequest('/copilot/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
    },
    async history(): Promise<Array<{ role: string; content: string }>> {
      return apiRequest('/copilot/history');
    },
    async clearHistory(): Promise<void> {
      return apiRequest('/copilot/history', {
        method: 'DELETE'
      });
    }
  },
  
  billing: {
    async checkout(provider: string): Promise<any> {
      return apiRequest('/billing/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider })
      });
    },
    async confirm(provider: string, referenceId: string): Promise<any> {
      return apiRequest('/billing/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, reference_id: referenceId })
      });
    }
  }
};
