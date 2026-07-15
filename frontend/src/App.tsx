import React, { useState, useEffect, useRef } from 'react';
import { 
  Users, Briefcase, Search, MessageSquare, UploadCloud, 
  Trash2, MapPin, DollarSign, LogOut, 
  AlertCircle, Sparkles, Send, Plus, X, Award, HelpCircle, Settings, CreditCard, CheckCircle,
  Mic, Volume2, VolumeX
} from 'lucide-react';
import { api } from './services/api';

const TitanLogo = ({ size = 24, style = {}, className = '' }: { size?: number; style?: React.CSSProperties; className?: string }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 100 100" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    className={className}
    style={{ display: 'inline-block', verticalAlign: 'middle', ...style }}
  >
    {/* Left Leg (Dark Charcoal) */}
    <path d="M50 36 L25 80 H40 L48 40 Z" fill="#444446" />
    {/* Right Leg (Muted Silver) */}
    <path d="M50 36 L75 80 H60 L52 40 Z" fill="#8e8e93" />
    {/* Top Globe (Stark White) */}
    <circle cx="50" cy="26" r="14" fill="#ffffff" />
    {/* Signature Nothing Red Glyph Indicator Dot */}
    <circle cx="70" cy="18" r="4.5" fill="#ff2d55" />
  </svg>
);

export default function App() {
  // Entrance Preloader state
  const [showEntrance, setShowEntrance] = useState(true);
  const [isClosingEntrance, setIsClosingEntrance] = useState(false);

  useEffect(() => {
    const closeStartTimer = setTimeout(() => {
      setIsClosingEntrance(true);
    }, 2400);

    const closeEndTimer = setTimeout(() => {
      setShowEntrance(false);
    }, 3300);

    return () => {
      clearTimeout(closeStartTimer);
      clearTimeout(closeEndTimer);
    };
  }, []);

  const renderPreloader = () => {
    if (!showEntrance) return null;
    return (
      <div className={`entrance-screen ${isClosingEntrance ? 'fade-out' : ''}`}>
        <div className="entrance-logo">
          <TitanLogo size={150} />
        </div>
        <div className="entrance-text">
          Atlas Work Intelligence
        </div>
        <div className="entrance-progress-track">
          <div className="entrance-progress-bar" />
        </div>
      </div>
    );
  };

  // Auth state
  const [token, setToken] = useState<string | null>(localStorage.getItem('atlas_token'));
  const [user, setUser] = useState<any>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [authError, setAuthError] = useState('');

  // App navigation
  const [activeTab, setActiveTab] = useState<'candidates' | 'jobs' | 'search' | 'copilot' | 'settings' | 'my_profile' | 'jobs_board' | 'interview_prep'>('copilot');

  // SaaS Tenant state
  const [orgName, setOrgName] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [isJoinOrg, setIsJoinOrg] = useState(false);

  // Business state
  const [candidates, setCandidates] = useState<any[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<any | null>(null);
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedJob, setSelectedJob] = useState<any | null>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const [recExplanation, setRecExplanation] = useState<{ candidate: string, text: string } | null>(null);

  // Interview Prep state
  const [prepJob, setPrepJob] = useState<any | null>(null);
  const [prepQuestion, setPrepQuestion] = useState<string>('');
  const [prepAnswer, setPrepAnswer] = useState<string>('');
  const [prepHistory, setPrepHistory] = useState<Array<{ question: string, answer: string, feedback: string, score: string }>>([]);
  const [prepLoading, setPrepLoading] = useState<boolean>(false);

  // File Upload state
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadError, setUploadError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Job creation state
  const [showCreateJob, setShowCreateJob] = useState(false);
  const [newJob, setNewJob] = useState({
    title: '',
    description: '',
    required_skills: '',
    salary: '',
    location: '',
    experience_years: 0,
    employment_type: 'Full-time'
  });

  // Semantic Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);

  // Copilot Chat state
  const [chatQuery, setChatQuery] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Voice Assistant state
  const [isListening, setIsListening] = useState<boolean>(false);
  const [voiceEnabled, setVoiceEnabled] = useState<boolean>(true); // default to true so it reads back immediately!
  const [recognitionInstance, setRecognitionInstance] = useState<any>(null);

  // Billing state
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [activeCheckoutSession, setActiveCheckoutSession] = useState<any | null>(null);
  const [paymentProcessing, setPaymentProcessing] = useState(false);
  const [paymentSuccessMsg, setPaymentSuccessMsg] = useState('');

  // Google Auth state
  const [showGoogleModal, setShowGoogleModal] = useState(false);

  // Post-login role choice
  const [selectedMode, setSelectedMode] = useState<string | null>(localStorage.getItem('atlas_mode'));

  const [appliedJobId, setAppliedJobId] = useState<number | null>(null);
  const myCandidateProfile = user ? candidates.find((c: any) => c.email?.toLowerCase() === user.email?.toLowerCase()) : null;

  // Public Job View states
  const [publicJobId, setPublicJobId] = useState<number | null>(null);
  const [publicJob, setPublicJob] = useState<any | null>(null);
  const [publicJobLoading, setPublicJobLoading] = useState(false);
  const [publicJobError, setPublicJobError] = useState('');
  
  // Public Apply Form states
  const [applyName, setApplyName] = useState('');
  const [applyEmail, setApplyEmail] = useState('');
  const [applyPhone, setApplyPhone] = useState('');
  const [applyFile, setApplyFile] = useState<File | null>(null);
  const [applyStatus, setApplyStatus] = useState('');
  const [applyError, setApplyError] = useState('');
  const [applySuccess, setApplySuccess] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const jobIdStr = params.get('publicJobId');
    if (jobIdStr) {
      const id = parseInt(jobIdStr);
      if (!isNaN(id)) {
        setPublicJobId(id);
        fetchPublicJob(id);
      }
    }
  }, []);

  const fetchPublicJob = async (id: number) => {
    setPublicJobLoading(true);
    setPublicJobError('');
    try {
      const job = await api.jobs.getPublic(id);
      setPublicJob(job);
    } catch (err: any) {
      setPublicJobError(err.message || 'Failed to retrieve job details.');
    } finally {
      setPublicJobLoading(false);
    }
  };

  const handlePublicApply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!publicJobId || !applyFile) return;
    setApplyStatus('Uploading resume and processing application...');
    setApplyError('');
    setApplySuccess(false);
    try {
      await api.jobs.applyPublic(publicJobId, applyName, applyEmail, applyPhone, applyFile);
      setApplySuccess(true);
      setApplyName('');
      setApplyEmail('');
      setApplyPhone('');
      setApplyFile(null);
    } catch (err: any) {
      setApplyError(err.message || 'Failed to submit application.');
    } finally {
      setApplyStatus('');
    }
  };


  // Load profile when token changes
  useEffect(() => {
    if (token) {
      api.auth.me()
        .then(res => setUser(res))
        .catch(() => handleLogout());
    }
  }, [token]);

  // Load lists when logged in
  useEffect(() => {
    if (user) {
      loadCandidates();
      loadJobs();
    }
  }, [user]);

  // Scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  // Load copilot chat history from database when activeTab changes to 'copilot'
  useEffect(() => {
    if (user && activeTab === 'copilot') {
      loadChatHistory();
    }
  }, [user, activeTab]);

  // Voice Assistant Speech Recognition & Synthesis Initializer
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-US';

      rec.onstart = () => {
        setIsListening(true);
      };

      rec.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setChatQuery(transcript);
      };

      rec.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
      };

      rec.onend = () => {
        setIsListening(false);
      };

      setRecognitionInstance(rec);
    }
  }, []);

  const handleToggleListening = () => {
    if (!recognitionInstance) {
      alert("Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.");
      return;
    }
    if (isListening) {
      recognitionInstance.stop();
    } else {
      try {
        recognitionInstance.start();
      } catch (err) {
        console.error(err);
      }
    }
  };

  const speakText = (text: string) => {
    if (!voiceEnabled || !window.speechSynthesis) return;

    // Stop any ongoing speech
    window.speechSynthesis.cancel();

    // Clean markdown formatting out of the text
    const cleanText = text
      .replace(/[*#_`\[\]()\-+]/g, '') // remove formatting symbols
      .replace(/https?:\/\/[^\s]+/g, 'link') // replace URLs with "link"
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;

    const voices = window.speechSynthesis.getVoices();
    const premiumVoice = voices.find(v => 
      v.lang.startsWith('en') && 
      (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Premium'))
    );
    if (premiumVoice) {
      utterance.voice = premiumVoice;
    }

    window.speechSynthesis.speak(utterance);
  };


  const loadChatHistory = async () => {
    try {
      const history = await api.copilot.history();
      setChatHistory(history);
    } catch (e) {
      console.error("Failed to load chat history:", e);
    }
  };

  const handleClearChatHistory = async () => {
    if (!window.confirm("Clear all copilot chat memory for your account?")) return;
    try {
      await api.copilot.clearHistory();
      setChatHistory([]);
    } catch (e) {
      alert("Failed to clear chat history");
    }
  };

  const handleStartPrep = async (job: any) => {
    setPrepJob(job);
    setPrepHistory([]);
    setPrepQuestion('');
    setPrepAnswer('');
    setPrepLoading(true);
    try {
      const q = "Generate the first technical mock interview question for the job opening: " + job.title + ". Focus on these required skills: " + job.required_skills + ". Please output ONLY the technical question and nothing else. Begin your response with 'QUESTION: '";
      const res = await api.copilot.chat(q);
      const cleanedQuestion = res.reply.replace(/QUESTION:\s*/i, '').trim();
      setPrepQuestion(cleanedQuestion || "Describe your experience working with " + job.required_skills.split(',')[0] + ".");
    } catch (err) {
      setPrepQuestion("Describe your experience building systems with " + job.required_skills + ".");
    } finally {
      setPrepLoading(false);
    }
  };

  const handleSubmitPrepAnswer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prepAnswer.trim() || !prepJob) return;

    const currentQ = prepQuestion;
    const currentAns = prepAnswer;

    setPrepLoading(true);
    try {
      const prompt = "You are an expert interviewer. Review my answer: '" + currentAns + "' to the technical question: '" + currentQ + "' for the job role: " + prepJob.title + ". Provide constructive feedback on accuracy, followed by a score rating from 0 to 10 in the format 'SCORE: [X]/10', and then output the next question in the format 'QUESTION: [next technical question here]'";
      const res = await api.copilot.chat(prompt);
      const reply = res.reply;

      // Extract Score
      const scoreMatch = reply.match(/SCORE:\s*([^\n\r]+)/i);
      const score = scoreMatch ? scoreMatch[1].trim() : "Completed";

      // Extract Next Question
      const questionMatch = reply.match(/QUESTION:\s*([\s\S]+)/i);
      const nextQuestion = questionMatch ? questionMatch[1].trim() : "Thank you for completing the interview mock session!";

      // Extract Feedback
      let feedback = reply;
      if (scoreMatch) feedback = feedback.replace(scoreMatch[0], '');
      if (questionMatch) feedback = feedback.replace(questionMatch[0], '');
      feedback = feedback.replace(/SCORE:|QUESTION:/gi, '').trim();

      setPrepHistory(prev => [
        { question: currentQ, answer: currentAns, feedback: feedback || "Good response.", score: score },
        ...prev
      ]);
      setPrepQuestion(nextQuestion);
      setPrepAnswer('');
    } catch (err) {
      alert("Prep assistant connection timeout. Please try again.");
    } finally {
      setPrepLoading(false);
    }
  };

  const loadCandidates = async () => {
    try {
      const res = await api.candidates.list();
      setCandidates(res);
    } catch (e) {
      console.error(e);
    }
  };

  const loadJobs = async () => {
    try {
      const res = await api.jobs.list();
      setJobs(res);
    } catch (e) {
      console.error(e);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    try {
      if (isRegister) {
        await api.auth.register(
          email,
          password,
          'recruiter',
          isJoinOrg ? undefined : orgName,
          isJoinOrg ? inviteCode : undefined
        );
        setIsRegister(false);
        setOrgName('');
        setInviteCode('');
        setAuthError('Registration successful! Please log in.');
      } else {
        await api.auth.login(email, password);
        setToken(localStorage.getItem('atlas_token'));
      }
    } catch (err: any) {
      setAuthError(err.message || 'Authentication transaction failed');
    }
  };

  const handleLogout = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    api.auth.logout();
    setToken(null);
    setUser(null);
    setCandidates([]);
    setJobs([]);
    setSelectedCandidate(null);
    setSelectedJob(null);
    setChatHistory([]);
    setSelectedMode(null);
    localStorage.removeItem('atlas_mode');
  };

  const handleStartCheckout = async (provider: string) => {
    try {
      const res = await api.billing.checkout(provider);
      setActiveCheckoutSession(res);
      setShowUpgradeModal(false);
    } catch (err: any) {
      alert(`Checkout failed: ${err.message}`);
    }
  };

  const handleConfirmCheckout = async () => {
    if (!activeCheckoutSession) return;
    setPaymentProcessing(true);
    try {
      const referenceId = activeCheckoutSession.provider === 'stripe' 
        ? activeCheckoutSession.session_id 
        : activeCheckoutSession.order_id;
      
      await api.billing.confirm(activeCheckoutSession.provider, referenceId);
      setPaymentSuccessMsg(`Payment Confirmed! Organization upgraded to PRO via ${activeCheckoutSession.provider.toUpperCase()}.`);
      
      // Reload user profile to refresh subscription_tier
      const freshUser = await api.auth.me();
      setUser(freshUser);
      
      // Refresh database records
      loadCandidates();
      loadJobs();
      
      setTimeout(() => {
        setActiveCheckoutSession(null);
        setPaymentSuccessMsg('');
      }, 3000);
    } catch (err: any) {
      alert(`Confirmation failed: ${err.message}`);
    } finally {
      setPaymentProcessing(false);
    }
  };

  const handleGoogleLogin = async (googleEmail: string) => {
    try {
      const mockToken = `mock-google-token-${googleEmail}-${Date.now()}`;
      await api.auth.google(googleEmail, mockToken);
      setToken(localStorage.getItem('atlas_token'));
      
      // Load user profile
      const freshUser = await api.auth.me();
      setUser(freshUser);
      loadCandidates();
      loadJobs();
      setShowGoogleModal(false);
    } catch (err: any) {
      alert(`Google Login failed: ${err.message}`);
    }
  };

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadStatus('Uploading file...');
    setUploadError('');
    try {
      setUploadStatus('Running AI extraction pipeline...');
      const createdCandidate = await api.candidates.upload(file);
      setUploadStatus('Indexing candidate embeddings...');
      
      if (selectedMode === 'for_hire' && createdCandidate) {
        try {
          await api.candidates.update(createdCandidate.id, { email: user.email });
        } catch (linkErr) {
          console.error("Auto-linking email failed:", linkErr);
        }
      }
      
      await loadCandidates();
      setUploadStatus('Resume processed successfully!');
      setSelectedCandidate(createdCandidate);
    } catch (err: any) {
      setUploadError(err.message || 'Pipeline processing aborted.');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // Delete Candidate
  const handleDeleteCandidate = async (id: number) => {
    if (!window.confirm('Delete candidate profile and FAISS vector index?')) return;
    try {
      await api.candidates.delete(id);
      if (selectedCandidate?.id === id) setSelectedCandidate(null);
      loadCandidates();
    } catch (e) {
      alert('Delete failed');
    }
  };

  // Create Job opening
  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const skillsArray = newJob.required_skills.split(',').map(s => s.trim()).filter(Boolean);
      await api.jobs.create({
        ...newJob,
        required_skills: skillsArray
      });
      setShowCreateJob(false);
      setNewJob({
        title: '',
        description: '',
        required_skills: '',
        salary: '',
        location: '',
        experience_years: 0,
        employment_type: 'Full-time'
      });
      loadJobs();
    } catch (err: any) {
      alert('Failed to publish job opening: ' + err.message);
    }
  };

  // Load candidate recommendations for selected Job
  const handleSelectJob = async (job: any) => {
    setSelectedJob(job);
    setRecommendations([]);
    setLoadingRecommendations(true);
    try {
      const matchResults = await api.jobs.recommendations(job.id);
      setRecommendations(matchResults);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingRecommendations(false);
    }
  };

  // Run Semantic search
  const handleSemanticSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const results = await api.search.candidates(searchQuery);
      setSearchResults(results);
    } catch (e: any) {
      alert('Search failed: ' + e.message);
    } finally {
      setSearching(false);
    }
  };

  // Copilot assistant chat trigger
  const handleSendChatMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatQuery.trim()) return;

    const userMessage = { role: 'user', content: chatQuery };
    setChatHistory(prev => [...prev, userMessage]);
    setChatQuery('');
    setChatLoading(true);

    try {
      const response = await api.copilot.chat(userMessage.content);
      setChatHistory(prev => [...prev, { role: 'assistant', content: response.reply }]);
      speakText(response.reply);
    } catch (err: any) {
      setChatHistory(prev => [...prev, { role: 'assistant', content: 'Connection timed out. Verify Ollama models are initialized.' }]);
    } finally {
      setChatLoading(false);
    }
  };



  // Public Job View rendering
  if (publicJobId) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: 'var(--bg-dark)' }}>
        {renderPreloader()}
        {/* Top Header */}
        <header className="glass-panel" style={{ borderRadius: '0', borderLeft: 'none', borderRight: 'none', borderTop: 'none', padding: '16px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <TitanLogo size={36} />
            <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#ffffff' }}>
              Atlas Work Intelligence
            </h1>
          </div>
          <div>
            <button 
              onClick={() => {
                setPublicJobId(null);
                window.history.pushState({}, '', window.location.pathname);
              }} 
              className="btn-secondary" 
              style={{ padding: '8px 16px', fontSize: '12px' }}
            >
              Go to Portal Login
            </button>
          </div>
        </header>

        <main style={{ flex: 1, maxWidth: '800px', width: '100%', margin: '40px auto', padding: '0 16px' }}>
          {publicJobLoading ? (
            <div className="glass-panel" style={{ padding: '48px', textAlign: 'center' }}>
              <Sparkles size={32} className="pulse-glow" style={{ margin: '0 auto 16px auto', color: 'var(--accent-orange)' }} />
              <p style={{ color: 'var(--text-muted)' }}>Loading job specification details...</p>
            </div>
          ) : publicJobError ? (
            <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              <AlertCircle size={48} style={{ color: '#ef4444', margin: '0 auto 16px auto' }} />
              <h3 style={{ color: '#fff', fontSize: '18px', marginBottom: '8px' }}>Job Listing Unavailable</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>{publicJobError}</p>
            </div>
          ) : publicJob ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {/* Job Info Card */}
              <div className="glass-panel lining-jobs" style={{ padding: '36px' }}>
                <span style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--accent-orange)', fontWeight: 600 }}>Active Job Opening</span>
                <h2 style={{ fontSize: '28px', color: '#fff', marginTop: '6px', marginBottom: '12px' }}>{publicJob.title}</h2>
                
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', fontSize: '14px', color: 'var(--text-muted)', marginBottom: '24px' }}>
                  {publicJob.location && <span>📍 {publicJob.location}</span>}
                  {publicJob.salary && <span>💰 {publicJob.salary}</span>}
                  {publicJob.employment_type && <span>💼 {publicJob.employment_type}</span>}
                  {publicJob.experience_years !== undefined && <span>⏳ Exp: {publicJob.experience_years} years</span>}
                </div>

                <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '24px' }}>
                  <h4 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '8px' }}>Description</h4>
                  <p style={{ fontSize: '15px', color: 'var(--text-muted)', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                    {publicJob.description}
                  </p>
                </div>

                {publicJob.required_skills?.length > 0 && (
                  <div style={{ marginTop: '24px' }}>
                    <h4 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '10px' }}>Skills & Requirements</h4>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {publicJob.required_skills.map((s: string, idx: number) => (
                        <span key={idx} style={{ padding: '4px 10px', fontSize: '12px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-glass)', borderRadius: '6px', color: 'var(--text-muted)' }}>
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Apply Form Card */}
              <div className="glass-panel" style={{ padding: '36px' }}>
                <h3 style={{ fontSize: '20px', color: '#fff', marginBottom: '8px' }}>Submit Your Application</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '24px' }}>
                  Upload your resume (.pdf, .docx, .txt) and fill in your details to apply. The hiring team will be notified immediately.
                </p>

                {applySuccess ? (
                  <div style={{ padding: '24px', background: 'rgba(34, 197, 94, 0.05)', border: '1px solid rgba(34, 197, 94, 0.15)', borderRadius: '12px', textAlign: 'center' }}>
                    <CheckCircle size={48} className="pulse-glow" style={{ color: 'var(--accent-green)', margin: '0 auto 16px auto' }} />
                    <h4 style={{ fontSize: '18px', color: '#fff', marginBottom: '6px' }}>Application Submitted!</h4>
                    <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Your profile has been created and linked. Recruiters will contact you directly.</p>
                  </div>
                ) : (
                  <form onSubmit={handlePublicApply} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {applyError && (
                      <div style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '8px', color: '#ef4444', fontSize: '13px' }}>
                        {applyError}
                      </div>
                    )}

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                      <div>
                        <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Full Name</label>
                        <input 
                          type="text" 
                          required 
                          className="input-field" 
                          placeholder="Jane Doe" 
                          value={applyName}
                          onChange={e => setApplyName(e.target.value)}
                        />
                      </div>
                      <div>
                        <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Email Address</label>
                        <input 
                          type="email" 
                          required 
                          className="input-field" 
                          placeholder="jane.doe@example.com" 
                          value={applyEmail}
                          onChange={e => setApplyEmail(e.target.value)}
                        />
                      </div>
                    </div>

                    <div>
                      <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Phone Number (Optional)</label>
                      <input 
                        type="text" 
                        className="input-field" 
                        placeholder="+1 (555) 000-0000" 
                        value={applyPhone}
                        onChange={e => setApplyPhone(e.target.value)}
                      />
                    </div>

                    <div>
                      <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Resume File (.pdf, .docx, .txt)</label>
                      <input 
                        type="file" 
                        required 
                        className="input-field" 
                        accept=".pdf,.docx,.txt"
                        onChange={e => setApplyFile(e.target.files?.[0] || null)}
                      />
                    </div>

                    <button type="submit" disabled={!!applyStatus} className="btn-primary lining-jobs" style={{ justifyContent: 'center', width: '100%', marginTop: '12px' }}>
                      <UploadCloud size={16} />
                      {applyStatus ? applyStatus : 'Submit Application'}
                    </button>
                  </form>
                )}
              </div>
            </div>
          ) : null}
          {/* Footer */}
          <footer style={{ borderTop: '1px solid var(--border-glass)', padding: '24px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.1em', marginTop: '40px' }}>
            Developed and Designed by Atlas Work Intelligence
          </footer>
        </main>
      </div>
    );
  }

  if (!token || !user) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '16px' }}>
        {renderPreloader()}
        <div className="glass-panel" style={{ width: '100%', maxWidth: '420px', padding: '32px' }}>
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <div style={{ display: 'inline-flex', padding: '12px', background: 'var(--accent-purple-glow)', borderRadius: '12px', marginBottom: '12px', color: 'var(--accent-purple)' }}>
              <TitanLogo size={60} className="pulse-glow" />
            </div>
            <h2 style={{ fontSize: '24px', color: '#fff', marginBottom: '8px' }}>Atlas Work Intelligence</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>AI-Powered Applicant Tracking System</p>
          </div>

          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {authError && (
              <div style={{ display: 'flex', gap: '8px', padding: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '8px', color: '#ef4444', fontSize: '14px' }}>
                <AlertCircle size={18} style={{ flexShrink: 0 }} />
                <span>{authError}</span>
              </div>
            )}

            <div>
              <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Email Address</label>
              <input 
                type="email" 
                required 
                className="input-field" 
                value={email} 
                onChange={e => setEmail(e.target.value)} 
                placeholder="recruiter@company.com" 
              />
            </div>

            <div>
              <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Password</label>
              <input 
                type="password" 
                required 
                className="input-field" 
                value={password} 
                onChange={e => setPassword(e.target.value)} 
                placeholder="••••••••" 
              />
            </div>

            {isRegister && (
              <>
                <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                  <button 
                    type="button" 
                    onClick={() => setIsJoinOrg(false)} 
                    className={!isJoinOrg ? 'btn-primary' : 'btn-secondary'} 
                    style={{ flex: 1, fontSize: '11px', padding: '6px', borderRadius: '15px' }}
                  >
                    New Organization
                  </button>
                  <button 
                    type="button" 
                    onClick={() => setIsJoinOrg(true)} 
                    className={isJoinOrg ? 'btn-primary' : 'btn-secondary'} 
                    style={{ flex: 1, fontSize: '11px', padding: '6px', borderRadius: '15px' }}
                  >
                    Join Team Code
                  </button>
                </div>

                {!isJoinOrg ? (
                  <div>
                    <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Organization Name</label>
                    <input 
                      type="text" 
                      required 
                      className="input-field" 
                      value={orgName} 
                      onChange={e => setOrgName(e.target.value)} 
                      placeholder="ACME Corp" 
                    />
                  </div>
                ) : (
                  <div>
                    <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Workspace Invite Code</label>
                    <input 
                      type="text" 
                      required 
                      className="input-field" 
                      value={inviteCode} 
                      onChange={e => setInviteCode(e.target.value)} 
                      placeholder="E.g., C9A4F3D0" 
                      style={{ fontFamily: 'monospace' }}
                    />
                  </div>
                )}
              </>
            )}

            <button type="submit" className="btn-primary" style={{ justifyContent: 'center', width: '100%', marginTop: '8px' }}>
              {isRegister ? 'Create Account' : 'Authenticate Credentials'}
            </button>

            <div style={{ display: 'flex', alignItems: 'center', margin: '16px 0', color: 'var(--text-dim)', fontSize: '11px' }}>
              <div style={{ flex: 1, height: '1px', background: 'var(--border-glass)' }}></div>
              <span style={{ padding: '0 10px', textTransform: 'uppercase', letterSpacing: '1px' }}>or</span>
              <div style={{ flex: 1, height: '1px', background: 'var(--border-glass)' }}></div>
            </div>

            <button 
              type="button" 
              onClick={() => setShowGoogleModal(true)} 
              className="btn-secondary" 
              style={{ width: '100%', justifyContent: 'center', gap: '8px', fontSize: '13px' }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Sign in with Google
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <button 
              type="button" 
              onClick={() => { setIsRegister(!isRegister); setAuthError(''); }}
              style={{ background: 'none', border: 'none', color: 'var(--accent-cyan)', cursor: 'pointer', fontSize: '13px' }}
            >
              {isRegister ? 'Already registered? Log in' : 'Request recruiter authorization credentials'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Choose mode screen right after login
  if (token && user && !selectedMode) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '16px' }}>
        {renderPreloader()}
        <div className="glass-panel animate-fade-in" style={{ width: '100%', maxWidth: '480px', padding: '36px', textAlign: 'center' }}>
          <div style={{ marginBottom: '28px' }}>
            <div style={{ display: 'inline-flex', padding: '12px', background: 'var(--accent-purple-glow)', borderRadius: '12px', marginBottom: '16px', color: 'var(--accent-purple)' }}>
              <Sparkles size={32} className="pulse-glow" />
            </div>
            <h2 style={{ fontSize: '24px', color: '#fff', marginBottom: '8px', fontWeight: 700 }}>Choose Your Path</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Welcome to Atlas Work Intelligence. Please select how you want to use the operating system today.</p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Mode: To Hire (Recruiter) */}
            <div 
              onClick={() => {
                setSelectedMode('hire');
                localStorage.setItem('atlas_mode', 'hire');
                setActiveTab('copilot');
              }}
              className="glass-panel" 
              style={{ 
                padding: '20px', 
                borderRadius: '12px', 
                cursor: 'pointer', 
                transition: 'all 0.3s ease', 
                textAlign: 'left', 
                border: '1px solid var(--border-glass)',
                background: 'rgba(255,255,255,0.01)'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = 'var(--accent-purple)';
                e.currentTarget.style.background = 'rgba(140,80,255,0.05)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = 'var(--border-glass)';
                e.currentTarget.style.background = 'rgba(255,255,255,0.01)';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                <div style={{ color: 'var(--accent-purple)' }}>
                  <Briefcase size={24} />
                </div>
                <h4 style={{ fontSize: '16px', color: '#fff', margin: 0, fontWeight: 600 }}>I want to Hire (Employer/Recruiter)</h4>
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: '12px', margin: 0, lineHeight: '1.4' }}>
                Access the recruiter portal, publish jobs, upload resumes, run semantic search and leverage Qwen3 matching engine.
              </p>
            </div>

            {/* Mode: For Hire (Candidate) */}
            <div 
              onClick={() => {
                setSelectedMode('for_hire');
                localStorage.setItem('atlas_mode', 'for_hire');
                setActiveTab('my_profile');
              }}
              className="glass-panel" 
              style={{ 
                padding: '20px', 
                borderRadius: '12px', 
                cursor: 'pointer', 
                transition: 'all 0.3s ease', 
                textAlign: 'left', 
                border: '1px solid var(--border-glass)',
                background: 'rgba(255,255,255,0.01)'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = 'var(--accent-cyan)';
                e.currentTarget.style.background = 'rgba(0,220,255,0.05)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = 'var(--border-glass)';
                e.currentTarget.style.background = 'rgba(255,255,255,0.01)';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                <div style={{ color: 'var(--accent-cyan)' }}>
                  <Users size={24} />
                </div>
                <h4 style={{ fontSize: '16px', color: '#fff', margin: 0, fontWeight: 600 }}>I am For Hire (Job Seeker/Candidate)</h4>
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: '12px', margin: 0, lineHeight: '1.4' }}>
                Upload your resume, verify your semantic score, view open roles, and prepare for interviews using ATLAS AI.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {renderPreloader()}
      {/* Top Header */}
      <header className="glass-panel" style={{ borderRadius: '0', borderLeft: 'none', borderRight: 'none', borderTop: 'none', padding: '16px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: '0', zIndex: 50 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <TitanLogo size={36} />
          <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#ffffff' }}>
            Atlas Work Intelligence
          </h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-muted)', padding: '6px 12px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-glass)', borderRadius: '20px' }}>
            {selectedMode === 'for_hire' ? 'Candidate Mode' : 'Recruiter Mode'}: {user.email}
          </span>
          <button 
            onClick={() => {
              setSelectedMode(null);
              localStorage.removeItem('atlas_mode');
            }} 
            className="btn-secondary" 
            style={{ padding: '8px 12px', fontSize: '12px' }}
          >
            <span>Switch Mode</span>
          </button>
          <button onClick={handleLogout} className="btn-secondary" style={{ padding: '8px 12px', fontSize: '12px' }}>
            <LogOut size={14} />
            <span>Sign Out</span>
          </button>
        </div>
      </header>

      {/* Tabs Switcher */}
      <div style={{ maxWidth: '1200px', width: '100%', margin: '24px auto 0 auto', padding: '0 16px' }}>
        <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '8px' }}>
          {selectedMode === 'for_hire' ? (
            <>
              <button 
                onClick={() => setActiveTab('my_profile')}
                className={activeTab === 'my_profile' ? 'btn-primary lining-candidates' : 'btn-secondary lining-candidates'} 
                style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
              >
                <Users size={16} /> My Profile
              </button>
              <button 
                onClick={() => setActiveTab('jobs_board')}
                className={activeTab === 'jobs_board' ? 'btn-primary lining-jobs' : 'btn-secondary lining-jobs'} 
                style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
              >
                <Briefcase size={16} /> Browse Jobs
              </button>
              <button 
                onClick={() => setActiveTab('copilot')}
                className={activeTab === 'copilot' ? 'btn-primary lining-copilot' : 'btn-secondary lining-copilot'} 
                style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
              >
                <MessageSquare size={16} /> Career Copilot
              </button>
              <button 
                onClick={() => {
                  setActiveTab('interview_prep');
                  setPrepJob(null);
                }}
                className={activeTab === 'interview_prep' ? 'btn-primary lining-copilot' : 'btn-secondary lining-copilot'} 
                style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
              >
                <Award size={16} /> Interview Prep Desk
              </button>
            </>
          ) : (
            <>
              <button 
                onClick={() => setActiveTab('copilot')}
                className={activeTab === 'copilot' ? 'btn-primary lining-copilot' : 'btn-secondary lining-copilot'} 
                style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
              >
                <MessageSquare size={16} /> Recruiter Copilot
              </button>
              <button 
                onClick={() => setActiveTab('candidates')}
                className={activeTab === 'candidates' ? 'btn-primary lining-candidates' : 'btn-secondary lining-candidates'} 
                style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
              >
                <Users size={16} /> Candidates
              </button>
              <button 
                onClick={() => setActiveTab('jobs')}
                className={activeTab === 'jobs' ? 'btn-primary lining-jobs' : 'btn-secondary lining-jobs'} 
                style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
              >
                <Briefcase size={16} /> Job Openings
              </button>
              <button 
                onClick={() => setActiveTab('search')}
                className={activeTab === 'search' ? 'btn-primary lining-search' : 'btn-secondary lining-search'} 
                style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
              >
                <Search size={16} /> Semantic Search
              </button>
              <button 
                onClick={() => setActiveTab('settings')}
                className={activeTab === 'settings' ? 'btn-primary lining-settings' : 'btn-secondary lining-settings'} 
                style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
              >
                <Settings size={16} /> Workspace Settings
              </button>
            </>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <main style={{ flex: 1, maxWidth: '1200px', width: '100%', margin: '0 auto', padding: '24px 16px' }}>

        {/* TAB: INTERVIEW PREP DESK */}
        {activeTab === 'interview_prep' && (
          <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ fontSize: '20px', color: '#fff', fontWeight: 600 }}>AI Interview Prep Desk</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '4px' }}>
                  Select an open job listing to trigger a simulated technical interview with Atlas AI.
                </p>
              </div>
              {prepJob && (
                <button 
                  onClick={() => setPrepJob(null)}
                  className="btn-secondary"
                  style={{ padding: '8px 16px', fontSize: '12px' }}
                >
                  Change Role
                </button>
              )}
            </div>

            {!prepJob ? (
              // Job Selector Grid
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
                {jobs.length === 0 ? (
                  <div className="glass-panel" style={{ gridColumn: '1/-1', padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No job listings available to prepare for. Ask a recruiter to publish a job.
                  </div>
                ) : (
                  jobs.map(job => (
                    <div key={job.id} className="glass-panel lining-jobs" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      <div>
                        <h3 style={{ fontSize: '16px', color: '#fff', fontWeight: 600 }}>{job.title}</h3>
                        <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginTop: '4px' }}>
                          📍 {job.location || 'Remote'} | 💰 {job.salary || 'Salary Undisclosed'}
                        </p>
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {job.required_skills.split(',').map((skill: string, idx: number) => (
                          <span key={idx} style={{ padding: '3px 8px', fontSize: '11px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-glass)', color: 'var(--text-muted)' }}>
                            {skill.trim()}
                          </span>
                        ))}
                      </div>
                      <button 
                        onClick={() => handleStartPrep(job)}
                        className="btn-primary lining-jobs"
                        style={{ width: '100%', justifyContent: 'center', marginTop: 'auto' }}
                      >
                        Start Mock Prep
                      </button>
                    </div>
                  ))
                )}
              </div>
            ) : (
              // Active Prep Area
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '24px', alignItems: 'start' }}>
                {/* Interview Interface */}
                <div className="glass-panel lining-copilot" style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
                  <div style={{ borderBottom: '1px solid var(--border-glass)', paddingBottom: '16px' }}>
                    <span style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--accent-orange)', fontWeight: 600 }}>Active Role</span>
                    <h3 style={{ fontSize: '18px', color: '#fff', marginTop: '4px' }}>{prepJob.title} Mock Interview</h3>
                  </div>

                  {prepLoading ? (
                    <div style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
                      <div className="pulse-glow" style={{ fontSize: '14px' }}>Atlas AI is reviewing response and drafting next question...</div>
                    </div>
                  ) : (
                    <>
                      <div style={{ background: 'rgba(255,255,255,0.01)', padding: '20px', borderRadius: '4px', borderLeft: '3px solid var(--accent-orange)' }}>
                        <span style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Question</span>
                        <p style={{ fontSize: '15px', color: '#fff', marginTop: '6px', lineHeight: '1.5' }}>{prepQuestion}</p>
                      </div>

                      <form onSubmit={handleSubmitPrepAnswer} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Your Answer</label>
                        <textarea 
                          required
                          rows={6}
                          className="input-field"
                          placeholder="Type your technical response here. Try to explain the concepts and list details..."
                          value={prepAnswer}
                          onChange={e => setPrepAnswer(e.target.value)}
                          style={{ resize: 'vertical', minHeight: '120px', background: 'rgba(255,255,255,0.01)' }}
                        />
                        <button 
                          type="submit"
                          className="btn-primary lining-copilot"
                          style={{ alignSelf: 'flex-end', marginTop: '8px' }}
                        >
                          Submit Answer
                        </button>
                      </form>
                    </>
                  )}
                </div>

                {/* Score & Feedback Logs */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <div className="glass-panel" style={{ padding: '24px' }}>
                    <h4 style={{ fontSize: '13px', color: '#fff', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>Prep Progress</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Questions Answered</span>
                        <span style={{ color: '#fff', fontWeight: 600 }}>{prepHistory.length}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Average Rating</span>
                        <span style={{ color: 'var(--accent-orange)', fontWeight: 600 }}>
                          {prepHistory.length > 0 
                            ? (prepHistory.reduce((acc, curr) => acc + (parseFloat(curr.score) || 0), 0) / prepHistory.length).toFixed(1) + " / 10"
                            : "N/A"
                          }
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px', maxHeight: '420px', overflowY: 'auto' }}>
                    <h4 style={{ fontSize: '13px', color: '#fff', textTransform: 'uppercase', letterSpacing: '0.05em' }}>History Log</h4>
                    {prepHistory.length === 0 ? (
                      <p style={{ color: 'var(--text-dim)', fontSize: '12px', textAlign: 'center', padding: '16px 0' }}>No responses graded yet.</p>
                    ) : (
                      prepHistory.map((item, idx) => (
                        <div key={idx} style={{ borderBottom: idx < prepHistory.length - 1 ? '1px solid var(--border-glass)' : 'none', paddingBottom: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Round {prepHistory.length - idx}</span>
                            <span style={{ fontSize: '11px', color: 'var(--accent-orange)', background: 'rgba(255, 45, 85, 0.05)', padding: '2px 8px', borderRadius: '12px', fontWeight: 600 }}>
                              {item.score}
                            </span>
                          </div>
                          <p style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic' }}>Q: {item.question}</p>
                          <p style={{ fontSize: '12px', color: '#fff' }}>A: {item.answer}</p>
                          <p style={{ fontSize: '11px', color: '#84cc16', background: 'rgba(132, 204, 22, 0.03)', padding: '8px', borderLeft: '2px solid #84cc16' }}>
                            {item.feedback}
                          </p>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB: MY PROFILE (CANDIDATE) */}
        {activeTab === 'my_profile' && (
          <div className="animate-fade-in">
            {myCandidateProfile ? (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '24px', alignItems: 'start' }}>
                {/* Main Profile Info */}
                <div className="glass-panel lining-candidates" style={{ padding: '32px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '24px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '20px' }}>
                    <div>
                      <h2 style={{ fontSize: '24px', color: '#fff', marginBottom: '4px' }}>{myCandidateProfile.name}</h2>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '13px', color: 'var(--text-muted)', marginTop: '8px' }}>
                        <span>📧 {myCandidateProfile.email}</span>
                        {myCandidateProfile.phone && <span>📞 {myCandidateProfile.phone}</span>}
                        {myCandidateProfile.location && <span>📍 {myCandidateProfile.location}</span>}
                      </div>
                    </div>
                    <div>
                      <input 
                        type="file" 
                        ref={fileInputRef} 
                        style={{ display: 'none' }} 
                        accept=".pdf,.docx,.txt"
                        onChange={handleResumeUpload}
                      />
                      <button 
                        onClick={() => fileInputRef.current?.click()} 
                        disabled={uploading}
                        className="btn-secondary lining-candidates"
                        style={{ fontSize: '12px', padding: '8px 16px' }}
                      >
                        <UploadCloud size={14} />
                        <span>Update Resume</span>
                      </button>
                    </div>
                  </div>

                  {uploading && (
                    <div className="pulse-glow" style={{ padding: '12px 16px', background: 'var(--accent-purple-glow)', border: '1px solid rgba(140,80,255,0.3)', borderRadius: '8px', marginBottom: '20px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Sparkles size={16} style={{ color: 'var(--accent-purple)' }} />
                      <span>{uploadStatus}</span>
                    </div>
                  )}

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    {myCandidateProfile.summary && (
                      <div>
                        <h4 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '8px', letterSpacing: '0.05em' }}>AI Professional Summary</h4>
                        <p style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: '1.6' }}>{myCandidateProfile.summary}</p>
                      </div>
                    )}

                    <div>
                      <h4 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '8px', letterSpacing: '0.05em' }}>Extracted Skills</h4>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {myCandidateProfile.skills.map((s: string, idx: number) => (
                          <span key={idx} style={{ padding: '4px 10px', fontSize: '12px', background: 'var(--accent-purple-glow)', border: '1px solid rgba(140,80,255,0.2)', borderRadius: '6px', color: 'var(--text-main)' }}>
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>

                    {myCandidateProfile.experience && myCandidateProfile.experience.length > 0 && (
                      <div>
                        <h4 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '12px', letterSpacing: '0.05em' }}>Work Experience</h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                          {myCandidateProfile.experience.map((exp: any, idx: number) => (
                            <div key={idx} style={{ fontSize: '13px', paddingLeft: '12px', borderLeft: '2px solid var(--border-glass)' }}>
                              <strong style={{ color: '#fff', fontSize: '15px' }}>{exp.role || 'Developer'}</strong> <span style={{ color: 'var(--text-muted)' }}>at {exp.company || 'Company'}</span>
                              <div style={{ color: 'var(--text-dim)', fontSize: '11px', margin: '4px 0' }}>{exp.duration}</div>
                              <p style={{ color: 'var(--text-muted)', marginTop: '6px', lineHeight: '1.5' }}>{exp.description}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {myCandidateProfile.education && myCandidateProfile.education.length > 0 && (
                      <div>
                        <h4 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '12px', letterSpacing: '0.05em' }}>Education</h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                          {myCandidateProfile.education.map((edu: any, idx: number) => (
                            <div key={idx} style={{ fontSize: '13px' }}>
                              <strong style={{ color: '#fff' }}>{edu.degree || 'Degree'}</strong> <span style={{ color: 'var(--text-muted)' }}>- {edu.institution || 'University'}</span>
                              <span style={{ color: 'var(--text-dim)', fontSize: '11px', marginLeft: '6px' }}>({edu.year})</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Right side Career Score card */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <div className="glass-panel" style={{ padding: '24px', textAlign: 'center' }}>
                    <span style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--accent-cyan)', fontWeight: 600 }}>ATLAS Identity Score</span>
                    <div style={{ margin: '20px 0', position: 'relative', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>
                      <div className="pulse-glow" style={{ width: '100px', height: '100px', borderRadius: '50%', background: 'rgba(0, 220, 255, 0.05)', border: '2px solid var(--accent-cyan)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                        <span style={{ fontSize: '28px', fontWeight: 800, color: '#fff' }}>
                          {myCandidateProfile.ai_score ? Math.round(myCandidateProfile.ai_score * 100) : 85}%
                        </span>
                        <span style={{ fontSize: '9px', color: 'var(--text-dim)' }}>FIT SCORE</span>
                      </div>
                    </div>
                    <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                      This profile is fully parsed, indexed, and available for recruiter semantic search queries across the org space.
                    </p>
                  </div>

                  <div className="glass-panel" style={{ padding: '24px' }}>
                    <h4 style={{ fontSize: '14px', color: '#fff', marginBottom: '12px' }}>Profile Completeness</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '12px', color: 'var(--text-muted)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Resume Parsed</span>
                        <span style={{ color: 'var(--accent-green)' }}>✓ Complete</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Skills Tagged</span>
                        <span style={{ color: 'var(--accent-green)' }}>{myCandidateProfile.skills.length} tagged</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Work Experience</span>
                        <span style={{ color: 'var(--accent-green)' }}>{myCandidateProfile.experience?.length || 0} items</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="glass-panel lining-candidates animate-fade-in" style={{ padding: '48px', textAlign: 'center', maxWidth: '600px', margin: '40px auto' }}>
                <UploadCloud size={64} style={{ margin: '0 auto 20px auto', color: 'var(--accent-cyan)', opacity: 0.8 }} />
                <h3 style={{ fontSize: '20px', color: '#fff', marginBottom: '12px' }}>Complete Your Candidate Profile</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '14px', marginBottom: '24px', lineHeight: '1.5' }}>
                  Please upload your resume file (.pdf, .docx, or .txt). The ATLAS AI pipeline will parse your skills and experience to unlock job match scoring.
                </p>

                <input 
                  type="file" 
                  ref={fileInputRef} 
                  style={{ display: 'none' }} 
                  accept=".pdf,.docx,.txt"
                  onChange={handleResumeUpload}
                />
                
                <button 
                  onClick={() => fileInputRef.current?.click()} 
                  disabled={uploading}
                  className="btn-primary lining-candidates"
                  style={{ padding: '12px 32px' }}
                >
                  <UploadCloud size={16} />
                  {uploading ? 'Processing resume...' : 'Upload Resume file'}
                </button>

                {uploading && (
                  <div className="pulse-glow" style={{ marginTop: '24px', padding: '12px', background: 'var(--accent-purple-glow)', borderRadius: '8px', fontSize: '13px', color: '#fff' }}>
                    {uploadStatus}
                  </div>
                )}
                {uploadError && (
                  <div style={{ marginTop: '24px', padding: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '8px', fontSize: '13px', color: '#ef4444' }}>
                    {uploadError}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB: BROWSE JOBS (CANDIDATE) */}
        {activeTab === 'jobs_board' && (
          <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '24px', alignItems: 'start', animation: 'fadeInUp 0.4s ease-out' }}>
            {/* Left Side: Jobs List */}
            <div className="glass-panel lining-jobs" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '18px', color: '#fff', marginBottom: '16px' }}>Open Positions</h3>
              {jobs.length === 0 ? (
                <div style={{ color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center', padding: '24px 0' }}>
                  No published job listings.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {jobs.map(j => {
                    // Compute basic match score if profile exists
                    let matchScore = 0;
                    if (myCandidateProfile && j.required_skills?.length > 0) {
                      const candidateSkills = new Set(myCandidateProfile.skills.map((s: string) => s.toLowerCase()));
                      const matches = j.required_skills.filter((s: string) => candidateSkills.has(s.toLowerCase()));
                      matchScore = Math.round((matches.length / j.required_skills.length) * 100);
                    } else if (myCandidateProfile) {
                      matchScore = 100;
                    }
                    
                    return (
                      <div 
                        key={j.id}
                        onClick={() => { setSelectedJob(j); setAppliedJobId(null); }}
                        style={{ 
                          padding: '16px', 
                          background: selectedJob?.id === j.id ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.01)',
                          border: '1px solid', 
                          borderColor: selectedJob?.id === j.id ? 'var(--accent-orange)' : 'var(--border-glass)',
                          borderRadius: '12px', 
                          cursor: 'pointer', 
                          transition: 'var(--transition-fast)'
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: '8px' }}>
                          <h4 style={{ fontSize: '15px', color: '#fff', marginBottom: '4px', flex: 1 }}>{j.title}</h4>
                          {myCandidateProfile && (
                            <span style={{ 
                              padding: '2px 6px', 
                              fontSize: '10px', 
                              borderRadius: '8px', 
                              fontWeight: 600,
                              background: matchScore >= 75 ? 'rgba(34, 197, 94, 0.15)' : matchScore >= 50 ? 'rgba(249, 115, 22, 0.15)' : 'rgba(255,255,255,0.05)',
                              color: matchScore >= 75 ? '#22c55e' : matchScore >= 50 ? '#f97316' : 'var(--text-muted)',
                              border: matchScore >= 75 ? '1px solid rgba(34, 197, 94, 0.3)' : matchScore >= 50 ? '1px solid rgba(249, 115, 22, 0.3)' : '1px solid var(--border-glass)'
                            }}>
                              {matchScore}% Match
                            </span>
                          )}
                        </div>
                        <div style={{ display: 'flex', gap: '12px', fontSize: '11px', color: 'var(--text-muted)', marginTop: '6px' }}>
                          <span>📍 {j.location || 'Remote'}</span>
                          <span>💰 {j.salary || 'N/A'}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Right Side: Selected Job Details */}
            <div className="glass-panel" style={{ padding: '32px', minHeight: '400px' }}>
              {selectedJob ? (
                <div>
                  <div style={{ borderBottom: '1px solid var(--border-glass)', paddingBottom: '20px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                    <div>
                      <h3 style={{ fontSize: '22px', color: '#fff', fontWeight: 700 }}>{selectedJob.title}</h3>
                      <div style={{ display: 'flex', gap: '16px', fontSize: '13px', color: 'var(--text-muted)', marginTop: '8px' }}>
                        <span>📍 {selectedJob.location || 'Remote'}</span>
                        <span>💰 {selectedJob.salary || 'N/A'}</span>
                        <span>💼 {selectedJob.employment_type || 'Full-time'}</span>
                        <span>⏳ Exp: {selectedJob.experience_years} years</span>
                      </div>
                    </div>
                    
                    <div>
                      {appliedJobId === selectedJob.id ? (
                        <span style={{ padding: '8px 16px', fontSize: '13px', background: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.2)', borderRadius: '6px', color: '#22c55e', fontWeight: 600, display: 'inline-block' }}>
                          ✓ Applied
                        </span>
                      ) : (
                        <button 
                          onClick={() => setAppliedJobId(selectedJob.id)} 
                          className="btn-primary lining-jobs"
                          style={{ padding: '8px 20px', fontSize: '13px' }}
                        >
                          Apply Now
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Skills match summary card */}
                  {myCandidateProfile && (
                    <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px', background: 'rgba(255,255,255,0.01)' }}>
                      <h4 style={{ fontSize: '13px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '12px' }}>Skills Match Analysis</h4>
                      
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <div>
                          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Skills In Common:</div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                            {selectedJob.required_skills.filter((s: string) => myCandidateProfile.skills.map((cs: string) => cs.toLowerCase()).includes(s.toLowerCase())).map((s: string, idx: number) => (
                              <span key={idx} style={{ padding: '2px 8px', fontSize: '11px', background: 'rgba(34, 197, 94, 0.15)', border: '1px solid rgba(34, 197, 94, 0.3)', borderRadius: '4px', color: '#22c55e' }}>
                                {s}
                              </span>
                            ))}
                            {selectedJob.required_skills.filter((s: string) => myCandidateProfile.skills.map((cs: string) => cs.toLowerCase()).includes(s.toLowerCase())).length === 0 && (
                              <span style={{ fontSize: '12px', color: 'var(--text-dim)', fontStyle: 'italic' }}>None</span>
                            )}
                          </div>
                        </div>

                        <div>
                          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Skills Missing from your Profile:</div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                            {selectedJob.required_skills.filter((s: string) => !myCandidateProfile.skills.map((cs: string) => cs.toLowerCase()).includes(s.toLowerCase())).map((s: string, idx: number) => (
                              <span key={idx} style={{ padding: '2px 8px', fontSize: '11px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-glass)', borderRadius: '4px', color: 'var(--text-muted)' }}>
                                {s}
                              </span>
                            ))}
                            {selectedJob.required_skills.filter((s: string) => !myCandidateProfile.skills.map((cs: string) => cs.toLowerCase()).includes(s.toLowerCase())).length === 0 && (
                              <span style={{ fontSize: '12px', color: 'var(--accent-green)', fontStyle: 'italic' }}>None! You match all required skills!</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div>
                      <h4 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '8px' }}>Job Description</h4>
                      <p style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                        {selectedJob.description}
                      </p>
                    </div>

                    {selectedJob.required_skills?.length > 0 && (
                      <div>
                        <h4 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '8px' }}>Required Skills</h4>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                          {selectedJob.required_skills.map((s: string, idx: number) => (
                            <span key={idx} style={{ padding: '4px 10px', fontSize: '12px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-glass)', borderRadius: '6px', color: 'var(--text-muted)' }}>
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '350px', color: 'var(--text-dim)' }}>
                  <Briefcase size={48} style={{ opacity: 0.5, marginBottom: '16px' }} />
                  <p>Select a job from the sidebar to review the description, analyze your skills match, and submit an application.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 1: CANDIDATES */}
        {activeTab === 'candidates' && (
          <div style={{ display: 'grid', gridTemplateColumns: selectedCandidate ? '1fr 400px' : '1fr', gap: '24px', alignItems: 'start' }}>
            <div className="glass-panel lining-candidates animate-fade-in" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                  <h2 style={{ fontSize: '20px', color: '#fff', marginBottom: '4px' }}>Candidate Profiles</h2>
                  <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Upload resumes to extract structured candidate details via phi4-mini.</p>
                </div>
                
                {/* Upload Button */}
                <div>
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    style={{ display: 'none' }} 
                    accept=".pdf,.docx,.txt"
                    onChange={handleResumeUpload}
                  />
                  <button 
                    onClick={() => fileInputRef.current?.click()} 
                    disabled={uploading}
                    className="btn-primary lining-candidates"
                  >
                    <UploadCloud size={16} />
                    {uploading ? 'Processing...' : 'Upload Resume'}
                  </button>
                </div>
              </div>

              {/* Status and Error banners */}
              {uploading && (
                <div className="pulse-glow" style={{ padding: '12px 16px', background: 'var(--accent-purple-glow)', border: '1px solid rgba(140,80,255,0.3)', borderRadius: '8px', marginBottom: '16px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Sparkles size={16} style={{ color: 'var(--accent-purple)' }} />
                  <span>{uploadStatus}</span>
                </div>
              )}
              {uploadError && (
                <div style={{ padding: '12px 16px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '8px', marginBottom: '16px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px', color: '#ef4444' }}>
                  <AlertCircle size={16} />
                  <span>{uploadError}</span>
                </div>
              )}

              {/* Candidates List */}
              {candidates.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '48px 16px', color: 'var(--text-dim)' }}>
                  <UploadCloud size={48} style={{ margin: '0 auto 16px auto', opacity: 0.5 }} />
                  <p style={{ fontSize: '15px' }}>No candidate profiles found. Click "Upload Resume" to begin parsing.</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {candidates.map(c => (
                    <div 
                      key={c.id} 
                      onClick={() => setSelectedCandidate(c)}
                      style={{ 
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center', 
                        padding: '16px', background: selectedCandidate?.id === c.id ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.01)',
                        border: '1px solid', borderColor: selectedCandidate?.id === c.id ? 'var(--accent-purple)' : 'var(--border-glass)',
                        borderRadius: '12px', cursor: 'pointer', transition: 'var(--transition-fast)'
                      }}
                    >
                      <div>
                        <h4 style={{ fontSize: '16px', color: '#fff', marginBottom: '4px' }}>{c.name}</h4>
                        <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: 'var(--text-muted)' }}>
                          <span>{c.email || 'No Email'}</span>
                          <span>{c.location || 'No Location'}</span>
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', maxWidth: '300px' }}>
                          {c.skills.slice(0, 3).map((s: string, idx: number) => (
                            <span key={idx} style={{ padding: '2px 8px', fontSize: '10px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', color: 'var(--text-muted)' }}>
                              {s}
                            </span>
                          ))}
                          {c.skills.length > 3 && <span style={{ fontSize: '10px', color: 'var(--text-dim)' }}>+{c.skills.length - 3} more</span>}
                        </div>
                        <button 
                          onClick={(e) => { e.stopPropagation(); handleDeleteCandidate(c.id); }}
                          style={{ background: 'none', border: 'none', color: 'rgba(239, 68, 68, 0.7)', cursor: 'pointer', padding: '4px' }}
                          title="Delete candidate profile"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Sidebar Candidate Details Panel */}
            {selectedCandidate && (
              <div className="glass-panel lining-candidates animate-fade-in" style={{ padding: '24px', borderLeft: '1px solid var(--border-glass)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '20px' }}>
                  <div>
                    <h3 style={{ fontSize: '18px', color: '#fff', marginBottom: '4px' }}>{selectedCandidate.name}</h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Profile details extracted via AI</p>
                  </div>
                  <button onClick={() => setSelectedCandidate(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                    <X size={18} />
                  </button>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  {selectedCandidate.summary && (
                    <div>
                      <h5 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '6px' }}>Professional Summary</h5>
                      <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.5' }}>{selectedCandidate.summary}</p>
                    </div>
                  )}

                  <div>
                    <h5 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '6px' }}>Core Skills</h5>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {selectedCandidate.skills.map((s: string, idx: number) => (
                        <span key={idx} style={{ padding: '4px 8px', fontSize: '11px', background: 'var(--accent-purple-glow)', border: '1px solid rgba(140,80,255,0.2)', borderRadius: '6px', color: 'var(--text-main)' }}>
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  {selectedCandidate.experience && selectedCandidate.experience.length > 0 && (
                    <div>
                      <h5 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '6px' }}>Professional Experience</h5>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {selectedCandidate.experience.map((exp: any, idx: number) => (
                          <div key={idx} style={{ fontSize: '12px', paddingLeft: '8px', borderLeft: '2px solid var(--border-glass)' }}>
                            <strong style={{ color: '#fff' }}>{exp.role || 'Developer'}</strong> at <span>{exp.company || 'Company'}</span>
                            <div style={{ color: 'var(--text-dim)', fontSize: '10px', margin: '2px 0' }}>{exp.duration}</div>
                            <p style={{ color: 'var(--text-muted)', marginTop: '4px' }}>{exp.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedCandidate.education && selectedCandidate.education.length > 0 && (
                    <div>
                      <h5 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '6px' }}>Education</h5>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {selectedCandidate.education.map((edu: any, idx: number) => (
                          <div key={idx} style={{ fontSize: '12px' }}>
                            <strong style={{ color: '#fff' }}>{edu.degree || 'Degree'}</strong> - <span>{edu.institution || 'University'}</span>
                            <span style={{ color: 'var(--text-dim)', fontSize: '11px', marginLeft: '6px' }}>({edu.year})</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: JOBS BOARD & RECOMMENDATIONS */}
        {activeTab === 'jobs' && (
          <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '24px', alignItems: 'start' }}>
            
            {/* Left Side Jobs List */}
            <div className="glass-panel lining-jobs animate-fade-in" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ fontSize: '18px', color: '#fff' }}>Job Postings</h2>
                <button 
                  onClick={() => setShowCreateJob(!showCreateJob)}
                  className="btn-primary lining-jobs" 
                  style={{ padding: '8px 12px', fontSize: '12px' }}
                >
                  <Plus size={14} /> Create Job
                </button>
              </div>

              {/* Create Job Form Overlay/Drawer */}
              {showCreateJob && (
                <form onSubmit={handleCreateJob} style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '12px', padding: '16px', marginBottom: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <h4 style={{ fontSize: '14px', color: '#fff' }}>New Job Spec</h4>
                  
                  <div>
                    <input 
                      type="text" 
                      required 
                      className="input-field" 
                      placeholder="Title (e.g., Python Lead)" 
                      value={newJob.title}
                      onChange={e => setNewJob({...newJob, title: e.target.value})}
                    />
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                    <input 
                      type="text" 
                      className="input-field" 
                      placeholder="Location (e.g. Remote)" 
                      value={newJob.location}
                      onChange={e => setNewJob({...newJob, location: e.target.value})}
                    />
                    <input 
                      type="text" 
                      className="input-field" 
                      placeholder="Salary (e.g. $120k)" 
                      value={newJob.salary}
                      onChange={e => setNewJob({...newJob, salary: e.target.value})}
                    />
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                    <input 
                      type="number" 
                      className="input-field" 
                      placeholder="Experience Yrs" 
                      value={newJob.experience_years}
                      onChange={e => setNewJob({...newJob, experience_years: parseInt(e.target.value) || 0})}
                    />
                    <select 
                      className="input-field"
                      value={newJob.employment_type}
                      onChange={e => setNewJob({...newJob, employment_type: e.target.value})}
                      style={{ background: 'rgba(0,0,0,0.5)' }}
                    >
                      <option value="Full-time">Full-time</option>
                      <option value="Part-time">Part-time</option>
                      <option value="Contract">Contract</option>
                    </select>
                  </div>

                  <div>
                    <input 
                      type="text" 
                      required
                      className="input-field" 
                      placeholder="Skills comma separated (e.g. Python, SQL)" 
                      value={newJob.required_skills}
                      onChange={e => setNewJob({...newJob, required_skills: e.target.value})}
                    />
                  </div>

                  <div>
                    <textarea 
                      required
                      className="input-field" 
                      placeholder="Job description details..." 
                      rows={3}
                      value={newJob.description}
                      onChange={e => setNewJob({...newJob, description: e.target.value})}
                      style={{ resize: 'none' }}
                    />
                  </div>

                  <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                    <button type="button" onClick={() => setShowCreateJob(false)} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }}>Cancel</button>
                    <button type="submit" className="btn-primary" style={{ padding: '6px 12px', fontSize: '12px' }}>Publish</button>
                  </div>
                </form>
              )}

              {/* Jobs List */}
              {jobs.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '32px 0', color: 'var(--text-dim)', fontSize: '13px' }}>
                  No published job listings.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {jobs.map(j => (
                    <div 
                      key={j.id}
                      onClick={() => handleSelectJob(j)}
                      style={{ 
                        padding: '16px', background: selectedJob?.id === j.id ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.01)',
                        border: '1px solid', borderColor: selectedJob?.id === j.id ? 'var(--accent-purple)' : 'var(--border-glass)',
                        borderRadius: '12px', cursor: 'pointer', transition: 'var(--transition-fast)'
                      }}
                    >
                      <h4 style={{ fontSize: '15px', color: '#fff', marginBottom: '4px' }}>{j.title}</h4>
                      <div style={{ display: 'flex', gap: '12px', fontSize: '11px', color: 'var(--text-muted)' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '2px' }}><MapPin size={10} /> {j.location || 'Remote'}</span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '2px' }}><DollarSign size={10} /> {j.salary || 'N/A'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Right Side Candidates Matching Recommendations Panel */}
            <div className="glass-panel animate-fade-in" style={{ padding: '24px', minHeight: '400px' }}>
              {selectedJob ? (
                <div>
                  <div style={{ borderBottom: '1px solid var(--border-glass)', paddingBottom: '16px', marginBottom: '20px' }}>
                    <span style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--accent-cyan)', fontWeight: 600 }}>Semantic Matching Engine</span>
                    <h3 style={{ fontSize: '20px', color: '#fff', marginTop: '4px' }}>Fit Recommendations for: {selectedJob.title}</h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '6px' }}>{selectedJob.description}</p>
                  </div>

                  {loadingRecommendations ? (
                    <div style={{ textAlign: 'center', padding: '64px 0', color: 'var(--text-muted)' }}>
                      <Sparkles size={32} className="pulse-glow" style={{ margin: '0 auto 16px auto', color: 'var(--accent-purple)' }} />
                      <p style={{ fontSize: '14px' }}>Calculating vector similarity and querying Qwen3 explanation...</p>
                    </div>
                  ) : recommendations.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '64px 0', color: 'var(--text-dim)', fontSize: '14px' }}>
                      No candidate vectors found. Upload resume files first to run matching models.
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {recommendations.map((rec, index) => (
                        <div key={index} className="glass-panel" style={{ padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div style={{ flex: 1, paddingRight: '20px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                              <h4 style={{ fontSize: '16px', color: '#fff' }}>{rec.candidate.name}</h4>
                              <span style={{ padding: '2px 8px', fontSize: '10px', background: 'rgba(0, 220, 255, 0.15)', border: '1px solid rgba(0, 220, 255, 0.3)', borderRadius: '12px', color: 'var(--accent-cyan)' }}>
                                Rank #{index + 1}
                              </span>
                            </div>
                            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px', lineClamp: 2, WebkitLineClamp: 2, display: '-webkit-box', WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                              {rec.candidate.summary}
                            </p>
                            
                            {/* Skills overlaps */}
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                              {rec.candidate.skills.slice(0, 5).map((s: string, idx: number) => {
                                const isOverlap = selectedJob.required_skills.map((rs: string) => rs.toLowerCase()).includes(s.toLowerCase());
                                return (
                                  <span key={idx} style={{ padding: '2px 8px', fontSize: '9px', borderRadius: '4px', background: isOverlap ? 'rgba(34, 197, 94, 0.15)' : 'rgba(255,255,255,0.03)', border: isOverlap ? '1px solid rgba(34, 197, 94, 0.3)' : '1px solid var(--border-glass)', color: isOverlap ? 'hsl(145, 80%, 45%)' : 'var(--text-muted)' }}>
                                    {s}
                                  </span>
                                );
                              })}
                            </div>
                          </div>

                          {/* Scores & Explanation Button */}
                          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', minWidth: '150px' }}>
                            <div style={{ textAlign: 'right', width: '100%', marginBottom: '4px' }}>
                              <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>Semantic Match Score</div>
                              <div style={{ fontSize: '18px', color: 'var(--accent-purple)', fontWeight: 700 }}>
                                {(rec.similarity_score * 100).toFixed(1)}%
                              </div>
                              <div style={{ fontSize: '10px', color: 'var(--text-dim)' }}>Skills Overlap: {Math.round(rec.skills_match_ratio * 100)}%</div>
                            </div>
                            
                            <button 
                              onClick={() => setRecExplanation({ candidate: rec.candidate.name, text: rec.explanation })}
                              className="btn-secondary" 
                              style={{ padding: '6px 12px', fontSize: '11px', width: '100%', justifyContent: 'center' }}
                            >
                              <Award size={12} /> Explain Fit
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '128px 0', color: 'var(--text-dim)' }}>
                  <Briefcase size={48} style={{ margin: '0 auto 16px auto', opacity: 0.5 }} />
                  <p>Select a job listing from the sidebar to calculate candidate recommendations matching.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: SEMANTIC SEARCH */}
        {activeTab === 'search' && (
          <div className="glass-panel animate-fade-in" style={{ padding: '24px' }}>
            <div style={{ marginBottom: '24px' }}>
              <h2 style={{ fontSize: '20px', color: '#fff', marginBottom: '4px' }}>Natural Language Candidate Search</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Find candidates semantically matching arbitrary descriptive terms (e.g. "React developer with cloud experience in location New York").</p>
            </div>

            <form onSubmit={handleSemanticSearch} style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
              <input 
                type="text" 
                required 
                className="input-field" 
                placeholder="Type profile search query..." 
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
              <button type="submit" disabled={searching} className="btn-primary">
                <Search size={16} />
                {searching ? 'Querying...' : 'Search'}
              </button>
            </form>

            {searching ? (
              <div style={{ textAlign: 'center', padding: '64px 0', color: 'var(--text-muted)' }}>
                <Sparkles size={32} className="pulse-glow" style={{ margin: '0 auto 16px auto', color: 'var(--accent-purple)' }} />
                <p>Generating query embedding vector...</p>
              </div>
            ) : searchResults.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '64px 0', color: 'var(--text-dim)', fontSize: '14px' }}>
                {searchQuery ? 'No match results found.' : 'Enter a query string above to scan FAISS vector store candidates.'}
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {searchResults.map((res, index) => (
                  <div key={index} className="glass-panel" style={{ padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h4 style={{ fontSize: '16px', color: '#fff', marginBottom: '4px' }}>{res.candidate.name}</h4>
                      <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>{res.candidate.summary}</p>
                      <div style={{ display: 'flex', gap: '6px' }}>
                        {res.candidate.skills.slice(0, 6).map((s: string, idx: number) => (
                          <span key={idx} style={{ padding: '2px 6px', fontSize: '9px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-glass)', borderRadius: '4px', color: 'var(--text-muted)' }}>
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right', minWidth: '120px' }}>
                      <div style={{ fontSize: '10px', color: 'var(--text-dim)' }}>Vector Cosine Sim</div>
                      <div style={{ fontSize: '18px', color: 'var(--accent-cyan)', fontWeight: 700 }}>
                        {(res.similarity_score * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 4: RECRUITER COPILOT CHAT */}
        {activeTab === 'copilot' && (
          <div className="glass-panel lining-copilot animate-fade-in" style={{ padding: '24px', display: 'flex', flexDirection: 'column', minHeight: '600px', gap: '16px' }}>
            
            {/* Minimalist Prompt Desk Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <TitanLogo size={24} />
                <span style={{ fontSize: '15px', fontWeight: 600, color: '#fff' }}>Atlas Work Intelligence Prompt Desk</span>
              </div>
              <button 
                onClick={handleClearChatHistory} 
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '11px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', padding: '4px 8px', borderRadius: '4px', transition: 'var(--transition-smooth)' }}
                onMouseOver={e => e.currentTarget.style.color = '#fff'}
                onMouseOut={e => e.currentTarget.style.color = 'var(--text-muted)'}
              >
                <Trash2 size={12} /> Clear Desk
              </button>
            </div>

            {/* Chat Box */}
            <div style={{ display: 'flex', flexDirection: 'column', flex: 1, height: '100%' }}>
              {/* Message History logs */}
              <div style={{ flex: 1, overflowY: 'auto', padding: '16px', background: 'rgba(0,0,0,0.1)', borderRadius: '12px', display: 'flex', flexDirection: 'column', gap: '16px', minHeight: '400px', maxHeight: '450px' }}>
                {chatHistory.length === 0 && (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', textAlign: 'center', padding: '48px 16px', gap: '16px', flex: 1 }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#fff', letterSpacing: '-0.02em' }}>
                      {selectedMode === 'for_hire' ? 'Hello. How can Atlas Career Copilot help you today?' : 'Hello. How can Atlas Work Intelligence help build your team today?'}
                    </h2>
                    <p style={{ color: 'var(--text-dim)', fontSize: '13px', maxWidth: '440px', lineHeight: '1.5' }}>
                      {selectedMode === 'for_hire' ? 
                        'Ask questions about open job specs, see what skills you are missing, or get advice on preparing for interviews within the workspace.' :
                        'Just tell me what candidate profile you are looking for. I will draft the ideal target resume summary and find matching talent in your database.'
                      }
                    </p>
                    <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.2)', fontStyle: 'italic' }}>
                      {selectedMode === 'for_hire' ?
                        'Example: "What are the required skills for the Python Lead job?"' :
                        'Example: "Find me a senior React engineer who knows Docker and AWS"'
                      }
                    </span>
                  </div>
                )}

                {chatHistory.map((msg, idx) => (
                  <div 
                    key={idx} 
                    style={{ 
                      alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      maxWidth: '80%',
                      background: msg.role === 'user' ? 'var(--accent-purple)' : 'rgba(255,255,255,0.04)',
                      border: msg.role === 'user' ? 'none' : '1px solid var(--border-glass)',
                      borderRadius: '12px',
                      padding: '12px 16px',
                      fontSize: '13px',
                      lineHeight: '1.5',
                      color: '#fff',
                      whiteSpace: 'pre-wrap'
                    }}
                  >
                    <strong>{msg.role === 'user' ? 'You' : 'ATLAS Copilot'}</strong>
                    <div style={{ marginTop: '4px' }}>{msg.content}</div>
                  </div>
                ))}
                
                {chatLoading && (
                  <div style={{ alignSelf: 'flex-start', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '12px', padding: '12px 16px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Sparkles size={14} className="pulse-glow" style={{ color: 'var(--accent-purple)' }} />
                    <span style={{ color: 'var(--text-muted)' }}>Copilot is thinking...</span>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Chat Input form */}
              <form onSubmit={handleSendChatMessage} style={{ display: 'flex', gap: '8px', marginTop: '16px', alignItems: 'center' }}>
                <input 
                  type="text" 
                  required 
                  className="input-field lining-copilot" 
                  placeholder={isListening ? "Listening... Speak clearly..." : "Ask a question about candidates or jobs..."} 
                  value={chatQuery}
                  onChange={e => setChatQuery(e.target.value)}
                  style={{ flex: 1 }}
                />
                
                {/* Voice Input Mic Button */}
                <button 
                  type="button"
                  onClick={handleToggleListening}
                  className={isListening ? "btn-primary lining-copilot pulse-glow" : "btn-secondary lining-copilot"}
                  style={{ padding: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  title="Speak to Assistant"
                >
                  <Mic size={16} style={{ color: isListening ? '#ff2d55' : 'inherit' }} />
                </button>

                {/* Voice Output Speaker Toggle Button */}
                <button 
                  type="button"
                  onClick={() => {
                    const nextVal = !voiceEnabled;
                    setVoiceEnabled(nextVal);
                    if (!nextVal && window.speechSynthesis) {
                      window.speechSynthesis.cancel();
                    }
                  }}
                  className={voiceEnabled ? "btn-primary lining-copilot" : "btn-secondary lining-copilot"}
                  style={{ padding: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  title="Toggle Read Aloud"
                >
                  {voiceEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
                </button>

                <button type="submit" disabled={chatLoading} className="btn-primary lining-copilot" style={{ padding: '10px 16px' }}>
                  <Send size={16} />
                </button>
              </form>
            </div>
          </div>
        )}
        {/* TAB 5: WORKSPACE SETTINGS & SAAS SUBSCRIPTION */}
        {activeTab === 'settings' && (() => {
          const maxCandidates = user?.subscription_tier === 'pro' ? 100 : 5;
          const maxJobs = user?.subscription_tier === 'pro' ? 10 : 2;
          const isPro = user?.subscription_tier === 'pro';
          return (
            <div className="glass-panel animate-fade-in" style={{ padding: '32px' }}>
              <h2 style={{ fontSize: '22px', color: '#fff', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Settings style={{ color: 'var(--accent-cyan)' }} /> Workspace Settings
              </h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '14px', marginBottom: '24px' }}>
                Manage your SaaS tenant subscription limits, pricing tiers, and invite team recruiters to collaborate.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', alignItems: 'start' }}>
                {/* Organization Profile info */}
                <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.01)' }}>
                  <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '16px' }}>Organization Workspace</h3>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div>
                      <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Workspace ID</label>
                      <div className="input-field" style={{ padding: '10px 12px', background: 'rgba(255,255,255,0.02)', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                        Tenant #{user?.tenant_id}
                      </div>
                    </div>

                    <div>
                      <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Invite Recruiter Code</label>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <input 
                          type="text" 
                          readOnly 
                          className="input-field" 
                          value={user?.invite_code || 'FREE-INVITE'} 
                          style={{ fontFamily: 'monospace', fontWeight: 'bold', color: 'var(--accent-cyan)' }} 
                        />
                        <button 
                          onClick={() => { navigator.clipboard.writeText(user?.invite_code || 'FREE-INVITE'); alert("Invite code copied!"); }} 
                          className="btn-secondary" 
                          style={{ fontSize: '12px' }}
                        >
                          Copy Invite
                        </button>
                      </div>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>
                        Share this code with other recruiters in your organization to let them register and join this workspace.
                      </span>
                    </div>
                  </div>
                </div>

                {/* Usage Quota limits tracker */}
                <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.01)' }}>
                  <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '16px' }}>SaaS Plan Usage Quotas</h3>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {/* Candidates limit count */}
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '8px' }}>
                        <span style={{ color: '#fff' }}>Candidates Resumes Uploaded</span>
                        <span style={{ color: 'var(--text-muted)' }}>{candidates.length} / {maxCandidates} profiles</span>
                      </div>
                      <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ width: `${Math.min(100, (candidates.length / maxCandidates) * 100)}%`, height: '100%', background: '#ffffff', borderRadius: '4px' }} />
                      </div>
                    </div>

                    {/* Active jobs limit count */}
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '8px' }}>
                        <span style={{ color: '#fff' }}>Active Job Listings Published</span>
                        <span style={{ color: 'var(--text-muted)' }}>{jobs.filter(j => j.is_active).length} / {maxJobs} openings</span>
                      </div>
                      <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ width: `${Math.min(100, (jobs.filter(j => j.is_active).length / maxJobs) * 100)}%`, height: '100%', background: '#ffffff', borderRadius: '4px' }} />
                      </div>
                    </div>

                    {isPro ? (
                      <div style={{ display: 'flex', gap: '8px', padding: '12px', background: 'rgba(34, 197, 94, 0.05)', border: '1px solid rgba(34, 197, 94, 0.15)', borderRadius: '8px', fontSize: '12px', color: '#22c55e', alignItems: 'center' }}>
                        <CheckCircle size={16} style={{ flexShrink: 0 }} />
                        <span>Recruiter Pro subscription plan active. Thank you!</span>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', gap: '8px', padding: '12px', background: 'rgba(236, 72, 153, 0.05)', border: '1px solid rgba(236, 72, 153, 0.15)', borderRadius: '8px', fontSize: '12px', color: '#ec4899' }}>
                        <HelpCircle size={16} style={{ flexShrink: 0 }} />
                        <span>Free Workspace subscription plan active. Limits are strictly monitored.</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Billing pricing tiers */}
              <div style={{ marginTop: '32px' }}>
                <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '16px' }}>Subscription Pricing Plans</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
                  {/* Free plan details */}
                  <div style={{ border: isPro ? '1px solid var(--border-glass)' : '1px solid var(--accent-cyan)', borderRadius: '12px', padding: '20px', background: 'rgba(255,255,255,0.01)', position: 'relative' }}>
                    {!isPro && <span style={{ position: 'absolute', top: '12px', right: '12px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-glass)', borderRadius: '12px', padding: '3px 8px', fontSize: '10px', color: 'var(--accent-cyan)' }}>Active Plan</span>}
                    <h4 style={{ fontSize: '15px', color: '#fff', marginBottom: '8px' }}>Free Basic</h4>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#fff', marginBottom: '16px' }}>$0 <span style={{ fontSize: '12px', fontWeight: 'normal', color: 'var(--text-muted)' }}>/mo</span></div>
                    <ul style={{ paddingLeft: '16px', color: 'var(--text-muted)', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                      <li>Up to 5 candidate resumes parsing</li>
                      <li>Up to 2 active job openings</li>
                      <li>Semantic vector search indexing</li>
                      <li>Basic Recruiter Copilot assistant</li>
                    </ul>
                  </div>

                  {/* Pro plan details */}
                  <div style={{ border: isPro ? '1px solid #22c55e' : '1px solid var(--accent-purple)', borderRadius: '12px', padding: '20px', background: isPro ? 'rgba(34, 197, 94, 0.02)' : 'rgba(147, 51, 234, 0.02)', position: 'relative' }}>
                    {isPro ? (
                      <span style={{ position: 'absolute', top: '12px', right: '12px', background: '#22c55e', borderRadius: '12px', padding: '3px 8px', fontSize: '10px', color: '#fff' }}>Active Plan</span>
                    ) : (
                      <span style={{ position: 'absolute', top: '12px', right: '12px', background: 'var(--accent-purple)', borderRadius: '12px', padding: '3px 8px', fontSize: '10px', color: '#fff' }}>Recommended</span>
                    )}
                    <h4 style={{ fontSize: '15px', color: '#fff', marginBottom: '8px' }}>Recruiter Pro</h4>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#fff', marginBottom: '16px' }}>$79 <span style={{ fontSize: '12px', fontWeight: 'normal', color: 'var(--text-muted)' }}>/mo</span></div>
                    <ul style={{ paddingLeft: '16px', color: 'var(--text-muted)', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                      <li>Up to 100 candidate resumes parsing</li>
                      <li>Up to 10 active job openings</li>
                      <li>Full history chat session memory</li>
                      <li>High-priority AI extraction parsing queues</li>
                    </ul>
                    {isPro ? (
                      <button disabled className="btn-secondary" style={{ width: '100%', justifyContent: 'center', fontSize: '12px', opacity: 0.6, cursor: 'not-allowed' }}>Subscribed</button>
                    ) : (
                      <button onClick={() => setShowUpgradeModal(true)} className="btn-primary" style={{ width: '100%', justifyContent: 'center', fontSize: '12px' }}>Upgrade to Pro</button>
                    )}
                  </div>

                  {/* Enterprise plan details */}
                  <div style={{ border: '1px solid var(--border-glass)', borderRadius: '12px', padding: '20px', background: 'rgba(255,255,255,0.01)' }}>
                    <h4 style={{ fontSize: '15px', color: '#fff', marginBottom: '8px' }}>Enterprise AI</h4>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#fff', marginBottom: '16px' }}>Custom <span style={{ fontSize: '12px', fontWeight: 'normal', color: 'var(--text-muted)' }}>billing</span></div>
                    <ul style={{ paddingLeft: '16px', color: 'var(--text-muted)', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                      <li>Unlimited candidate uploads & jobs</li>
                      <li>Custom dedicated LLM integrations</li>
                      <li>Audit history tracking exports</li>
                      <li>SLA support & private instance hosts</li>
                    </ul>
                    <button onClick={() => alert("Contacting sales team...")} className="btn-secondary" style={{ width: '100%', justifyContent: 'center', fontSize: '12px' }}>Contact Sales</button>
                  </div>
                </div>
              </div>
            </div>
          );
        })()}
      </main>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border-glass)', padding: '24px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.1em', marginTop: 'auto' }}>
        Developed and Designed by Atlas Work Intelligence
      </footer>

      {/* MATCH EXPLANATION MODAL */}
      {recExplanation && (
        <div style={{ position: 'fixed', top: '0', left: '0', width: '100%', height: '100%', background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000, padding: '16px' }}>
          <div className="glass-panel animate-fade-in" style={{ width: '100%', maxWidth: '600px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkles size={18} style={{ color: 'var(--accent-cyan)' }} />
                <h3 style={{ fontSize: '18px', color: '#fff' }}>Fit Explanation: {recExplanation.candidate}</h3>
              </div>
              <button onClick={() => setRecExplanation(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={18} />
              </button>
            </div>
            
            <p style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
              {recExplanation.text}
            </p>
            
            <div style={{ textAlign: 'right', marginTop: '20px' }}>
              <button onClick={() => setRecExplanation(null)} className="btn-primary" style={{ padding: '8px 16px', fontSize: '13px' }}>Close</button>
            </div>
          </div>
        </div>
      )}

      {/* CHOOSE PAYMENT GATEWAY MODAL */}
      {showUpgradeModal && (
        <div style={{ position: 'fixed', top: '0', left: '0', width: '100%', height: '100%', background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000, padding: '16px' }}>
          <div className="glass-panel lining-copilot animate-fade-in" style={{ width: '100%', maxWidth: '480px', padding: '28px', background: '#080808' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ fontSize: '18px', color: '#fff', fontWeight: 700 }}>Choose Payment Method</h3>
              <button onClick={() => setShowUpgradeModal(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={18} />
              </button>
            </div>
            
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '24px', lineHeight: '1.4' }}>
              ATLAS AWi provides localized payment routing. Choose the gateway matching your location:
            </p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Razorpay (INR) */}
              <div 
                onClick={() => handleStartCheckout('razorpay')}
                className="glass-panel lining-jobs" 
                style={{ padding: '16px', borderRadius: '12px', cursor: 'pointer', transition: 'var(--transition-smooth)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
              >
                <div>
                  <div style={{ fontWeight: 'bold', color: '#fff', fontSize: '14px' }}>🇮🇳 India Local Payment</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>Pay in INR via UPI (GPay, PhonePe) or Netbanking</div>
                </div>
                <div style={{ fontWeight: 'bold', color: 'var(--accent-orange)', fontSize: '14px' }}>₹6500 / yr</div>
              </div>
              
              {/* Stripe (USD) */}
              <div 
                onClick={() => handleStartCheckout('stripe')}
                className="glass-panel lining-search" 
                style={{ padding: '16px', borderRadius: '12px', cursor: 'pointer', transition: 'var(--transition-smooth)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
              >
                <div>
                  <div style={{ fontWeight: 'bold', color: '#fff', fontSize: '14px' }}>🌐 Global Cards & Wallets</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>Pay in USD via Visa, Mastercard, Apple Pay</div>
                </div>
                <div style={{ fontWeight: 'bold', color: 'var(--accent-blue)', fontSize: '14px' }}>$79 / yr</div>
              </div>
            </div>
            
            <div style={{ marginTop: '24px', textAlign: 'right' }}>
              <button onClick={() => setShowUpgradeModal(false)} className="btn-secondary" style={{ padding: '8px 16px', fontSize: '12px' }}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      {/* CHECKOUT PORTAL SIMULATOR MODAL */}
      {activeCheckoutSession && (
        <div style={{ position: 'fixed', top: '0', left: '0', width: '100%', height: '100%', background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(10px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1001, padding: '16px' }}>
          <div className="glass-panel animate-fade-in" style={{ width: '100%', maxWidth: '440px', padding: '32px', background: activeCheckoutSession.provider === 'stripe' ? '#111216' : '#0e1118', border: activeCheckoutSession.provider === 'stripe' ? '1px solid #635bff' : '1px solid #3399cc', boxShadow: '0 20px 40px rgba(0,0,0,0.5)' }}>
            
            {paymentSuccessMsg ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '24px 0', textAlign: 'center' }}>
                <CheckCircle size={48} className="pulse-glow" style={{ color: '#22c55e', marginBottom: '16px' }} />
                <h3 style={{ fontSize: '20px', color: '#fff', fontWeight: 'bold', marginBottom: '8px' }}>Payment Completed</h3>
                <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{paymentSuccessMsg}</p>
              </div>
            ) : (
              <div>
                {/* Header branding */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '16px', marginBottom: '20px' }}>
                  <div>
                    <span style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.1em', color: activeCheckoutSession.provider === 'stripe' ? '#635bff' : '#3399cc', fontWeight: 'bold' }}>
                      {activeCheckoutSession.provider === 'stripe' ? 'Stripe Checkout Portal' : 'Razorpay Secure'}
                    </span>
                    <h3 style={{ fontSize: '16px', color: '#fff', fontWeight: 'bold', marginTop: '2px' }}>
                      Upgrade Organization
                    </h3>
                  </div>
                  <button onClick={() => setActiveCheckoutSession(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                    <X size={18} />
                  </button>
                </div>

                {/* Amount display */}
                <div style={{ background: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '10px', marginBottom: '24px', textAlign: 'center' }}>
                  <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>TOTAL DUE</span>
                  <div style={{ fontSize: '28px', fontWeight: 800, color: '#fff', marginTop: '4px' }}>
                    {activeCheckoutSession.provider === 'stripe' ? '$79.00 USD' : '₹6,500.00 INR'}
                  </div>
                </div>

                {/* Simulator Inputs */}
                {activeCheckoutSession.provider === 'stripe' ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px' }}>
                        <CreditCard size={12} style={{ color: '#635bff' }} /> CARD DETAILS (MOCK SANDBOX)
                      </label>
                      <input type="text" readOnly className="input-field" value="4242  4242  4242  4242" style={{ letterSpacing: '2px', fontFamily: 'monospace' }} />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                      <div>
                        <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px' }}>EXPIRY</label>
                        <input type="text" readOnly className="input-field" value="12 / 29" style={{ fontFamily: 'monospace' }} />
                      </div>
                      <div>
                        <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px' }}>CVC</label>
                        <input type="text" readOnly className="input-field" value="123" style={{ fontFamily: 'monospace' }} />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'center' }}>
                    <div style={{ background: '#fff', padding: '12px', borderRadius: '12px', display: 'inline-block', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
                      <div style={{ width: '120px', height: '120px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', border: '2px dashed #3399cc', color: '#111' }}>
                        <span style={{ fontSize: '24px', marginBottom: '4px' }}>📱</span>
                        <span style={{ fontSize: '9px', fontWeight: 'bold', color: '#3399cc' }}>UPI QR CODE</span>
                        <span style={{ fontSize: '8px', color: '#666' }}>Scan with GPay/BHIM</span>
                      </div>
                    </div>
                    <div style={{ width: '100%' }}>
                      <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px', textAlign: 'center' }}>OR PAY VIA UPI ID</label>
                      <input type="text" readOnly className="input-field" value="atlasrecruiting@paytm" style={{ textAlign: 'center', fontFamily: 'monospace', color: 'var(--accent-orange)' }} />
                    </div>
                  </div>
                )}

                {/* Confirm Action Button */}
                <button 
                  onClick={handleConfirmCheckout} 
                  disabled={paymentProcessing}
                  className="btn-primary" 
                  style={{ 
                    width: '100%', 
                    justifyContent: 'center', 
                    marginTop: '28px', 
                    padding: '14px', 
                    fontSize: '13px',
                    background: activeCheckoutSession.provider === 'stripe' ? '#635bff' : '#3399cc',
                    border: 'none',
                    borderRadius: '8px',
                    fontWeight: 'bold',
                    opacity: paymentProcessing ? 0.6 : 1
                  }}
                >
                  {paymentProcessing ? 'Processing Transaction...' : `Complete Simulated Payment`}
                </button>
              </div>
            )}
            
          </div>
        </div>
      )}

      {/* GOOGLE SIGN IN SIMULATOR MODAL */}
      {showGoogleModal && (
        <div style={{ position: 'fixed', top: '0', left: '0', width: '100%', height: '100%', background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(10px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 2000, padding: '16px' }}>
          <div className="glass-panel animate-fade-in" style={{ width: '100%', maxWidth: '380px', padding: '28px', background: '#ffffff', color: '#1f1f1f', border: '1px solid #dadce0', boxShadow: '0 8px 30px rgba(0,0,0,0.3)' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '24px' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginBottom: '12px' }}>
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#1f1f1f' }}>Sign in with Google</h3>
              <span style={{ fontSize: '12px', color: '#5f6368', marginTop: '4px' }}>to continue to ATLAS AWi</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div 
                onClick={() => handleGoogleLogin('recruiter.billing@gmail.com')}
                style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', borderRadius: '8px', border: '1px solid #dadce0', cursor: 'pointer', transition: 'background 0.2s', background: '#f8f9fa' }}
                onMouseOver={e => e.currentTarget.style.background = '#f1f3f4'}
                onMouseOut={e => e.currentTarget.style.background = '#f8f9fa'}
              >
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--accent-purple)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', fontWeight: 'bold' }}>R</div>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#3c4043' }}>Recruiter Billing</div>
                  <div style={{ fontSize: '11px', color: '#5f6368' }}>recruiter.billing@gmail.com</div>
                </div>
              </div>

              <div 
                onClick={() => handleGoogleLogin('gaurav.founder@company.com')}
                style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', borderRadius: '8px', border: '1px solid #dadce0', cursor: 'pointer', transition: 'background 0.2s', background: '#f8f9fa' }}
                onMouseOver={e => e.currentTarget.style.background = '#f1f3f4'}
                onMouseOut={e => e.currentTarget.style.background = '#f8f9fa'}
              >
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--accent-cyan)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', fontWeight: 'bold' }}>G</div>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#3c4043' }}>Gaurav Founder</div>
                  <div style={{ fontSize: '11px', color: '#5f6368' }}>gaurav.founder@company.com</div>
                </div>
              </div>
            </div>

            <button 
              onClick={() => setShowGoogleModal(false)} 
              style={{ width: '100%', marginTop: '20px', background: 'none', border: 'none', color: '#1a73e8', fontSize: '13px', cursor: 'pointer', padding: '8px', textAlign: 'center', fontWeight: 'bold' }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
