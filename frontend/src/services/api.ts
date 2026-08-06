const BASE_URL = (import.meta as any).env?.VITE_API_URL ||
  ((window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && window.location.port === '5173'
    ? 'http://localhost:8000/api/v1'
    : '/api/v1');

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('atlas_token');
  const headers = new Headers(options.headers || {});
  
  // Bypass localtunnel warning page for remote staging clients
  headers.set('bypass-tunnel-reminder', 'true');
  
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers
    });
  } catch (networkErr: any) {
    // Network-level failure (server down, no internet, CORS)
    throw new Error('Unable to reach the ATLAS server. Please check your connection and try again.');
  }
  
  if (response.status === 204) {
    return null as unknown as T;
  }
  
  // Safely parse response — server may return HTML on 502/503/nginx errors
  const contentType = response.headers.get('content-type') || '';
  let data: any = null;
  if (contentType.includes('application/json')) {
    try {
      data = await response.json();
    } catch {
      throw new Error('The server returned an unexpected response. Please try again.');
    }
  } else {
    // Non-JSON response (HTML error page, plain text, etc.)
    const text = await response.text().catch(() => '');
    if (!response.ok) {
      // Map common HTTP status codes to friendly messages
      if (response.status === 502 || response.status === 503) {
        throw new Error('The server is temporarily unavailable. Please wait a moment and try again.');
      }
      if (response.status === 504) {
        throw new Error('The server request timed out. Please try again.');
      }
      throw new Error(`Server error (${response.status}). Please try again.`);
    }
    return text as unknown as T;
  }
  
  if (!response.ok) {
    let errorMsg = data?.detail || 'An error occurred. Please try again.';
    if (Array.isArray(errorMsg)) {
      // FastAPI validation error array — extract the first meaningful message
      errorMsg = errorMsg.map((e: any) => e.msg || JSON.stringify(e)).join('. ');
    }
    throw new Error(errorMsg);
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
      inviteCode?: string,
      recoveryEmail?: string
    ): Promise<any> {
      return apiRequest('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          role,
          org_name: orgName || undefined,
          invite_code: inviteCode || undefined,
          recovery_email: recoveryEmail || undefined
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
    
    async forgotPassword(email: string): Promise<{ message: string; reset_token?: string }> {
      return apiRequest('/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
    },

    async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
      return apiRequest('/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: newPassword })
      });
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

    async createQuestionnaire(data: {
      name: string;
      email: string;
      phone?: string;
      location?: string;
      qualification: string;
      skills: string[];
      experience_years?: number;
      work_highlights?: string;
      projects?: string;
      desired_role?: string;
    }): Promise<any> {
      return apiRequest('/candidates/questionnaire', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
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
    },
    // Chat channels — stored as posts with post_type='channel'
    async listChannels(): Promise<any[]> {
      const all = await apiRequest<any[]>('/community/posts');
      return (all || []).filter((p: any) => p.post_type === 'channel');
    },
    async createChannel(name: string, description: string): Promise<any> {
      return apiRequest<any>('/community/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: name, content: description, is_anonymous: false, post_type: 'channel' })
      });
    },
    async getMessages(channelId: number): Promise<any[]> {
      return apiRequest<any[]>(`/community/posts/${channelId}/comments`);
    },
    async sendMessage(channelId: number, text: string, isAnonymous: boolean): Promise<any> {
      return apiRequest<any>(`/community/posts/${channelId}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: text, is_anonymous: isAnonymous })
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
  },

  sso: {
    async getConfig(): Promise<any> {
      return apiRequest<any>('/sso/config');
    },
    async updateConfig(idpEntityId: string, idpSsoUrl: string, x509Certificate: string): Promise<any> {
      return apiRequest<any>('/sso/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idp_entity_id: idpEntityId,
          idp_sso_url: idpSsoUrl,
          x509_certificate: x509Certificate
        })
      });
    },
    async loginMock(email: string, orgName: string): Promise<any> {
      const res = await apiRequest<any>('/sso/login-mock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, org_name: orgName })
      });
      localStorage.setItem('atlas_token', res.access_token);
      return res;
    }
  },

  developer: {
    async listKeys(): Promise<any[]> {
      return apiRequest<any[]>('/developer/keys');
    },
    async createKey(name: string): Promise<any> {
      return apiRequest<any>('/developer/keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
    },
    async deleteKey(keyId: number): Promise<any> {
      return apiRequest<any>(`/developer/keys/${keyId}`, {
        method: 'DELETE'
      });
    },
    async listWebhooks(): Promise<any[]> {
      return apiRequest<any[]>('/developer/webhooks');
    },
    async createWebhook(url: string, secretToken: string, events: string[]): Promise<any> {
      return apiRequest<any>('/developer/webhooks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, secret_token: secretToken, events })
      });
    },
    async deleteWebhook(webhookId: number): Promise<any> {
      return apiRequest<any>(`/developer/webhooks/${webhookId}`, {
        method: 'DELETE'
      });
    }
  },

  automations: {
    async listWorkflows(): Promise<any[]> {
      return apiRequest<any[]>('/automations/workflows');
    },
    async createWorkflow(name: string, triggerEvent: string, conditions: any, actionType: string, actionPayload: any): Promise<any> {
      return apiRequest<any>('/automations/workflows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          trigger_event: triggerEvent,
          conditions,
          action_type: actionType,
          action_payload: actionPayload
        })
      });
    },
    async deleteWorkflow(id: number): Promise<any> {
      return apiRequest<any>(`/automations/workflows/${id}`, {
        method: 'DELETE'
      });
    },
    async toggleWorkflow(id: number): Promise<any> {
      return apiRequest<any>(`/automations/workflows/${id}/toggle`, {
        method: 'POST'
      });
    }
  },

  integrations: {
    async list(): Promise<any[]> {
      return apiRequest<any[]>('/integrations');
    },
    async toggle(providerName: string): Promise<any> {
      return apiRequest<any>('/integrations/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider_name: providerName })
      });
    }
  },

  analytics: {
    async getThroughput(): Promise<any> {
      return apiRequest<any>('/analytics/throughput');
    },
    async getTimeToHire(): Promise<any> {
      return apiRequest<any>('/analytics/time-to-hire');
    }
  },

  academy: {
    async getStats(): Promise<any> { return apiRequest('/academy/stats'); },
    async listCourses(params?: { category?: string; level?: string; search?: string }): Promise<any[]> {
      const q = new URLSearchParams(params as any).toString();
      return apiRequest(`/academy/courses${q ? '?' + q : ''}`);
    },
    async getCourse(id: number): Promise<any> { return apiRequest(`/academy/courses/${id}`); },
    async createCourse(data: any): Promise<any> {
      return apiRequest('/academy/courses', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    },
    async publishCourse(id: number): Promise<any> {
      return apiRequest(`/academy/courses/${id}/publish`, { method: 'PUT' });
    },
    async addModule(courseId: number, data: any): Promise<any> {
      return apiRequest(`/academy/courses/${courseId}/modules`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    },
    async addLesson(moduleId: number, data: any): Promise<any> {
      return apiRequest(`/academy/modules/${moduleId}/lessons`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    },
    async enroll(courseId: number): Promise<any> {
      return apiRequest(`/academy/enroll/${courseId}`, { method: 'POST' });
    },
    async myEnrollments(): Promise<any[]> { return apiRequest('/academy/my-enrollments'); },
    async updateProgress(courseId: number, lessonId: number): Promise<any> {
      return apiRequest(`/academy/progress/${courseId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ lesson_id: lessonId }) });
    },
    async completeCourse(courseId: number): Promise<any> {
      return apiRequest(`/academy/complete/${courseId}`, { method: 'POST' });
    },
    async myCertificates(): Promise<any[]> { return apiRequest('/academy/certificates'); },
    async addReview(courseId: number, rating: number, body?: string): Promise<any> {
      return apiRequest(`/academy/reviews/${courseId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ rating, body }) });
    },
    async applyInstructor(data: any): Promise<any> {
      return apiRequest('/academy/instructor/apply', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    },
    async getInstructorProfile(): Promise<any> { return apiRequest('/academy/instructor/me'); },
    async skillGap(data: any): Promise<any> {
      return apiRequest('/academy/skill-gap', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    },
    async skillGapHistory(): Promise<any[]> { return apiRequest('/academy/skill-gap/history'); },
    async aiMentor(question: string): Promise<any> {
      return apiRequest('/academy/ai-mentor', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question }) });
    },
    async generateRoadmap(goal: string): Promise<any> {
      return apiRequest('/academy/roadmap', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ goal }) });
    },
    async submitProject(courseId: number, data: any): Promise<any> {
      return apiRequest(`/academy/projects/${courseId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    },
  },

  career: {
    async generateResume(data: { template?: string; target_role?: string }): Promise<any> {
      return apiRequest('/career/resume/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    },
    async scoreResume(data: { resume_text: string; job_description: string }): Promise<any> {
      return apiRequest('/career/resume/score', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    },
    async matchResumeToJob(jobId: number): Promise<any> {
      return apiRequest(`/career/resume/match-job/${jobId}`, { method: 'POST' });
    },
    async getSalaryInsights(data: { job_title: string; location?: string; experience_years?: number }): Promise<any> {
      return apiRequest('/career/salary/insights', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    },
    async getCareerAnalytics(): Promise<any> {
      return apiRequest('/career/career/analytics');
    },
    async getProfileScore(): Promise<any> {
      return apiRequest('/career/career/profile-score');
    },
    async getGamificationStats(): Promise<any> {
      return apiRequest('/career/gamification/stats');
    },
    async getLeaderboard(): Promise<any> {
      return apiRequest('/career/gamification/leaderboard');
    },
    async submitShowcaseProject(data: any): Promise<any> {
      return apiRequest('/career/showcase/submit', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    },
    async listShowcaseProjects(): Promise<any> {
      return apiRequest('/career/showcase/projects');
    },
    async startInterview(data: { job_title: string; skills?: string }): Promise<any> {
      return apiRequest('/career/interview/start', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    },
    async gradeInterviewRound(data: { job_title: string; current_round: number; question: string; answer: string }): Promise<any> {
      return apiRequest('/career/interview/grade-round', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    },
  },

  tv: {
    async channels(): Promise<any> {
      return apiRequest('/tv/channels');
    },
    async feed(channel: string = 'all', page: number = 1): Promise<any> {
      return apiRequest(`/tv/feed?channel=${channel}&page=${page}`);
    },
    async video(id: number): Promise<any> {
      return apiRequest(`/tv/videos/${id}`);
    },
    async watchVideo(id: number): Promise<any> {
      return apiRequest(`/tv/videos/${id}/watch`, { method: 'POST' });
    },
    async live(): Promise<any> {
      return apiRequest('/tv/live');
    },
    async search(q: string): Promise<any> {
      return apiRequest(`/tv/search?q=${encodeURIComponent(q)}`);
    },
    async bookmarks(): Promise<any> {
      return apiRequest('/tv/bookmarks');
    },
    async addBookmark(videoId: number): Promise<any> {
      return apiRequest(`/tv/bookmarks/${videoId}`, { method: 'POST' });
    },
    async removeBookmark(videoId: number): Promise<any> {
      return apiRequest(`/tv/bookmarks/${videoId}`, { method: 'DELETE' });
    },
    async aiSummary(videoId: number): Promise<any> {
      return apiRequest(`/tv/ai/summary/${videoId}`, { method: 'POST' });
    },
    async aiQuiz(videoId: number): Promise<any> {
      return apiRequest(`/tv/ai/quiz/${videoId}`, { method: 'POST' });
    },
    async seed(): Promise<any> {
      return apiRequest('/tv/seed');
    },
  },

  ats: {
    async score(data: { job_description: string; resume_text: string }): Promise<any> {
      return apiRequest('/ats/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
    },
  },

  advertise: {
    async packages(): Promise<any> {
      return apiRequest('/advertise/packages');
    },
    async inquire(data: {
      company_name: string;
      contact_name: string;
      contact_email: string;
      contact_phone?: string;
      website?: string;
      package_id: string;
      budget_range?: string;
      goals?: string;
      currency?: string;
    }): Promise<any> {
      return apiRequest('/advertise/inquire', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
    },
    async checkout(data: {
      inquiry_id: string;
      package_id: string;
      provider: string;
      currency: string;
    }): Promise<any> {
      return apiRequest('/advertise/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
    },
    async campaigns(): Promise<any> {
      return apiRequest('/advertise/campaigns');
    },
    async stats(): Promise<any> {
      return apiRequest('/advertise/stats');
    },
  },

  contacts: {
    async me(): Promise<any> { return apiRequest('/contacts/me'); },
    async lookup(atlasNo: string): Promise<any> { return apiRequest(`/contacts/lookup/${atlasNo}`); },
    async add(atlasNo: string, nickname?: string): Promise<any> {
      return apiRequest('/contacts/add', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ atlas_no: atlasNo, nickname }) });
    },
    async book(): Promise<any> { return apiRequest('/contacts/book'); },
    async savedMe(): Promise<any> { return apiRequest('/contacts/saved-me'); },
    async remove(entryId: number): Promise<any> {
      return apiRequest(`/contacts/remove/${entryId}`, { method: 'DELETE' });
    },
    // Messaging
    async sendMessage(atlasNo: string, content: string): Promise<any> {
      return apiRequest('/contacts/message/send', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ atlas_no: atlasNo, content }) });
    },
    async conversation(atlasNo: string, limit = 50): Promise<any> {
      return apiRequest(`/contacts/message/conversation/${atlasNo}?limit=${limit}`);
    },
    async inbox(): Promise<any> { return apiRequest('/contacts/message/inbox'); },
    // Video calls
    async inviteCall(atlasNo: string): Promise<any> {
      return apiRequest(`/contacts/calls/invite/${atlasNo}`, { method: 'POST' });
    },
    async checkIncoming(): Promise<any> { return apiRequest('/contacts/calls/incoming'); },
    async acceptCall(callId: number): Promise<any> {
      return apiRequest(`/contacts/calls/${callId}/accept`, { method: 'POST' });
    },
    async declineCall(callId: number): Promise<any> {
      return apiRequest(`/contacts/calls/${callId}/decline`, { method: 'POST' });
    },
    async endCall(callId: number): Promise<any> {
      return apiRequest(`/contacts/calls/${callId}/end`, { method: 'POST' });
    },
    async sendSignal(callId: number, signalType: string, data: any): Promise<any> {
      const payloadData = typeof data === 'string' ? data : JSON.stringify(data);
      return apiRequest(`/contacts/calls/${callId}/signal`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ signal_type: signalType, data: payloadData }) });
    },
    async getSignals(callId: number, afterId = 0): Promise<any> {
      return apiRequest(`/contacts/calls/${callId}/signals?after_id=${afterId}`);
    },
  },
};


