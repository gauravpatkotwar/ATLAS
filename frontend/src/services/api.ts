const BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && window.location.port === '5173'
  ? 'http://localhost:8000/api/v1'
  : '/api/v1';

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('atlas_token');
  const headers = new Headers(options.headers || {});
  
  // Bypass localtunnel warning page for remote staging clients
  headers.set('bypass-tunnel-reminder', 'true');
  
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
    
    async me(): Promise<{ id: number; email: string; role: string; is_active: boolean; video_path?: string }> {
      return apiRequest('/auth/me');
    },
    
    async uploadVideo(fileBlob: Blob): Promise<{ status: string; video_path: string }> {
      const formData = new FormData();
      formData.append('file', fileBlob, 'video.webm');
      return apiRequest<{ status: string; video_path: string }>('/video/users/video', {
        method: 'POST',
        body: formData
      });
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
    },
    
    async uploadVideo(candidateId: number, fileBlob: Blob): Promise<{ status: string; video_path: string }> {
      const formData = new FormData();
      formData.append('file', fileBlob, 'video.webm');
      return apiRequest<{ status: string; video_path: string }>(`/video/candidates/${candidateId}/video`, {
        method: 'POST',
        body: formData
      });
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
  },
  
  meet: {
    async createRoom(): Promise<{ room_code: string }> {
      return apiRequest<{ room_code: string }>('/meet/create', { method: 'POST' });
    },
    async joinRoom(roomCode: string, participantId: string, name: string): Promise<{ status: string; other_participants: any[] }> {
      return apiRequest<{ status: string; other_participants: any[] }>(`/meet/join/${roomCode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ participant_id: participantId, name })
      });
    },
    async sendSignal(roomCode: string, senderId: string, targetId: string, type: string, data: any): Promise<{ status: string }> {
      return apiRequest<{ status: string }>(`/meet/signal/${roomCode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sender_id: senderId, target_id: targetId, type, data })
      });
    },
    async poll(roomCode: string, participantId: string): Promise<{ signals: any[]; participants: any[] }> {
      return apiRequest<{ signals: any[]; participants: any[] }>(`/meet/poll/${roomCode}/${participantId}`);
    },
    async leave(roomCode: string, participantId: string): Promise<{ status: string }> {
      return apiRequest<{ status: string }>(`/meet/leave/${roomCode}/${participantId}`, { method: 'POST' });
    }
  },
  
  community: {
    async listPosts(): Promise<any[]> {
      return apiRequest<any[]>('/community/posts');
    },
    async createPost(title: string, content: string, isAnonymous: boolean, postType: string): Promise<any> {
      return apiRequest<any>('/community/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, is_anonymous: isAnonymous, post_type: postType })
      });
    },
    async vote(postId: number, direction: 'up' | 'down'): Promise<any> {
      return apiRequest<any>(`/community/posts/${postId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ direction })
      });
    },
    async listComments(postId: number): Promise<any[]> {
      return apiRequest<any[]>(`/community/posts/${postId}/comments`);
    },
    async createComment(postId: number, content: string, isAnonymous: boolean): Promise<any> {
      return apiRequest<any>(`/community/posts/${postId}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, is_anonymous: isAnonymous })
      });
    }
  },

  marketplace: {
    async listProducts(): Promise<any[]> {
      return apiRequest<any[]>('/marketplace/products');
    },
    async createProduct(name: string, description: string, price: number, category: string, downloadUrl?: string): Promise<any> {
      return apiRequest<any>('/marketplace/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description, price, category, download_url: downloadUrl })
      });
    },
    async purchaseProduct(productId: number): Promise<any> {
      return apiRequest<any>(`/marketplace/products/${productId}/purchase`, {
        method: 'POST'
      });
    },
    async listPurchases(): Promise<any[]> {
      return apiRequest<any[]>('/marketplace/purchases');
    }
  }
};
