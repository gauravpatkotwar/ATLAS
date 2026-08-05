import React, { useState, useEffect, useRef } from 'react';
import { 
 Users, Briefcase, Search, MessageSquare, UploadCloud, 
 Trash2, MapPin, DollarSign, LogOut, 
 AlertCircle, Sparkles, Send, Plus, X, Award, HelpCircle, Settings, CreditCard, CheckCircle,
 Mic, Volume2, VolumeX, Phone, PhoneOff, Video, VideoOff, MicOff, TrendingUp, Shield, Key, Activity, Share2, ShoppingBag, GraduationCap, BookOpen, Star, CheckCircle2, Lock, PlayCircle, Trophy, Zap, Target, FileText, Github, ExternalLink, Copy
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
 {/* Signature Blue Ink Indicator Dot */}
 <circle cx="70" cy="18" r="4.5" fill="#0052CC" />
 </svg>
);

const AtlasNovaLogo = ({ size = 24, style = {}, className = '' }: { size?: number; style?: React.CSSProperties; className?: string }) => (
 <svg 
 width={size} 
 height={size} 
 viewBox="0 0 100 100" 
 fill="none" 
 xmlns="http://www.w3.org/2000/svg"
 className={className}
 style={{ display: 'inline-block', verticalAlign: 'middle', ...style }}
 >
 <defs>
 <linearGradient id="novaGoldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
 <stop offset="0%" stopColor="#ffe9b8" />
 <stop offset="50%" stopColor="#ffcf87" />
 <stop offset="100%" stopColor="#ffa834" />
 </linearGradient>
 </defs>
 
 {/* Circular Orbit Ring (Monochromatic) */}
 <circle cx="50" cy="55" r="25" stroke="currentColor" strokeWidth="9" fill="none" opacity="0.95" />
 
 {/* Golden Gradient Star */}
 <path 
 d="M 50 10 Q 50 30 38 30 Q 50 30 50 50 Q 50 30 62 30 Q 50 30 50 10 Z" 
 fill="url(#novaGoldGradient)" 
 />
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
 <div className="entrance-text" style={{ textTransform: 'uppercase', letterSpacing: '0.2em' }}>
 ATLAS
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
 const [activeTab, setActiveTab] = useState<'candidates' | 'jobs' | 'search' | 'copilot' | 'settings' | 'my_profile' | 'jobs_board' | 'interview_prep' | 'community' | 'marketplace' | 'analytics' | 'academy' | 'resume_builder'>('copilot');
 const [settingsSubPage, setSettingsSubPage] = useState<'appearance' | 'sso' | 'developer' | 'automations' | 'integrations'>('appearance');

 // ATLAS ACADEMY STATE 
 const [academySubView, setAcademySubView] = useState<'discover' | 'my_learning' | 'instructor' | 'skill_gap' | 'ai_mentor' | 'course_detail'>('discover');
 const [academyCourses, setAcademyCourses] = useState<any[]>([]);
 const [academyEnrollments, setAcademyEnrollments] = useState<any[]>([]);
 const [academyCertificates, setAcademyCertificates] = useState<any[]>([]);
 const [academyStats, setAcademyStats] = useState<any>(null);
 const [academyInstructor, setAcademyInstructor] = useState<any>(null);
 const [academySelectedCourse, setAcademySelectedCourse] = useState<any>(null);
 const [academyCategoryFilter, setAcademyCategoryFilter] = useState<string>('');
 const [academySearchQuery, setAcademySearchQuery] = useState<string>('');
 const [academySkillGapResult, setAcademySkillGapResult] = useState<any>(null);
 const [academySkillGapLoading, setAcademySkillGapLoading] = useState(false);
 const [academyMentorMessages, setAcademyMentorMessages] = useState<{role:string;content:string}[]>([]);
 const [academyMentorInput, setAcademyMentorInput] = useState('');
 const [academyMentorLoading, setAcademyMentorLoading] = useState(false);
 const [academyRoadmap, setAcademyRoadmap] = useState<string>('');
 const [academyRoadmapGoal, setAcademyRoadmapGoal] = useState<string>('');
 const [academyRoadmapLoading, setAcademyRoadmapLoading] = useState(false);
 const [academyInstructorForm, setAcademyInstructorForm] = useState({ display_name: '', bio: '', expertise: '' });
 const [academyCourseForm, setAcademyCourseForm] = useState({ title: '', description: '', short_description: '', category: 'Programming', level: 'beginner', skills_taught: '', tags: '', is_free: true, price: 0 });
 const [academySkillGapJobTitle, setAcademySkillGapJobTitle] = useState('');
 const [academySkillGapJobSkills, setAcademySkillGapJobSkills] = useState('');
 // 

 // RESUME BUILDER STATE 
 const [resumeSubView, setResumeSubView] = useState<'builder' | 'score' | 'salary' | 'analytics' | 'showcase' | 'gamification'>('builder');
 const [resumeTemplate, setResumeTemplate] = useState<'modern' | 'minimal' | 'technical'>('modern');
 const [resumeTargetRole, setResumeTargetRole] = useState('');
 const [resumeGenerated, setResumeGenerated] = useState<any>(null);
 const [resumeGenerating, setResumeGenerating] = useState(false);
 const [resumeScoreResult, setResumeScoreResult] = useState<any>(null);
 const [resumeScoreLoading, setResumeScoreLoading] = useState(false);
 const [resumeTextInput, setResumeTextInput] = useState('');
 const [resumeJobDescInput, setResumeJobDescInput] = useState('');
 const [salaryJobTitle, setSalaryJobTitle] = useState('');
 const [salaryLocation, setSalaryLocation] = useState('Remote');
 const [salaryExpYears, setSalaryExpYears] = useState(3);
 const [salaryResult, setSalaryResult] = useState<any>(null);
 const [salaryLoading, setSalaryLoading] = useState(false);
 const [careerAnalytics, setCareerAnalytics] = useState<any>(null);
 const [profileScore, setProfileScore] = useState<any>(null);
 const [gamificationStats, setGamificationStats] = useState<any>(null);
 const [leaderboard, setLeaderboard] = useState<any[]>([]);
 const [showcaseProjects, setShowcaseProjects] = useState<any[]>([]);
 const [showcaseForm, setShowcaseForm] = useState({ title: '', description: '', github_url: '', demo_url: '', tech_stack: '', category: 'Web Development' });
 const [showcaseSubmitting, setShowcaseSubmitting] = useState(false);
 // 

 // SaaS Tenant state
 const [orgName, setOrgName] = useState('');
 const [inviteCode, setInviteCode] = useState('');
 const [isJoinOrg, setIsJoinOrg] = useState(false);
 const [isSSOLogin, setIsSSOLogin] = useState(false);

 // SSO configuration state
 const [ssoEntityId, setSsoEntityId] = useState('');
 const [ssoUrl, setSsoUrl] = useState('');
 const [ssoCert, setSsoCert] = useState('');

 // Developer API keys & webhooks state
 const [apiKeys, setApiKeys] = useState<any[]>([]);
 const [webhooks, setWebhooks] = useState<any[]>([]);
 const [newKeyName, setNewKeyName] = useState('');
 const [webhookUrl, setWebhookUrl] = useState('');
 const [webhookSecret, setWebhookSecret] = useState('');
 const [webhookEvents, setWebhookEvents] = useState<string[]>(['candidate.created']);
 const [latestRawKey, setLatestRawKey] = useState('');

 // Automation workflows state
 const [workflows, setWorkflows] = useState<any[]>([]);
 const [newWorkflowName, setNewWorkflowName] = useState('');
 const [workflowTrigger, setWorkflowTrigger] = useState('candidate_status_changed');
 const [workflowAction, setWorkflowAction] = useState('send_email');
 const [workflowEmail, setWorkflowEmail] = useState('');

 // Integrations state
 const [integrationsList, setIntegrationsList] = useState<any[]>([]);

 // Analytics state
 const [analyticsThroughput, setAnalyticsThroughput] = useState<any>({ applied: 0, screening: 0, interviewing: 0, offered: 0 });
 const [analyticsTimeToHire, setAnalyticsTimeToHire] = useState<any>({ screening_days: 3.4, interview_days: 8.2, offer_days: 4.1, total_days: 15.7 });

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
 const [prepHistory, setPrepHistory] = useState<Array<{ question: string, answer: string, feedback: string, score: string, modelAnswer?: string, category?: string }>>([]);
 const [prepLoading, setPrepLoading] = useState<boolean>(false);
 const [prepRound, setPrepRound] = useState<number>(1);
 const [prepCategory, setPrepCategory] = useState<string>('System Architecture');
 const [prepHint, setPrepHint] = useState<string>('');
 const [prepFinished, setPrepFinished] = useState<boolean>(false);

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
 const [voiceEnabled, setVoiceEnabled] = useState<boolean>(false); // Default OFF — only speaks when user explicitly turns Voice ON!
 const [novaVoiceGender, setNovaVoiceGender] = useState<'female' | 'male'>('female'); // Female & Male Sound Packs
 const [loadedVoiceName, setLoadedVoiceName] = useState<string>('');
 const [recognitionInstance, setRecognitionInstance] = useState<any>(null);

 // WebRTC Calling states
 const [activeCall, setActiveCall] = useState<any | null>(null); // { candidateId: number, status: 'calling' | 'ringing' | 'connected', role: 'caller' | 'receiver', peerName: string }
 const [localStream, setLocalStream] = useState<MediaStream | null>(null);
 const [micMuted, setMicMuted] = useState<boolean>(false);
 const [videoDisabled, setVideoDisabled] = useState<boolean>(false);
 const [incomingCall, setIncomingCall] = useState<any | null>(null); // Incoming call details from poll
 const localVideoRef = useRef<HTMLVideoElement>(null);
 const remoteVideoRef = useRef<HTMLVideoElement>(null);

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

 // Video Recorder & Uploader states
 const [recording, setRecording] = useState(false);
 const [recordedVideoUrl, setRecordedVideoUrl] = useState<string | null>(null);
 const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
 const [cameraActive, setCameraActive] = useState(false);
 
 const mediaRecorderRef = useRef<MediaRecorder | null>(null);
 const recordingPreviewRef = useRef<HTMLVideoElement>(null);
 const recorderStreamRef = useRef<MediaStream | null>(null);

 // Community & Whistleblower states
 const [communityPosts, setCommunityPosts] = useState<any[]>([]);
 const [communityLoading, setCommunityLoading] = useState(false);
 const [newPostTitle, setNewPostTitle] = useState('');
 const [newPostContent, setNewPostContent] = useState('');
 const [newPostIsAnonymous, setNewPostIsAnonymous] = useState(true);
 const [newPostType, setNewPostType] = useState('discussion'); // 'discussion' or 'whistleblower'
 const [expandedPostIds, setExpandedPostIds] = useState<number[]>([]);
 // @ts-ignore — used in comment forms
 const [newCommentIsAnonymous, setNewCommentIsAnonymous] = useState<Record<number, boolean>>({});
 const [newCommentText, setNewCommentText] = useState<Record<number, string>>({});
 const [activePostComments, setActivePostComments] = useState<Record<number, any[]>>({});
 const [communityFilter, setCommunityFilter] = useState('all'); // 'all', 'discussion', 'whistleblower'

 // Chat room state
 const [chatView, setChatView] = useState<'chat' | 'board'>('chat'); // toggle between chat and board
 const [chatChannels, setChatChannels] = useState<any[]>([]);
 const [activeChannel, setActiveChannel] = useState<any | null>(null);
 const [chatMessages, setChatMessages] = useState<any[]>([]);
 const [chatInput, setChatInput] = useState('');
 const [chatAnon, setChatAnon] = useState(true);
 const [chatRoomLoading, setChatRoomLoading] = useState(false);
 const [showCreateChannel, setShowCreateChannel] = useState(false);
 const [newChannelName, setNewChannelName] = useState('');
 const [newChannelDesc, setNewChannelDesc] = useState('');
 const chatMessagesEndRef = useRef<HTMLDivElement | null>(null);
 const chatPollRef = useRef<any>(null);

 // Marketplace states
 const [marketplaceProducts, setMarketplaceProducts] = useState<any[]>([]);
 const [marketplacePurchases, setMarketplacePurchases] = useState<any[]>([]);
 const [marketplaceLoading, setMarketplaceLoading] = useState(false);
 const [newProductName, setNewProductName] = useState('');
 const [newProductDescription, setNewProductDescription] = useState('');
 const [newProductPrice, setNewProductPrice] = useState('');
 const [newProductCategory, setNewProductCategory] = useState('software'); // 'software' or 'service'
 const [newProductDownloadUrl, setNewProductDownloadUrl] = useState('');


 const [accentColor, setAccentColor] = useState<'default' | 'cyan' | 'mint'>(() => (localStorage.getItem('atlas_accent') as any) || 'default');
 const [densityMode, setDensityMode] = useState<'relaxed' | 'compact'>(() => (localStorage.getItem('atlas_density') as any) || 'relaxed');

 useEffect(() => {
 const root = document.documentElement;
 // Always enforce dark liquid glass tokens
 root.style.setProperty('--bg-dark', '#000000');
 root.style.setProperty('--bg-card', '#0a0a0c');
 root.style.setProperty('--text-main', '#f5f5f7');
 root.style.setProperty('--text-muted', '#86868b');
 root.style.setProperty('--border-glass', 'rgba(255, 255, 255, 0.08)');
 localStorage.setItem('atlas_theme', 'dark');
 }, []);

 useEffect(() => {
 const root = document.documentElement;
 if (accentColor === 'cyan') {
 root.style.setProperty('--accent-orange', '#00d2ff');
 root.style.setProperty('--accent-orange-glow', 'rgba(192, 192, 192, 0.15)');
 } else if (accentColor === 'mint') {
 root.style.setProperty('--accent-orange', '#00ffaa');
 root.style.setProperty('--accent-orange-glow', 'rgba(0, 255, 170, 0.15)');
 } else {
 root.style.setProperty('--accent-orange', '#808080');
 root.style.setProperty('--accent-orange-glow', 'rgba(128, 128, 128, 0.12)');
 }
 localStorage.setItem('atlas_accent', accentColor);
 }, [accentColor]);

 useEffect(() => {
 localStorage.setItem('atlas_density', densityMode);
 }, [densityMode]);

 // Meet Choice Popup Modal states
 const [showMeetChoiceModal, setShowMeetChoiceModal] = useState(false);
 const [meetChoiceInputCode, setMeetChoiceInputCode] = useState('');

 // Meet / Zoom states
 const [activeMeetRoom, setActiveMeetRoom] = useState<string | null>(null);
 const [meetIsJoined, setMeetIsJoined] = useState(false);
 const [copyMeetSuccess, setCopyMeetSuccess] = useState(false);
 const [meetParticipants, setMeetParticipants] = useState<any[]>([]);
 const [meetLocalStream, setMeetLocalStream] = useState<MediaStream | null>(null);
 const [meetRemoteStreams, setMeetRemoteStreams] = useState<Record<string, MediaStream>>({});
 const meetPeerConnectionsRef = useRef<Record<string, RTCPeerConnection>>({}); // useRef avoids re-render on every ICE tick
 const [meetMicMuted, setMeetMicMuted] = useState(false);
 const [meetVideoDisabled, setMeetVideoDisabled] = useState(false);
 const meetLocalVideoRef = useRef<HTMLVideoElement | null>(null); // stable ref — srcObject set once via effect
 const meetRemoteVideoRefs = useRef<Record<string, HTMLVideoElement | null>>({});

 // Ensure local video element always updates its srcObject when meetLocalStream changes or component mounts
 useEffect(() => {
 if (meetLocalVideoRef.current && meetLocalStream) {
 meetLocalVideoRef.current.srcObject = meetLocalStream;
 meetLocalVideoRef.current.play().catch(e => console.warn("Video play error:", e));
 }
 }, [meetLocalStream, meetIsJoined]);

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


 // 15-Minute Auto-Logout for Inactivity (protects server resources)
 useEffect(() => {
 if (!token) return;

 const INACTIVITY_TIMEOUT_MS = 15 * 60 * 1000; // 15 minutes
 let inactivityTimer: any = null;

 const resetTimer = () => {
 if (inactivityTimer) clearTimeout(inactivityTimer);
 inactivityTimer = setTimeout(() => {
 handleLogout();
 setAuthError('You have been automatically logged out after 15 minutes of inactivity.');
 }, INACTIVITY_TIMEOUT_MS);
 };

 const events = ['mousemove', 'keydown', 'mousedown', 'touchstart', 'scroll', 'click'];
 events.forEach(evt => window.addEventListener(evt, resetTimer));

 // Initialize timer
 resetTimer();

 return () => {
 if (inactivityTimer) clearTimeout(inactivityTimer);
 events.forEach(evt => window.removeEventListener(evt, resetTimer));
 };
 }, [token]);

 // Load profile when token changes
 useEffect(() => {
 if (token) {
 api.auth.me()
 .then(res => {
 setUser(res);
 const role = res.role || 'recruiter';
 if (role === 'candidate') {
 setSelectedMode('for_hire');
 localStorage.setItem('atlas_mode', 'for_hire');
 } else {
 setSelectedMode('hire');
 localStorage.setItem('atlas_mode', 'hire');
 }
 })
 .catch(() => handleLogout());
 }
 }, [token]);

 // Load lists when logged in
 useEffect(() => {
 if (user) {
 loadCandidates();
 loadJobs();
 loadCommunityPosts();
 loadMarketplaceData();
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
 if (user && activeTab === 'community') {
 loadCommunityPosts();
 }
 if (user && activeTab === 'marketplace') {
 loadMarketplaceData();
 }
 if (user && activeTab === 'settings') {
 loadSSOConfig();
 loadDeveloperData();
 loadWorkflows();
 loadIntegrations();
 }
 if (user && activeTab === 'analytics') {
 loadAnalyticsData();
 }
 if (user && activeTab === 'academy') {
 (async () => {
 try {
 const [courses, enrollments, certs, stats, instr] = await Promise.all([
 api.academy.listCourses(),
 api.academy.myEnrollments(),
 api.academy.myCertificates(),
 api.academy.getStats(),
 api.academy.getInstructorProfile(),
 ]);
 setAcademyCourses(courses || []);
 setAcademyEnrollments(enrollments || []);
 setAcademyCertificates(certs || []);
 setAcademyStats(stats);
 setAcademyInstructor(instr);
 } catch (e) { console.error('Academy load failed:', e); }
 })();
 }
 if (user && activeTab === 'resume_builder') {
 (async () => {
 try {
 const [analytics, pScore, gamStats, lb, showcase] = await Promise.all([
 api.career.getCareerAnalytics(),
 api.career.getProfileScore(),
 api.career.getGamificationStats(),
 api.career.getLeaderboard(),
 api.career.listShowcaseProjects(),
 ]);
 setCareerAnalytics(analytics);
 setProfileScore(pScore);
 setGamificationStats(gamStats);
 setLeaderboard(lb?.leaderboard || []);
 setShowcaseProjects(showcase?.projects || []);
 } catch (e) { console.error('Career Hub load failed:', e); }
 })();
 }
 }, [user, activeTab]);


 // Voice: isSpeaking state ref 
 const [isSpeaking, setIsSpeaking] = React.useState(false);
 const [voiceContinuous, setVoiceContinuous] = React.useState(false);
 const [interimTranscript, setInterimTranscript] = React.useState('');
 const autoSendTimerRef = React.useRef<any>(null);

 // Voice Assistant Speech Recognition & Synthesis Initializer
 useEffect(() => {
 const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
 if (SpeechRecognition) {
 const rec = new SpeechRecognition();
 rec.continuous = true; // keep listening while user talks
 rec.interimResults = true; // show live transcript
 rec.lang = 'en-US';

 rec.onstart = () => setIsListening(true);

 rec.onresult = (event: any) => {
 let interim = '';
 let final = '';
 for (let i = event.resultIndex; i < event.results.length; i++) {
 const t = event.results[i][0].transcript;
 if (event.results[i].isFinal) final += t;
 else interim += t;
 }
 if (final) {
 setChatQuery(prev => (prev + ' ' + final).trim());
 setInterimTranscript('');
 // Auto-send after 800ms pause
 clearTimeout(autoSendTimerRef.current);
 autoSendTimerRef.current = setTimeout(() => {
 rec.stop();
 }, 800);
 } else {
 setInterimTranscript(interim);
 }
 };

 rec.onerror = (event: any) => {
 console.error('Speech recognition error:', event.error);
 setIsListening(false);
 setInterimTranscript('');
 };

 rec.onend = () => {
 setIsListening(false);
 setInterimTranscript('');
 // If we have a query, auto-submit it
 setChatQuery(prev => {
 if (prev.trim()) {
 setTimeout(() => {
 const form = document.getElementById('nova-chat-form') as HTMLFormElement;
 if (form) form.requestSubmit();
 }, 100);
 }
 return prev;
 });
 };

 setRecognitionInstance(rec);
 }
 }, []);

 const handleToggleListening = () => {
 if (!recognitionInstance) {
 alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
 return;
 }
 // Stop Nova speaking if we press mic
 if (window.speechSynthesis) window.speechSynthesis.cancel();
 setIsSpeaking(false);
 if (isListening) {
 recognitionInstance.stop();
 } else {
 setChatQuery('');
 try { recognitionInstance.start(); } catch (err) { console.error(err); }
 }
 };

 const speakText = (text: string, onDone?: () => void) => {
 if (!voiceEnabled || !window.speechSynthesis) { onDone?.(); return; }
 window.speechSynthesis.cancel();

 const cleanText = text
 .replace(/#{1,6}\s/g, '') // headings
 .replace(/\*\*(.+?)\*\*/g, '$1') // bold
 .replace(/\*(.+?)\*/g, '$1') // italic
 .replace(/`[^`]+`/g, '') // inline code
 .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // links
 .replace(/https?:\/\/[^\s]+/g, 'link')
 .replace(/[-•*]\s/g, '')
 .replace(/\n{2,}/g, '. ')
 .replace(/\n/g, ' ')
 .trim();

 if (!cleanText) { onDone?.(); return; }

 // Extract ONLY main summary words (first 1-2 key sentences, max 25 words)
 const sentences = cleanText.match(/[^.!?]+[.!?]+/g) || [cleanText];
 const keySummaryText = sentences.slice(0, 2).join(' ');
 const mainWordsOnly = keySummaryText.split(/\s+/).slice(0, 25).join(' ');

 if (!mainWordsOnly) { onDone?.(); return; }

 const chunks = [mainWordsOnly];

 const pickVoice = () => {
 const voices = window.speechSynthesis.getVoices();
 if (novaVoiceGender === 'female') {
 const femalePriority = [
 (v: SpeechSynthesisVoice) => v.name.includes('Ava') || v.name.includes('Jenny') || v.name.includes('Aria'),
 (v: SpeechSynthesisVoice) => v.name.includes('Natural') && (v.name.includes('Female') || v.name.includes('Jenny') || v.name.includes('Aria')),
 (v: SpeechSynthesisVoice) => v.name.includes('Neural') && (v.name.includes('Jenny') || v.name.includes('Aria') || v.name.includes('Emma')),
 (v: SpeechSynthesisVoice) => v.name === 'Samantha' && v.lang === 'en-US',
 (v: SpeechSynthesisVoice) => v.name.includes('Samantha'),
 (v: SpeechSynthesisVoice) => v.name.includes('Victoria') || v.name.includes('Karen') || v.name.includes('Serena'),
 (v: SpeechSynthesisVoice) => v.name.toLowerCase().includes('google') && v.lang.startsWith('en') && !v.name.toLowerCase().includes('male'),
 (v: SpeechSynthesisVoice) => v.lang === 'en-US',
 (v: SpeechSynthesisVoice) => v.lang.startsWith('en'),
 ];
 for (const test of femalePriority) {
 const found = voices.find(test);
 if (found) return found;
 }
 } else {
 const malePriority = [
 (v: SpeechSynthesisVoice) => v.name.includes('Andrew') || v.name.includes('Guy') || v.name.includes('Brian'),
 (v: SpeechSynthesisVoice) => v.name.includes('Natural') && (v.name.includes('Male') || v.name.includes('Guy') || v.name.includes('Christopher')),
 (v: SpeechSynthesisVoice) => v.name.includes('Neural') && (v.name.includes('Guy') || v.name.includes('Christopher') || v.name.includes('Eric')),
 (v: SpeechSynthesisVoice) => v.name === 'Daniel' || v.name === 'Alex' || v.name === 'Fred',
 (v: SpeechSynthesisVoice) => v.name.toLowerCase().includes('male'),
 (v: SpeechSynthesisVoice) => v.name.toLowerCase().includes('google') && v.name.toLowerCase().includes('male'),
 (v: SpeechSynthesisVoice) => v.lang === 'en-US',
 (v: SpeechSynthesisVoice) => v.lang.startsWith('en'),
 ];
 for (const test of malePriority) {
 const found = voices.find(test);
 if (found) return found;
 }
 }
 return null;
 };

 const selectedVoice = pickVoice();
 if (selectedVoice) setLoadedVoiceName(selectedVoice.name);

 let index = 0;
 setIsSpeaking(true);

 const speakChunk = () => {
 if (index >= chunks.length) {
 setIsSpeaking(false);
 onDone?.();
 if (voiceContinuous && recognitionInstance) {
 setTimeout(() => {
 setChatQuery('');
 try { recognitionInstance.start(); } catch (_) {}
 }, 400);
 }
 return;
 }

 const chunkText = chunks[index].trim();
 index++;

 if (!chunkText) {
 speakChunk();
 return;
 }

 const utterance = new SpeechSynthesisUtterance(chunkText);
 if (selectedVoice) utterance.voice = selectedVoice;

 // Natural Human Inflection Tuning based on sentence type
 const isQuestion = chunkText.endsWith('?');
 const isExclamation = chunkText.endsWith('!');

 if (novaVoiceGender === 'female') {
 utterance.pitch = isQuestion ? 1.15 : isExclamation ? 1.12 : 1.04;
 utterance.rate = isExclamation ? 1.05 : 1.01;
 } else {
 utterance.pitch = isQuestion ? 1.05 : isExclamation ? 1.02 : 0.94;
 utterance.rate = isExclamation ? 1.02 : 0.97;
 }
 utterance.volume = 1.0;

 utterance.onend = () => {
 // Natural human breath pause between sentences
 setTimeout(speakChunk, 120);
 };
 utterance.onerror = () => {
 setIsSpeaking(false);
 onDone?.();
 };

 window.speechSynthesis.speak(utterance);
 };

 speakChunk();
 };


 // Poll for incoming calls (For Candidates / Employees)
 useEffect(() => {
 let interval: any = null;
 if (user && selectedMode === 'for_hire' && myCandidateProfile?.id && !activeCall) {
 interval = setInterval(async () => {
 try {
 const statusRes = await api.candidates.getCallStatus(myCandidateProfile.id);
 if (statusRes && statusRes.status === 'ringing') {
 setIncomingCall({
 candidateId: myCandidateProfile.id,
 callerName: statusRes.caller_name || 'Employer'
 });
 } else {
 setIncomingCall(null);
 }
 } catch (e) {
 console.error("Failed to poll call status:", e);
 }
 }, 4000);
 }
 return () => {
 if (interval) clearInterval(interval);
 };
 }, [user, selectedMode, myCandidateProfile, activeCall]);

 // Bind video streams to elements
 useEffect(() => {
 if (localStream && localVideoRef.current) {
 localVideoRef.current.srcObject = localStream;
 }
 }, [localStream, activeCall]);

 useEffect(() => {
 if (localStream && remoteVideoRef.current && activeCall?.status === 'connected') {
 remoteVideoRef.current.srcObject = localStream;
 }
 }, [localStream, activeCall]);

 const handleInitiateCall = async (candidate: any) => {
 try {
 const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
 setLocalStream(stream);
 setMicMuted(false);
 setVideoDisabled(false);

 await api.candidates.initiateCall(candidate.id, "sdp_mock_offer");
 setActiveCall({
 candidateId: candidate.id,
 status: 'calling',
 role: 'caller',
 peerName: candidate.name
 });

 const pollResponse = setInterval(async () => {
 try {
 const statusRes = await api.candidates.getCallStatus(candidate.id);
 if (statusRes.status === 'accepted') {
 setActiveCall((prev: any) => prev ? { ...prev, status: 'connected' } : null);
 } else if (statusRes.status === 'rejected' || statusRes.status === 'ended') {
 handleEndCall(candidate.id);
 }
 } catch (e) {
 console.error(e);
 }
 }, 3000);

 (window as any)._activeCallPoll = pollResponse;
 } catch (err: any) {
 alert("Failed to access camera/microphone: " + err.message);
 }
 };

 const handleAcceptCall = async () => {
 if (!incomingCall) return;
 try {
 const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
 setLocalStream(stream);
 setMicMuted(false);
 setVideoDisabled(false);

 await api.candidates.respondCall(incomingCall.candidateId, 'accepted', 'sdp_mock_answer');
 setActiveCall({
 candidateId: incomingCall.candidateId,
 status: 'connected',
 role: 'receiver',
 peerName: incomingCall.callerName
 });
 setIncomingCall(null);

 const pollEnded = setInterval(async () => {
 try {
 const statusRes = await api.candidates.getCallStatus(incomingCall.candidateId);
 if (statusRes.status === 'ended' || statusRes.status === 'idle') {
 handleEndCall(incomingCall.candidateId);
 }
 } catch (e) {
 console.error(e);
 }
 }, 3000);
 (window as any)._activeCallPoll = pollEnded;
 } catch (err: any) {
 alert("Failed to access camera/microphone: " + err.message);
 }
 };

 const handleRejectCall = async () => {
 if (!incomingCall) return;
 try {
 await api.candidates.respondCall(incomingCall.candidateId, 'rejected');
 setIncomingCall(null);
 } catch (e) {
 console.error(e);
 }
 };

 const handleEndCall = async (candidateId: number) => {
 if (localStream) {
 localStream.getTracks().forEach(track => track.stop());
 setLocalStream(null);
 }
 try {
 await api.candidates.respondCall(candidateId, 'ended');
 } catch (e) {
 console.error(e);
 }
 setActiveCall(null);
 setIncomingCall(null);
 if ((window as any)._activeCallPoll) {
 clearInterval((window as any)._activeCallPoll);
 }
 };

 const handleToggleMic = () => {
 if (localStream) {
 const audioTrack = localStream.getAudioTracks()[0];
 if (audioTrack) {
 audioTrack.enabled = !audioTrack.enabled;
 setMicMuted(!audioTrack.enabled);
 }
 }
 };

 const handleToggleVideo = () => {
 if (localStream) {
 const videoTrack = localStream.getVideoTracks()[0];
 if (videoTrack) {
 videoTrack.enabled = !videoTrack.enabled;
 setVideoDisabled(!videoTrack.enabled);
 }
 }
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
 setPrepRound(1);
 setPrepFinished(false);
 setPrepLoading(true);
 try {
 const data = await api.career.startInterview({ job_title: job.title, skills: job.required_skills });
 setPrepQuestion(data.question);
 setPrepCategory(data.category || 'General');
 setPrepHint(data.hint || '');
 setPrepRound(data.round || 1);
 // Auto-read question aloud if voice enabled
 if (voiceEnabled) speakText(data.question);
 } catch (err) {
 setPrepQuestion("Walk me through a key project you built as a " + job.title + ". What design decisions did you make?");
 setPrepCategory("System Design");
 setPrepHint("Focus on trade-offs, architecture, and measurable impact.");
 } finally {
 setPrepLoading(false);
 }
 };

 const handleSubmitPrepAnswer = async (e: React.FormEvent) => {
 e.preventDefault();
 if (!prepAnswer.trim() || !prepJob) return;

 const currentQ = prepQuestion;
 const currentAns = prepAnswer;
 const currentCat = prepCategory;

 setPrepLoading(true);
 try {
 const data = await api.career.gradeInterviewRound({
 job_title: prepJob.title,
 current_round: prepRound,
 question: currentQ,
 answer: currentAns
 });

 const newHistoryItem = {
 question: currentQ,
 answer: currentAns,
 feedback: data.feedback,
 score: `${data.score} / 10`,
 modelAnswer: data.model_answer,
 category: currentCat
 };

 setPrepHistory(prev => [newHistoryItem, ...prev]);

 if (data.is_final || !data.next_round) {
 setPrepFinished(true);
 setPrepQuestion("Congratulations! You completed all 5 interview rounds.");
 if (voiceEnabled) speakText("Congratulations! You completed all 5 rounds of your mock interview session. Check your detailed feedback below!");
 // Refresh gamification stats to show updated XP
 api.career.getGamificationStats().then(setGamificationStats).catch(() => {});
 } else {
 setPrepRound(data.next_round.round);
 setPrepQuestion(data.next_round.question);
 setPrepCategory(data.next_round.category);
 setPrepHint(data.next_round.hint);
 setPrepAnswer('');
 if (voiceEnabled) speakText(data.next_round.question);
 }
 } catch (err) {
 alert("Prep assistant connection error. Please try submitting again.");
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

 const loadSSOConfig = async () => {
 try {
 const res = await api.sso.getConfig();
 if (res) {
 setSsoEntityId(res.idp_entity_id || '');
 setSsoUrl(res.idp_sso_url || '');
 setSsoCert(res.x509_certificate || '');
 }
 } catch (e) {
 console.error("Failed to load SSO config:", e);
 }
 };

 const loadDeveloperData = async () => {
 try {
 const [keys, hooks] = await Promise.all([
 api.developer.listKeys(),
 api.developer.listWebhooks()
 ]);
 setApiKeys(keys);
 setWebhooks(hooks);
 } catch (e) {
 console.error("Failed to load Developer data:", e);
 }
 };

 const loadWorkflows = async () => {
 try {
 const res = await api.automations.listWorkflows();
 setWorkflows(res);
 } catch (e) {
 console.error("Failed to load Workflows:", e);
 }
 };

 const loadIntegrations = async () => {
 try {
 const res = await api.integrations.list();
 setIntegrationsList(res);
 } catch (e) {
 console.error("Failed to load Integrations:", e);
 }
 };

 const loadAnalyticsData = async () => {
 try {
 const [throughput, hire] = await Promise.all([
 api.analytics.getThroughput(),
 api.analytics.getTimeToHire()
 ]);
 setAnalyticsThroughput(throughput);
 setAnalyticsTimeToHire(hire);
 } catch (e) {
 console.error("Failed to load Analytics data:", e);
 }
 };

 const handleSaveSSO = async (e: React.FormEvent) => {
 e.preventDefault();
 try {
 await api.sso.updateConfig(ssoEntityId, ssoUrl, ssoCert);
 alert("SAML SSO Configuration updated successfully!");
 } catch (err: any) {
 alert("Error: " + err.message);
 }
 };

 const handleCreateAPIKey = async (e: React.FormEvent) => {
 e.preventDefault();
 if (!newKeyName) return;
 try {
 const res = await api.developer.createKey(newKeyName);
 setLatestRawKey(res.raw_key);
 setApiKeys([res, ...apiKeys]);
 setNewKeyName('');
 } catch (err: any) {
 alert("Error: " + err.message);
 }
 };

 const handleDeleteAPIKey = async (keyId: number) => {
 if (!confirm("Revoke this API Key? Credentials signed with it will immediately fail.")) return;
 try {
 await api.developer.deleteKey(keyId);
 setApiKeys(apiKeys.filter(k => k.id !== keyId));
 } catch (err: any) {
 alert("Error: " + err.message);
 }
 };

 const handleCreateWebhook = async (e: React.FormEvent) => {
 e.preventDefault();
 if (!webhookUrl || !webhookSecret) return;
 try {
 const res = await api.developer.createWebhook(webhookUrl, webhookSecret, webhookEvents);
 setWebhooks([res, ...webhooks]);
 setWebhookUrl('');
 setWebhookSecret('');
 alert("Webhook endpoint registered successfully!");
 } catch (err: any) {
 alert("Error: " + err.message);
 }
 };

 const handleDeleteWebhook = async (id: number) => {
 if (!confirm("Delete this webhook?")) return;
 try {
 await api.developer.deleteWebhook(id);
 setWebhooks(webhooks.filter(w => w.id !== id));
 } catch (err: any) {
 alert("Error: " + err.message);
 }
 };

 const handleCreateWorkflow = async (e: React.FormEvent) => {
 e.preventDefault();
 if (!newWorkflowName || !workflowEmail) return;
 try {
 const res = await api.automations.createWorkflow(
 newWorkflowName,
 workflowTrigger,
 {},
 workflowAction,
 { email: workflowEmail }
 );
 setWorkflows([res, ...workflows]);
 setNewWorkflowName('');
 setWorkflowEmail('');
 alert("Workflow rule active!");
 } catch (err: any) {
 alert("Error: " + err.message);
 }
 };

 const handleDeleteWorkflow = async (id: number) => {
 if (!confirm("Delete this workflow?")) return;
 try {
 await api.automations.deleteWorkflow(id);
 setWorkflows(workflows.filter(w => w.id !== id));
 } catch (err: any) {
 alert("Error: " + err.message);
 }
 };

 const handleToggleWorkflow = async (id: number) => {
 try {
 const res = await api.automations.toggleWorkflow(id);
 setWorkflows(workflows.map(w => w.id === id ? res : w));
 } catch (err: any) {
 alert("Error: " + err.message);
 }
 };

 const handleToggleIntegration = async (providerName: string) => {
 try {
 const res = await api.integrations.toggle(providerName);
 setIntegrationsList(
 integrationsList.some(i => i.provider_name === providerName)
 ? integrationsList.map(i => i.provider_name === providerName ? res : i)
 : [...integrationsList, res]
 );
 } catch (err: any) {
 alert("Error: " + err.message);
 }
 };

 // --- WEBCAM VIDEO INTRO RECORDER LOGIC ---

 // After cameraActive flips to true, React has rendered the <video> element —
 // now it's safe to assign srcObject to it.
 useEffect(() => {
 if (cameraActive && recorderStreamRef.current && recordingPreviewRef.current) {
 recordingPreviewRef.current.srcObject = recorderStreamRef.current;
 recordingPreviewRef.current.play().catch(() => {});
 }
 }, [cameraActive]);

 const handleStartCamera = async () => {
 try {
 setRecordedVideoUrl(null);
 setRecordedBlob(null);
 const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
 recorderStreamRef.current = stream;
 // Don't assign srcObject here — the <video> element isn't mounted yet.
 // The useEffect above handles it once cameraActive becomes true.
 setCameraActive(true);
 } catch (e: any) {
 console.error('Failed to start camera:', e);
 alert('Could not access webcam or microphone: ' + e.message);
 }
 };

 const handleStopCamera = () => {
 if (mediaRecorderRef.current && recording) {
 mediaRecorderRef.current.stop();
 }
 if (recorderStreamRef.current) {
 recorderStreamRef.current.getTracks().forEach(t => t.stop());
 recorderStreamRef.current = null;
 }
 if (recordingPreviewRef.current) {
 recordingPreviewRef.current.srcObject = null;
 }
 setCameraActive(false);
 setRecording(false);
 };

 const getSupportedMimeType = () => {
 const types = [
 'video/webm;codecs=vp9,opus',
 'video/webm;codecs=vp8,opus',
 'video/webm',
 'video/mp4',
 '',
 ];
 return types.find(t => t === '' || MediaRecorder.isTypeSupported(t)) || '';
 };

 const handleStartRecording = () => {
 if (!recorderStreamRef.current) return;
 const chunks: Blob[] = [];
 const mimeType = getSupportedMimeType();
 const recorder = mimeType
 ? new MediaRecorder(recorderStreamRef.current, { mimeType })
 : new MediaRecorder(recorderStreamRef.current);

 recorder.ondataavailable = (e) => {
 if (e.data && e.data.size > 0) chunks.push(e.data);
 };
 recorder.onstop = () => {
 const blob = new Blob(chunks, { type: mimeType || 'video/webm' });
 setRecordedBlob(blob);
 setRecordedVideoUrl(URL.createObjectURL(blob));
 };
 mediaRecorderRef.current = recorder;
 recorder.start(100); // collect chunks every 100ms for reliability
 setRecording(true);
 };

 const handleStopRecording = () => {
 if (mediaRecorderRef.current && recording) {
 mediaRecorderRef.current.stop();
 setRecording(false);
 }
 };

 const handleUploadVideoFile = async (e: React.ChangeEvent<HTMLInputElement> | null, target: 'user' | 'candidate', candidateId?: number) => {
 let file: File | Blob | null = null;
 if (e && e.target.files && e.target.files[0]) {
 file = e.target.files[0];
 } else if (recordedBlob) {
 file = recordedBlob;
 }

 if (!file) {
 alert("No video file selected or recorded.");
 return;
 }

 try {
 if (target === 'user') {
 await api.auth.uploadVideo(file);
 } else {
 const id = candidateId || myCandidateProfile?.id;
 if (!id) {
 alert("No candidate profile found to attach video.");
 return;
 }
 await api.candidates.uploadVideo(id, file);
 }

 alert("Video introduction uploaded successfully!");
 handleStopCamera();
 setRecordedVideoUrl(null);
 setRecordedBlob(null);

 // Reload profile
 if (target === 'user') {
 const me = await api.auth.me();
 setUser(me);
 } else {
 await loadCandidates();
 }
 } catch (err: any) {
 alert("Failed to upload video: " + err.message);
 }
 };

 // --- COMMUNITY & WHISTLEBLOWER FORUM LOGIC ---
 const loadCommunityPosts = async () => {
 setCommunityLoading(true);
 try {
 const posts = await api.community.listPosts();
 setCommunityPosts(posts);
 } catch (e) {
 console.error("Failed to load community board posts:", e);
 } finally {
 setCommunityLoading(false);
 }
 };

 const handleCreatePost = async (e: React.FormEvent) => {
 e.preventDefault();
 if (!newPostTitle.trim() || !newPostContent.trim()) {
 alert("Title and content body are required.");
 return;
 }
 try {
 await api.community.createPost(
 newPostTitle,
 newPostContent,
 newPostType === 'whistleblower' ? true : newPostIsAnonymous,
 newPostType
 );
 setNewPostTitle('');
 setNewPostContent('');
 setNewPostIsAnonymous(true);
 setNewPostType('discussion');
 await loadCommunityPosts();
 alert("Post published on ATLAS Community successfully!");
 } catch (err: any) {
 alert("Failed to create post: " + err.message);
 }
 };

 const handleVotePost = async (postId: number, direction: 'up' | 'down') => {
 try {
 await api.community.vote(postId, direction);
 await loadCommunityPosts();
 } catch (e: any) {
 alert("Failed to record vote: " + e.message);
 }
 };

 const handleToggleComments = async (postId: number) => {
 const isExpanded = expandedPostIds.includes(postId);
 if (isExpanded) {
 setExpandedPostIds(prev => prev.filter(id => id !== postId));
 } else {
 setExpandedPostIds(prev => [...prev, postId]);
 try {
 const comments = await api.community.listComments(postId);
 setActivePostComments(prev => ({ ...prev, [postId]: comments }));
 } catch (e) {
 console.error("Failed to retrieve comments:", e);
 }
 }
 };

 const handleSubmitComment = async (postId: number) => {
 const text = newCommentText[postId] || "";
 const isAnon = newCommentIsAnonymous[postId] ?? true;
 if (!text.trim()) { alert("Comment content cannot be empty."); return; }
 try {
 await api.community.createComment(postId, text, isAnon);
 setNewCommentText(prev => ({ ...prev, [postId]: "" }));
 const comments = await api.community.listComments(postId);
 setActivePostComments(prev => ({ ...prev, [postId]: comments }));
 } catch (e: any) { alert("Failed to post comment: " + e.message); }
 };

 // --- CHAT ROOM LOGIC ---
 const loadChatChannels = async () => {
 try {
 const channels = await api.community.listChannels();
 setChatChannels(channels);
 // seed default channels if none exist
 if (channels.length === 0) {
 await api.community.createChannel('# general', 'General discussion for everyone');
 await api.community.createChannel('# jobs-talk', 'Talk about job openings and opportunities');
 await api.community.createChannel('# salary-confess', 'Anonymously share salary & compensation insights');
 await api.community.createChannel('# recruiter-rants', 'Vent about the hiring process');
 await api.community.createChannel('# whistleblower', 'Leak workplace misconduct anonymously');
 const fresh = await api.community.listChannels();
 setChatChannels(fresh);
 }
 } catch (e) { console.error('Failed to load chat channels', e); }
 };

 const selectChannel = async (channel: any) => {
 setActiveChannel(channel);
 setChatMessages([]);
 setChatRoomLoading(true);
 // clear existing poll
 if (chatPollRef.current) clearInterval(chatPollRef.current);
 const fetchMsgs = async () => {
 try {
 const msgs = await api.community.getMessages(channel.id);
 setChatMessages(msgs);
 } catch (e) { console.error(e); }
 };
 await fetchMsgs();
 setChatRoomLoading(false);
 // poll every 3 seconds for new messages
 chatPollRef.current = setInterval(fetchMsgs, 3000);
 };

 const sendChatMessage = async (e: React.FormEvent) => {
 e.preventDefault();
 if (!chatInput.trim() || !activeChannel) return;
 const text = chatInput;
 setChatInput('');
 try {
 await api.community.sendMessage(activeChannel.id, text, chatAnon);
 const msgs = await api.community.getMessages(activeChannel.id);
 setChatMessages(msgs);
 } catch (e: any) { console.error('Failed to send message', e); }
 };

 const handleCreateChannel = async (e: React.FormEvent) => {
 e.preventDefault();
 if (!newChannelName.trim()) return;
 try {
 await api.community.createChannel('# ' + newChannelName.trim(), newChannelDesc.trim() || 'Anonymous channel');
 setNewChannelName(''); setNewChannelDesc('');
 setShowCreateChannel(false);
 await loadChatChannels();
 } catch (e: any) { alert('Failed to create channel: ' + e.message); }
 };

 // auto-scroll chat to bottom on new messages
 useEffect(() => {
 if (chatMessagesEndRef.current) {
 chatMessagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
 }
 }, [chatMessages]);

 // load channels when community tab opens
 useEffect(() => {
 if (activeTab === 'community') {
 loadChatChannels();
 loadCommunityPosts();
 }
 return () => { if (chatPollRef.current) clearInterval(chatPollRef.current); };
 }, [activeTab]);

 // --- DEVELOPER SOFTWARE & SERVICES MARKETPLACE LOGIC ---
 const loadMarketplaceData = async () => {
 setMarketplaceLoading(true);
 try {
 const [prods, purchs] = await Promise.all([
 api.marketplace.listProducts(),
 api.marketplace.listPurchases()
 ]);
 setMarketplaceProducts(prods);
 setMarketplacePurchases(purchs);
 } catch (e) {
 console.error("Failed to load marketplace details:", e);
 } finally {
 setMarketplaceLoading(false);
 }
 };

 const handleCreateProduct = async (e: React.FormEvent) => {
 e.preventDefault();
 if (!newProductName.trim() || !newProductDescription.trim() || !newProductPrice.trim()) {
 alert("Product name, description, and price cannot be empty.");
 return;
 }
 const priceNum = parseFloat(newProductPrice);
 if (isNaN(priceNum) || priceNum < 0) {
 alert("Please enter a valid price (greater than or equal to 0).");
 return;
 }
 try {
 await api.marketplace.createProduct(
 newProductName,
 newProductDescription,
 priceNum,
 newProductCategory,
 newProductDownloadUrl || undefined
 );
 setNewProductName('');
 setNewProductDescription('');
 setNewProductPrice('');
 setNewProductCategory('software');
 setNewProductDownloadUrl('');
 await loadMarketplaceData();
 alert("Listing published on ATLAS Marketplace successfully!");
 } catch (e: any) {
 alert("Failed to publish listing: " + e.message);
 }
 };

 const handlePurchaseProduct = async (productId: number) => {
 try {
 const res = await api.marketplace.purchaseProduct(productId);
 alert(res.message);
 await loadMarketplaceData();
 } catch (e: any) {
 alert("Failed to purchase product: " + e.message);
 }
 };

 // --- ZOOM / MEET ROOM LOGIC ---
 const handleCreateMeetRoom = async () => {
 try {
 const res = await api.meet.createRoom();
 setActiveMeetRoom(res.room_code);
 } catch (e: any) {
 alert("Failed to create meeting room: " + e.message);
 }
 };

 const handleJoinMeetRoom = async (roomCode: string) => {
 if (!roomCode.trim()) return;
 try {
 const myId = 'user_' + Math.random().toString(36).substring(2, 11);
 (window as any)._meetMyId = myId;
 
 const userEmail = user?.email || 'Guest Participant';
 const res = await api.meet.joinRoom(roomCode, myId, userEmail);
 if (res.status !== 'success') {
 alert("Failed to join meeting space.");
 return;
 }

 // Try acquiring media stream with progressive fallback
 let stream: MediaStream | null = null;
 try {
 stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
 } catch (err1) {
 console.warn("Video/Audio access failed, trying audio-only:", err1);
 try {
 stream = await navigator.mediaDevices.getUserMedia({ video: false, audio: true });
 } catch (err2) {
 console.warn("Audio access failed, creating view-only stream:", err2);
 stream = new MediaStream();
 }
 }

 setMeetLocalStream(stream);
 setMeetIsJoined(true);

 const pcs = meetPeerConnectionsRef.current;

 // Initiate WebRTC offers to all existing participants in the room
 for (const other of (res.other_participants || [])) {
 const peerId = other.id;
 try {
 const pc = new RTCPeerConnection({
 iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
 });

 if (stream) {
 stream.getTracks().forEach(track => pc.addTrack(track, stream!));
 }

 pc.onicecandidate = (event) => {
 if (event.candidate) {
 api.meet.sendSignal(roomCode, myId, peerId, 'candidate', event.candidate);
 }
 };

 pc.ontrack = (event) => {
 const remoteStream = event.streams[0] || new MediaStream([event.track]);
 setMeetRemoteStreams(prev => ({ ...prev, [peerId]: remoteStream }));
 };

 const offer = await pc.createOffer();
 await pc.setLocalDescription(offer);
 await api.meet.sendSignal(roomCode, myId, peerId, 'offer', offer);
 pcs[peerId] = pc;
 } catch (pcErr) {
 console.error("Error creating initial offer for peer:", peerId, pcErr);
 }
 }

 // Start signaling poll loop
 const pollInterval = setInterval(async () => {
 try {
 const pollRes = await api.meet.poll(roomCode, myId);
 setMeetParticipants(pollRes.participants);

 for (const sig of pollRes.signals) {
 const sender = sig.sender_id;
 
 if (sig.type === 'offer') {
 const pc = new RTCPeerConnection({
 iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
 });
 
 if (stream) {
 stream.getTracks().forEach(track => pc.addTrack(track, stream!));
 }

 pc.onicecandidate = (event) => {
 if (event.candidate) {
 api.meet.sendSignal(roomCode, myId, sender, 'candidate', event.candidate);
 }
 };

 pc.ontrack = (event) => {
 const remoteStream = event.streams[0] || new MediaStream([event.track]);
 setMeetRemoteStreams(prev => ({ ...prev, [sender]: remoteStream }));
 };

 await pc.setRemoteDescription(new RTCSessionDescription(sig.data));
 const answer = await pc.createAnswer();
 await pc.setLocalDescription(answer);
 await api.meet.sendSignal(roomCode, myId, sender, 'answer', answer);

 pcs[sender] = pc;
 } 
 else if (sig.type === 'answer') {
 const pc = pcs[sender];
 if (pc) {
 await pc.setRemoteDescription(new RTCSessionDescription(sig.data));
 }
 } 
 else if (sig.type === 'candidate') {
 const pc = pcs[sender];
 if (pc) {
 await pc.addIceCandidate(new RTCIceCandidate(sig.data));
 }
 }
 }

 // clean up disconnected peers
 const activePeerIds = pollRes.participants.map((p: any) => p.id);
 for (const peerId of Object.keys(pcs)) {
 if (!activePeerIds.includes(peerId)) {
 pcs[peerId].close();
 delete pcs[peerId];
 setMeetRemoteStreams(prev => {
 const updated = { ...prev };
 delete updated[peerId];
 return updated;
 });
 }
 }
 } catch (e) {
 console.error("Meet signaling error:", e);
 }
 }, 1500);

 (window as any)._meetPollInterval = pollInterval;

 } catch (err: any) {
 alert("Failed to join meeting: " + err.message);
 }
 };

 const handleLeaveMeetRoom = async () => {
 if (activeMeetRoom) {
 const myId = (window as any)._meetMyId;
 if (myId) {
 try {
 await api.meet.leave(activeMeetRoom, myId);
 } catch (e) {
 console.error(e);
 }
 }
 }

 if (meetLocalStream) {
 meetLocalStream.getTracks().forEach(track => track.stop());
 }
 setMeetLocalStream(null);

 for (const key of Object.keys(meetPeerConnectionsRef.current)) {
 meetPeerConnectionsRef.current[key].close();
 }
 meetPeerConnectionsRef.current = {};
 setMeetRemoteStreams({});
 setMeetParticipants([]);
 setMeetIsJoined(false);
 setActiveMeetRoom(null);

 if ((window as any)._meetPollInterval) {
 clearInterval((window as any)._meetPollInterval);
 }
 };

 const handleMeetToggleMic = () => {
 if (meetLocalStream) {
 const audioTrack = meetLocalStream.getAudioTracks()[0];
 if (audioTrack) {
 audioTrack.enabled = !audioTrack.enabled;
 setMeetMicMuted(!audioTrack.enabled);
 }
 }
 };

 const handleMeetToggleVideo = () => {
 if (meetLocalStream) {
 const videoTrack = meetLocalStream.getVideoTracks()[0];
 if (videoTrack) {
 videoTrack.enabled = !videoTrack.enabled;
 setMeetVideoDisabled(!videoTrack.enabled);
 }
 }
 };

 const handleLogin = async (e: React.FormEvent) => {
 e.preventDefault();
 setAuthError('');
 try {
 if (isRegister) {
 const computedOrgName = orgName.trim() || `${email.split('@')[0]}'s Workspace`;
 const computedRole = selectedMode === 'for_hire' ? 'candidate' : 'recruiter';
 
 await api.auth.register(
 email,
 password,
 computedRole,
 computedOrgName,
 inviteCode.trim() || undefined
 );
 
 // Auto log in immediately after registration!
 await api.auth.login(email, password);
 setToken(localStorage.getItem('atlas_token'));
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
 console.error("Google login error:", err);
 alert(`Google Login failed: ${err.message || JSON.stringify(err)}`);
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
 <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#ffffff', letterSpacing: '0.05em' }}>
 ATLAS
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
 <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', border: '1px solid rgba(128, 128, 128, 0.2)' }}>
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
 {publicJob.location && <span> {publicJob.location}</span>}
 {publicJob.salary && <span> {publicJob.salary}</span>}
 {publicJob.employment_type && <span> {publicJob.employment_type}</span>}
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
 <CheckCircle size={48} className="pulse-glow" style={{ color: 'var(--accent-gold)', margin: '0 auto 16px auto' }} />
 <h4 style={{ fontSize: '18px', color: '#fff', marginBottom: '6px' }}>Application Submitted!</h4>
 <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Your profile has been created and linked. Recruiters will contact you directly.</p>
 </div>
 ) : (
 <form onSubmit={handlePublicApply} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
 {applyError && (
 <div style={{ padding: '12px', background: 'rgba(128, 128, 128, 0.1)', border: '1px solid rgba(128, 128, 128, 0.2)', borderRadius: '8px', color: '#ef4444', fontSize: '13px' }}>
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
 DEVELOPED AND DESIGNED BY ATLAS WORK INTELLIGENCE TEAM
 </footer>
 </main>
 </div>
 );
 }

 const renderMeetRoom = () => {
 const otherPeers = meetParticipants.filter(p => p.id !== (window as any)._meetMyId);
 const totalTiles = 1 + otherPeers.length;
 let gridStyle: React.CSSProperties = {
 display: 'grid',
 gap: '16px',
 width: '100%',
 height: '100%',
 maxHeight: '70vh'
 };
 if (totalTiles === 1) {
 gridStyle.gridTemplateColumns = '1fr';
 } else if (totalTiles === 2) {
 gridStyle.gridTemplateColumns = '1fr 1fr';
 } else if (totalTiles <= 4) {
 gridStyle.gridTemplateColumns = '1fr 1fr';
 gridStyle.gridTemplateRows = '1fr 1fr';
 } else {
 gridStyle.gridTemplateColumns = '1fr 1fr 1fr';
 gridStyle.gridTemplateRows = '1fr 1fr';
 }

 if (!meetIsJoined) {
 return (
 <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flex: 1, padding: '32px' }}>
 <div className="glass-panel" style={{ width: '100%', maxWidth: '480px', padding: '32px', textAlign: 'center' }}>
 <h3 style={{ fontSize: '20px', color: '#fff', marginBottom: '16px' }}>Join Meeting Room</h3>
 <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '24px' }}>
 You are about to enter room code: <strong style={{ color: '#fff', fontFamily: 'monospace' }}>{activeMeetRoom}</strong>
 </p>
 
 <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
 <button onClick={handleLeaveMeetRoom} className="btn-secondary" style={{ padding: '10px 20px', fontSize: '13px' }}>
 Cancel
 </button>
 <button onClick={() => handleJoinMeetRoom(activeMeetRoom!)} className="btn-primary lining-settings" style={{ padding: '10px 20px', fontSize: '13px' }}>
 Join Meet Room
 </button>
 </div>
 </div>
 </div>
 );
 }

 const publicMeetUrl = `${window.location.origin}${window.location.pathname}?meet=${activeMeetRoom}`;

 return (
 <div style={{ display: 'flex', flex: 1, height: 'calc(100vh - 60px)', padding: '24px', gap: '24px' }}>
 {/* Left Grid: Participant Tiles */}
 <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>
 <div style={gridStyle}>
 {/* Local Video — srcObject assigned once via stable ref */}
 <div className="glass-panel" style={{ position: 'relative', overflow: 'hidden', background: '#000', borderRadius: '12px', minHeight: '200px' }}>
 <video
 ref={el => {
 meetLocalVideoRef.current = el;
 if (el && meetLocalStream && el.srcObject !== meetLocalStream) {
 el.srcObject = meetLocalStream;
 el.play().catch(() => {});
 }
 }}
 autoPlay
 playsInline
 muted
 style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }}
 />
 <div style={{ position: 'absolute', bottom: '12px', left: '12px', background: 'rgba(0,0,0,0.5)', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', color: '#fff' }}>
 You ({user.email}) {meetMicMuted && ' Muted'}
 </div>
 </div>

 {/* Remote Videos — srcObject assigned once per stream via stable ref map */}
 {otherPeers.map((p) => {
 const remoteStream = meetRemoteStreams[p.id];
 return (
 <div key={p.id} className="glass-panel" style={{ position: 'relative', overflow: 'hidden', background: '#000', borderRadius: '12px', minHeight: '200px' }}>
 {remoteStream ? (
 <video
 ref={el => {
 if (el && meetRemoteVideoRefs.current[p.id] !== el) {
 meetRemoteVideoRefs.current[p.id] = el;
 el.srcObject = remoteStream;
 } else if (el && el.srcObject !== remoteStream) {
 // stream changed (e.g. reconnect) — update once
 el.srcObject = remoteStream;
 }
 }}
 autoPlay
 playsInline
 style={{ width: '100%', height: '100%', objectFit: 'cover' }}
 />
 ) : (
 <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%', color: 'var(--text-muted)' }}>
 Connecting audio/video streams...
 </div>
 )}
 <div style={{ position: 'absolute', bottom: '12px', left: '12px', background: 'rgba(0,0,0,0.5)', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', color: '#fff' }}>
 {p.name}
 </div>
 </div>
 );
 })}
 </div>

 {/* Meeting Space Bottom Controls */}
 <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', padding: '16px', borderRadius: '40px' }}>
 <button 
 onClick={handleMeetToggleMic} 
 className={meetMicMuted ? "btn-secondary" : "btn-primary"} 
 style={{ width: '48px', height: '48px', padding: 0, borderRadius: '50%', justifyContent: 'center', color: meetMicMuted ? '#808080' : 'inherit' }}
 >
 {meetMicMuted ? <MicOff size={18} /> : <Mic size={18} />}
 </button>

 <button 
 onClick={handleMeetToggleVideo} 
 className={meetVideoDisabled ? "btn-secondary" : "btn-primary"} 
 style={{ width: '48px', height: '48px', padding: 0, borderRadius: '50%', justifyContent: 'center', color: meetVideoDisabled ? '#808080' : 'inherit' }}
 >
 {meetVideoDisabled ? <VideoOff size={18} /> : <Video size={18} />}
 </button>

 <button 
 onClick={handleLeaveMeetRoom} 
 className="btn-primary" 
 style={{ width: '48px', height: '48px', padding: 0, borderRadius: '50%', justifyContent: 'center', background: '#808080', border: 'none', color: '#fff' }}
 >
 <PhoneOff size={18} />
 </button>
 </div>
 </div>

 {/* Right Sidebar: Share details & participants list */}
 <div className="glass-panel" style={{ width: '320px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
 <div>
 <h4 style={{ fontSize: '14px', color: '#fff', marginBottom: '8px' }}>Invite Link</h4>
 <div style={{ display: 'flex', gap: '8px' }}>
 <input 
 type="text" 
 readOnly 
 className="input-field" 
 value={publicMeetUrl} 
 style={{ fontSize: '11px', fontFamily: 'monospace', flex: 1 }}
 />
 <button 
 type="button"
 onClick={() => {
 copyToClipboard(publicMeetUrl);
 setCopyMeetSuccess(true);
 setTimeout(() => setCopyMeetSuccess(false), 2500);
 }}
 className="btn-primary"
 style={{ padding: '8px 12px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px', borderRadius: '10px', flexShrink: 0 }}
 title="Copy Invite Link"
 >
 <Copy size={14} />
 <span>{copyMeetSuccess ? 'Copied!' : 'Copy'}</span>
 </button>
 </div>
 <span style={{ fontSize: '10px', color: 'var(--text-dim)', marginTop: '6px', display: 'block' }}>
 Share this link to invite candidates or guests to your meeting.
 </span>
 </div>

 <div style={{ flex: 1 }}>
 <h4 style={{ fontSize: '14px', color: '#fff', marginBottom: '12px' }}>Participants ({meetParticipants.length})</h4>
 <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
 {meetParticipants.map(p => (
 <div key={p.id} style={{ display: 'flex', justifyItems: 'center', justifyContent: 'space-between', padding: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '8px' }}>
 <span style={{ fontSize: '13px', color: '#fff' }}>{p.name}</span>
 <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
 {p.id === (window as any)._meetMyId ? 'You' : 'Guest'}
 </span>
 </div>
 ))}
 </div>
 </div>
 </div>
 </div>
 );
 };

 const copyToClipboard = (text: string) => {
 if (navigator.clipboard && window.isSecureContext) {
 navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
 } else {
 fallbackCopy(text);
 }
 };

 const fallbackCopy = (text: string) => {
 const textArea = document.createElement("textarea");
 textArea.value = text;
 textArea.style.position = "fixed";
 textArea.style.left = "-999999px";
 textArea.style.top = "-999999px";
 document.body.appendChild(textArea);
 textArea.focus();
 textArea.select();
 try {
 document.execCommand('copy');
 } catch (err) {
 console.error('Fallback copy failed', err);
 }
 document.body.removeChild(textArea);
 };

 const renderMeetChoiceModal = () => {
 if (!showMeetChoiceModal) return null;

 return (
 <div className="modal-overlay" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(12px)', zIndex: 9999, padding: '20px' }}>
 <div className="glass-panel" style={{ width: '100%', maxWidth: '440px', padding: '32px', borderRadius: '24px', border: '1px solid var(--border-glass)', boxShadow: '0 20px 50px rgba(0,0,0,0.6)', textAlign: 'center', position: 'relative' }}>
 <button 
 onClick={() => setShowMeetChoiceModal(false)}
 style={{ position: 'absolute', top: '16px', right: '16px', background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
 >
 <X size={20} />
 </button>

 <div style={{ width: '56px', height: '56px', borderRadius: '50%', background: 'rgba(255,207,135,0.1)', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px auto' }}>
 <Video size={28} />
 </div>

 <h3 style={{ fontSize: '20px', color: '#fff', fontWeight: 600, marginBottom: '8px' }}>Meeting Space</h3>
 <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '24px' }}>
 Choose an option to start a new instant meeting or join an existing meeting room.
 </p>

 <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
 {/* Option 1: Start Instant Meeting */}
 <button
 onClick={() => {
 setShowMeetChoiceModal(false);
 handleCreateMeetRoom();
 }}
 className="btn-primary lining-settings"
 style={{ width: '100%', padding: '14px', fontSize: '14px', borderRadius: '12px', justifyContent: 'center', fontWeight: 600 }}
 >
 Start New Meeting
 </button>

 <div style={{ display: 'flex', alignItems: 'center', gap: '12px', margin: '4px 0' }}>
 <div style={{ flex: 1, height: '1px', background: 'var(--border-glass)' }} />
 <span style={{ fontSize: '11px', color: 'var(--text-dim)', textTransform: 'uppercase' }}>OR</span>
 <div style={{ flex: 1, height: '1px', background: 'var(--border-glass)' }} />
 </div>

 {/* Option 2: Join Existing Meeting */}
 <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', textAlign: 'left' }}>
 <label style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>Join Existing Room</label>
 <div style={{ display: 'flex', gap: '8px' }}>
 <input 
 type="text" 
 className="input-field" 
 placeholder="Enter Room Code (e.g. abc-defg-hij)"
 value={meetChoiceInputCode}
 onChange={e => setMeetChoiceInputCode(e.target.value)}
 style={{ fontSize: '12px', fontFamily: 'monospace' }}
 />
 <button
 onClick={() => {
 if (!meetChoiceInputCode.trim()) {
 alert("Please enter a valid room code.");
 return;
 }
 setActiveMeetRoom(meetChoiceInputCode.trim());
 setShowMeetChoiceModal(false);
 setMeetChoiceInputCode('');
 }}
 className="btn-secondary"
 style={{ padding: '10px 16px', fontSize: '13px', borderRadius: '10px', flexShrink: 0 }}
 >
 Join
 </button>
 </div>
 </div>
 </div>
 </div>
 </div>
 );
 };

 if (activeMeetRoom) {
 return (
 <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: '#0b0c10', color: '#fff' }}>
 {renderPreloader()}
 {renderMeetRoom()}
 </div>
 );
 }

 if (!token || !user) {
 return (
 <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '20px' }}>
 <svg style={{ position: 'absolute', width: 0, height: 0 }} xmlns="http://www.w3.org/2000/svg">
 <defs>
 <filter id="lg-dist" x="-20%" y="-20%" width="140%" height="140%" colorInterpolationFilters="linearRGB">
 <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" seed="2" result="noise" />
 <feDisplacementMap in="SourceGraphic" in2="noise" scale="8" xChannelSelector="R" yChannelSelector="G" result="displaced" />
 <feGaussianBlur in="displaced" stdDeviation="1.2" />
 </filter>
 </defs>
 </svg>
 {renderPreloader()}
 <div style={{ position: 'relative', width: '100%', maxWidth: '440px', borderRadius: '28px', overflow: 'hidden', boxShadow: '0 32px 80px rgba(0,0,0,0.50), 0 4px 16px rgba(0,0,0,0.30)' }}>
 <div style={{ position: 'absolute', inset: 0, zIndex: 0, backdropFilter: 'blur(40px) saturate(200%)', WebkitBackdropFilter: 'blur(40px) saturate(200%)' }} />
 <div style={{ position: 'absolute', inset: 0, zIndex: 1, background: 'rgba(255,255,255,0.16)' }} />
 <div style={{ position: 'absolute', inset: 0, zIndex: 2, borderRadius: '28px', pointerEvents: 'none', boxShadow: 'inset 1.5px 1.5px 0 rgba(255,255,255,0.72), inset 0 0 18px rgba(255,255,255,0.07), inset 0 -1px 0 rgba(0,0,0,0.16)', border: '1px solid rgba(255,255,255,0.22)' }} />
 <div style={{ position: 'relative', zIndex: 3, padding: '40px 36px' }}>
 <div style={{ textAlign: 'center', marginBottom: '28px' }}>
 <div style={{ display: 'inline-flex', padding: '14px', background: 'rgba(255,255,255,0.15)', borderRadius: '20px', marginBottom: '16px', boxShadow: 'inset 1px 1px 0 rgba(255,255,255,0.5), 0 4px 12px rgba(0,0,0,0.20)' }}>
 <TitanLogo size={56} className="pulse-glow" />
 </div>
 <h2 style={{ fontSize: '26px', color: '#fff', marginBottom: '8px', letterSpacing: '-0.02em', fontWeight: 700 }}>ATLAS</h2>
 <p style={{ color: 'rgba(255,255,255,0.62)', fontSize: '14px' }}>AI-Powered Work Intelligence System</p>
 </div>
 <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
 {authError && (
 <div style={{ display: 'flex', gap: '8px', padding: '12px 14px', background: 'rgba(128,128,128,0.15)', border: '1px solid rgba(128,128,128,0.35)', borderRadius: '12px', color: '#ff6b89', fontSize: '13px' }}>
 <AlertCircle size={16} style={{ flexShrink: 0, marginTop: '1px' }} />
 <span>{authError}</span>
 </div>
 )}
 {/* Role Toggle Selector */}
 <div>
 <label style={{ display: 'block', color: 'rgba(255,255,255,0.65)', fontSize: '12px', fontWeight: 500, marginBottom: '6px' }}>Account Role</label>
 <div style={{ display: 'flex', gap: '6px', padding: '4px', background: 'rgba(255,255,255,0.10)', borderRadius: '14px', border: '1px solid rgba(255,255,255,0.16)' }}>
 <button type="button" onClick={() => setSelectedMode('hire')} style={{ flex: 1, padding: '9px', borderRadius: '10px', border: 'none', cursor: 'pointer', fontSize: '12px', fontWeight: 600, fontFamily: 'var(--font-body)', background: selectedMode !== 'for_hire' ? 'rgba(255,255,255,0.90)' : 'transparent', color: selectedMode !== 'for_hire' ? '#000' : 'rgba(255,255,255,0.70)', transition: 'all 0.2s ease' }}>Recruiter / Employer</button>
 <button type="button" onClick={() => setSelectedMode('for_hire')} style={{ flex: 1, padding: '9px', borderRadius: '10px', border: 'none', cursor: 'pointer', fontSize: '12px', fontWeight: 600, fontFamily: 'var(--font-body)', background: selectedMode === 'for_hire' ? 'rgba(255,255,255,0.90)' : 'transparent', color: selectedMode === 'for_hire' ? '#000' : 'rgba(255,255,255,0.70)', transition: 'all 0.2s ease' }}>Candidate / Job Seeker</button>
 </div>
 </div>

 <div>
 <label style={{ display: 'block', color: 'rgba(255,255,255,0.65)', fontSize: '12px', fontWeight: 500, marginBottom: '6px' }}>Email Address</label>
 <input type="email" required className="input-field" value={email} onChange={e => setEmail(e.target.value)} placeholder={selectedMode === 'for_hire' ? "candidate@example.com" : "recruiter@company.com"} />
 </div>

 <div>
 <label style={{ display: 'block', color: 'rgba(255,255,255,0.65)', fontSize: '12px', fontWeight: 500, marginBottom: '6px' }}>Password</label>
 <input type="password" required className="input-field" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" />
 </div>

 {isRegister && selectedMode !== 'for_hire' && (
 <div>
 <label style={{ display: 'block', color: 'rgba(255,255,255,0.65)', fontSize: '12px', fontWeight: 500, marginBottom: '6px' }}>Organization Name</label>
 <input type="text" required className="input-field" value={orgName} onChange={e => setOrgName(e.target.value)} placeholder="ACME Corp" />
 </div>
 )}

 <button type="submit" className="btn-primary" style={{ justifyContent: 'center', width: '100%', marginTop: '6px', padding: '13px', fontSize: '15px', borderRadius: '14px' }}>
 {isRegister ? 'Create Account' : 'Sign In to ATLAS'}
 </button>
 </form>
 <div style={{ textAlign: 'center', marginTop: '18px' }}>
 <button type="button" onClick={() => { setIsRegister(!isRegister); setAuthError(''); }} style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.55)', cursor: 'pointer', fontSize: '13px', fontFamily: 'var(--font-body)' }}>
 {isRegister ? 'Already have an account? Sign in' : 'New to ATLAS? Create an account'}
 </button>
 </div>
 </div>
 </div>
 {showGoogleModal && (
 <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(16px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 2000, padding: '16px' }}>
 <div className="glass-panel animate-fade-in" style={{ width: '100%', maxWidth: '380px', padding: '32px' }}>
 <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '24px' }}>
 <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginBottom: '14px' }}>
 <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
 <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
 <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
 <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
 </svg>
 <h3 style={{ fontSize: '17px', fontWeight: 600, color: '#fff' }}>Choose an Account</h3>
 <span style={{ fontSize: '12px', color: 'rgba(255,255,255,0.55)', marginTop: '4px' }}>to continue to ATLAS</span>
 </div>
 <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
 {[{ email: 'recruiter.billing@gmail.com', name: 'Recruiter Billing', initial: 'R', grad: 'linear-gradient(135deg,#6c3de8,#9b5de5)' }, { email: 'gaurav.founder@company.com', name: 'Gaurav Founder', initial: 'G', grad: 'linear-gradient(135deg,#00b4d8,#0077b6)' }].map(acc => (
 <div key={acc.email} onClick={() => handleGoogleLogin(acc.email)}
 style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 14px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)', borderRadius: '14px', cursor: 'pointer', transition: 'all 0.2s ease' }}
 onMouseEnter={e => { e.currentTarget.style.background='rgba(255,255,255,0.12)'; e.currentTarget.style.borderColor='rgba(255,255,255,0.25)'; }}
 onMouseLeave={e => { e.currentTarget.style.background='rgba(255,255,255,0.06)'; e.currentTarget.style.borderColor='rgba(255,255,255,0.12)'; }}>
 <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: acc.grad, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '15px', fontWeight: 700, flexShrink: 0 }}>{acc.initial}</div>
 <div>
 <div style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>{acc.name}</div>
 <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.50)', marginTop: '2px' }}>{acc.email}</div>
 </div>
 </div>
 ))}
 </div>
 <button onClick={() => setShowGoogleModal(false)} className="btn-secondary" style={{ width: '100%', marginTop: '16px', justifyContent: 'center', padding: '10px', fontSize: '13px', borderRadius: '12px' }}>Cancel</button>
 </div>
 </div>
 )}
 </div>
 );
 }

 return (
 <div className={densityMode === 'compact' ? 'theme-compact' : ''} style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
 {renderPreloader()}
 {renderMeetChoiceModal()}
 {/* Vertical Floating Navigation Bar */}
 <div 
 className="glass-panel" 
 style={{ 
 position: 'fixed', 
 left: '20px', 
 top: '50%', 
 transform: 'translateY(-50%)', 
 display: 'flex', 
 flexDirection: 'column', 
 gap: '20px', 
 padding: '24px 12px', 
 zIndex: 1000, 
 borderRadius: '32px', 
 background: 'rgba(10, 10, 12, 0.45)', 
 backdropFilter: 'blur(20px)', 
 border: '1px solid var(--border-glass)',
 boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)' 
 }}
 >
 <button 
 onClick={() => setShowMeetChoiceModal(true)}
 className="btn-secondary" 
 style={{ width: '40px', height: '40px', borderRadius: '50%', padding: 0, justifyContent: 'center', color: 'var(--accent-gold)' }}
 title="Meeting Space"
 >
 <Video size={18} />
 </button>

 <button 
 onClick={() => setActiveTab('community')}
 className={activeTab === 'community' ? 'btn-primary lining-settings' : 'btn-secondary'} 
 style={{ width: '40px', height: '40px', borderRadius: '50%', padding: 0, justifyContent: 'center' }}
 title="Atlas Community Board"
 >
 <MessageSquare size={18} />
 </button>

 <button 
 onClick={() => setActiveTab('analytics')}
 className={activeTab === 'analytics' ? 'btn-primary lining-settings' : 'btn-secondary'} 
 style={{ width: '40px', height: '40px', borderRadius: '50%', padding: 0, justifyContent: 'center' }}
 title="BI Analytics"
 >
 <TrendingUp size={18} />
 </button>

 <button 
 onClick={() => setActiveTab('academy')}
 className={activeTab === 'academy' ? 'btn-primary' : 'btn-secondary'} 
 style={{ width: '40px', height: '40px', borderRadius: '50%', padding: 0, justifyContent: 'center', background: activeTab === 'academy' ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : undefined }}
 title="Atlas Academy"
 >
 <GraduationCap size={18} />
 </button>

 <button 
 onClick={() => setActiveTab('resume_builder')}
 className={activeTab === 'resume_builder' ? 'btn-primary' : 'btn-secondary'} 
 style={{ width: '40px', height: '40px', borderRadius: '50%', padding: 0, justifyContent: 'center', background: activeTab === 'resume_builder' ? 'linear-gradient(135deg, #10b981, #059669)' : undefined }}
 title="Career Hub"
 >
 <FileText size={18} />
 </button>

 <button 
 onClick={() => setActiveTab('copilot')}
 className={activeTab === 'copilot' ? 'btn-primary lining-copilot' : 'btn-secondary'} 
 style={{ width: '46px', height: '46px', borderRadius: '50%', padding: 0, justifyContent: 'center' }}
 title="Ask Nova"
 >
 <AtlasNovaLogo size={24} />
 </button>
 </div>
 {/* Top Header — full-width, positioned absolutely over the sidebar too */}
 <header style={{
 position: 'sticky',
 top: 0,
 zIndex: 50,
 width: '100%',
 padding: '14px 32px 14px 100px',
 display: 'flex',
 justifyContent: 'space-between',
 alignItems: 'center',
 backdropFilter: 'blur(40px) saturate(200%)',
 WebkitBackdropFilter: 'blur(40px) saturate(200%)',
 background: 'rgba(255,255,255,0.12)',
 borderBottom: '1px solid rgba(255,255,255,0.14)',
 boxShadow: 'inset 0 -1px 0 rgba(255,255,255,0.08), inset 0 1px 0 rgba(255,255,255,0.22), 0 4px 24px rgba(0,0,0,0.20)',
 }}>
 <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
 <TitanLogo size={36} />
 <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#ffffff', letterSpacing: '0.05em' }}>
 ATLAS
 </h1>
 </div>
 <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
 <span style={{ fontSize: '13px', color: 'var(--text-muted)', padding: '6px 12px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-glass)', borderRadius: '20px' }}>
 {selectedMode === 'for_hire' ? 'Candidate Mode' : 'Recruiter Mode'}: {user.email}
 </span>
 <button onClick={handleLogout} className="btn-secondary" style={{ padding: '8px 12px', fontSize: '12px' }}>
 <LogOut size={14} />
 <span>Sign Out</span>
 </button>
 </div>
 </header>

 {/* Tabs Switcher */}
 <div style={{ maxWidth: '1200px', width: '100%', margin: '24px auto 0 auto', padding: '0 16px 0 96px' }}>
 <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '8px' }}>
 {selectedMode === 'for_hire' ? (
 <>
 <button 
 onClick={() => setActiveTab('copilot')}
 className={activeTab === 'copilot' ? 'btn-primary lining-copilot' : 'btn-secondary lining-copilot'} 
 style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px', display: 'flex', alignItems: 'center', gap: '8px' }}
 >
 <AtlasNovaLogo size={16} /> Career Nova
 </button>
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
 onClick={() => {
 setActiveTab('interview_prep');
 setPrepJob(null);
 }}
 className={activeTab === 'interview_prep' ? 'btn-primary lining-copilot' : 'btn-secondary lining-copilot'} 
 style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
 >
 <Award size={16} /> Interview Prep Desk
 </button>
 <button 
 onClick={() => setActiveTab('community')}
 className={activeTab === 'community' ? 'btn-primary lining-settings' : 'btn-secondary lining-settings'} 
 style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
 >
 <MessageSquare size={16} /> Community
 </button>
 <button 
 onClick={() => setActiveTab('marketplace')}
 className={activeTab === 'marketplace' ? 'btn-primary lining-settings' : 'btn-secondary lining-settings'} 
 style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
 >
 <ShoppingBag size={16} style={{ color: 'var(--accent-cyan)' }} /> Developer Store
 </button>
 <button 
 onClick={() => setActiveTab('settings')}
 className={activeTab === 'settings' ? 'btn-primary lining-settings' : 'btn-secondary lining-settings'} 
 style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
 >
 <Settings size={16} /> Settings
 </button>
 </>
 ) : (
 <>
 <button 
 onClick={() => setActiveTab('copilot')}
 className={activeTab === 'copilot' ? 'btn-primary lining-copilot' : 'btn-secondary lining-copilot'} 
 style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px', display: 'flex', alignItems: 'center', gap: '8px' }}
 >
 <AtlasNovaLogo size={16} /> Recruiter Nova
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
 onClick={() => setActiveTab('community')}
 className={activeTab === 'community' ? 'btn-primary lining-settings' : 'btn-secondary lining-settings'} 
 style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
 >
 <MessageSquare size={16} /> Community
 </button>
 <button 
 onClick={() => setActiveTab('marketplace')}
 className={activeTab === 'marketplace' ? 'btn-primary lining-settings' : 'btn-secondary lining-settings'} 
 style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
 >
 <Sparkles size={16} style={{ color: 'var(--accent-cyan)' }} /> Developer Store
 </button>
 <button 
 onClick={() => setActiveTab('analytics')}
 className={activeTab === 'analytics' ? 'btn-primary lining-settings' : 'btn-secondary lining-settings'} 
 style={{ padding: '10px 16px', fontSize: '14px', borderRadius: '30px' }}
 >
 <TrendingUp size={16} /> Analytics
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
 <main style={{ flex: 1, maxWidth: '1200px', width: '100%', margin: '0 auto', padding: '24px 16px 24px 96px' }}>

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
 {job.location || 'Remote'} | {job.salary || 'Salary Undisclosed'}
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
 <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '24px', alignItems: 'start' }}>
 {/* Interview Interface */}
 <div className="glass-panel lining-copilot" style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-glass)', paddingBottom: '16px' }}>
 <div>
 <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
 <span style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--accent-orange)', fontWeight: 600 }}>
 Round {prepRound} of 5
 </span>
 {prepCategory && (
 <span style={{ fontSize: '11px', background: 'rgba(201,168,76,0.15)', border: '1px solid rgba(201,168,76,0.3)', color: '#c9a84c', padding: '2px 8px', borderRadius: '12px' }}>
 {prepCategory}
 </span>
 )}
 </div>
 <h3 style={{ fontSize: '18px', color: '#fff', marginTop: '4px' }}>{prepJob.title} Mock Interview</h3>
 </div>

 {/* Voice Read Aloud Question Button */}
 <button
 type="button"
 onClick={() => speakText(prepQuestion)}
 className="btn-secondary"
 style={{ padding: '6px 12px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}
 title="Read Question Aloud"
 >
 <Volume2 size={14} /> Read Question
 </button>
 </div>

 {prepLoading ? (
 <div style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
 <div className="pulse-glow" style={{ fontSize: '14px' }}>Atlas AI is reviewing your answer & generating next question...</div>
 </div>
 ) : prepFinished ? (
 <div style={{ padding: '32px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', background: 'rgba(201,168,76,0.05)', border: '1px solid rgba(201,168,76,0.2)', borderRadius: '12px' }}>
 <div style={{ fontSize: '48px' }}></div>
 <h3 style={{ fontSize: '20px', color: '#fff', fontWeight: 700 }}>Mock Interview Completed!</h3>
 <p style={{ color: 'var(--text-muted)', fontSize: '13px', maxWidth: '440px', lineHeight: '1.6' }}>
 Awesome job! You answered all 5 interview rounds for <strong>{prepJob.title}</strong>. Review your performance breakdown and gold-standard model answers on the right.
 </p>
 <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginTop: '8px' }}>
 <span style={{ fontSize: '14px', color: '#c9a84c', fontWeight: 700, background: 'rgba(201,168,76,0.15)', padding: '6px 16px', borderRadius: '20px', border: '1px solid #c9a84c' }}>
 +150 XP Earned! 
 </span>
 <button onClick={() => handleStartPrep(prepJob)} className="btn-primary lining-jobs" style={{ padding: '8px 20px' }}>
 Retake Interview
 </button>
 </div>
 </div>
 ) : (
 <>
 <div style={{ background: 'rgba(255,255,255,0.02)', padding: '20px', borderRadius: '8px', borderLeft: '3px solid var(--accent-orange)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
 <span style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>Question {prepRound}</span>
 <p style={{ fontSize: '15px', color: '#fff', lineHeight: '1.6', margin: 0 }}>{prepQuestion}</p>
 {prepHint && (
 <div style={{ fontSize: '12px', color: 'rgba(201,168,76,0.8)', background: 'rgba(201,168,76,0.06)', padding: '8px 12px', borderRadius: '6px', marginTop: '6px' }}>
 <strong>Tip:</strong> {prepHint}
 </div>
 )}
 </div>

 <form onSubmit={handleSubmitPrepAnswer} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
 <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Your Answer</label>
 {/* Mic Answer Button */}
 <button
 type="button"
 onClick={handleToggleListening}
 className={isListening ? "btn-primary pulse-glow" : "btn-secondary"}
 style={{ padding: '4px 12px', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '5px' }}
 >
 <Mic size={13} /> {isListening ? 'Listening...' : 'Dictate Answer'}
 </button>
 </div>

 <textarea 
 required
 rows={6}
 className="input-field"
 placeholder={isListening ? " Listening to your response... speak clearly..." : "Type or speak your technical response here. Explain concepts, design decisions, and measurable outcomes..."}
 value={prepAnswer}
 onChange={e => setPrepAnswer(e.target.value)}
 style={{ resize: 'vertical', minHeight: '130px', background: 'rgba(255,255,255,0.01)', fontSize: '14px', lineHeight: '1.6' }}
 />

 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px' }}>
 <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
 {prepAnswer.split(/\s+/).filter(Boolean).length} words
 </span>
 <button 
 type="submit"
 disabled={!prepAnswer.trim() || prepLoading}
 className="btn-primary lining-copilot"
 style={{ padding: '10px 24px' }}
 >
 Submit Answer & Next →
 </button>
 </div>
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
 <span style={{ color: 'var(--text-muted)' }}>Rounds Answered</span>
 <span style={{ color: '#fff', fontWeight: 600 }}>{prepHistory.length} / 5</span>
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

 <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px', maxHeight: '480px', overflowY: 'auto' }}>
 <h4 style={{ fontSize: '13px', color: '#fff', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Round Feedback & Gold Answers</h4>
 {prepHistory.length === 0 ? (
 <p style={{ color: 'var(--text-dim)', fontSize: '12px', textAlign: 'center', padding: '16px 0' }}>No rounds evaluated yet. Submit your first response to see AI feedback!</p>
 ) : (
 prepHistory.map((item, idx) => (
 <div key={idx} style={{ borderBottom: idx < prepHistory.length - 1 ? '1px solid var(--border-glass)' : 'none', paddingBottom: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
 <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>Round {prepHistory.length - idx}</span>
 <span style={{ fontSize: '11px', color: '#c9a84c', background: 'rgba(201,168,76,0.1)', border: '1px solid rgba(201,168,76,0.2)', padding: '2px 8px', borderRadius: '12px', fontWeight: 600 }}>
 {item.score}
 </span>
 </div>
 <p style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic', margin: 0 }}>Q: {item.question}</p>
 <p style={{ fontSize: '12px', color: '#fff', margin: 0 }}>A: {item.answer}</p>
 <div style={{ background: 'rgba(255,255,255,0.02)', padding: '8px 12px', borderRadius: '6px', fontSize: '11.5px', color: 'var(--text-muted)', borderLeft: '2px solid #22c55e' }}>
 <strong>Feedback:</strong> {item.feedback}
 </div>
 {item.modelAnswer && (
 <div style={{ background: 'rgba(201,168,76,0.04)', padding: '8px 12px', borderRadius: '6px', fontSize: '11.5px', color: '#c9a84c', borderLeft: '2px solid #c9a84c' }}>
 <strong>Gold Answer:</strong> {item.modelAnswer}
 </div>
 )}
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
 <span> {myCandidateProfile.email}</span>
 {myCandidateProfile.phone && <span> {myCandidateProfile.phone}</span>}
 {myCandidateProfile.location && <span> {myCandidateProfile.location}</span>}
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
 <Sparkles size={16} style={{ color: 'var(--accent-gold)' }} />
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
 <span style={{ color: 'var(--accent-gold)' }}> Complete</span>
 </div>
 <div style={{ display: 'flex', justifyContent: 'space-between' }}>
 <span>Skills Tagged</span>
 <span style={{ color: 'var(--accent-gold)' }}>{myCandidateProfile.skills.length} tagged</span>
 </div>
 <div style={{ display: 'flex', justifyContent: 'space-between' }}>
 <span>Work Experience</span>
 <span style={{ color: 'var(--accent-gold)' }}>{myCandidateProfile.experience?.length || 0} items</span>
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
 <div style={{ marginTop: '24px', padding: '12px', background: 'rgba(128, 128, 128, 0.1)', border: '1px solid rgba(128, 128, 128, 0.2)', borderRadius: '8px', fontSize: '13px', color: '#ef4444' }}>
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
 <span> {j.location || 'Remote'}</span>
 <span> {j.salary || 'N/A'}</span>
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
 <span> {selectedJob.location || 'Remote'}</span>
 <span> {selectedJob.salary || 'N/A'}</span>
 <span> {selectedJob.employment_type || 'Full-time'}</span>
 <span>⏳ Exp: {selectedJob.experience_years} years</span>
 </div>
 </div>
 
 <div>
 {appliedJobId === selectedJob.id ? (
 <span style={{ padding: '8px 16px', fontSize: '13px', background: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.2)', borderRadius: '6px', color: '#22c55e', fontWeight: 600, display: 'inline-block' }}>
 Applied
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
 <span style={{ fontSize: '12px', color: 'var(--accent-gold)', fontStyle: 'italic' }}>None! You match all required skills!</span>
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
 <Sparkles size={16} style={{ color: 'var(--accent-gold)' }} />
 <span>{uploadStatus}</span>
 </div>
 )}
 {uploadError && (
 <div style={{ padding: '12px 16px', background: 'rgba(128, 128, 128, 0.1)', border: '1px solid rgba(128, 128, 128, 0.2)', borderRadius: '8px', marginBottom: '16px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px', color: '#ef4444' }}>
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
 border: '1px solid', borderColor: selectedCandidate?.id === c.id ? 'var(--accent-gold)' : 'var(--border-glass)',
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
 style={{ background: 'none', border: 'none', color: 'rgba(128, 128, 128, 0.7)', cursor: 'pointer', padding: '4px' }}
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
 {/* Real-time Call Option */}
 <div style={{ paddingBottom: '16px', borderBottom: '1px solid var(--border-glass)' }}>
 <button 
 onClick={() => handleInitiateCall(selectedCandidate)}
 className="btn-primary lining-candidates"
 style={{ width: '100%', justifyContent: 'center', gap: '8px', fontSize: '13px', padding: '10px' }}
 >
 <Phone size={14} />
 <span>Initiate Call Desk Session</span>
 </button>
 </div>
 
 {/* Candidate Video Introduction Subsection */}
 {selectedCandidate.video_path && (
 <div style={{ paddingBottom: '16px', borderBottom: '1px solid var(--border-glass)' }}>
 <h5 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '8px' }}>Video Introduction Pitch</h5>
 <video 
 src={selectedCandidate.video_path} 
 controls 
 style={{ width: '100%', borderRadius: '8px', background: '#000', border: '1px solid var(--border-glass)' }} 
 />
 </div>
 )}

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
 border: '1px solid', borderColor: selectedJob?.id === j.id ? 'var(--accent-gold)' : 'var(--border-glass)',
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
 <Sparkles size={32} className="pulse-glow" style={{ margin: '0 auto 16px auto', color: 'var(--accent-gold)' }} />
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
 <div style={{ fontSize: '18px', color: 'var(--accent-gold)', fontWeight: 700 }}>
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
 <Sparkles size={32} className="pulse-glow" style={{ margin: '0 auto 16px auto', color: 'var(--accent-gold)' }} />
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

 {/* Nova Header */}
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-glass)', paddingBottom: '14px', marginBottom: '8px' }}>
 <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
 {/* Animated Nova avatar */}
 <div style={{ position: 'relative' }}>
 <div style={{
 position: 'absolute', inset: -4, borderRadius: '50%',
 background: 'conic-gradient(from 0deg, #c9a84c, #e8c97a, #c9a84c)',
 opacity: isSpeaking ? 1 : 0,
 animation: isSpeaking ? 'nova-ring 1.2s linear infinite' : 'none',
 transition: 'opacity 0.3s'
 }} />
 <AtlasNovaLogo size={38} />
 </div>
 <div>
 <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
 <span style={{ fontSize: '17px', fontWeight: 700, color: '#fff', letterSpacing: '0.04em' }}>Nova</span>
 {isSpeaking && (
 <span style={{ fontSize: '10px', color: '#c9a84c', display: 'flex', alignItems: 'center', gap: '4px' }}>
 <span className="nova-speaking-dot" /><span className="nova-speaking-dot" style={{ animationDelay: '0.15s' }} /><span className="nova-speaking-dot" style={{ animationDelay: '0.3s' }} />
 speaking
 </span>
 )}
 {isListening && !isSpeaking && (
 <span style={{ fontSize: '10px', color: '#22c55e', display: 'flex', alignItems: 'center', gap: '4px' }}>
 <span className="nova-listening-pulse" /> listening
 </span>
 )}
 {!isSpeaking && !isListening && <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>AI career companion · online</span>}
 </div>
 <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '1px' }}>Powered by phi4-mini · 100% local · private</div>
 </div>
 </div>
 <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
 {/* Human Female & Male Voice Pack Selector */}
 <div style={{ display: 'flex', gap: '3px', background: 'rgba(255,255,255,0.06)', borderRadius: '20px', padding: '2px', border: '1px solid var(--border-glass)', alignItems: 'center' }}>
 <button 
 type="button"
 onClick={() => setNovaVoiceGender('female')}
 style={{ 
 padding: '4px 10px', 
 borderRadius: '16px', 
 border: 'none', 
 cursor: 'pointer', 
 fontSize: '11px', 
 fontWeight: 600, 
 fontFamily: 'var(--font-body)',
 background: novaVoiceGender === 'female' ? 'rgba(255,255,255,0.90)' : 'transparent', 
 color: novaVoiceGender === 'female' ? '#000' : 'rgba(255,255,255,0.60)',
 transition: 'all 0.2s ease'
 }}
 >
 Female Voice
 </button>
 <button 
 type="button"
 onClick={() => setNovaVoiceGender('male')}
 style={{ 
 padding: '4px 10px', 
 borderRadius: '16px', 
 border: 'none', 
 cursor: 'pointer', 
 fontSize: '11px', 
 fontWeight: 600, 
 fontFamily: 'var(--font-body)',
 background: novaVoiceGender === 'male' ? 'rgba(255,255,255,0.90)' : 'transparent', 
 color: novaVoiceGender === 'male' ? '#000' : 'rgba(255,255,255,0.60)',
 transition: 'all 0.2s ease'
 }}
 >
 Male Voice
 </button>
 </div>
 
 {loadedVoiceName && (
 <span style={{ fontSize: '10px', color: '#c9a84c', background: 'rgba(201,168,76,0.10)', border: '1px solid rgba(201,168,76,0.25)', padding: '3px 8px', borderRadius: '12px', fontWeight: 500 }}>
 Voice: {loadedVoiceName}
 </span>
 )}

 {/* Continuous voice mode toggle */}
 <button
 type="button"
 onClick={() => setVoiceContinuous(v => !v)}
 title={voiceContinuous ? 'Continuous voice mode ON — click to disable' : 'Enable continuous voice conversation'}
 style={{ background: voiceContinuous ? 'rgba(201,168,76,0.15)' : 'none', border: `1px solid ${voiceContinuous ? '#c9a84c' : 'var(--border-glass)'}`, color: voiceContinuous ? '#c9a84c' : 'var(--text-muted)', fontSize: '10px', cursor: 'pointer', padding: '4px 10px', borderRadius: '20px', display: 'flex', alignItems: 'center', gap: '5px', transition: 'all 0.2s' }}
 >
 {voiceContinuous ? 'Voice ON' : 'Voice mode'}
 </button>
 <button
 onClick={handleClearChatHistory}
 style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '11px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', padding: '4px 8px', borderRadius: '4px', transition: 'var(--transition-smooth)' }}
 onMouseOver={e => (e.currentTarget.style.color = '#fff')}
 onMouseOut={e => (e.currentTarget.style.color = 'var(--text-muted)')}
 >
 <Trash2 size={12} /> Clear
 </button>
 </div>
 </div>

 {/* Chat messages */}
 <div style={{ flex: 1, overflowY: 'auto', padding: '16px', background: 'rgba(0,0,0,0.12)', borderRadius: '14px', display: 'flex', flexDirection: 'column', gap: '18px', minHeight: '400px', maxHeight: '460px' }}>
 {chatHistory.length === 0 && (
 <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', textAlign: 'center', padding: '40px 16px', gap: '18px' }}>
 <div style={{ fontSize: '42px' }}></div>
 <h2 style={{ fontSize: '22px', fontWeight: 700, color: '#fff', letterSpacing: '-0.02em', margin: 0 }}>
 {selectedMode === 'for_hire' ? "Hey! I'm Nova, your career companion." : "Hey! I'm Nova, your recruiting assistant."}
 </h2>
 <p style={{ color: 'var(--text-muted)', fontSize: '14px', maxWidth: '420px', lineHeight: '1.6', margin: 0 }}>
 {selectedMode === 'for_hire'
 ? "Tell me about the job you're chasing — I'll help you get it. Ask about skill gaps, resume tips, interview prep, or salary negotiation."
 : "Tell me what kind of candidate you're looking for. I'll find matches, explain why they fit, and help you craft the perfect job description."}
 </p>
 <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'center', marginTop: '8px' }}>
 {(selectedMode === 'for_hire'
 ? ["What skills do I need for a senior dev role?", "How do I negotiate salary?", "Review my resume", "Prep me for a system design interview"]
 : ["Find a senior React engineer", "What makes a good job description?", "Compare top candidates", "Suggest interview questions for a PM role"]
 ).map(q => (
 <button key={q} type="button" onClick={() => setChatQuery(q)}
 style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border-glass)', color: 'var(--text-muted)', fontSize: '12px', padding: '6px 12px', borderRadius: '20px', cursor: 'pointer', transition: 'all 0.2s' }}
 onMouseOver={e => { e.currentTarget.style.background = 'rgba(201,168,76,0.1)'; e.currentTarget.style.color = '#c9a84c'; e.currentTarget.style.borderColor = '#c9a84c'; }}
 onMouseOut={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.borderColor = 'var(--border-glass)'; }}
 >{q}</button>
 ))}
 </div>
 <p style={{ fontSize: '11px', color: 'rgba(255,255,255,0.2)', margin: 0 }}> Type or tap to speak</p>
 </div>
 )}

 {chatHistory.map((msg, idx) => (
 <div key={idx} style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
 {/* Avatar */}
 <div style={{ flexShrink: 0, width: 32, height: 32, borderRadius: '50%', background: msg.role === 'user' ? 'linear-gradient(135deg,#c9a84c,#a07838)' : 'rgba(255,255,255,0.06)', border: '1px solid var(--border-glass)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>
 {msg.role === 'user' ? '' : <AtlasNovaLogo size={16} />}
 </div>
 {/* Bubble */}
 <div style={{
 maxWidth: '78%',
 background: msg.role === 'user' ? 'linear-gradient(135deg, rgba(201,168,76,0.25), rgba(201,168,76,0.12))' : 'rgba(255,255,255,0.04)',
 border: `1px solid ${msg.role === 'user' ? 'rgba(201,168,76,0.3)' : 'var(--border-glass)'}`,
 borderRadius: msg.role === 'user' ? '18px 4px 18px 18px' : '4px 18px 18px 18px',
 padding: '12px 16px',
 fontSize: '13.5px',
 lineHeight: '1.65',
 color: '#fff',
 whiteSpace: 'pre-wrap',
 }}>
 <div style={{ fontSize: '10px', color: msg.role === 'user' ? 'rgba(201,168,76,0.7)' : 'rgba(255,255,255,0.3)', marginBottom: '5px', fontWeight: 600, letterSpacing: '0.05em' }}>
 {msg.role === 'user' ? 'YOU' : 'NOVA'}
 </div>
 {msg.content}
 {/* Replay TTS button on Nova messages */}
 {msg.role === 'assistant' && voiceEnabled && (
 <button type="button" onClick={() => speakText(msg.content)}
 title="Read aloud"
 style={{ marginTop: '8px', background: 'none', border: 'none', color: 'rgba(255,255,255,0.25)', fontSize: '11px', cursor: 'pointer', padding: '0', display: 'flex', alignItems: 'center', gap: '4px' }}
 onMouseOver={e => (e.currentTarget.style.color = '#c9a84c')}
 onMouseOut={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.25)')}
 > replay</button>
 )}
 </div>
 </div>
 ))}

 {/* Thinking indicator */}
 {chatLoading && (
 <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
 <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-glass)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
 <AtlasNovaLogo size={16} />
 </div>
 <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border-glass)', borderRadius: '4px 18px 18px 18px', padding: '14px 18px', display: 'flex', alignItems: 'center', gap: '6px' }}>
 <span className="nova-dot" /><span className="nova-dot" style={{ animationDelay: '0.2s' }} /><span className="nova-dot" style={{ animationDelay: '0.4s' }} />
 <span style={{ fontSize: '12px', color: 'var(--text-muted)', marginLeft: '6px' }}>Nova is thinking...</span>
 </div>
 </div>
 )}

 {/* Live interim transcript */}
 {isListening && interimTranscript && (
 <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
 <div style={{ background: 'rgba(201,168,76,0.08)', border: '1px dashed rgba(201,168,76,0.3)', borderRadius: '18px 4px 18px 18px', padding: '10px 16px', fontSize: '13px', color: 'rgba(255,255,255,0.5)', fontStyle: 'italic', maxWidth: '78%' }}>
 {interimTranscript}...
 </div>
 </div>
 )}

 <div ref={chatEndRef} />
 </div>

 {/* Waveform visualizer while listening */}
 {isListening && (
 <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px', height: '32px' }}>
 {[...Array(12)].map((_, i) => (
 <div key={i} className="nova-wave-bar" style={{ animationDelay: `${i * 0.08}s` }} />
 ))}
 <span style={{ fontSize: '12px', color: '#22c55e', marginLeft: '10px' }}>Listening — speak now</span>
 </div>
 )}

 {/* Input row */}
 <form id="nova-chat-form" onSubmit={handleSendChatMessage} style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
 <div style={{ flex: 1, position: 'relative' }}>
 <input
 type="text"
 className="input-field lining-copilot"
 placeholder={isListening ? ' Listening... speak now' : isSpeaking ? ' Nova is speaking...' : 'Message Nova — or click to speak'}
 value={chatQuery}
 onChange={e => setChatQuery(e.target.value)}
 onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendChatMessage(e as any); } }}
 disabled={chatLoading}
 style={{ width: '100%', paddingRight: chatQuery ? '40px' : '12px' }}
 />
 {chatQuery && (
 <button type="button" onClick={() => setChatQuery('')}
 style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '16px', lineHeight: 1 }}
 >×</button>
 )}
 </div>

 {/* Mic */}
 <button type="button" onClick={handleToggleListening}
 title={isListening ? 'Stop listening' : 'Speak to Nova'}
 style={{
 padding: '10px 12px', borderRadius: '10px', border: 'none', cursor: 'pointer',
 background: isListening ? 'rgba(239,68,68,0.2)' : 'rgba(255,255,255,0.06)',
 color: isListening ? '#ef4444' : 'var(--text-muted)',
 display: 'flex', alignItems: 'center', gap: '5px', fontSize: '12px',
 transition: 'all 0.2s',
 boxShadow: isListening ? '0 0 12px rgba(239,68,68,0.3)' : 'none'
 }}
 >
 <Mic size={15} />
 </button>

 {/* Speaker — stop or toggle */}
 <button type="button"
 onClick={() => {
 if (isSpeaking) { window.speechSynthesis?.cancel(); setIsSpeaking(false); }
 else { setVoiceEnabled(v => { const n = !v; if (!n) window.speechSynthesis?.cancel(); return n; }); }
 }}
 title={isSpeaking ? 'Stop Nova speaking' : voiceEnabled ? 'Voice output ON — click to mute' : 'Voice output OFF — click to enable'}
 style={{
 padding: '10px 12px', borderRadius: '10px', border: 'none', cursor: 'pointer',
 background: isSpeaking ? 'rgba(201,168,76,0.2)' : voiceEnabled ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.03)',
 color: isSpeaking ? '#c9a84c' : voiceEnabled ? 'var(--text-muted)' : 'rgba(255,255,255,0.2)',
 display: 'flex', alignItems: 'center', fontSize: '12px',
 transition: 'all 0.2s',
 boxShadow: isSpeaking ? '0 0 12px rgba(201,168,76,0.25)' : 'none'
 }}
 >
 {isSpeaking ? <VolumeX size={15} /> : voiceEnabled ? <Volume2 size={15} /> : <VolumeX size={15} />}
 </button>

 {/* Send */}
 <button type="submit" disabled={chatLoading || !chatQuery.trim()}
 className="btn-primary lining-copilot"
 style={{ padding: '10px 18px', display: 'flex', alignItems: 'center', gap: '6px', opacity: (!chatQuery.trim() || chatLoading) ? 0.5 : 1 }}
 >
 <Send size={15} />
 </button>
 </form>
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
 <Settings style={{ color: 'var(--accent-cyan)' }} /> 
 <span>{selectedMode === 'for_hire' ? 'Appearance & Theme Settings' : 'Workspace & Platform Settings'}</span>
 </h2>
 <p style={{ color: 'var(--text-muted)', fontSize: '14px', marginBottom: '24px' }}>
 Configure UI visual properties, manage SAML SSO, developer tools, workflows, and integrations.
 </p>

 {/* Settings Sub-navigation Tabs */}
 {selectedMode !== 'for_hire' && (
 <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px', marginBottom: '24px', flexWrap: 'wrap' }}>
 <button 
 onClick={() => setSettingsSubPage('appearance')} 
 className={settingsSubPage === 'appearance' ? 'btn-primary' : 'btn-secondary'}
 style={{ fontSize: '12px', padding: '6px 12px', borderRadius: '15px' }}
 >
 <Settings size={14} /> Profile & Appearance
 </button>
 <button 
 onClick={() => setSettingsSubPage('sso')} 
 className={settingsSubPage === 'sso' ? 'btn-primary' : 'btn-secondary'}
 style={{ fontSize: '12px', padding: '6px 12px', borderRadius: '15px' }}
 >
 <Shield size={14} /> SAML SSO
 </button>
 <button 
 onClick={() => setSettingsSubPage('developer')} 
 className={settingsSubPage === 'developer' ? 'btn-primary' : 'btn-secondary'}
 style={{ fontSize: '12px', padding: '6px 12px', borderRadius: '15px' }}
 >
 <Key size={14} /> API & Webhooks
 </button>
 <button 
 onClick={() => setSettingsSubPage('automations')} 
 className={settingsSubPage === 'automations' ? 'btn-primary' : 'btn-secondary'}
 style={{ fontSize: '12px', padding: '6px 12px', borderRadius: '15px' }}
 >
 <Activity size={14} /> Workflows
 </button>
 <button 
 onClick={() => setSettingsSubPage('integrations')} 
 className={settingsSubPage === 'integrations' ? 'btn-primary' : 'btn-secondary'}
 style={{ fontSize: '12px', padding: '6px 12px', borderRadius: '15px' }}
 >
 <Share2 size={14} /> Integrations
 </button>
 </div>
 )}

 {/* Subpage 1: Profile & Appearance */}
 {(selectedMode === 'for_hire' || settingsSubPage === 'appearance') && (
 <div>
 <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', alignItems: 'start' }}>
 
 {/* Left Column: Tenant profile/limits OR Profile video upload */}
 <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
 {selectedMode !== 'for_hire' ? (
 <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.01)' }}>
 <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '16px', fontWeight: 600 }}>Organization Workspace</h3>
 
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
 </div>

 {/* Active candidates count */}
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
 ) : (
 <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.01)' }}>
 <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '8px', fontWeight: 600 }}>Candidate Profile Overview</h3>
 <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '16px' }}>
 Your candidate matching score is active. Keep your details and introduction video updated.
 </p>
 <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
 <div style={{ color: '#fff' }}><strong>Email:</strong> {user.email}</div>
 <div style={{ color: '#fff' }}><strong>Status:</strong> Vectorized & Searchable</div>
 </div>
 </div>
 )}

 {/* Profile Video Intro Recorder Section */}
 <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.01)' }}>
 <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '12px', fontWeight: 600 }}>Webcam Video Introduction</h3>
 <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '16px' }}>
 Record a short pitch video directly to attach to your profile card.
 </p>

 {/* Camera Recording Window */}
 {cameraActive && (
 <div style={{ position: 'relative', background: '#000', borderRadius: '12px', overflow: 'hidden', marginBottom: '16px', aspectRatio: '16/9' }}>
 <video ref={recordingPreviewRef} autoPlay playsInline muted style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
 <div style={{ position: 'absolute', top: '12px', right: '12px', display: 'flex', gap: '8px' }}>
 <span className="pulse-glow" style={{ background: recording ? '#808080' : 'rgba(255,255,255,0.2)', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', color: '#fff', fontWeight: 'bold' }}>
 {recording ? ' RECORDING' : 'CAMERA ACTIVE'}
 </span>
 </div>
 </div>
 )}

 {/* Upload/Record preview */}
 {recordedVideoUrl && !cameraActive && (
 <div style={{ position: 'relative', borderRadius: '12px', overflow: 'hidden', marginBottom: '16px', background: '#000', aspectRatio: '16/9' }}>
 <video src={recordedVideoUrl} controls style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
 </div>
 )}

 {/* Camera Control Buttons */}
 <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
 {!cameraActive ? (
 <button onClick={handleStartCamera} className="btn-secondary" style={{ fontSize: '12px' }}>
 Enable Camera
 </button>
 ) : (
 <>
 {!recording ? (
 <button onClick={handleStartRecording} className="btn-primary" style={{ fontSize: '12px', background: '#22c55e', border: 'none', color: '#fff' }}>
 Start Record
 </button>
 ) : (
 <button onClick={handleStopRecording} className="btn-primary" style={{ fontSize: '12px', background: '#808080', border: 'none', color: '#fff' }}>
 Stop Record
 </button>
 )}
 <button onClick={handleStopCamera} className="btn-secondary" style={{ fontSize: '12px' }}>
 Turn Off
 </button>
 </>
 )}

 {recordedBlob && (
 <button 
 onClick={() => handleUploadVideoFile(null, selectedMode === 'for_hire' ? 'candidate' : 'user')} 
 className="btn-primary lining-settings" 
 style={{ fontSize: '12px' }}
 >
 Upload Recorded Video
 </button>
 )}
 </div>

 {/* Upload Video file manually */}
 <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '16px' }}>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '8px' }}>
 Or upload pre-recorded video file (.mp4, .webm, .mov)
 </label>
 <input 
 type="file" 
 accept="video/*" 
 onChange={(e) => handleUploadVideoFile(e, selectedMode === 'for_hire' ? 'candidate' : 'user')} 
 style={{ fontSize: '12px', color: 'var(--text-muted)' }}
 />
 </div>

 {/* Stream Current Video Intro */}
 {(selectedMode === 'for_hire' ? myCandidateProfile?.video_path : user?.video_path) && (
 <div style={{ marginTop: '20px', borderTop: '1px solid var(--border-glass)', paddingTop: '16px' }}>
 <h4 style={{ fontSize: '13px', color: '#fff', marginBottom: '10px' }}>Active Profile Video Intro:</h4>
 <video 
 src={selectedMode === 'for_hire' ? myCandidateProfile?.video_path : user?.video_path} 
 controls 
 style={{ width: '100%', borderRadius: '8px', background: '#000', border: '1px solid var(--border-glass)' }} 
 />
 </div>
 )}
 </div>
 </div>

 {/* Right Column: Theme & Appearance customizing dashboard */}
 <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-glass)', display: 'flex', flexDirection: 'column', gap: '20px' }}>
 <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '4px', fontWeight: 600 }}>App Customization</h3>
 <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '12px' }}>
 Adjust typography themes, highlight colors, and layout densities.
 </p>

 {/* Theme Mode — Dark Only */}
 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '8px', fontWeight: 'bold' }}>UI Theme</label>
 <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 14px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)', borderRadius: '12px' }}>
 <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-gold)', boxShadow: '0 0 6px var(--accent-purple)' }} />
 <span style={{ fontSize: '13px', color: '#fff', fontWeight: 500 }}>Titan Dark</span>
 <span style={{ marginLeft: 'auto', fontSize: '11px', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.08)', padding: '2px 8px', borderRadius: '20px' }}>Active</span>
 </div>
 </div>

 {/* Accent Highlight Color Selector */}
 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '8px', fontWeight: 'bold' }}>Accent Palette</label>
 <div style={{ display: 'flex', gap: '8px' }}>
 <button 
 onClick={() => setAccentColor('default')} 
 className={accentColor === 'default' ? 'btn-primary' : 'btn-secondary'}
 style={{ flex: 1, fontSize: '12px', padding: '10px', justifyContent: 'center', borderColor: accentColor === 'default' ? '#808080' : undefined }}
 >
 Violet
 </button>
 <button 
 onClick={() => setAccentColor('cyan')} 
 className={accentColor === 'cyan' ? 'btn-primary' : 'btn-secondary'}
 style={{ flex: 1, fontSize: '12px', padding: '10px', justifyContent: 'center', borderColor: accentColor === 'cyan' ? '#00d2ff' : undefined }}
 >
 Cyan
 </button>
 <button 
 onClick={() => setAccentColor('mint')} 
 className={accentColor === 'mint' ? 'btn-primary' : 'btn-secondary'}
 style={{ flex: 1, fontSize: '12px', padding: '10px', justifyContent: 'center', borderColor: accentColor === 'mint' ? '#00ffaa' : undefined }}
 >
 Mint
 </button>
 </div>
 </div>

 {/* Density Grid Padding Selector */}
 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '8px', fontWeight: 'bold' }}>Layout Density</label>
 <div style={{ display: 'flex', gap: '8px' }}>
 <button 
 onClick={() => setDensityMode('relaxed')} 
 className={densityMode === 'relaxed' ? 'btn-primary' : 'btn-secondary'}
 style={{ flex: 1, fontSize: '12px', padding: '10px', justifyContent: 'center' }}
 >
 Relaxed
 </button>
 <button 
 onClick={() => setDensityMode('compact')} 
 className={densityMode === 'compact' ? 'btn-primary' : 'btn-secondary'}
 style={{ flex: 1, fontSize: '12px', padding: '10px', justifyContent: 'center' }}
 >
 Compact
 </button>
 </div>
 </div>
 </div>

 </div>

 {selectedMode !== 'for_hire' && (
 /* Billing Pricing Plans for Recruiter */
 <div style={{ marginTop: '32px', borderTop: '1px solid var(--border-glass)', paddingTop: '32px' }}>
 <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '16px' }}>Subscription Pricing Plans</h3>
 <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
 <div style={{ border: isPro ? '1px solid var(--border-glass)' : '1px solid var(--accent-cyan)', borderRadius: '12px', padding: '20px', background: 'rgba(255,255,255,0.01)', position: 'relative' }}>
 {!isPro && <span style={{ position: 'absolute', top: '12px', right: '12px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-glass)', borderRadius: '12px', padding: '3px 8px', fontSize: '10px', color: 'var(--accent-cyan)' }}>Active Plan</span>}
 <h4 style={{ fontSize: '15px', color: '#fff', marginBottom: '8px' }}>Free Basic</h4>
 <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#fff', marginBottom: '16px' }}>$0 <span style={{ fontSize: '12px', fontWeight: 'normal', color: 'var(--text-muted)' }}>/mo</span></div>
 <ul style={{ paddingLeft: '16px', color: 'var(--text-muted)', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
 <li>Up to 5 candidate resumes parsing</li>
 <li>Up to 2 active job openings</li>
 <li>Semantic vector search indexing</li>
 <li>Basic Recruiter Nova assistant</li>
 </ul>
 </div>

 <div style={{ border: isPro ? '1px solid #22c55e' : '1px solid var(--accent-purple)', borderRadius: '12px', padding: '20px', background: isPro ? 'rgba(34, 197, 94, 0.02)' : 'rgba(147, 51, 234, 0.02)', position: 'relative' }}>
 {isPro ? (
 <span style={{ position: 'absolute', top: '12px', right: '12px', background: '#22c55e', borderRadius: '12px', padding: '3px 8px', fontSize: '10px', color: '#fff' }}>Active Plan</span>
 ) : (
 <span style={{ position: 'absolute', top: '12px', right: '12px', background: 'var(--accent-gold)', borderRadius: '12px', padding: '3px 8px', fontSize: '10px', color: '#fff' }}>Recommended</span>
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
 )}
 </div>
 )}

 {/* Subpage 2: SAML SSO */}
 {selectedMode !== 'for_hire' && settingsSubPage === 'sso' && (
 <form onSubmit={handleSaveSSO} className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.01)', display: 'flex', flexDirection: 'column', gap: '20px' }}>
 <h3 style={{ fontSize: '16px', color: '#fff', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
 <Shield size={18} style={{ color: 'var(--accent-cyan)' }} /> SAML Identity Provider Configuration
 </h3>
 <p style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
 Establish Single Sign-On (SSO) configurations so company recruiters authenticate directly via corporate login systems.
 </p>

 <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>IdP Entity ID</label>
 <input 
 type="text" 
 required 
 className="input-field" 
 placeholder="https://okta.com/entity-id/atlas"
 value={ssoEntityId}
 onChange={e => setSsoEntityId(e.target.value)}
 />
 </div>

 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>IdP Single Sign-On URL (SAML Target Endlink)</label>
 <input 
 type="url" 
 required 
 className="input-field" 
 placeholder="https://mycorp.okta.com/app/atlas/sso/saml"
 value={ssoUrl}
 onChange={e => setSsoUrl(e.target.value)}
 />
 </div>

 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>x509 Public Cryptography Certificate (PEM Format)</label>
 <textarea 
 required 
 className="input-field" 
 placeholder="-----BEGIN CERTIFICATE-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END CERTIFICATE-----"
 value={ssoCert}
 onChange={e => setSsoCert(e.target.value)}
 style={{ minHeight: '140px', fontFamily: 'monospace', fontSize: '11px', resize: 'vertical' }}
 />
 </div>
 </div>

 <button type="submit" className="btn-primary lining-settings" style={{ alignSelf: 'flex-start' }}>
 Save SSO Configuration
 </button>
 </form>
 )}

 {/* Subpage 3: API & Webhooks */}
 {selectedMode !== 'for_hire' && settingsSubPage === 'developer' && (
 <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', alignItems: 'start' }}>
 
 {/* Left Column: API keys generation */}
 <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.01)', display: 'flex', flexDirection: 'column', gap: '20px' }}>
 <h3 style={{ fontSize: '16px', color: '#fff', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
 <Key size={18} style={{ color: 'var(--accent-cyan)' }} /> Developer API Keys
 </h3>
 <p style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
 Generate API tokens to securely query candidate records or submit job profiles programmatically.
 </p>

 <form onSubmit={handleCreateAPIKey} style={{ display: 'flex', gap: '8px' }}>
 <input 
 type="text" 
 required 
 className="input-field" 
 placeholder="Key Name (e.g. ATS Integration)" 
 value={newKeyName}
 onChange={e => setNewKeyName(e.target.value)}
 />
 <button type="submit" className="btn-primary lining-settings" style={{ flexShrink: 0 }}>
 Generate
 </button>
 </form>

 {latestRawKey && (
 <div style={{ padding: '12px', background: 'rgba(192, 192, 192, 0.05)', border: '1px solid rgba(192, 192, 192, 0.2)', borderRadius: '8px', fontSize: '12px' }}>
 <span style={{ display: 'block', color: 'var(--accent-cyan)', fontWeight: 'bold', marginBottom: '4px' }}> Copy API Key (Shown Once):</span>
 <code style={{ background: '#000', padding: '6px', borderRadius: '4px', display: 'block', wordBreak: 'break-all', fontFamily: 'monospace', border: '1px solid var(--border-glass)' }}>
 {latestRawKey}
 </code>
 </div>
 )}

 <div style={{ marginTop: '10px' }}>
 <h4 style={{ fontSize: '13px', color: '#fff', marginBottom: '8px' }}>Active API Access Keys ({apiKeys.length})</h4>
 {apiKeys.length === 0 ? (
 <div style={{ color: 'var(--text-muted)', fontSize: '12px', fontStyle: 'italic', padding: '12px', textAlign: 'center' }}>No API keys generated.</div>
 ) : (
 <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
 {apiKeys.map(k => (
 <div key={k.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '8px' }}>
 <div>
 <strong style={{ color: '#fff', fontSize: '13px' }}>{k.name}</strong>
 <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Prefix: <code style={{ color: 'var(--accent-cyan)' }}>{k.key_prefix}</code> • Created {new Date(k.created_at).toLocaleDateString()}</div>
 </div>
 <button onClick={() => handleDeleteAPIKey(k.id)} className="btn-secondary" style={{ padding: '6px', color: '#808080', border: 'none' }} title="Revoke API key">
 <Trash2 size={14} />
 </button>
 </div>
 ))}
 </div>
 )}
 </div>
 </div>

 {/* Right Column: Webhook endpoints registry */}
 <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.01)', display: 'flex', flexDirection: 'column', gap: '20px' }}>
 <h3 style={{ fontSize: '16px', color: '#fff', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
 <Activity size={18} style={{ color: 'var(--accent-cyan)' }} /> Webhook Endpoints
 </h3>
 <p style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
 Register payload target URLs to receive real-time JSON event alerts (e.g. candidate created or hired status changes).
 </p>

 <form onSubmit={handleCreateWebhook} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '11px', marginBottom: '4px' }}>Payload Destination URL</label>
 <input 
 type="url" 
 required 
 className="input-field" 
 placeholder="https://mycorp.com/webhooks/atlas" 
 value={webhookUrl}
 onChange={e => setWebhookUrl(e.target.value)}
 />
 </div>
 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '11px', marginBottom: '4px' }}>Signature Secret Token</label>
 <input 
 type="text" 
 required 
 className="input-field" 
 placeholder="E.g., whsec_secret_hash_code" 
 value={webhookSecret}
 onChange={e => setWebhookSecret(e.target.value)}
 />
 </div>
 
 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '11px', marginBottom: '4px' }}>Subscribed Trigger Events</label>
 <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: '#fff', marginTop: '6px' }}>
 <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
 <input 
 type="checkbox" 
 checked={webhookEvents.includes('candidate.created')}
 onChange={(e) => {
 if (e.target.checked) setWebhookEvents([...webhookEvents, 'candidate.created']);
 else setWebhookEvents(webhookEvents.filter(x => x !== 'candidate.created'));
 }}
 />
 <span>Candidate Created</span>
 </label>
 <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
 <input 
 type="checkbox" 
 checked={webhookEvents.includes('candidate.hired')}
 onChange={(e) => {
 if (e.target.checked) setWebhookEvents([...webhookEvents, 'candidate.hired']);
 else setWebhookEvents(webhookEvents.filter(x => x !== 'candidate.hired'));
 }}
 />
 <span>Candidate Hired</span>
 </label>
 </div>
 </div>

 <button type="submit" className="btn-primary lining-settings" style={{ alignSelf: 'flex-start' }}>
 Register Webhook
 </button>
 </form>

 <div style={{ marginTop: '10px' }}>
 <h4 style={{ fontSize: '13px', color: '#fff', marginBottom: '8px' }}>Active Webhooks ({webhooks.length})</h4>
 {webhooks.length === 0 ? (
 <div style={{ color: 'var(--text-muted)', fontSize: '12px', fontStyle: 'italic', padding: '12px', textAlign: 'center' }}>No webhooks registered.</div>
 ) : (
 <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
 {webhooks.map(w => (
 <div key={w.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '8px' }}>
 <div style={{ maxWidth: '80%' }}>
 <div style={{ color: '#fff', fontSize: '13px', wordBreak: 'break-all', fontFamily: 'monospace' }}>{w.url}</div>
 <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>Events: <code style={{ color: 'var(--accent-cyan)' }}>{w.events.join(', ')}</code></div>
 </div>
 <button onClick={() => handleDeleteWebhook(w.id)} className="btn-secondary" style={{ padding: '6px', color: '#808080', border: 'none' }} title="Remove Webhook">
 <Trash2 size={14} />
 </button>
 </div>
 ))}
 </div>
 )}
 </div>
 </div>

 </div>
 )}

 {/* Subpage 4: Workflow Automations */}
 {selectedMode !== 'for_hire' && settingsSubPage === 'automations' && (
 <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', alignItems: 'start' }}>
 
 {/* Left Column: Create Rule */}
 <form onSubmit={handleCreateWorkflow} className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.01)', display: 'flex', flexDirection: 'column', gap: '20px' }}>
 <h3 style={{ fontSize: '16px', color: '#fff', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
 <Activity size={18} style={{ color: 'var(--accent-cyan)' }} /> Create Workflow Rule
 </h3>
 <p style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
 Define target events that trigger automatic system actions (e.g. sending alert emails on status migrations).
 </p>

 <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Workflow Name</label>
 <input 
 type="text" 
 required 
 className="input-field" 
 placeholder="Rejection Notify Alert" 
 value={newWorkflowName}
 onChange={e => setNewWorkflowName(e.target.value)}
 />
 </div>

 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Event Trigger</label>
 <select 
 className="input-field" 
 value={workflowTrigger}
 onChange={e => setWorkflowTrigger(e.target.value)}
 style={{ background: '#000', color: '#fff' }}
 >
 <option value="candidate_status_changed">Candidate Status Changed to Rejected</option>
 <option value="candidate_applied">Candidate Applied to Job Opening</option>
 </select>
 </div>

 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Action Triggered</label>
 <select 
 className="input-field" 
 value={workflowAction}
 onChange={e => setWorkflowAction(e.target.value)}
 style={{ background: '#000', color: '#fff' }}
 >
 <option value="send_email">Send Email Notification</option>
 <option value="notify_slack">Post Update into Slack Channel</option>
 </select>
 </div>

 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Target Email / Hook</label>
 <input 
 type="email" 
 required 
 className="input-field" 
 placeholder="notify@mycorp.com" 
 value={workflowEmail}
 onChange={e => setWorkflowEmail(e.target.value)}
 />
 </div>
 </div>

 <button type="submit" className="btn-primary lining-settings" style={{ alignSelf: 'flex-start' }}>
 Activate Workflow
 </button>
 </form>

 {/* Right Column: Workflow Rules List */}
 <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.01)' }}>
 <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '8px', fontWeight: 600 }}>Active Rules Engine ({workflows.length})</h3>
 <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '20px' }}>
 Below are the active pipelines running checks automatically on data modifications.
 </p>

 {workflows.length === 0 ? (
 <div style={{ color: 'var(--text-muted)', fontSize: '12px', fontStyle: 'italic', padding: '12px', textAlign: 'center' }}>No workflow rules active.</div>
 ) : (
 <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
 {workflows.map(w => (
 <div key={w.id} style={{ padding: '16px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
 <div>
 <strong style={{ color: '#fff', fontSize: '14px' }}>{w.name}</strong>
 <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
 Trigger: <code style={{ color: 'var(--accent-cyan)' }}>{w.trigger_event}</code>
 </div>
 <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
 Action: <code style={{ color: 'var(--accent-gold)' }}>{w.action_type}</code> to {w.action_payload?.email}
 </div>
 </div>
 <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
 <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', fontSize: '11px', color: w.is_active ? '#22c55e' : 'var(--text-muted)' }}>
 <input 
 type="checkbox" 
 checked={w.is_active} 
 onChange={() => handleToggleWorkflow(w.id)}
 />
 <span>{w.is_active ? 'Active' : 'Paused'}</span>
 </label>
 <button onClick={() => handleDeleteWorkflow(w.id)} className="btn-secondary" style={{ padding: '6px', color: '#808080', border: 'none' }} title="Delete rule">
 <Trash2 size={14} />
 </button>
 </div>
 </div>
 ))}
 </div>
 )}
 </div>

 </div>
 )}

 {/* Subpage 5: Integrations */}
 {selectedMode !== 'for_hire' && settingsSubPage === 'integrations' && (
 <div>
 <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '8px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
 <Share2 size={18} style={{ color: 'var(--accent-cyan)' }} /> App Integrations Center
 </h3>
 <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '24px' }}>
 Link your ATLAS workspace with external utilities to synchronize events, export listings, and alert team channels.
 </p>

 <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
 {/* Google Calendar */}
 {(() => {
 const isConnected = integrationsList.some(i => i.provider_name === 'google_calendar' && i.is_active);
 return (
 <div style={{ border: isConnected ? '1px solid #22c55e' : '1px solid var(--border-glass)', borderRadius: '12px', padding: '24px', background: 'rgba(255,255,255,0.01)', display: 'flex', flexDirection: 'column', gap: '16px' }}>
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
 <span style={{ fontSize: '24px' }}></span>
 <span style={{ fontSize: '10px', padding: '3px 8px', borderRadius: '12px', background: isConnected ? 'rgba(34,197,94,0.1)' : 'rgba(255,255,255,0.05)', color: isConnected ? '#22c55e' : 'var(--text-muted)' }}>
 {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
 </span>
 </div>
 <div>
 <h4 style={{ fontSize: '15px', color: '#fff', marginBottom: '6px' }}>Google Calendar</h4>
 <p style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Sync interview timings and auto-generate meeting invites on Google Meet.</p>
 </div>
 <button 
 onClick={() => handleToggleIntegration('google_calendar')} 
 className={isConnected ? 'btn-secondary' : 'btn-primary lining-settings'} 
 style={{ width: '100%', justifyContent: 'center', fontSize: '12px', borderColor: isConnected ? '#808080' : undefined }}
 >
 {isConnected ? 'Disconnect' : 'Connect Account'}
 </button>
 </div>
 );
 })()}

 {/* Slack */}
 {(() => {
 const isConnected = integrationsList.some(i => i.provider_name === 'slack' && i.is_active);
 return (
 <div style={{ border: isConnected ? '1px solid #22c55e' : '1px solid var(--border-glass)', borderRadius: '12px', padding: '24px', background: 'rgba(255,255,255,0.01)', display: 'flex', flexDirection: 'column', gap: '16px' }}>
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
 <span style={{ fontSize: '24px' }}></span>
 <span style={{ fontSize: '10px', padding: '3px 8px', borderRadius: '12px', background: isConnected ? 'rgba(34,197,94,0.1)' : 'rgba(255,255,255,0.05)', color: isConnected ? '#22c55e' : 'var(--text-muted)' }}>
 {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
 </span>
 </div>
 <div>
 <h4 style={{ fontSize: '15px', color: '#fff', marginBottom: '6px' }}>Slack Workspace</h4>
 <p style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Broadcast candidate applications and ratings alerts directly to dev channels.</p>
 </div>
 <button 
 onClick={() => handleToggleIntegration('slack')} 
 className={isConnected ? 'btn-secondary' : 'btn-primary lining-settings'} 
 style={{ width: '100%', justifyContent: 'center', fontSize: '12px', borderColor: isConnected ? '#808080' : undefined }}
 >
 {isConnected ? 'Disconnect' : 'Connect Slack'}
 </button>
 </div>
 );
 })()}

 {/* LinkedIn */}
 {(() => {
 const isConnected = integrationsList.some(i => i.provider_name === 'linkedin' && i.is_active);
 return (
 <div style={{ border: isConnected ? '1px solid #22c55e' : '1px solid var(--border-glass)', borderRadius: '12px', padding: '24px', background: 'rgba(255,255,255,0.01)', display: 'flex', flexDirection: 'column', gap: '16px' }}>
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
 <span style={{ fontSize: '24px' }}></span>
 <span style={{ fontSize: '10px', padding: '3px 8px', borderRadius: '12px', background: isConnected ? 'rgba(34,197,94,0.1)' : 'rgba(255,255,255,0.05)', color: isConnected ? '#22c55e' : 'var(--text-muted)' }}>
 {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
 </span>
 </div>
 <div>
 <h4 style={{ fontSize: '15px', color: '#fff', marginBottom: '6px' }}>LinkedIn Jobs</h4>
 <p style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Cross-publish active job listings automatically onto LinkedIn boards.</p>
 </div>
 <button 
 onClick={() => handleToggleIntegration('linkedin')} 
 className={isConnected ? 'btn-secondary' : 'btn-primary lining-settings'} 
 style={{ width: '100%', justifyContent: 'center', fontSize: '12px', borderColor: isConnected ? '#808080' : undefined }}
 >
 {isConnected ? 'Disconnect' : 'Connect LinkedIn'}
 </button>
 </div>
 );
 })()}
 </div>
 </div>
 )}
 </div>
 );
 })()}

 {/* TAB: ATLAS ACADEMY */}
 {activeTab === 'academy' && (() => {
 const ACADEMY_CATEGORIES = ['Programming','AI','Cloud','DevOps','Cybersecurity','Electronics','Marketing','Sales','Finance','HR','UI/UX','Communication','Interview Prep'];
 const LEVEL_COLORS: Record<string,string> = { beginner: '#22c55e', intermediate: '#f59e0b', advanced: '#ef4444' };

 const filteredCourses = academyCourses.filter(c => {
 const matchCat = !academyCategoryFilter || c.category === academyCategoryFilter;
 const matchSearch = !academySearchQuery || c.title.toLowerCase().includes(academySearchQuery.toLowerCase()) || (c.description||'').toLowerCase().includes(academySearchQuery.toLowerCase());
 return matchCat && matchSearch;
 });

 const handleEnroll = async (courseId: number) => {
 try { await api.academy.enroll(courseId); const courses = await api.academy.listCourses(); setAcademyCourses(courses||[]); const enrollments = await api.academy.myEnrollments(); setAcademyEnrollments(enrollments||[]); alert(' Enrolled successfully!'); } catch(e:any){ alert(e.message); }
 };

 const handleSkillGap = async () => {
 if (!academySkillGapJobTitle || !academySkillGapJobSkills) return;
 setAcademySkillGapLoading(true);
 try {
 const skills = academySkillGapJobSkills.split(',').map((s:string) => s.trim()).filter(Boolean);
 const result = await api.academy.skillGap({ job_title: academySkillGapJobTitle, job_skills: skills });
 setAcademySkillGapResult(result);
 } catch(e:any){ alert(e.message); } finally { setAcademySkillGapLoading(false); }
 };

 const handleMentorSend = async () => {
 if (!academyMentorInput.trim()) return;
 const msg = academyMentorInput.trim();
 setAcademyMentorMessages(prev => [...prev, { role:'user', content: msg }]);
 setAcademyMentorInput('');
 setAcademyMentorLoading(true);
 try {
 const res = await api.academy.aiMentor(msg);
 setAcademyMentorMessages(prev => [...prev, { role:'assistant', content: res.reply }]);
 } catch { setAcademyMentorMessages(prev => [...prev, { role:'assistant', content:'Sorry, I had trouble connecting. Please try again.' }]); }
 finally { setAcademyMentorLoading(false); }
 };

 const handleRoadmap = async () => {
 if (!academyRoadmapGoal.trim()) return;
 setAcademyRoadmapLoading(true);
 try { const res = await api.academy.generateRoadmap(academyRoadmapGoal); setAcademyRoadmap(res.roadmap); } catch(e:any){ alert(e.message); } finally { setAcademyRoadmapLoading(false); }
 };

 const handleApplyInstructor = async () => {
 try {
 const res = await api.academy.applyInstructor({ ...academyInstructorForm, expertise: academyInstructorForm.expertise.split(',').map((s:string)=>s.trim()).filter(Boolean) });
 alert(res.message);
 const instr = await api.academy.getInstructorProfile();
 setAcademyInstructor(instr);
 } catch(e:any){ alert(e.message); }
 };

 const handleCreateCourse = async () => {
 try {
 const res = await api.academy.createCourse({ ...academyCourseForm, skills_taught: academyCourseForm.skills_taught.split(',').map((s:string)=>s.trim()).filter(Boolean), tags: academyCourseForm.tags.split(',').map((s:string)=>s.trim()).filter(Boolean) });
 alert(res.message || 'Course created!');
 const instr = await api.academy.getInstructorProfile();
 setAcademyInstructor(instr);
 } catch(e:any){ alert(e.message); }
 };

 const handlePublishCourse = async (courseId: number) => {
 try { const res = await api.academy.publishCourse(courseId); alert(res.message); const instr = await api.academy.getInstructorProfile(); setAcademyInstructor(instr); } catch(e:any){ alert(e.message); }
 };

 const handleCompleteCourse = async (courseId: number) => {
 try { const res = await api.academy.completeCourse(courseId); alert(res.message); const [certs, enrollments] = await Promise.all([api.academy.myCertificates(), api.academy.myEnrollments()]); setAcademyCertificates(certs||[]); setAcademyEnrollments(enrollments||[]); } catch(e:any){ alert(e.message); }
 };

 return (
 <div className="animate-fade-in" style={{ display:'flex', flexDirection:'column', gap:'0', minHeight:'100%' }}>

 {/* ACADEMY HEADER HERO */}
 <div style={{ background:'linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%)', borderBottom:'1px solid rgba(99,102,241,0.2)', padding:'28px 32px', marginBottom:'0', position:'relative', overflow:'hidden' }}>
 <div style={{ position:'absolute', top:'-40px', right:'-40px', width:'200px', height:'200px', background:'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)', borderRadius:'50%' }} />
 <div style={{ position:'absolute', bottom:'-60px', left:'30%', width:'300px', height:'300px', background:'radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%)', borderRadius:'50%' }} />
 <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', position:'relative', zIndex:1 }}>
 <div>
 <div style={{ display:'flex', alignItems:'center', gap:'12px', marginBottom:'8px' }}>
 <div style={{ width:'42px', height:'42px', background:'linear-gradient(135deg, #6366f1, #8b5cf6)', borderRadius:'12px', display:'flex', alignItems:'center', justifyContent:'center' }}>
 <GraduationCap size={22} color="#fff" />
 </div>
 <div>
 <h1 style={{ fontSize:'26px', fontWeight:800, color:'#fff', margin:0, letterSpacing:'-0.5px' }}>Atlas Academy</h1>
 <p style={{ color:'rgba(99,102,241,0.9)', fontSize:'13px', margin:0, fontWeight:500 }}>Learn · Build · Get Hired</p>
 </div>
 </div>
 <p style={{ color:'var(--text-muted)', fontSize:'14px', maxWidth:'480px', lineHeight:'1.5' }}>
 AI-powered learning platform. Identify skill gaps, learn from experts, earn certificates — all inside ATLAS.
 </p>
 </div>
 {/* Stats */}
 <div style={{ display:'flex', gap:'20px', flexShrink:0 }}>
 {[
 { label:'Courses', value: academyStats?.total_courses ?? academyCourses.length, icon:'' },
 { label:'Enrolled', value: academyStats?.my_enrolled_courses ?? academyEnrollments.length, icon:'' },
 { label:'Certificates', value: academyStats?.my_certificates ?? academyCertificates.length, icon:'' },
 ].map(s => (
 <div key={s.label} style={{ textAlign:'center', background:'rgba(255,255,255,0.05)', borderRadius:'12px', padding:'12px 18px', border:'1px solid rgba(99,102,241,0.15)' }}>
 <div style={{ fontSize:'22px', marginBottom:'2px' }}>{s.icon}</div>
 <div style={{ fontSize:'22px', fontWeight:800, color:'#fff' }}>{s.value}</div>
 <div style={{ fontSize:'11px', color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'0.5px' }}>{s.label}</div>
 </div>
 ))}
 </div>
 </div>

 {/* Sub-nav */}
 <div style={{ display:'flex', gap:'6px', marginTop:'20px', flexWrap:'wrap' }}>
 {([
 { id:'discover', label:' Discover', },
 { id:'my_learning', label:' My Learning', },
 { id:'skill_gap', label:' Skill Gap AI', },
 { id:'ai_mentor', label:' AI Mentor', },
 { id:'instructor', label:' Instructor', },
 ] as const).map(tab => (
 <button key={tab.id} onClick={() => setAcademySubView(tab.id)}
 style={{ padding:'7px 16px', borderRadius:'20px', fontSize:'13px', fontWeight:600, border:'none', cursor:'pointer', transition:'all 0.2s',
 background: academySubView === tab.id ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'rgba(255,255,255,0.07)',
 color: academySubView === tab.id ? '#fff' : 'var(--text-muted)' }}>
 {tab.label}
 </button>
 ))}
 </div>
 </div>

 {/* MAIN CONTENT AREA */}
 <div style={{ padding:'28px 32px', flex:1 }}>

 {/* DISCOVER */}
 {academySubView === 'discover' && (
 <div style={{ display:'flex', flexDirection:'column', gap:'24px' }}>
 {/* Search + filters */}
 <div style={{ display:'flex', gap:'12px', flexWrap:'wrap', alignItems:'center' }}>
 <div style={{ flex:1, minWidth:'240px', position:'relative' }}>
 <Search size={15} style={{ position:'absolute', left:'12px', top:'50%', transform:'translateY(-50%)', color:'var(--text-muted)' }} />
 <input value={academySearchQuery} onChange={e=>setAcademySearchQuery(e.target.value)}
 placeholder="Search courses, skills, instructors…"
 style={{ width:'100%', paddingLeft:'36px', paddingRight:'12px', paddingTop:'10px', paddingBottom:'10px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'10px', color:'#fff', fontSize:'14px', boxSizing:'border-box' }} />
 </div>
 <select value={academyCategoryFilter} onChange={e=>setAcademyCategoryFilter(e.target.value)}
 style={{ padding:'10px 14px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'10px', color:'#fff', fontSize:'13px', cursor:'pointer' }}>
 <option value="">All Categories</option>
 {ACADEMY_CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
 </select>
 {['beginner','intermediate','advanced'].map(l => (
 <button key={l} onClick={async()=>{ const r = await api.academy.listCourses({level:l}); setAcademyCourses(r||[]); }}
 style={{ padding:'8px 14px', borderRadius:'20px', border:'1px solid rgba(255,255,255,0.1)', background:'rgba(255,255,255,0.05)', color:LEVEL_COLORS[l]||'#fff', fontSize:'12px', cursor:'pointer', fontWeight:600, textTransform:'capitalize' }}>
 {l}
 </button>
 ))}
 <button onClick={async()=>{ const r = await api.academy.listCourses(); setAcademyCourses(r||[]); setAcademyCategoryFilter(''); setAcademySearchQuery(''); }}
 style={{ padding:'8px 14px', borderRadius:'20px', border:'1px solid rgba(255,255,255,0.1)', background:'rgba(255,255,255,0.05)', color:'var(--text-muted)', fontSize:'12px', cursor:'pointer' }}>
 Clear
 </button>
 </div>

 {/* Category pills */}
 <div style={{ display:'flex', gap:'8px', flexWrap:'wrap' }}>
 {ACADEMY_CATEGORIES.map(cat => (
 <button key={cat} onClick={()=>setAcademyCategoryFilter(academyCategoryFilter===cat?'':cat)}
 style={{ padding:'5px 13px', borderRadius:'20px', fontSize:'12px', fontWeight:600, cursor:'pointer', transition:'all 0.2s', border:'1px solid',
 borderColor: academyCategoryFilter===cat ? '#6366f1' : 'rgba(255,255,255,0.1)',
 background: academyCategoryFilter===cat ? 'rgba(99,102,241,0.2)' : 'transparent',
 color: academyCategoryFilter===cat ? '#a5b4fc' : 'var(--text-muted)' }}>
 {cat}
 </button>
 ))}
 </div>

 {/* Course grid */}
 {filteredCourses.length === 0 ? (
 <div style={{ textAlign:'center', padding:'60px 20px', color:'var(--text-muted)' }}>
 <GraduationCap size={48} style={{ opacity:0.3, marginBottom:'16px' }} />
 <p style={{ fontSize:'18px', fontWeight:600, color:'#fff', marginBottom:'8px' }}>No courses yet</p>
 <p style={{ fontSize:'14px' }}>Be the first instructor to create a course!</p>
 <button onClick={()=>setAcademySubView('instructor')} style={{ marginTop:'16px', padding:'10px 24px', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', border:'none', borderRadius:'10px', color:'#fff', fontWeight:600, cursor:'pointer' }}>
 Become an Instructor
 </button>
 </div>
 ) : (
 <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(300px,1fr))', gap:'20px' }}>
 {filteredCourses.map((course:any) => (
 <div key={course.id} className="glass-panel" style={{ padding:'0', overflow:'hidden', cursor:'pointer', transition:'transform 0.2s, box-shadow 0.2s', borderRadius:'14px' }}
 onMouseEnter={e=>{(e.currentTarget as HTMLElement).style.transform='translateY(-4px)';(e.currentTarget as HTMLElement).style.boxShadow='0 12px 40px rgba(99,102,241,0.2)';}}
 onMouseLeave={e=>{(e.currentTarget as HTMLElement).style.transform='';(e.currentTarget as HTMLElement).style.boxShadow='';}}>
 {/* Thumbnail */}
 <div style={{ height:'140px', background:`linear-gradient(135deg, ${['#6366f1','#8b5cf6','#06b6d4','#10b981','#f59e0b'][course.id%5]} 0%, rgba(0,0,0,0.3) 100%)`, display:'flex', alignItems:'center', justifyContent:'center', position:'relative' }}>
 <BookOpen size={40} color="rgba(255,255,255,0.6)" />
 <div style={{ position:'absolute', top:'10px', left:'10px', padding:'3px 10px', borderRadius:'20px', fontSize:'11px', fontWeight:700, background:LEVEL_COLORS[course.level]||'#6366f1', color:'#fff' }}>{course.level}</div>
 {course.is_free && <div style={{ position:'absolute', top:'10px', right:'10px', padding:'3px 10px', borderRadius:'20px', fontSize:'11px', fontWeight:700, background:'rgba(16,185,129,0.9)', color:'#fff' }}>FREE</div>}
 {course.enrolled && <div style={{ position:'absolute', bottom:'10px', right:'10px', padding:'3px 10px', borderRadius:'20px', fontSize:'11px', fontWeight:700, background:'rgba(99,102,241,0.9)', color:'#fff' }}> Enrolled</div>}
 </div>
 <div style={{ padding:'16px' }}>
 <div style={{ fontSize:'12px', color:'#a5b4fc', fontWeight:600, marginBottom:'4px', textTransform:'uppercase', letterSpacing:'0.5px' }}>{course.category}</div>
 <h3 style={{ fontSize:'15px', fontWeight:700, color:'#fff', marginBottom:'8px', lineHeight:'1.3' }}>{course.title}</h3>
 <p style={{ fontSize:'12px', color:'var(--text-muted)', marginBottom:'12px', lineHeight:'1.4', display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical', overflow:'hidden' }}>{course.short_description||course.description}</p>
 <div style={{ display:'flex', alignItems:'center', gap:'12px', marginBottom:'12px' }}>
 <div style={{ display:'flex', alignItems:'center', gap:'4px' }}>
 <Star size={12} color="#f59e0b" fill="#f59e0b" />
 <span style={{ fontSize:'12px', color:'#fff', fontWeight:600 }}>{course.avg_rating?.toFixed(1)||'New'}</span>
 </div>
 <span style={{ fontSize:'12px', color:'var(--text-muted)' }}> {course.total_enrolled||0} students</span>
 <span style={{ fontSize:'12px', color:'var(--text-muted)' }}> {course.total_lessons||0} lessons</span>
 </div>
 {course.enrolled && (
 <div style={{ marginBottom:'10px' }}>
 <div style={{ height:'4px', background:'rgba(255,255,255,0.1)', borderRadius:'2px', overflow:'hidden' }}>
 <div style={{ height:'100%', width:`${course.progress_pct||0}%`, background:'linear-gradient(90deg,#6366f1,#8b5cf6)', borderRadius:'2px', transition:'width 0.5s' }} />
 </div>
 <span style={{ fontSize:'11px', color:'var(--text-muted)', marginTop:'4px', display:'block' }}>{course.progress_pct||0}% complete</span>
 </div>
 )}
 {course.instructor && (
 <div style={{ fontSize:'12px', color:'var(--text-muted)', marginBottom:'12px' }}>
 by <span style={{ color:'#a5b4fc', fontWeight:600 }}>{course.instructor.display_name}</span>
 {course.instructor.verified && <span style={{ marginLeft:'4px', color:'#22c55e' }}></span>}
 </div>
 )}
 {course.enrolled ? (
 <div style={{ display:'flex', gap:'8px' }}>
 <button onClick={()=>{ setAcademySelectedCourse(course); setAcademySubView('course_detail'); }}
 style={{ flex:1, padding:'8px', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', border:'none', borderRadius:'8px', color:'#fff', fontWeight:600, fontSize:'13px', cursor:'pointer' }}>
 Continue Learning →
 </button>
 {(course.progress_pct||0) >= 80 && (
 <button onClick={()=>handleCompleteCourse(course.id)}
 style={{ padding:'8px 12px', background:'rgba(16,185,129,0.15)', border:'1px solid #10b981', borderRadius:'8px', color:'#10b981', fontWeight:600, fontSize:'12px', cursor:'pointer' }}>
 Claim Cert
 </button>
 )}
 </div>
 ) : (
 <button onClick={()=>handleEnroll(course.id)}
 style={{ width:'100%', padding:'9px', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', border:'none', borderRadius:'8px', color:'#fff', fontWeight:600, fontSize:'13px', cursor:'pointer' }}>
 {course.is_free ? 'Enroll Free' : `Enroll — $${course.price}`}
 </button>
 )}
 </div>
 </div>
 ))}
 </div>
 )}
 </div>
 )}

 {/* COURSE DETAIL */}
 {academySubView === 'course_detail' && academySelectedCourse && (
 <div style={{ display:'flex', flexDirection:'column', gap:'20px' }}>
 <button onClick={()=>setAcademySubView('discover')} style={{ display:'flex', alignItems:'center', gap:'6px', background:'none', border:'none', color:'var(--text-muted)', cursor:'pointer', fontSize:'13px', padding:0 }}>
 ← Back to Discover
 </button>
 <div className="glass-panel" style={{ padding:'24px' }}>
 <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', flexWrap:'wrap', gap:'16px' }}>
 <div>
 <span style={{ fontSize:'12px', color:'#a5b4fc', fontWeight:700, textTransform:'uppercase' }}>{academySelectedCourse.category}</span>
 <h2 style={{ fontSize:'22px', fontWeight:800, color:'#fff', margin:'6px 0 8px' }}>{academySelectedCourse.title}</h2>
 <p style={{ color:'var(--text-muted)', fontSize:'14px', lineHeight:'1.5', maxWidth:'600px' }}>{academySelectedCourse.description}</p>
 <div style={{ display:'flex', gap:'16px', marginTop:'12px', flexWrap:'wrap' }}>
 <span style={{ fontSize:'13px', color:LEVEL_COLORS[academySelectedCourse.level]||'#fff', fontWeight:600, textTransform:'capitalize' }}> {academySelectedCourse.level}</span>
 <span style={{ fontSize:'13px', color:'var(--text-muted)' }}> {academySelectedCourse.total_lessons||0} lessons</span>
 <span style={{ fontSize:'13px', color:'var(--text-muted)' }}> {academySelectedCourse.avg_rating?.toFixed(1)||'New'}</span>
 <span style={{ fontSize:'13px', color:'var(--text-muted)' }}> {academySelectedCourse.total_enrolled||0} enrolled</span>
 </div>
 {academySelectedCourse.skills_taught?.length > 0 && (
 <div style={{ display:'flex', gap:'6px', flexWrap:'wrap', marginTop:'12px' }}>
 {academySelectedCourse.skills_taught.map((s:string)=>(
 <span key={s} style={{ padding:'3px 10px', background:'rgba(99,102,241,0.15)', border:'1px solid rgba(99,102,241,0.3)', borderRadius:'20px', fontSize:'11px', color:'#a5b4fc', fontWeight:600 }}>{s}</span>
 ))}
 </div>
 )}
 </div>
 <div style={{ display:'flex', flexDirection:'column', gap:'8px', alignItems:'flex-end' }}>
 {!academySelectedCourse.enrolled && (
 <button onClick={()=>handleEnroll(academySelectedCourse.id)} style={{ padding:'12px 28px', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', border:'none', borderRadius:'10px', color:'#fff', fontWeight:700, fontSize:'15px', cursor:'pointer' }}>
 {academySelectedCourse.is_free ? 'Enroll Free' : `Enroll — $${academySelectedCourse.price}`}
 </button>
 )}
 {academySelectedCourse.enrolled && (academySelectedCourse.progress_pct||0) >= 80 && (
 <button onClick={()=>handleCompleteCourse(academySelectedCourse.id)} style={{ padding:'10px 20px', background:'rgba(16,185,129,0.15)', border:'1px solid #10b981', borderRadius:'10px', color:'#10b981', fontWeight:700, fontSize:'13px', cursor:'pointer' }}>
 Claim Certificate
 </button>
 )}
 </div>
 </div>
 {academySelectedCourse.enrolled && (
 <div style={{ marginTop:'16px' }}>
 <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'6px' }}>
 <span style={{ fontSize:'13px', color:'var(--text-muted)' }}>Your Progress</span>
 <span style={{ fontSize:'13px', color:'#fff', fontWeight:700 }}>{academySelectedCourse.progress_pct||0}%</span>
 </div>
 <div style={{ height:'8px', background:'rgba(255,255,255,0.08)', borderRadius:'4px', overflow:'hidden' }}>
 <div style={{ height:'100%', width:`${academySelectedCourse.progress_pct||0}%`, background:'linear-gradient(90deg,#6366f1,#8b5cf6)', borderRadius:'4px', transition:'width 0.5s' }} />
 </div>
 </div>
 )}
 </div>
 {/* Modules & Lessons */}
 {academySelectedCourse.modules?.length > 0 && (
 <div style={{ display:'flex', flexDirection:'column', gap:'12px' }}>
 <h3 style={{ color:'#fff', fontSize:'16px', fontWeight:700 }}>Course Content</h3>
 {academySelectedCourse.modules.map((mod:any, mi:number) => (
 <div key={mod.id} className="glass-panel" style={{ padding:'16px' }}>
 <div style={{ display:'flex', alignItems:'center', gap:'10px', marginBottom:'12px' }}>
 <div style={{ width:'28px', height:'28px', background:'rgba(99,102,241,0.2)', borderRadius:'8px', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'13px', fontWeight:700, color:'#a5b4fc' }}>{mi+1}</div>
 <span style={{ color:'#fff', fontWeight:700, fontSize:'15px' }}>{mod.title}</span>
 </div>
 <div style={{ display:'flex', flexDirection:'column', gap:'6px' }}>
 {mod.lessons?.map((lesson:any) => {
 const isCompleted = academySelectedCourse.completed_lesson_ids?.includes(lesson.id);
 const isLocked = !academySelectedCourse.enrolled && !lesson.is_preview;
 return (
 <div key={lesson.id} style={{ display:'flex', alignItems:'center', gap:'12px', padding:'10px 12px', borderRadius:'8px', background: isCompleted ? 'rgba(16,185,129,0.08)' : 'rgba(255,255,255,0.03)', border:`1px solid ${isCompleted?'rgba(16,185,129,0.2)':'rgba(255,255,255,0.06)'}` }}>
 {isCompleted ? <CheckCircle2 size={16} color="#10b981" /> : isLocked ? <Lock size={16} color="var(--text-muted)" /> : <PlayCircle size={16} color="#6366f1" />}
 <span style={{ flex:1, fontSize:'13px', color: isLocked ? 'var(--text-muted)' : '#fff' }}>{lesson.title}</span>
 {lesson.is_preview && <span style={{ fontSize:'11px', color:'#22c55e', fontWeight:600 }}>Preview</span>}
 <span style={{ fontSize:'12px', color:'var(--text-muted)' }}>{lesson.duration_mins}m</span>
 {academySelectedCourse.enrolled && !isCompleted && (
 <button onClick={async()=>{
 const res = await api.academy.updateProgress(academySelectedCourse.id, lesson.id);
 const updated = {...academySelectedCourse, completed_lesson_ids: res.completed_lesson_ids, progress_pct: res.progress_pct};
 setAcademySelectedCourse(updated);
 setAcademyCourses(prev => prev.map((c:any)=>c.id===updated.id?{...c,progress_pct:res.progress_pct}:c));
 }} style={{ padding:'3px 10px', background:'rgba(99,102,241,0.2)', border:'1px solid rgba(99,102,241,0.3)', borderRadius:'6px', color:'#a5b4fc', fontSize:'11px', cursor:'pointer', fontWeight:600 }}>
 Mark Done
 </button>
 )}
 </div>
 );
 })}
 </div>
 </div>
 ))}
 </div>
 )}
 </div>
 )}

 {/* MY LEARNING */}
 {academySubView === 'my_learning' && (
 <div style={{ display:'flex', flexDirection:'column', gap:'28px' }}>
 {/* Certificates */}
 {academyCertificates.length > 0 && (
 <div>
 <h3 style={{ color:'#fff', fontSize:'16px', fontWeight:700, marginBottom:'16px', display:'flex', alignItems:'center', gap:'8px' }}>
 <Trophy size={18} color="#f59e0b" /> Earned Certificates
 </h3>
 <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(280px,1fr))', gap:'16px' }}>
 {academyCertificates.map((cert:any) => (
 <div key={cert.id} className="glass-panel" style={{ padding:'20px', background:'linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.05))', border:'1px solid rgba(99,102,241,0.25)', position:'relative', overflow:'hidden' }}>
 <div style={{ position:'absolute', top:'-20px', right:'-20px', width:'80px', height:'80px', background:'radial-gradient(circle,rgba(99,102,241,0.2),transparent)', borderRadius:'50%' }} />
 <div style={{ fontSize:'32px', marginBottom:'8px' }}></div>
 <div style={{ fontSize:'11px', color:'#a5b4fc', fontWeight:700, textTransform:'uppercase', marginBottom:'4px' }}>Certificate of Completion</div>
 <div style={{ fontSize:'15px', fontWeight:800, color:'#fff', marginBottom:'4px' }}>{cert.course_title}</div>
 <div style={{ fontSize:'12px', color:'var(--text-muted)', marginBottom:'12px' }}>Instructor: {cert.instructor_name}</div>
 <div style={{ fontSize:'10px', color:'rgba(99,102,241,0.7)', fontFamily:'monospace', letterSpacing:'1px', background:'rgba(99,102,241,0.1)', padding:'4px 8px', borderRadius:'4px', display:'inline-block' }}>
 ID: {cert.credential_id.slice(0,16)}…
 </div>
 <div style={{ fontSize:'11px', color:'var(--text-muted)', marginTop:'8px' }}>Issued: {new Date(cert.issued_at).toLocaleDateString()}</div>
 </div>
 ))}
 </div>
 </div>
 )}
 {/* Enrolled Courses */}
 <div>
 <h3 style={{ color:'#fff', fontSize:'16px', fontWeight:700, marginBottom:'16px', display:'flex', alignItems:'center', gap:'8px' }}>
 <BookOpen size={18} color="#6366f1" /> My Courses ({academyEnrollments.length})
 </h3>
 {academyEnrollments.length === 0 ? (
 <div style={{ textAlign:'center', padding:'48px', color:'var(--text-muted)' }}>
 <BookOpen size={40} style={{ opacity:0.3, marginBottom:'12px' }} />
 <p>You haven't enrolled in any courses yet.</p>
 <button onClick={()=>setAcademySubView('discover')} style={{ marginTop:'12px', padding:'9px 22px', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', border:'none', borderRadius:'8px', color:'#fff', fontWeight:600, cursor:'pointer' }}>
 Browse Courses
 </button>
 </div>
 ) : (
 <div style={{ display:'flex', flexDirection:'column', gap:'12px' }}>
 {academyEnrollments.map((course:any) => (
 <div key={course.id} className="glass-panel" style={{ padding:'16px', display:'flex', alignItems:'center', gap:'16px' }}>
 <div style={{ width:'48px', height:'48px', background:`linear-gradient(135deg, ${['#6366f1','#8b5cf6','#06b6d4','#10b981','#f59e0b'][course.id%5]}, rgba(0,0,0,0.3))`, borderRadius:'10px', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
 <BookOpen size={20} color="rgba(255,255,255,0.8)" />
 </div>
 <div style={{ flex:1, minWidth:0 }}>
 <div style={{ fontSize:'14px', fontWeight:700, color:'#fff', marginBottom:'4px', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{course.title}</div>
 <div style={{ fontSize:'12px', color:'var(--text-muted)', marginBottom:'8px' }}>{course.category} · {course.level}</div>
 <div style={{ height:'6px', background:'rgba(255,255,255,0.08)', borderRadius:'3px', overflow:'hidden', marginBottom:'4px' }}>
 <div style={{ height:'100%', width:`${course.progress_pct||0}%`, background:'linear-gradient(90deg,#6366f1,#8b5cf6)', borderRadius:'3px', transition:'width 0.5s' }} />
 </div>
 <div style={{ fontSize:'11px', color:'var(--text-muted)' }}>{course.progress_pct||0}% complete</div>
 </div>
 <div style={{ display:'flex', gap:'8px', flexShrink:0 }}>
 <button onClick={async()=>{const detail=await api.academy.getCourse(course.id);setAcademySelectedCourse({...detail,enrolled:true,progress_pct:course.progress_pct,completed_lesson_ids:course.completed_lesson_ids});setAcademySubView('course_detail');}} style={{ padding:'7px 14px', background:'rgba(99,102,241,0.2)', border:'1px solid rgba(99,102,241,0.3)', borderRadius:'8px', color:'#a5b4fc', fontSize:'12px', cursor:'pointer', fontWeight:600 }}>
 Continue →
 </button>
 {(course.progress_pct||0) >= 80 && !course.completed_at && (
 <button onClick={()=>handleCompleteCourse(course.id)} style={{ padding:'7px 14px', background:'rgba(16,185,129,0.15)', border:'1px solid #10b981', borderRadius:'8px', color:'#10b981', fontSize:'12px', cursor:'pointer', fontWeight:600 }}>
 Finish
 </button>
 )}
 {course.completed_at && <span style={{ padding:'7px 14px', color:'#10b981', fontSize:'12px', fontWeight:700 }}> Done</span>}
 </div>
 </div>
 ))}
 </div>
 )}
 </div>
 </div>
 )}

 {/* SKILL GAP ENGINE */}
 {academySubView === 'skill_gap' && (
 <div style={{ display:'flex', flexDirection:'column', gap:'24px', maxWidth:'800px' }}>
 <div>
 <h2 style={{ color:'#fff', fontSize:'20px', fontWeight:800, marginBottom:'6px', display:'flex', alignItems:'center', gap:'10px' }}>
 <Target size={22} color="#6366f1" /> AI Skill Gap Engine
 </h2>
 <p style={{ color:'var(--text-muted)', fontSize:'14px' }}>
 Enter a job title and its required skills. Atlas AI compares them against your profile and recommends exactly what to learn.
 </p>
 </div>
 <div className="glass-panel" style={{ padding:'24px', display:'flex', flexDirection:'column', gap:'16px' }}>
 <div>
 <label style={{ fontSize:'13px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'6px' }}>Job Title</label>
 <input value={academySkillGapJobTitle} onChange={e=>setAcademySkillGapJobTitle(e.target.value)}
 placeholder="e.g. Senior Backend Engineer"
 style={{ width:'100%', padding:'10px 14px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.12)', borderRadius:'10px', color:'#fff', fontSize:'14px', boxSizing:'border-box' }} />
 </div>
 <div>
 <label style={{ fontSize:'13px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'6px' }}>Required Skills (comma-separated)</label>
 <input value={academySkillGapJobSkills} onChange={e=>setAcademySkillGapJobSkills(e.target.value)}
 placeholder="e.g. Python, Docker, Kubernetes, AWS, Redis"
 style={{ width:'100%', padding:'10px 14px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.12)', borderRadius:'10px', color:'#fff', fontSize:'14px', boxSizing:'border-box' }} />
 </div>
 <button onClick={handleSkillGap} disabled={academySkillGapLoading}
 style={{ padding:'12px 28px', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', border:'none', borderRadius:'10px', color:'#fff', fontWeight:700, fontSize:'14px', cursor:'pointer', display:'flex', alignItems:'center', gap:'8px', alignSelf:'flex-start', opacity: academySkillGapLoading?0.7:1 }}>
 {academySkillGapLoading ? <><span className="pulse-glow">⏳</span> Analyzing…</> : <><Zap size={16} /> Analyze Gap</>}
 </button>
 </div>

 {academySkillGapResult && (
 <div style={{ display:'flex', flexDirection:'column', gap:'16px' }}>
 {/* Match Score */}
 <div className="glass-panel" style={{ padding:'20px', textAlign:'center', background:'linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.05))' }}>
 <div style={{ fontSize:'48px', fontWeight:900, color: academySkillGapResult.match_score>=70?'#22c55e':academySkillGapResult.match_score>=40?'#f59e0b':'#ef4444' }}>{academySkillGapResult.match_score}%</div>
 <div style={{ color:'var(--text-muted)', fontSize:'14px' }}>Match Score for <strong style={{ color:'#fff' }}>{academySkillGapResult.job_title}</strong></div>
 <div style={{ height:'8px', background:'rgba(255,255,255,0.08)', borderRadius:'4px', margin:'12px 0', overflow:'hidden' }}>
 <div style={{ height:'100%', width:`${academySkillGapResult.match_score}%`, background:`linear-gradient(90deg,${academySkillGapResult.match_score>=70?'#22c55e':academySkillGapResult.match_score>=40?'#f59e0b':'#ef4444'},#6366f1)`, transition:'width 1s' }} />
 </div>
 </div>
 {/* Skills Grid */}
 <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'16px' }}>
 <div className="glass-panel" style={{ padding:'16px', border:'1px solid rgba(34,197,94,0.2)' }}>
 <h4 style={{ color:'#22c55e', fontSize:'13px', fontWeight:700, marginBottom:'12px', display:'flex', alignItems:'center', gap:'6px' }}><CheckCircle size={14} /> You Have ({academySkillGapResult.matching_skills.length})</h4>
 <div style={{ display:'flex', flexWrap:'wrap', gap:'6px' }}>
 {academySkillGapResult.matching_skills.map((s:string)=>(
 <span key={s} style={{ padding:'4px 10px', background:'rgba(34,197,94,0.1)', border:'1px solid rgba(34,197,94,0.25)', borderRadius:'20px', fontSize:'12px', color:'#22c55e', fontWeight:600 }}>{s}</span>
 ))}
 </div>
 </div>
 <div className="glass-panel" style={{ padding:'16px', border:'1px solid rgba(239,68,68,0.2)' }}>
 <h4 style={{ color:'#ef4444', fontSize:'13px', fontWeight:700, marginBottom:'12px', display:'flex', alignItems:'center', gap:'6px' }}> Missing ({academySkillGapResult.missing_skills.length})</h4>
 <div style={{ display:'flex', flexWrap:'wrap', gap:'6px' }}>
 {academySkillGapResult.missing_skills.map((s:string)=>(
 <span key={s} style={{ padding:'4px 10px', background:'rgba(239,68,68,0.1)', border:'1px solid rgba(239,68,68,0.25)', borderRadius:'20px', fontSize:'12px', color:'#ef4444', fontWeight:600 }}>{s}</span>
 ))}
 </div>
 </div>
 </div>
 {/* AI Roadmap */}
 {academySkillGapResult.ai_roadmap && (
 <div className="glass-panel" style={{ padding:'20px' }}>
 <h4 style={{ color:'#fff', fontSize:'14px', fontWeight:700, marginBottom:'12px', display:'flex', alignItems:'center', gap:'8px' }}><Zap size={16} color="#6366f1" /> AI Learning Roadmap</h4>
 <pre style={{ color:'var(--text-muted)', fontSize:'13px', lineHeight:'1.7', whiteSpace:'pre-wrap', fontFamily:'inherit', margin:0 }}>{academySkillGapResult.ai_roadmap}</pre>
 </div>
 )}
 {/* Recommended Courses */}
 {academySkillGapResult.recommended_courses?.length > 0 && (
 <div>
 <h4 style={{ color:'#fff', fontSize:'14px', fontWeight:700, marginBottom:'12px' }}> Recommended Courses</h4>
 <div style={{ display:'flex', flexDirection:'column', gap:'10px' }}>
 {academySkillGapResult.recommended_courses.map((c:any)=>(
 <div key={c.id} className="glass-panel" style={{ padding:'14px 16px', display:'flex', alignItems:'center', justifyContent:'space-between', gap:'12px' }}>
 <div>
 <div style={{ fontSize:'14px', fontWeight:700, color:'#fff', marginBottom:'4px' }}>{c.title}</div>
 <div style={{ display:'flex', gap:'6px', flexWrap:'wrap' }}>
 {c.covers_skills?.map((s:string)=>(
 <span key={s} style={{ padding:'2px 8px', background:'rgba(99,102,241,0.15)', borderRadius:'10px', fontSize:'11px', color:'#a5b4fc', fontWeight:600 }}>{s}</span>
 ))}
 </div>
 </div>
 <button onClick={()=>handleEnroll(c.id)} style={{ padding:'8px 16px', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', border:'none', borderRadius:'8px', color:'#fff', fontWeight:600, fontSize:'12px', cursor:'pointer', flexShrink:0 }}>
 {c.is_free ? 'Enroll Free' : `$${c.price}`}
 </button>
 </div>
 ))}
 </div>
 </div>
 )}
 </div>
 )}

 {/* AI Roadmap Generator */}
 <div className="glass-panel" style={{ padding:'20px', marginTop:'8px' }}>
 <h3 style={{ color:'#fff', fontSize:'15px', fontWeight:700, marginBottom:'6px', display:'flex', alignItems:'center', gap:'8px' }}><Zap size={16} color="#8b5cf6" /> Career Roadmap Generator</h3>
 <p style={{ color:'var(--text-muted)', fontSize:'13px', marginBottom:'14px' }}>Tell us your dream career goal and get a personalized month-by-month roadmap.</p>
 <div style={{ display:'flex', gap:'10px' }}>
 <input value={academyRoadmapGoal} onChange={e=>setAcademyRoadmapGoal(e.target.value)}
 placeholder="e.g. Become an AI Engineer, Get a job at Google, Learn DevOps"
 style={{ flex:1, padding:'10px 14px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.12)', borderRadius:'10px', color:'#fff', fontSize:'14px' }} />
 <button onClick={handleRoadmap} disabled={academyRoadmapLoading}
 style={{ padding:'10px 20px', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', border:'none', borderRadius:'10px', color:'#fff', fontWeight:600, fontSize:'13px', cursor:'pointer', opacity:academyRoadmapLoading?0.7:1, flexShrink:0 }}>
 {academyRoadmapLoading ? '⏳ Building…' : ' Generate'}
 </button>
 </div>
 {academyRoadmap && (
 <pre style={{ marginTop:'16px', color:'var(--text-muted)', fontSize:'13px', lineHeight:'1.7', whiteSpace:'pre-wrap', fontFamily:'inherit', background:'rgba(255,255,255,0.03)', padding:'14px', borderRadius:'8px' }}>{academyRoadmap}</pre>
 )}
 </div>
 </div>
 )}

 {/* AI MENTOR */}
 {academySubView === 'ai_mentor' && (
 <div style={{ display:'flex', flexDirection:'column', gap:'20px', maxWidth:'760px' }}>
 <div>
 <h2 style={{ color:'#fff', fontSize:'20px', fontWeight:800, marginBottom:'6px', display:'flex', alignItems:'center', gap:'10px' }}>
 <Sparkles size={22} color="#8b5cf6" /> AI Mentor — Nova
 </h2>
 <p style={{ color:'var(--text-muted)', fontSize:'14px' }}>Ask anything — explain concepts, quiz me, review my code, build my roadmap.</p>
 </div>
 <div className="glass-panel" style={{ padding:'0', overflow:'hidden' }}>
 <div style={{ padding:'20px', borderBottom:'1px solid rgba(255,255,255,0.06)', display:'flex', flexWrap:'wrap', gap:'8px' }}>
 {['Explain Kubernetes','Quiz me on React','Review this code','Build my roadmap','What is Docker?','Help me with Python'].map(prompt=>(
 <button key={prompt} onClick={()=>{ setAcademyMentorInput(prompt); }}
 style={{ padding:'5px 12px', background:'rgba(99,102,241,0.1)', border:'1px solid rgba(99,102,241,0.2)', borderRadius:'20px', color:'#a5b4fc', fontSize:'12px', cursor:'pointer', fontWeight:500 }}>
 {prompt}
 </button>
 ))}
 </div>
 <div style={{ height:'400px', overflowY:'auto', padding:'20px', display:'flex', flexDirection:'column', gap:'14px' }}>
 {academyMentorMessages.length === 0 && (
 <div style={{ textAlign:'center', paddingTop:'60px', color:'var(--text-muted)' }}>
 <Sparkles size={36} style={{ opacity:0.3, marginBottom:'12px' }} />
 <p style={{ fontSize:'15px', color:'rgba(255,255,255,0.5)' }}>Hi! I'm Nova, your AI mentor.<br/>Ask me anything about your learning journey.</p>
 </div>
 )}
 {academyMentorMessages.map((msg, i) => (
 <div key={i} style={{ display:'flex', justifyContent: msg.role==='user'?'flex-end':'flex-start' }}>
 <div style={{ maxWidth:'75%', padding:'12px 16px', borderRadius: msg.role==='user'?'16px 16px 4px 16px':'16px 16px 16px 4px',
 background: msg.role==='user'?'linear-gradient(135deg,#6366f1,#8b5cf6)':'rgba(255,255,255,0.05)',
 color: msg.role==='user'?'#fff':'var(--text-primary)', fontSize:'13px', lineHeight:'1.6', whiteSpace:'pre-wrap' }}>
 {msg.role==='assistant' && <div style={{ fontSize:'11px', color:'#8b5cf6', fontWeight:700, marginBottom:'6px' }}> Nova</div>}
 {msg.content}
 </div>
 </div>
 ))}
 {academyMentorLoading && (
 <div style={{ display:'flex' }}>
 <div style={{ padding:'12px 16px', borderRadius:'16px 16px 16px 4px', background:'rgba(255,255,255,0.05)', color:'var(--text-muted)', fontSize:'13px' }}>
 <span className="pulse-glow"> Nova is thinking…</span>
 </div>
 </div>
 )}
 </div>
 <div style={{ padding:'16px', borderTop:'1px solid rgba(255,255,255,0.06)', display:'flex', gap:'10px' }}>
 <input value={academyMentorInput} onChange={e=>setAcademyMentorInput(e.target.value)}
 onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();handleMentorSend();}}}
 placeholder="Ask Nova anything…"
 style={{ flex:1, padding:'10px 14px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'10px', color:'#fff', fontSize:'14px' }} />
 <button onClick={handleMentorSend} disabled={academyMentorLoading}
 style={{ padding:'10px 18px', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', border:'none', borderRadius:'10px', color:'#fff', cursor:'pointer', display:'flex', alignItems:'center', gap:'6px', fontWeight:600, fontSize:'13px', opacity:academyMentorLoading?0.7:1 }}>
 <Send size={14} /> Ask
 </button>
 </div>
 </div>
 </div>
 )}

 {/* INSTRUCTOR PORTAL */}
 {academySubView === 'instructor' && (
 <div style={{ display:'flex', flexDirection:'column', gap:'24px' }}>
 {(!academyInstructor || !academyInstructor.is_instructor) ? (
 /* Apply to become instructor */
 <div style={{ maxWidth:'560px' }}>
 <h2 style={{ color:'#fff', fontSize:'20px', fontWeight:800, marginBottom:'6px', display:'flex', alignItems:'center', gap:'10px' }}>
 <GraduationCap size={22} color="#6366f1" /> Become an Instructor
 </h2>
 <p style={{ color:'var(--text-muted)', fontSize:'14px', marginBottom:'24px' }}>
 Share your expertise. Earn revenue. Build a following. Create courses on Atlas Academy and help thousands of professionals grow.
 </p>
 <div className="glass-panel" style={{ padding:'24px', display:'flex', flexDirection:'column', gap:'16px' }}>
 <div>
 <label style={{ fontSize:'13px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'6px' }}>Display Name</label>
 <input value={academyInstructorForm.display_name} onChange={e=>setAcademyInstructorForm(p=>({...p,display_name:e.target.value}))}
 placeholder="Your instructor name"
 style={{ width:'100%', padding:'10px 14px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.12)', borderRadius:'10px', color:'#fff', fontSize:'14px', boxSizing:'border-box' }} />
 </div>
 <div>
 <label style={{ fontSize:'13px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'6px' }}>Bio</label>
 <textarea value={academyInstructorForm.bio} onChange={e=>setAcademyInstructorForm(p=>({...p,bio:e.target.value}))}
 placeholder="Tell students about your background…" rows={3}
 style={{ width:'100%', padding:'10px 14px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.12)', borderRadius:'10px', color:'#fff', fontSize:'14px', resize:'vertical', boxSizing:'border-box' }} />
 </div>
 <div>
 <label style={{ fontSize:'13px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'6px' }}>Expertise (comma-separated)</label>
 <input value={academyInstructorForm.expertise} onChange={e=>setAcademyInstructorForm(p=>({...p,expertise:e.target.value}))}
 placeholder="e.g. Python, Machine Learning, Cloud Architecture"
 style={{ width:'100%', padding:'10px 14px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.12)', borderRadius:'10px', color:'#fff', fontSize:'14px', boxSizing:'border-box' }} />
 </div>
 <button onClick={handleApplyInstructor} style={{ padding:'12px', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', border:'none', borderRadius:'10px', color:'#fff', fontWeight:700, fontSize:'14px', cursor:'pointer' }}>
 Apply as Instructor
 </button>
 </div>
 </div>
 ) : (
 /* Instructor Dashboard */
 <div style={{ display:'flex', flexDirection:'column', gap:'24px' }}>
 {/* Dashboard header */}
 <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:'12px' }}>
 <div>
 <h2 style={{ color:'#fff', fontSize:'20px', fontWeight:800, marginBottom:'4px' }}>
 Instructor Dashboard
 {academyInstructor.verified && <span style={{ marginLeft:'8px', fontSize:'12px', color:'#22c55e', background:'rgba(34,197,94,0.1)', padding:'2px 8px', borderRadius:'20px', verticalAlign:'middle' }}> Verified</span>}
 </h2>
 <p style={{ color:'var(--text-muted)', fontSize:'13px' }}>Welcome back, {academyInstructor.display_name}</p>
 </div>
 </div>
 {/* Stats */}
 <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(180px,1fr))', gap:'14px' }}>
 {[
 { label:'Total Courses', value: academyInstructor.courses?.length||0, icon:'', color:'#6366f1' },
 { label:'Total Students', value: academyInstructor.total_students||0, icon:'', color:'#22c55e' },
 { label:'Total Revenue', value: `$${(academyInstructor.total_revenue||0).toFixed(2)}`, icon:'', color:'#f59e0b' },
 { label:'Revenue Share', value: `${((academyInstructor.revenue_share||0.7)*100).toFixed(0)}%`, icon:'', color:'#8b5cf6' },
 ].map(s=>(
 <div key={s.label} className="glass-panel" style={{ padding:'16px', textAlign:'center', border:`1px solid ${s.color}25` }}>
 <div style={{ fontSize:'24px', marginBottom:'4px' }}>{s.icon}</div>
 <div style={{ fontSize:'22px', fontWeight:800, color:s.color }}>{s.value}</div>
 <div style={{ fontSize:'11px', color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'0.5px' }}>{s.label}</div>
 </div>
 ))}
 </div>

 {/* Create Course */}
 <div className="glass-panel" style={{ padding:'22px' }}>
 <h3 style={{ color:'#fff', fontSize:'15px', fontWeight:700, marginBottom:'16px', display:'flex', alignItems:'center', gap:'8px' }}><Plus size={16} color="#6366f1" /> Create New Course</h3>
 <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'12px' }}>
 <div style={{ gridColumn:'1/-1' }}>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Course Title</label>
 <input value={academyCourseForm.title} onChange={e=>setAcademyCourseForm(p=>({...p,title:e.target.value}))}
 placeholder="e.g. Complete Kubernetes Bootcamp"
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }} />
 </div>
 <div style={{ gridColumn:'1/-1' }}>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Description</label>
 <textarea value={academyCourseForm.description} onChange={e=>setAcademyCourseForm(p=>({...p,description:e.target.value}))} rows={2}
 placeholder="What will students learn?"
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', resize:'vertical', boxSizing:'border-box' }} />
 </div>
 <div>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Category</label>
 <select value={academyCourseForm.category} onChange={e=>setAcademyCourseForm(p=>({...p,category:e.target.value}))}
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }}>
 {ACADEMY_CATEGORIES.map(c=><option key={c} value={c}>{c}</option>)}
 </select>
 </div>
 <div>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Level</label>
 <select value={academyCourseForm.level} onChange={e=>setAcademyCourseForm(p=>({...p,level:e.target.value}))}
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }}>
 <option value="beginner">Beginner</option>
 <option value="intermediate">Intermediate</option>
 <option value="advanced">Advanced</option>
 </select>
 </div>
 <div>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Skills Taught (comma-separated)</label>
 <input value={academyCourseForm.skills_taught} onChange={e=>setAcademyCourseForm(p=>({...p,skills_taught:e.target.value}))}
 placeholder="e.g. Kubernetes, Docker, Helm"
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }} />
 </div>
 <div>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Price ($) — 0 for free</label>
 <input type="number" min="0" value={academyCourseForm.price} onChange={e=>setAcademyCourseForm(p=>({...p,price:Number(e.target.value),is_free:Number(e.target.value)===0}))}
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }} />
 </div>
 </div>
 <button onClick={handleCreateCourse} style={{ marginTop:'14px', padding:'10px 24px', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', border:'none', borderRadius:'8px', color:'#fff', fontWeight:700, fontSize:'13px', cursor:'pointer' }}>
 + Create Course
 </button>
 </div>

 {/* My Courses list */}
 {academyInstructor.courses?.length > 0 && (
 <div>
 <h3 style={{ color:'#fff', fontSize:'15px', fontWeight:700, marginBottom:'12px' }}>My Courses</h3>
 <div style={{ display:'flex', flexDirection:'column', gap:'10px' }}>
 {academyInstructor.courses.map((course:any) => (
 <div key={course.id} className="glass-panel" style={{ padding:'14px 16px', display:'flex', alignItems:'center', gap:'14px' }}>
 <div style={{ width:'40px', height:'40px', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', borderRadius:'10px', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
 <BookOpen size={18} color="#fff" />
 </div>
 <div style={{ flex:1 }}>
 <div style={{ fontSize:'14px', fontWeight:700, color:'#fff', marginBottom:'3px' }}>{course.title}</div>
 <div style={{ fontSize:'12px', color:'var(--text-muted)' }}>
 {course.category} · {course.level} · {course.total_enrolled} · {course.avg_rating?.toFixed(1)||'New'}
 </div>
 </div>
 <span style={{ padding:'4px 10px', borderRadius:'20px', fontSize:'11px', fontWeight:700, background: course.is_published?'rgba(34,197,94,0.1)':'rgba(245,158,11,0.1)', color: course.is_published?'#22c55e':'#f59e0b', border:`1px solid ${course.is_published?'rgba(34,197,94,0.25)':'rgba(245,158,11,0.25)'}` }}>
 {course.is_published ? ' Live' : 'Draft'}
 </span>
 {!course.is_published && (
 <button onClick={()=>handlePublishCourse(course.id)} style={{ padding:'7px 14px', background:'linear-gradient(135deg,#22c55e,#16a34a)', border:'none', borderRadius:'8px', color:'#fff', fontWeight:600, fontSize:'12px', cursor:'pointer' }}>
 Publish
 </button>
 )}
 </div>
 ))}
 </div>
 </div>
 )}
 </div>
 )}
 </div>
 )}

 </div>
 </div>
 );
 })()}

 {/* TAB: CAREER HUB */}
 {activeTab === 'resume_builder' && (() => {
 const handleGenerateResume = async () => {
 setResumeGenerating(true);
 try {
 const res = await api.career.generateResume({ template: resumeTemplate, target_role: resumeTargetRole });
 setResumeGenerated(res);
 if (res.resume_text) setResumeTextInput(res.resume_text);
 } catch(e:any){ alert(e.message); } finally { setResumeGenerating(false); }
 };

 const handleScoreResume = async () => {
 if (!resumeTextInput || !resumeJobDescInput) return;
 setResumeScoreLoading(true);
 try {
 const res = await api.career.scoreResume({ resume_text: resumeTextInput, job_description: resumeJobDescInput });
 setResumeScoreResult(res);
 } catch(e:any){ alert(e.message); } finally { setResumeScoreLoading(false); }
 };

 const handleSalaryLookup = async () => {
 if (!salaryJobTitle) return;
 setSalaryLoading(true);
 try {
 const res = await api.career.getSalaryInsights({ job_title: salaryJobTitle, location: salaryLocation, experience_years: salaryExpYears });
 setSalaryResult(res);
 } catch(e:any){ alert(e.message); } finally { setSalaryLoading(false); }
 };

 const handleSubmitShowcase = async () => {
 if (!showcaseForm.title) return;
 setShowcaseSubmitting(true);
 try {
 await api.career.submitShowcaseProject(showcaseForm);
 alert(' Project submitted!');
 setShowcaseForm({ title: '', description: '', github_url: '', demo_url: '', tech_stack: '', category: 'Web Development' });
 const showcase = await api.career.listShowcaseProjects();
 setShowcaseProjects(showcase?.projects || []);
 } catch(e:any){ alert(e.message); } finally { setShowcaseSubmitting(false); }
 };

 const scoreColor = (s: number) => s >= 75 ? '#22c55e' : s >= 50 ? '#f59e0b' : '#ef4444';
 const verdictBg: Record<string,string> = { 'Excellent Match': '#22c55e', 'Strong Match': '#22c55e', 'Good Match': '#f59e0b', 'Partial Match': '#f59e0b', 'Weak Match': '#ef4444' };

 return (
 <div className="animate-fade-in" style={{ display:'flex', flexDirection:'column', gap:'0', minHeight:'100%' }}>

 {/* CAREER HUB HEADER */}
 <div style={{ background:'linear-gradient(135deg, #0a1a0a 0%, #0d2818 50%, #0f3020 100%)', borderBottom:'1px solid rgba(16,185,129,0.2)', padding:'28px 32px', position:'relative', overflow:'hidden' }}>
 <div style={{ position:'absolute', top:'-40px', right:'-40px', width:'200px', height:'200px', background:'radial-gradient(circle, rgba(16,185,129,0.12) 0%, transparent 70%)', borderRadius:'50%' }} />
 <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', flexWrap:'wrap', gap:'16px', position:'relative', zIndex:1 }}>
 <div>
 <div style={{ display:'flex', alignItems:'center', gap:'12px', marginBottom:'8px' }}>
 <div style={{ width:'42px', height:'42px', background:'linear-gradient(135deg, #10b981, #059669)', borderRadius:'12px', display:'flex', alignItems:'center', justifyContent:'center' }}>
 <FileText size={22} color="#fff" />
 </div>
 <div>
 <h1 style={{ fontSize:'26px', fontWeight:800, color:'#fff', margin:0 }}>Career Hub</h1>
 <p style={{ color:'rgba(16,185,129,0.9)', fontSize:'13px', margin:0, fontWeight:500 }}>Build · Score · Earn · Showcase</p>
 </div>
 </div>
 <p style={{ color:'var(--text-muted)', fontSize:'14px', maxWidth:'500px', lineHeight:'1.5' }}>
 AI-powered resume builder, salary intelligence, career analytics, gamification & project showcase.
 </p>
 </div>
 {/* Quick stats */}
 <div style={{ display:'flex', gap:'14px', flexWrap:'wrap' }}>
 {[
 { label: 'XP Level', value: gamificationStats ? `Lv.${gamificationStats.level}` : '—', emoji:'', color:'#f59e0b' },
 { label: 'Profile', value: profileScore ? `${profileScore.total_score}pts` : '—', emoji:'', color:'#10b981' },
 { label: 'Applications', value: careerAnalytics?.total_applications ?? '—', emoji:'', color:'#6366f1' },
 { label: 'Response Rate', value: careerAnalytics ? `${careerAnalytics.response_rate}%` : '—', emoji:'', color:'#22c55e' },
 ].map(s => (
 <div key={s.label} style={{ textAlign:'center', background:'rgba(255,255,255,0.04)', borderRadius:'12px', padding:'10px 16px', border:`1px solid ${s.color}25` }}>
 <div style={{ fontSize:'18px' }}>{s.emoji}</div>
 <div style={{ fontSize:'18px', fontWeight:800, color:s.color }}>{s.value}</div>
 <div style={{ fontSize:'10px', color:'var(--text-muted)', textTransform:'uppercase' }}>{s.label}</div>
 </div>
 ))}
 </div>
 </div>

 {/* Sub-nav */}
 <div style={{ display:'flex', gap:'6px', marginTop:'20px', flexWrap:'wrap' }}>
 {([
 { id: 'builder', label: ' Resume Builder' },
 { id: 'score', label: ' ATS Score' },
 { id: 'salary', label: ' Salary Intel' },
 { id: 'analytics', label: ' Career Analytics' },
 { id: 'gamification', label: ' Achievements' },
 { id: 'showcase', label: ' Showcase' },
 ] as const).map(t => (
 <button key={t.id} onClick={() => setResumeSubView(t.id)}
 style={{ padding:'7px 16px', borderRadius:'20px', fontSize:'13px', fontWeight:600, border:'none', cursor:'pointer', transition:'all 0.2s',
 background: resumeSubView === t.id ? 'linear-gradient(135deg, #10b981, #059669)' : 'rgba(255,255,255,0.07)',
 color: resumeSubView === t.id ? '#fff' : 'var(--text-muted)' }}>
 {t.label}
 </button>
 ))}
 </div>
 </div>

 <div style={{ padding:'28px 32px', flex:1 }}>

 {/* RESUME BUILDER */}
 {resumeSubView === 'builder' && (
 <div style={{ display:'flex', flexDirection:'column', gap:'24px' }}>
 <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'24px' }}>
 {/* Left: Config */}
 <div style={{ display:'flex', flexDirection:'column', gap:'16px' }}>
 <div className="glass-panel" style={{ padding:'22px' }}>
 <h3 style={{ color:'#fff', fontSize:'15px', fontWeight:700, marginBottom:'16px', display:'flex', alignItems:'center', gap:'8px' }}>
 <FileText size={16} color="#10b981" /> Generate AI Resume
 </h3>
 <div style={{ display:'flex', flexDirection:'column', gap:'12px' }}>
 <div>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Template Style</label>
 <div style={{ display:'flex', gap:'8px' }}>
 {(['modern', 'minimal', 'technical'] as const).map(t => (
 <button key={t} onClick={() => setResumeTemplate(t)}
 style={{ flex:1, padding:'8px', borderRadius:'8px', border:`1px solid ${resumeTemplate===t?'#10b981':'rgba(255,255,255,0.1)'}`, background: resumeTemplate===t?'rgba(16,185,129,0.15)':'transparent', color: resumeTemplate===t?'#10b981':'var(--text-muted)', fontSize:'12px', cursor:'pointer', fontWeight:600, textTransform:'capitalize' }}>
 {t}
 </button>
 ))}
 </div>
 </div>
 <div>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Target Role (optional)</label>
 <input value={resumeTargetRole} onChange={e => setResumeTargetRole(e.target.value)}
 placeholder="e.g. Senior Full Stack Engineer"
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }} />
 </div>
 <button onClick={handleGenerateResume} disabled={resumeGenerating}
 style={{ padding:'11px', background:'linear-gradient(135deg,#10b981,#059669)', border:'none', borderRadius:'8px', color:'#fff', fontWeight:700, fontSize:'13px', cursor:'pointer', opacity:resumeGenerating?0.7:1, display:'flex', alignItems:'center', justifyContent:'center', gap:'8px' }}>
 {resumeGenerating ? <><span className="pulse-glow">⏳</span> Building Your Resume…</> : ' Generate AI Resume'}
 </button>
 </div>
 </div>

 {/* ATS Score card after generation */}
 {resumeGenerated && (
 <div className="glass-panel" style={{ padding:'18px', border:'1px solid rgba(16,185,129,0.2)' }}>
 <h4 style={{ color:'#fff', fontSize:'14px', fontWeight:700, marginBottom:'12px' }}> Resume Report</h4>
 <div style={{ display:'flex', gap:'12px', marginBottom:'12px' }}>
 <div style={{ flex:1, textAlign:'center', background:'rgba(16,185,129,0.08)', borderRadius:'10px', padding:'12px' }}>
 <div style={{ fontSize:'28px', fontWeight:900, color: scoreColor(resumeGenerated.ats_score) }}>{resumeGenerated.ats_score}</div>
 <div style={{ fontSize:'11px', color:'var(--text-muted)', textTransform:'uppercase' }}>ATS Score</div>
 </div>
 <div style={{ flex:1, textAlign:'center', background:'rgba(99,102,241,0.08)', borderRadius:'10px', padding:'12px' }}>
 <div style={{ fontSize:'28px', fontWeight:900, color:'#6366f1' }}>{resumeGenerated.word_count}</div>
 <div style={{ fontSize:'11px', color:'var(--text-muted)', textTransform:'uppercase' }}>Words</div>
 </div>
 </div>
 {resumeGenerated.tips?.map((tip: string, i: number) => (
 <div key={i} style={{ display:'flex', gap:'8px', marginBottom:'6px', fontSize:'12px', color:'var(--text-muted)', alignItems:'flex-start' }}>
 <span style={{ color:'#f59e0b', flexShrink:0 }}></span>{tip}
 </div>
 ))}
 </div>
 )}
 </div>

 {/* Right: Generated Resume */}
 <div className="glass-panel" style={{ padding:'0', overflow:'hidden', display:'flex', flexDirection:'column' }}>
 <div style={{ padding:'12px 16px', borderBottom:'1px solid rgba(255,255,255,0.06)', display:'flex', alignItems:'center', justifyContent:'space-between' }}>
 <span style={{ fontSize:'13px', color:'var(--text-muted)', fontWeight:600 }}>
 {resumeGenerated ? ` Generated (${resumeTemplate} template)` : 'Your Resume Preview'}
 </span>
 {resumeGenerated && (
 <button onClick={() => { navigator.clipboard.writeText(resumeGenerated.resume_text); alert('Copied to clipboard!'); }}
 style={{ padding:'4px 12px', background:'rgba(16,185,129,0.15)', border:'1px solid #10b981', borderRadius:'6px', color:'#10b981', fontSize:'12px', cursor:'pointer', fontWeight:600 }}>
 Copy
 </button>
 )}
 </div>
 <textarea value={resumeTextInput} onChange={e => setResumeTextInput(e.target.value)}
 placeholder="Your AI-generated resume will appear here...&#10;&#10;You can also paste your existing resume here to score it against job descriptions."
 style={{ flex:1, minHeight:'400px', padding:'16px', background:'transparent', border:'none', color:'#fff', fontSize:'13px', lineHeight:'1.6', resize:'none', fontFamily:'monospace', outline:'none' }} />
 </div>
 </div>

 {/* Score against JD */}
 <div className="glass-panel" style={{ padding:'20px' }}>
 <h3 style={{ color:'#fff', fontSize:'15px', fontWeight:700, marginBottom:'4px', display:'flex', alignItems:'center', gap:'8px' }}>
 Quick ATS Check — Score Against a Job
 </h3>
 <p style={{ color:'var(--text-muted)', fontSize:'13px', marginBottom:'14px' }}>Paste a job description below to instantly score your resume.</p>
 <div style={{ display:'flex', gap:'12px', alignItems:'flex-end' }}>
 <div style={{ flex:1 }}>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Job Description</label>
 <textarea value={resumeJobDescInput} onChange={e => setResumeJobDescInput(e.target.value)} rows={3}
 placeholder="Paste the job description here…"
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', resize:'vertical', boxSizing:'border-box' }} />
 </div>
 <button onClick={handleScoreResume} disabled={resumeScoreLoading}
 style={{ padding:'10px 20px', background:'linear-gradient(135deg,#10b981,#059669)', border:'none', borderRadius:'8px', color:'#fff', fontWeight:700, fontSize:'13px', cursor:'pointer', opacity:resumeScoreLoading?0.7:1, flexShrink:0, height:'48px' }}>
 {resumeScoreLoading ? '⏳' : ' Score'}
 </button>
 </div>
 {resumeScoreResult && (
 <div style={{ marginTop:'16px', display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(140px,1fr))', gap:'10px' }}>
 {[
 { label:'Overall Score', value: resumeScoreResult.overall_score, color: scoreColor(resumeScoreResult.overall_score) },
 { label:'ATS Friendly', value: resumeScoreResult.ats_score, color: scoreColor(resumeScoreResult.ats_score) },
 { label:'Keyword Match', value: resumeScoreResult.keyword_match_score, color: scoreColor(resumeScoreResult.keyword_match_score) },
 { label:'Experience Fit', value: resumeScoreResult.experience_match, color: scoreColor(resumeScoreResult.experience_match) },
 ].map(m => (
 <div key={m.label} style={{ textAlign:'center', background:'rgba(255,255,255,0.03)', borderRadius:'10px', padding:'12px', border:`1px solid ${m.color}30` }}>
 <div style={{ fontSize:'26px', fontWeight:900, color:m.color }}>{m.value}%</div>
 <div style={{ fontSize:'11px', color:'var(--text-muted)' }}>{m.label}</div>
 </div>
 ))}
 </div>
 )}
 </div>
 </div>
 )}

 {/* ATS SCORE (DETAILED) */}
 {resumeSubView === 'score' && (
 <div style={{ display:'flex', flexDirection:'column', gap:'24px', maxWidth:'800px' }}>
 <div>
 <h2 style={{ color:'#fff', fontSize:'20px', fontWeight:800, marginBottom:'6px' }}> Detailed Resume Scorer</h2>
 <p style={{ color:'var(--text-muted)', fontSize:'14px' }}>Deep analysis of your resume vs any job description. Get keyword gaps, strengths, and improvements.</p>
 </div>
 <div className="glass-panel" style={{ padding:'22px', display:'flex', flexDirection:'column', gap:'14px' }}>
 <div>
 <label style={{ fontSize:'13px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'6px' }}>Your Resume</label>
 <textarea value={resumeTextInput} onChange={e => setResumeTextInput(e.target.value)} rows={8}
 placeholder="Paste your resume text here…"
 style={{ width:'100%', padding:'10px 14px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.12)', borderRadius:'10px', color:'#fff', fontSize:'13px', resize:'vertical', boxSizing:'border-box', fontFamily:'monospace', lineHeight:'1.5' }} />
 </div>
 <div>
 <label style={{ fontSize:'13px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'6px' }}>Job Description</label>
 <textarea value={resumeJobDescInput} onChange={e => setResumeJobDescInput(e.target.value)} rows={5}
 placeholder="Paste the target job description…"
 style={{ width:'100%', padding:'10px 14px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.12)', borderRadius:'10px', color:'#fff', fontSize:'13px', resize:'vertical', boxSizing:'border-box' }} />
 </div>
 <button onClick={handleScoreResume} disabled={resumeScoreLoading}
 style={{ padding:'12px', background:'linear-gradient(135deg,#10b981,#059669)', border:'none', borderRadius:'10px', color:'#fff', fontWeight:700, fontSize:'14px', cursor:'pointer', opacity:resumeScoreLoading?0.7:1, display:'flex', alignItems:'center', justifyContent:'center', gap:'8px' }}>
 {resumeScoreLoading ? <><span className="pulse-glow">⏳</span> Analyzing…</> : ' Deep Analyze'}
 </button>
 </div>

 {resumeScoreResult && (
 <div style={{ display:'flex', flexDirection:'column', gap:'16px' }}>
 {/* Big score + verdict */}
 <div className="glass-panel" style={{ padding:'24px', textAlign:'center', background:`linear-gradient(135deg, ${scoreColor(resumeScoreResult.overall_score)}15, transparent)`, border:`1px solid ${scoreColor(resumeScoreResult.overall_score)}30` }}>
 <div style={{ fontSize:'64px', fontWeight:900, color:scoreColor(resumeScoreResult.overall_score), lineHeight:1 }}>{resumeScoreResult.overall_score}%</div>
 <div style={{ marginTop:'8px', display:'inline-block', padding:'4px 14px', borderRadius:'20px', fontSize:'13px', fontWeight:700, background: `${verdictBg[resumeScoreResult.verdict]||'#6366f1'}20`, color: verdictBg[resumeScoreResult.verdict]||'#6366f1', border:`1px solid ${verdictBg[resumeScoreResult.verdict]||'#6366f1'}40` }}>
 {resumeScoreResult.verdict}
 </div>
 <p style={{ color:'var(--text-muted)', fontSize:'14px', marginTop:'10px' }}>{resumeScoreResult.summary}</p>
 </div>
 {/* Sub-scores */}
 <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:'12px' }}>
 {[
 { label:'ATS', value:resumeScoreResult.ats_score },
 { label:'Keywords', value:resumeScoreResult.keyword_match_score },
 { label:'Experience', value:resumeScoreResult.experience_match },
 ].map(m=>(
 <div key={m.label} className="glass-panel" style={{ padding:'14px', textAlign:'center' }}>
 <div style={{ height:'4px', background:'rgba(255,255,255,0.08)', borderRadius:'2px', marginBottom:'10px', overflow:'hidden' }}>
 <div style={{ height:'100%', width:`${m.value}%`, background:`linear-gradient(90deg,${scoreColor(m.value)},#6366f1)`, borderRadius:'2px' }} />
 </div>
 <div style={{ fontSize:'22px', fontWeight:800, color:scoreColor(m.value) }}>{m.value}%</div>
 <div style={{ fontSize:'11px', color:'var(--text-muted)', textTransform:'uppercase' }}>{m.label}</div>
 </div>
 ))}
 </div>
 {/* Keywords */}
 <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'14px' }}>
 <div className="glass-panel" style={{ padding:'16px', border:'1px solid rgba(34,197,94,0.2)' }}>
 <h4 style={{ color:'#22c55e', fontSize:'13px', fontWeight:700, marginBottom:'10px' }}> Matching Keywords ({resumeScoreResult.matching_keywords?.length||0})</h4>
 <div style={{ display:'flex', flexWrap:'wrap', gap:'6px' }}>
 {resumeScoreResult.matching_keywords?.map((k:string)=><span key={k} style={{ padding:'3px 9px', background:'rgba(34,197,94,0.1)', border:'1px solid rgba(34,197,94,0.25)', borderRadius:'20px', fontSize:'12px', color:'#22c55e', fontWeight:600 }}>{k}</span>)}
 </div>
 </div>
 <div className="glass-panel" style={{ padding:'16px', border:'1px solid rgba(239,68,68,0.2)' }}>
 <h4 style={{ color:'#ef4444', fontSize:'13px', fontWeight:700, marginBottom:'10px' }}> Missing Keywords ({resumeScoreResult.missing_keywords?.length||0})</h4>
 <div style={{ display:'flex', flexWrap:'wrap', gap:'6px' }}>
 {resumeScoreResult.missing_keywords?.map((k:string)=><span key={k} style={{ padding:'3px 9px', background:'rgba(239,68,68,0.1)', border:'1px solid rgba(239,68,68,0.25)', borderRadius:'20px', fontSize:'12px', color:'#ef4444', fontWeight:600 }}>{k}</span>)}
 </div>
 </div>
 </div>
 {/* Strengths + Improvements */}
 <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'14px' }}>
 <div className="glass-panel" style={{ padding:'16px' }}>
 <h4 style={{ color:'#22c55e', fontSize:'13px', fontWeight:700, marginBottom:'10px' }}> Strengths</h4>
 {resumeScoreResult.strengths?.map((s:string,i:number)=><div key={i} style={{ display:'flex', gap:'8px', marginBottom:'6px', fontSize:'12px', color:'var(--text-muted)' }}><span style={{ color:'#22c55e' }}>→</span>{s}</div>)}
 </div>
 <div className="glass-panel" style={{ padding:'16px' }}>
 <h4 style={{ color:'#f59e0b', fontSize:'13px', fontWeight:700, marginBottom:'10px' }}> Improvements</h4>
 {resumeScoreResult.improvements?.map((s:string,i:number)=><div key={i} style={{ display:'flex', gap:'8px', marginBottom:'6px', fontSize:'12px', color:'var(--text-muted)' }}><span style={{ color:'#f59e0b' }}>→</span>{s}</div>)}
 </div>
 </div>
 </div>
 )}
 </div>
 )}

 {/* SALARY INTELLIGENCE */}
 {resumeSubView === 'salary' && (
 <div style={{ display:'flex', flexDirection:'column', gap:'24px', maxWidth:'800px' }}>
 <div>
 <h2 style={{ color:'#fff', fontSize:'20px', fontWeight:800, marginBottom:'6px' }}> Salary Intelligence</h2>
 <p style={{ color:'var(--text-muted)', fontSize:'14px' }}>AI-powered market salary data. Know your worth before you negotiate.</p>
 </div>
 <div className="glass-panel" style={{ padding:'22px', display:'flex', gap:'12px', flexWrap:'wrap', alignItems:'flex-end' }}>
 <div style={{ flex:'1 1 200px' }}>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Job Title</label>
 <input value={salaryJobTitle} onChange={e=>setSalaryJobTitle(e.target.value)}
 placeholder="e.g. Senior Software Engineer"
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }} />
 </div>
 <div style={{ flex:'1 1 150px' }}>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Location</label>
 <input value={salaryLocation} onChange={e=>setSalaryLocation(e.target.value)}
 placeholder="Remote / NYC / London"
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }} />
 </div>
 <div style={{ flex:'0 1 120px' }}>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Experience (yrs)</label>
 <input type="number" min={0} max={30} value={salaryExpYears} onChange={e=>setSalaryExpYears(Number(e.target.value))}
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }} />
 </div>
 <button onClick={handleSalaryLookup} disabled={salaryLoading}
 style={{ padding:'10px 22px', background:'linear-gradient(135deg,#10b981,#059669)', border:'none', borderRadius:'8px', color:'#fff', fontWeight:700, fontSize:'13px', cursor:'pointer', opacity:salaryLoading?0.7:1, flexShrink:0, height:'40px' }}>
 {salaryLoading ? '⏳' : ' Look Up'}
 </button>
 </div>

 {salaryResult && (
 <div style={{ display:'flex', flexDirection:'column', gap:'16px' }}>
 {/* Hero */}
 <div className="glass-panel" style={{ padding:'24px', background:'linear-gradient(135deg,rgba(16,185,129,0.08),rgba(5,150,105,0.04))', border:'1px solid rgba(16,185,129,0.2)' }}>
 <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', flexWrap:'wrap', gap:'16px' }}>
 <div>
 <div style={{ fontSize:'13px', color:'#10b981', fontWeight:700, marginBottom:'4px', textTransform:'uppercase', letterSpacing:'0.5px' }}>{salaryResult.experience_band} · {salaryResult.location}</div>
 <h2 style={{ fontSize:'22px', fontWeight:800, color:'#fff', margin:'0 0 4px' }}>{salaryResult.role}</h2>
 <div style={{ display:'flex', alignItems:'center', gap:'8px' }}>
 <span style={{ fontSize:'32px', fontWeight:900, color:'#10b981' }}>${(salaryResult.salary_range?.median||0).toLocaleString()}</span>
 <span style={{ color:'var(--text-muted)', fontSize:'14px' }}>median / year</span>
 </div>
 </div>
 <div style={{ textAlign:'center' }}>
 <div style={{ fontSize:'13px', color:'var(--text-muted)', marginBottom:'4px' }}>Market Trend</div>
 <div style={{ fontSize:'18px', fontWeight:800, color: salaryResult.market_trend==='rising'?'#22c55e':salaryResult.market_trend==='declining'?'#ef4444':'#f59e0b' }}>
 {salaryResult.market_trend==='rising'?'↑':salaryResult.market_trend==='declining'?'↓':'→'} {salaryResult.trend_pct > 0 ? '+' : ''}{salaryResult.trend_pct}% YoY
 </div>
 <div style={{ fontSize:'12px', color:'var(--text-muted)' }}>Demand: {salaryResult.demand_score}/100</div>
 </div>
 </div>
 </div>
 {/* Salary bands */}
 <div className="glass-panel" style={{ padding:'20px' }}>
 <h4 style={{ color:'#fff', fontSize:'14px', fontWeight:700, marginBottom:'16px' }}>Salary Range</h4>
 {[
 { label:'25th Percentile', value: salaryResult.salary_range?.p25, pct:25 },
 { label:'Median (50th)', value: salaryResult.salary_range?.median, pct:50 },
 { label:'75th Percentile', value: salaryResult.salary_range?.p75, pct:75 },
 { label:'Top Earners (90th)', value: salaryResult.salary_range?.p90, pct:90 },
 ].map(band=>(
 <div key={band.label} style={{ marginBottom:'12px' }}>
 <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'4px' }}>
 <span style={{ fontSize:'12px', color:'var(--text-muted)' }}>{band.label}</span>
 <span style={{ fontSize:'13px', color:'#fff', fontWeight:700 }}>${(band.value||0).toLocaleString()}</span>
 </div>
 <div style={{ height:'6px', background:'rgba(255,255,255,0.08)', borderRadius:'3px', overflow:'hidden' }}>
 <div style={{ height:'100%', width:`${band.pct}%`, background:'linear-gradient(90deg,#10b981,#059669)', borderRadius:'3px' }} />
 </div>
 </div>
 ))}
 </div>
 {/* Total comp + skills premium */}
 <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'14px' }}>
 <div className="glass-panel" style={{ padding:'18px' }}>
 <h4 style={{ color:'#fff', fontSize:'13px', fontWeight:700, marginBottom:'12px' }}> Total Compensation</h4>
 {[
 { label:'Base Salary', value:`$${(salaryResult.total_compensation?.base||0).toLocaleString()}` },
 { label:'Annual Bonus', value:`+${salaryResult.total_compensation?.bonus_pct||0}%` },
 { label:'Equity (est.)', value:`$${(salaryResult.total_compensation?.equity_usd||0).toLocaleString()}/yr` },
 ].map(r=>(
 <div key={r.label} style={{ display:'flex', justifyContent:'space-between', marginBottom:'8px' }}>
 <span style={{ fontSize:'12px', color:'var(--text-muted)' }}>{r.label}</span>
 <span style={{ fontSize:'12px', color:'#10b981', fontWeight:700 }}>{r.value}</span>
 </div>
 ))}
 </div>
 <div className="glass-panel" style={{ padding:'18px' }}>
 <h4 style={{ color:'#fff', fontSize:'13px', fontWeight:700, marginBottom:'12px' }}> High-Value Skills</h4>
 {salaryResult.hot_skills_premium?.map((s:any)=>(
 <div key={s.skill} style={{ display:'flex', justifyContent:'space-between', marginBottom:'8px' }}>
 <span style={{ fontSize:'12px', color:'var(--text-muted)' }}>{s.skill}</span>
 <span style={{ fontSize:'12px', color:'#f59e0b', fontWeight:700 }}>+{s.premium_pct}% premium</span>
 </div>
 ))}
 </div>
 </div>
 {/* Top companies */}
 <div className="glass-panel" style={{ padding:'16px' }}>
 <h4 style={{ color:'#fff', fontSize:'13px', fontWeight:700, marginBottom:'10px' }}> Top Paying Companies</h4>
 <div style={{ display:'flex', gap:'8px', flexWrap:'wrap' }}>
 {salaryResult.top_paying_companies?.map((c:string,i:number)=>(
 <span key={c} style={{ padding:'5px 12px', background:`rgba(16,185,129,${0.15-i*0.02})`, border:'1px solid rgba(16,185,129,0.25)', borderRadius:'20px', fontSize:'12px', color:'#10b981', fontWeight:700 }}>
 {i===0?'':i===1?'':i===2?'':''} {c}
 </span>
 ))}
 </div>
 {salaryResult.insight && <p style={{ fontSize:'13px', color:'var(--text-muted)', marginTop:'12px', lineHeight:'1.5', fontStyle:'italic' }}>"{salaryResult.insight}"</p>}
 </div>
 </div>
 )}
 </div>
 )}

 {/* CAREER ANALYTICS */}
 {resumeSubView === 'analytics' && (
 <div style={{ display:'flex', flexDirection:'column', gap:'24px' }}>
 <div>
 <h2 style={{ color:'#fff', fontSize:'20px', fontWeight:800, marginBottom:'6px' }}> Career Analytics</h2>
 <p style={{ color:'var(--text-muted)', fontSize:'14px' }}>Track your job search performance and profile strength.</p>
 </div>
 {/* Application funnel */}
 {careerAnalytics && (
 <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(160px,1fr))', gap:'14px' }}>
 {[
 { label:'Applications', value:careerAnalytics.total_applications, icon:'', color:'#6366f1' },
 { label:'Response Rate', value:`${careerAnalytics.response_rate}%`, icon:'', color:'#10b981' },
 { label:'Interview Rate', value:`${careerAnalytics.interview_rate}%`, icon:'', color:'#f59e0b' },
 { label:'Offer Rate', value:`${careerAnalytics.offer_rate}%`, icon:'', color:'#22c55e' },
 { label:'Interview→Offer', value:`${careerAnalytics.interview_to_offer}%`, icon:'', color:'#8b5cf6' },
 { label:'Profile Score', value:profileScore ? `${profileScore.total_score}pts` : '—', icon:'', color:'#f59e0b' },
 ].map(s=>(
 <div key={s.label} className="glass-panel" style={{ padding:'16px', textAlign:'center', border:`1px solid ${s.color}25` }}>
 <div style={{ fontSize:'22px', marginBottom:'4px' }}>{s.icon}</div>
 <div style={{ fontSize:'22px', fontWeight:800, color:s.color }}>{s.value}</div>
 <div style={{ fontSize:'11px', color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'0.5px' }}>{s.label}</div>
 </div>
 ))}
 </div>
 )}
 {/* Profile completeness */}
 {profileScore && (
 <div className="glass-panel" style={{ padding:'20px' }}>
 <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'16px' }}>
 <h3 style={{ color:'#fff', fontSize:'15px', fontWeight:700 }}> Profile Strength</h3>
 <span style={{ padding:'4px 12px', borderRadius:'20px', fontSize:'12px', fontWeight:700, background:'rgba(16,185,129,0.15)', color:'#10b981', border:'1px solid rgba(16,185,129,0.3)' }}>{profileScore.rank}</span>
 </div>
 <div style={{ height:'8px', background:'rgba(255,255,255,0.08)', borderRadius:'4px', marginBottom:'16px', overflow:'hidden' }}>
 <div style={{ height:'100%', width:`${profileScore.total_score}%`, background:'linear-gradient(90deg,#10b981,#059669)', borderRadius:'4px', transition:'width 0.5s' }} />
 </div>
 <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(220px,1fr))', gap:'8px' }}>
 {profileScore.sections?.map((s:any)=>(
 <div key={s.name} style={{ display:'flex', alignItems:'center', gap:'10px', padding:'8px 12px', borderRadius:'8px', background:'rgba(255,255,255,0.03)' }}>
 <div style={{ width:'20px', height:'20px', borderRadius:'50%', background: s.done?'rgba(34,197,94,0.2)':'rgba(239,68,68,0.15)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'11px', flexShrink:0 }}>
 {s.done ? '' : ''}
 </div>
 <span style={{ flex:1, fontSize:'12px', color: s.done?'#fff':'var(--text-muted)' }}>{s.name}</span>
 <span style={{ fontSize:'11px', color: s.done?'#22c55e':'var(--text-muted)', fontWeight:700 }}>+{s.points}pts</span>
 </div>
 ))}
 </div>
 {profileScore.next_action && (
 <div style={{ marginTop:'14px', padding:'12px 16px', background:'rgba(99,102,241,0.08)', borderRadius:'10px', border:'1px solid rgba(99,102,241,0.2)', fontSize:'13px', color:'#a5b4fc' }}>
 <strong>Next:</strong> {profileScore.next_action}
 </div>
 )}
 </div>
 )}
 {/* Recommended actions */}
 {careerAnalytics?.recommended_actions?.length > 0 && (
 <div>
 <h3 style={{ color:'#fff', fontSize:'15px', fontWeight:700, marginBottom:'12px' }}> Recommended Actions</h3>
 <div style={{ display:'flex', flexDirection:'column', gap:'10px' }}>
 {careerAnalytics.recommended_actions.map((a:any,i:number)=>(
 <div key={i} className="glass-panel" style={{ padding:'14px 16px', display:'flex', alignItems:'center', gap:'14px' }}>
 <span style={{ fontSize:'22px', flexShrink:0 }}>{a.icon}</span>
 <div style={{ flex:1 }}>
 <div style={{ fontSize:'14px', color:'#fff', fontWeight:600 }}>{a.action}</div>
 </div>
 <span style={{ padding:'3px 10px', borderRadius:'20px', fontSize:'11px', fontWeight:700,
 background: a.impact==='high'?'rgba(239,68,68,0.15)':'rgba(245,158,11,0.15)',
 color: a.impact==='high'?'#ef4444':'#f59e0b',
 border:`1px solid ${a.impact==='high'?'rgba(239,68,68,0.25)':'rgba(245,158,11,0.25)'}` }}>
 {a.impact} impact
 </span>
 </div>
 ))}
 </div>
 </div>
 )}
 </div>
 )}

 {/* GAMIFICATION / ACHIEVEMENTS */}
 {resumeSubView === 'gamification' && (
 <div style={{ display:'flex', flexDirection:'column', gap:'24px' }}>
 <div>
 <h2 style={{ color:'#fff', fontSize:'20px', fontWeight:800, marginBottom:'6px' }}> Achievements & Leaderboard</h2>
 <p style={{ color:'var(--text-muted)', fontSize:'14px' }}>Earn XP, unlock badges, climb the leaderboard.</p>
 </div>
 {/* XP Card */}
 {gamificationStats && (
 <div className="glass-panel" style={{ padding:'24px', background:'linear-gradient(135deg,rgba(245,158,11,0.08),rgba(234,179,8,0.04))', border:'1px solid rgba(245,158,11,0.2)' }}>
 <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:'16px', marginBottom:'16px' }}>
 <div>
 <div style={{ fontSize:'12px', color:'#f59e0b', fontWeight:700, textTransform:'uppercase', letterSpacing:'0.5px', marginBottom:'4px' }}>Your Rank</div>
 <div style={{ fontSize:'24px', fontWeight:800, color:'#fff' }}>{gamificationStats.rank_title}</div>
 </div>
 <div style={{ textAlign:'center' }}>
 <div style={{ fontSize:'48px', fontWeight:900, color:'#f59e0b', lineHeight:1 }}>Lv.{gamificationStats.level}</div>
 <div style={{ fontSize:'12px', color:'var(--text-muted)', marginTop:'4px' }}>{gamificationStats.xp.toLocaleString()} XP total</div>
 </div>
 </div>
 <div>
 <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'6px' }}>
 <span style={{ fontSize:'12px', color:'var(--text-muted)' }}>Progress to Level {gamificationStats.level+1}</span>
 <span style={{ fontSize:'12px', color:'#f59e0b', fontWeight:700 }}>{gamificationStats.xp_to_next_level} XP to go</span>
 </div>
 <div style={{ height:'10px', background:'rgba(255,255,255,0.08)', borderRadius:'5px', overflow:'hidden' }}>
 <div style={{ height:'100%', width:`${gamificationStats.xp_progress_pct}%`, background:'linear-gradient(90deg,#f59e0b,#f97316)', borderRadius:'5px', transition:'width 0.5s' }} />
 </div>
 </div>
 {/* XP breakdown */}
 <div style={{ display:'flex', gap:'16px', marginTop:'16px' }}>
 <div style={{ textAlign:'center', flex:1, background:'rgba(255,255,255,0.04)', borderRadius:'10px', padding:'10px' }}>
 <div style={{ fontSize:'20px', fontWeight:800, color:'#6366f1' }}>{gamificationStats.total_courses}</div>
 <div style={{ fontSize:'11px', color:'var(--text-muted)' }}>Courses</div>
 </div>
 <div style={{ textAlign:'center', flex:1, background:'rgba(255,255,255,0.04)', borderRadius:'10px', padding:'10px' }}>
 <div style={{ fontSize:'20px', fontWeight:800, color:'#22c55e' }}>{gamificationStats.total_certificates}</div>
 <div style={{ fontSize:'11px', color:'var(--text-muted)' }}>Certificates</div>
 </div>
 <div style={{ textAlign:'center', flex:1, background:'rgba(255,255,255,0.04)', borderRadius:'10px', padding:'10px' }}>
 <div style={{ fontSize:'20px', fontWeight:800, color:'#f59e0b' }}>{gamificationStats.streak_days}</div>
 <div style={{ fontSize:'11px', color:'var(--text-muted)' }}>Day Streak </div>
 </div>
 </div>
 </div>
 )}
 {/* Badges */}
 {gamificationStats?.badges?.length > 0 && (
 <div>
 <h3 style={{ color:'#fff', fontSize:'15px', fontWeight:700, marginBottom:'12px' }}> Your Badges</h3>
 <div style={{ display:'flex', gap:'12px', flexWrap:'wrap' }}>
 {gamificationStats.badges.map((b:any)=>(
 <div key={b.id} className="glass-panel" style={{ padding:'16px 20px', textAlign:'center', minWidth:'110px', border:'1px solid rgba(245,158,11,0.2)' }}>
 <div style={{ fontSize:'32px', marginBottom:'6px' }}>{b.emoji}</div>
 <div style={{ fontSize:'12px', fontWeight:700, color:'#fff', marginBottom:'2px' }}>{b.name}</div>
 <div style={{ fontSize:'10px', color:'var(--text-muted)' }}>{b.desc}</div>
 </div>
 ))}
 {/* Locked preview badges */}
 {[
 { emoji:'', name:'Global Top 100', desc:'Reach global leaderboard' },
 { emoji:'', name:'7-Day Streak', desc:'Learn 7 days in a row' },
 { emoji:'', name:'Legend', desc:'Reach Level 7' },
 ].filter(()=>gamificationStats.badges.length < 6).map(b=>(
 <div key={b.name} className="glass-panel" style={{ padding:'16px 20px', textAlign:'center', minWidth:'110px', opacity:0.4, filter:'grayscale(1)', position:'relative' }}>
 <div style={{ fontSize:'32px', marginBottom:'6px' }}>{b.emoji}</div>
 <div style={{ fontSize:'12px', fontWeight:700, color:'#fff', marginBottom:'2px' }}>{b.name}</div>
 <div style={{ fontSize:'10px', color:'var(--text-muted)' }}>{b.desc}</div>
 <div style={{ position:'absolute', top:'6px', right:'6px', fontSize:'10px' }}></div>
 </div>
 ))}
 </div>
 </div>
 )}
 {/* Leaderboard */}
 <div>
 <h3 style={{ color:'#fff', fontSize:'15px', fontWeight:700, marginBottom:'12px' }}> Global Leaderboard</h3>
 {leaderboard.length === 0 ? (
 <div className="glass-panel" style={{ padding:'32px', textAlign:'center', color:'var(--text-muted)' }}>
 <Trophy size={32} style={{ opacity:0.3, marginBottom:'8px' }} />
 <p>Start learning to appear on the leaderboard!</p>
 <button onClick={()=>setActiveTab('academy')} style={{ marginTop:'12px', padding:'8px 20px', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', border:'none', borderRadius:'8px', color:'#fff', fontWeight:600, cursor:'pointer', fontSize:'13px' }}>
 Go to Academy
 </button>
 </div>
 ) : (
 <div style={{ display:'flex', flexDirection:'column', gap:'8px' }}>
 {leaderboard.map((u:any)=>(
 <div key={u.user_id} className="glass-panel" style={{ padding:'12px 16px', display:'flex', alignItems:'center', gap:'14px', background: u.is_current_user?'rgba(245,158,11,0.08)':undefined, border: u.is_current_user?'1px solid rgba(245,158,11,0.25)':undefined }}>
 <div style={{ width:'30px', textAlign:'center', fontSize:'16px', fontWeight:800, color: u.rank===1?'#f59e0b':u.rank===2?'#9ca3af':u.rank===3?'#d97706':'var(--text-muted)', flexShrink:0 }}>
 {u.rank===1?'':u.rank===2?'':u.rank===3?'':u.rank}
 </div>
 <div style={{ flex:1 }}>
 <div style={{ fontSize:'14px', fontWeight:700, color:'#fff' }}>{u.name}{u.is_current_user && <span style={{ marginLeft:'6px', fontSize:'11px', color:'#f59e0b' }}>← You</span>}</div>
 <div style={{ fontSize:'12px', color:'var(--text-muted)' }}>Level {u.level} · {u.certificates} certificates</div>
 </div>
 <div style={{ textAlign:'right' }}>
 <div style={{ fontSize:'16px', fontWeight:800, color:'#f59e0b' }}>{u.xp.toLocaleString()}</div>
 <div style={{ fontSize:'11px', color:'var(--text-muted)' }}>XP</div>
 </div>
 </div>
 ))}
 </div>
 )}
 </div>
 </div>
 )}

 {/* PROJECT SHOWCASE */}
 {resumeSubView === 'showcase' && (
 <div style={{ display:'flex', flexDirection:'column', gap:'24px' }}>
 <div>
 <h2 style={{ color:'#fff', fontSize:'20px', fontWeight:800, marginBottom:'6px' }}> Project Showcase</h2>
 <p style={{ color:'var(--text-muted)', fontSize:'14px' }}>Share what you've built. Let recruiters discover your work. Get upvotes from the community.</p>
 </div>
 {/* Submit form */}
 <div className="glass-panel" style={{ padding:'22px' }}>
 <h3 style={{ color:'#fff', fontSize:'15px', fontWeight:700, marginBottom:'16px', display:'flex', alignItems:'center', gap:'8px' }}>
 <Plus size={16} color="#10b981" /> Submit a Project
 </h3>
 <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'12px' }}>
 <div style={{ gridColumn:'1/-1' }}>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Project Title</label>
 <input value={showcaseForm.title} onChange={e=>setShowcaseForm(p=>({...p,title:e.target.value}))}
 placeholder="e.g. AI-Powered Job Matcher"
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }} />
 </div>
 <div style={{ gridColumn:'1/-1' }}>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Description</label>
 <textarea value={showcaseForm.description} onChange={e=>setShowcaseForm(p=>({...p,description:e.target.value}))} rows={2}
 placeholder="What does it do? What problem does it solve?"
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', resize:'vertical', boxSizing:'border-box' }} />
 </div>
 <div>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>GitHub URL</label>
 <input value={showcaseForm.github_url} onChange={e=>setShowcaseForm(p=>({...p,github_url:e.target.value}))}
 placeholder="https://github.com/user/repo"
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }} />
 </div>
 <div>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Live Demo URL</label>
 <input value={showcaseForm.demo_url} onChange={e=>setShowcaseForm(p=>({...p,demo_url:e.target.value}))}
 placeholder="https://your-demo.com"
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }} />
 </div>
 <div>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Tech Stack (comma-separated)</label>
 <input value={showcaseForm.tech_stack} onChange={e=>setShowcaseForm(p=>({...p,tech_stack:e.target.value}))}
 placeholder="React, FastAPI, PostgreSQL, Docker"
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }} />
 </div>
 <div>
 <label style={{ fontSize:'12px', color:'var(--text-muted)', fontWeight:600, display:'block', marginBottom:'5px' }}>Category</label>
 <select value={showcaseForm.category} onChange={e=>setShowcaseForm(p=>({...p,category:e.target.value}))}
 style={{ width:'100%', padding:'9px 13px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'8px', color:'#fff', fontSize:'13px', boxSizing:'border-box' }}>
 {['Web Development','Mobile','AI/ML','DevOps','Data Science','Cybersecurity','Blockchain','Hardware'].map(c=><option key={c} value={c}>{c}</option>)}
 </select>
 </div>
 </div>
 <button onClick={handleSubmitShowcase} disabled={showcaseSubmitting}
 style={{ marginTop:'14px', padding:'10px 24px', background:'linear-gradient(135deg,#10b981,#059669)', border:'none', borderRadius:'8px', color:'#fff', fontWeight:700, fontSize:'13px', cursor:'pointer', opacity:showcaseSubmitting?0.7:1 }}>
 {showcaseSubmitting ? '⏳ Submitting…' : ' Submit Project'}
 </button>
 </div>
 {/* Projects grid */}
 {showcaseProjects.length === 0 ? (
 <div style={{ textAlign:'center', padding:'48px', color:'var(--text-muted)' }}>
 <ExternalLink size={40} style={{ opacity:0.3, marginBottom:'12px' }} />
 <p style={{ fontSize:'16px', color:'rgba(255,255,255,0.5)', marginBottom:'8px' }}>No projects showcased yet</p>
 <p>Be the first to share your work with the ATLAS community!</p>
 </div>
 ) : (
 <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(300px,1fr))', gap:'16px' }}>
 {showcaseProjects.map((p:any,i:number)=>(
 <div key={i} className="glass-panel" style={{ padding:'18px', transition:'transform 0.2s' }}
 onMouseEnter={e=>(e.currentTarget as HTMLElement).style.transform='translateY(-3px)'}
 onMouseLeave={e=>(e.currentTarget as HTMLElement).style.transform=''}>
 <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:'8px' }}>
 <span style={{ fontSize:'11px', color:'#10b981', fontWeight:700, textTransform:'uppercase', background:'rgba(16,185,129,0.1)', padding:'2px 8px', borderRadius:'20px' }}>{p.category}</span>
 <div style={{ display:'flex', gap:'6px' }}>
 {p.github_url && <a href={p.github_url} target="_blank" rel="noopener noreferrer" style={{ color:'var(--text-muted)' }}><Github size={14} /></a>}
 {p.demo_url && <a href={p.demo_url} target="_blank" rel="noopener noreferrer" style={{ color:'var(--text-muted)' }}><ExternalLink size={14} /></a>}
 </div>
 </div>
 <h3 style={{ fontSize:'15px', fontWeight:700, color:'#fff', marginBottom:'6px' }}>{p.title}</h3>
 <p style={{ fontSize:'12px', color:'var(--text-muted)', lineHeight:'1.5', marginBottom:'10px' }}>{p.description}</p>
 {p.extracted_skills?.length > 0 && (
 <div style={{ display:'flex', gap:'6px', flexWrap:'wrap' }}>
 {p.extracted_skills.slice(0,5).map((s:string)=>(
 <span key={s} style={{ padding:'2px 8px', background:'rgba(16,185,129,0.1)', border:'1px solid rgba(16,185,129,0.2)', borderRadius:'10px', fontSize:'11px', color:'#10b981', fontWeight:600 }}>{s}</span>
 ))}
 </div>
 )}
 <div style={{ marginTop:'10px', fontSize:'12px', color:'var(--text-muted)' }}>by {p.author}</div>
 </div>
 ))}
 </div>
 )}
 </div>
 )}

 </div>
 </div>
 );
 })()}

 {/* TAB: BI ANALYTICS DASHBOARD */}
 {activeTab === 'analytics' && (

 <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
 <h2 style={{ fontSize: '22px', color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
 <TrendingUp style={{ color: 'var(--accent-cyan)' }} />
 <span>Workspace BI Analytics</span>
 </h2>
 <p style={{ color: 'var(--text-muted)', fontSize: '14px', marginTop: '-12px', marginBottom: '12px' }}>
 Real-time recruitment performance metrics, funnel conversion analytics, and time-to-hire distributions.
 </p>

 {/* Metric Cards Grid */}
 <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '20px' }}>
 <div className="glass-panel" style={{ padding: '20px', background: 'rgba(255,255,255,0.01)' }}>
 <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 'bold', textTransform: 'uppercase' }}>Active Talent Pool</span>
 <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#fff', marginTop: '6px' }}>
 {analyticsThroughput ? (Object.values(analyticsThroughput).reduce((a: number, b: unknown) => a + (Number(b) || 0), 0) as number) : 0}
 </div>
 <div style={{ fontSize: '11px', color: '#10b981', marginTop: '4px' }}>↑ Live tracked candidate profiles</div>
 </div>

 <div className="glass-panel" style={{ padding: '20px', background: 'rgba(255,255,255,0.01)' }}>
 <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 'bold', textTransform: 'uppercase' }}>Avg Time to Hire</span>
 <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#fff', marginTop: '6px' }}>
 {analyticsTimeToHire?.average_time_to_hire_days || 15.2} <span style={{ fontSize: '14px', fontWeight: 'normal', color: 'var(--text-muted)' }}>days</span>
 </div>
 <div style={{ fontSize: '11px', color: 'var(--accent-cyan)', marginTop: '4px' }}>Avg duration from apply to offer</div>
 </div>

 <div className="glass-panel" style={{ padding: '20px', background: 'rgba(255,255,255,0.01)' }}>
 <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 'bold', textTransform: 'uppercase' }}>Active Job Openings</span>
 <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#fff', marginTop: '6px' }}>
 {jobs.filter(j => j.is_active).length}
 </div>
 <div style={{ fontSize: '11px', color: '#a0a0a0', marginTop: '4px' }}>Currently published job listings</div>
 </div>

 <div className="glass-panel" style={{ padding: '20px', background: 'rgba(255,255,255,0.01)' }}>
 <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 'bold', textTransform: 'uppercase' }}>Pipeline Velocity</span>
 <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#fff', marginTop: '6px' }}>
 94.8%
 </div>
 <div style={{ fontSize: '11px', color: '#10b981', marginTop: '4px' }}> SLA target completion rate</div>
 </div>
 </div>

 {/* Graphs Grid */}
 <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '24px', alignItems: 'start' }}>
 {/* Funnel Chart */}
 {(() => {
 const applied = analyticsThroughput?.applied || 0;
 const screening = analyticsThroughput?.screening || 0;
 const interviewing = analyticsThroughput?.interviewing || 0;
 const offered = analyticsThroughput?.offered || 0;
 
 const stages = [
 { label: 'Applied', count: applied, color: 'var(--accent-cyan)' },
 { label: 'Screening', count: screening, color: 'var(--accent-gold)' },
 { label: 'Interviewing', count: interviewing, color: '#a0a0a0' },
 { label: 'Offered', count: offered, color: '#10b981' }
 ];

 const maxCount = Math.max(...stages.map(s => s.count), 1);

 return (
 <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.01)' }}>
 <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '20px', fontWeight: 600 }}>Candidate Recruitment Funnel</h3>
 <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
 {stages.map((st, idx) => {
 const widthPercent = (st.count / maxCount) * 100;
 const convRate = idx === 0 ? 100 : stages[idx - 1].count > 0 ? Math.round((st.count / stages[idx - 1].count) * 100) : 0;
 return (
 <div key={st.label}>
 <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
 <span style={{ color: '#fff', fontWeight: 500 }}>{st.label}</span>
 <span style={{ color: 'var(--text-muted)' }}>
 <strong>{st.count}</strong> candidates {idx > 0 && `(${convRate}% step conversion)`}
 </span>
 </div>
 <div style={{ height: '24px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', overflow: 'hidden', display: 'flex', alignItems: 'center', padding: '0 4px', border: '1px solid var(--border-glass)' }}>
 <div 
 style={{ 
 width: `${Math.max(5, widthPercent)}%`, 
 height: '16px', 
 background: `linear-gradient(90deg, ${st.color}88, ${st.color})`, 
 borderRadius: '8px',
 transition: 'width 1s ease-in-out'
 }} 
 />
 </div>
 </div>
 );
 })}
 </div>
 </div>
 );
 })()}

 {/* Time to Hire stage chart */}
 {(() => {
 const steps = [
 { label: 'Screening', days: analyticsTimeToHire?.by_stage?.screening || 3.2, color: 'var(--accent-cyan)' },
 { label: 'Tech Code', days: analyticsTimeToHire?.by_stage?.tech_code || 5.4, color: 'var(--accent-gold)' },
 { label: 'Mgr Interview', days: analyticsTimeToHire?.by_stage?.mgr_interview || 4.1, color: '#a0a0a0' },
 { label: 'Offer Prep', days: analyticsTimeToHire?.by_stage?.offer_prep || 2.5, color: '#10b981' }
 ];

 const maxDays = Math.max(...steps.map(s => s.days), 1);
 const chartHeight = 180;
 
 return (
 <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.01)' }}>
 <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '20px', fontWeight: 600 }}>Average Days Spent by Stage</h3>
 <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'flex-end', height: `${chartHeight}px`, borderBottom: '1px solid var(--border-glass)', paddingBottom: '10px' }}>
 {steps.map(st => {
 const barHeight = (st.days / maxDays) * (chartHeight - 40);
 return (
 <div key={st.label} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '60px' }}>
 <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px' }}>{st.days}d</span>
 <div 
 style={{ 
 width: '32px', 
 height: `${Math.max(10, barHeight)}px`, 
 background: `linear-gradient(0deg, ${st.color}88, ${st.color})`, 
 borderRadius: '6px 6px 0 0',
 transition: 'height 1s ease-in-out'
 }} 
 />
 <span style={{ fontSize: '10px', color: '#fff', marginTop: '8px', textAlign: 'center', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden', width: '100%' }} title={st.label}>
 {st.label}
 </span>
 </div>
 );
 })}
 </div>
 </div>
 );
 })()}
 </div>
 </div>
 )}

 {/* TAB 9: COMMUNITY DISCUSSION BOARD & WHISTLEBLOWER NEWS */}
 {activeTab === 'community' && (
 <div className="animate-fade-in" style={{ display: 'flex', height: 'calc(100vh - 140px)', gap: 0, borderRadius: '20px', overflow: 'hidden', boxShadow: '0 20px 60px rgba(0,0,0,0.40)', border: '1px solid rgba(255,255,255,0.14)' }}>

 {/* CHANNELS SIDEBAR */}
 <div style={{ width: '240px', flexShrink: 0, background: 'rgba(255,255,255,0.06)', backdropFilter: 'blur(40px)', borderRight: '1px solid rgba(255,255,255,0.10)', display: 'flex', flexDirection: 'column' }}>
 {/* Server header */}
 <div style={{ padding: '16px', borderBottom: '1px solid rgba(255,255,255,0.10)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
 <div>
 <div style={{ fontSize: '14px', fontWeight: 700, color: '#fff', letterSpacing: '-0.01em' }}>ATLAS Community</div>
 <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.45)', marginTop: '2px' }}>Anonymous · Encrypted</div>
 </div>
 <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#a0a0a0', boxShadow: '0 0 6px #a0a0a0' }} title="Online" />
 </div>

 {/* View toggle */}
 <div style={{ display: 'flex', gap: '4px', padding: '10px 10px 6px' }}>
 <button onClick={() => setChatView('chat')} style={{ flex: 1, padding: '6px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontSize: '11px', fontWeight: 600, fontFamily: 'var(--font-body)', background: chatView === 'chat' ? 'rgba(255,255,255,0.18)' : 'transparent', color: chatView === 'chat' ? '#fff' : 'rgba(255,255,255,0.5)', transition: 'all 0.2s' }}> Chat</button>
 <button onClick={() => setChatView('board')} style={{ flex: 1, padding: '6px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontSize: '11px', fontWeight: 600, fontFamily: 'var(--font-body)', background: chatView === 'board' ? 'rgba(255,255,255,0.18)' : 'transparent', color: chatView === 'board' ? '#fff' : 'rgba(255,255,255,0.5)', transition: 'all 0.2s' }}> Board</button>
 </div>

 {chatView === 'chat' && (
 <>
 {/* Channels list */}
 <div style={{ flex: 1, overflowY: 'auto', padding: '4px 8px' }}>
 <div style={{ fontSize: '10px', fontWeight: 700, color: 'rgba(255,255,255,0.35)', letterSpacing: '0.08em', padding: '8px 6px 4px', textTransform: 'uppercase' }}>Channels</div>
 {chatChannels.map(ch => (
 <div key={ch.id} onClick={() => selectChannel(ch)}
 style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '7px 10px', borderRadius: '8px', cursor: 'pointer', marginBottom: '2px', transition: 'background 0.15s', background: activeChannel?.id === ch.id ? 'rgba(255,255,255,0.16)' : 'transparent', color: activeChannel?.id === ch.id ? '#fff' : 'rgba(255,255,255,0.60)' }}
 onMouseEnter={e => { if (activeChannel?.id !== ch.id) e.currentTarget.style.background = 'rgba(255,255,255,0.08)'; }}
 onMouseLeave={e => { if (activeChannel?.id !== ch.id) e.currentTarget.style.background = 'transparent'; }}>
 <span style={{ fontSize: '14px' }}></span>
 <span style={{ fontSize: '13px', fontWeight: activeChannel?.id === ch.id ? 600 : 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{ch.title}</span>
 </div>
 ))}
 </div>

 {/* Create channel button */}
 <div style={{ padding: '10px' }}>
 <button onClick={() => setShowCreateChannel(true)} className="btn-secondary" style={{ width: '100%', justifyContent: 'center', fontSize: '12px', padding: '8px', borderRadius: '10px' }}>+ New Channel</button>
 </div>
 </>
 )}
 </div>

 {/* MAIN AREA */}
 <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'rgba(255,255,255,0.04)', backdropFilter: 'blur(40px)' }}>

 {chatView === 'chat' ? (
 <>
 {/* Channel header */}
 <div style={{ padding: '14px 20px', borderBottom: '1px solid rgba(255,255,255,0.10)', display: 'flex', alignItems: 'center', gap: '10px', background: 'rgba(255,255,255,0.05)' }}>
 {activeChannel ? (
 <>
 <span style={{ fontSize: '18px' }}></span>
 <div>
 <div style={{ fontSize: '15px', fontWeight: 700, color: '#fff' }}>{activeChannel.title}</div>
 <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.45)' }}>{activeChannel.content} · All identities masked</div>
 </div>
 <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'rgba(255,255,255,0.45)' }}>
 <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#a0a0a0' }} />
 Live
 </div>
 </>
 ) : (
 <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.45)' }}>← Select a channel to start chatting</div>
 )}
 </div>

 {/* Messages area */}
 <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
 {!activeChannel ? (
 <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'rgba(255,255,255,0.30)', gap: '12px' }}>
 <div style={{ fontSize: '48px' }}></div>
 <div style={{ fontSize: '16px', fontWeight: 600, color: 'rgba(255,255,255,0.50)' }}>ATLAS Anonymous Chat</div>
 <div style={{ fontSize: '13px', textAlign: 'center', maxWidth: '260px', lineHeight: '1.6' }}>Pick a channel on the left to join the conversation. All messages are end-to-end anonymous.</div>
 </div>
 ) : chatRoomLoading ? (
 <div style={{ textAlign: 'center', color: 'rgba(255,255,255,0.40)', padding: '40px', fontSize: '13px' }}>Loading messages...</div>
 ) : chatMessages.length === 0 ? (
 <div style={{ textAlign: 'center', color: 'rgba(255,255,255,0.35)', padding: '40px 20px' }}>
 <div style={{ fontSize: '36px', marginBottom: '10px' }}></div>
 <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>No messages yet</div>
 <div style={{ fontSize: '12px' }}>Be the first to say something in {activeChannel.title}</div>
 </div>
 ) : (
 chatMessages.map((msg: any, i: number) => {
 const prevMsg = chatMessages[i - 1];
 const sameAuthor = prevMsg && prevMsg.is_anonymous === msg.is_anonymous && (!prevMsg.user || !msg.user || prevMsg.user?.email === msg.user?.email);
 const showHeader = !sameAuthor;
 const isAnon = msg.is_anonymous;
 const displayName = isAnon ? 'Anonymous' : (msg.user?.email?.split('@')[0] || 'User');
 const avatarColor = isAnon ? '#6e6e80' : `hsl(${(displayName.charCodeAt(0) * 47) % 360}, 50%, 45%)`;
 const avatarInitial = isAnon ? '?' : displayName[0].toUpperCase();
 const timeStr = new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
 return (
 <div key={msg.id} style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', padding: showHeader ? '10px 6px 2px' : '1px 6px 1px', borderRadius: '8px', transition: 'background 0.1s' }}
 onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.04)'}
 onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
 {showHeader ? (
 <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: avatarColor, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', fontWeight: 700, color: '#fff', flexShrink: 0, marginTop: '2px' }}>{avatarInitial}</div>
 ) : (
 <div style={{ width: '36px', flexShrink: 0 }} />
 )}
 <div style={{ flex: 1, minWidth: 0 }}>
 {showHeader && (
 <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '3px' }}>
 <span style={{ fontSize: '13px', fontWeight: 600, color: isAnon ? 'rgba(255,255,255,0.65)' : '#fff' }}>{displayName}</span>
 {isAnon && <span style={{ fontSize: '10px', background: 'rgba(255,255,255,0.08)', padding: '1px 6px', borderRadius: '10px', color: 'rgba(255,255,255,0.45)' }}>anon</span>}
 <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.30)' }}>{timeStr}</span>
 </div>
 )}
 <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.88)', lineHeight: '1.5', wordBreak: 'break-word' }}>{msg.content}</div>
 </div>
 </div>
 );
 })
 )}
 <div ref={chatMessagesEndRef} />
 </div>

 {/* Message input bar */}
 {activeChannel && (
 <form onSubmit={sendChatMessage} style={{ padding: '12px 16px', borderTop: '1px solid rgba(255,255,255,0.08)', display: 'flex', gap: '10px', alignItems: 'center', background: 'rgba(255,255,255,0.04)' }}>
 <div style={{ flex: 1, position: 'relative' }}>
 <input
 value={chatInput}
 onChange={e => setChatInput(e.target.value)}
 placeholder={`Message ${activeChannel?.title || 'channel'}...`}
 className="input-field"
 style={{ width: '100%', paddingRight: '44px', fontSize: '14px' }}
 onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChatMessage(e as any); } }}
 />
 </div>
 <button type="button" onClick={() => setChatAnon(!chatAnon)}
 title={chatAnon ? 'Posting anonymously — click to reveal identity' : 'Posting as yourself — click to go anonymous'}
 style={{ flexShrink: 0, width: '38px', height: '38px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.15)', background: chatAnon ? 'rgba(128,128,128,0.18)' : 'rgba(160,160,160,0.18)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', transition: 'all 0.2s' }}>
 {chatAnon ? '' : ''}
 </button>
 <button type="submit" className="btn-primary" style={{ flexShrink: 0, padding: '9px 18px', fontSize: '13px', borderRadius: '10px' }} disabled={!chatInput.trim()}>Send</button>
 </form>
 )}
 </>
 ) : (
 /* BOARD VIEW (posts/whistleblower) */
 <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
 <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>Community Board</h3>
 <div style={{ display: 'flex', gap: '6px' }}>
 <button onClick={() => setCommunityFilter('all')} className={communityFilter === 'all' ? 'btn-primary' : 'btn-secondary'} style={{ fontSize: '11px', padding: '6px 12px', borderRadius: '8px' }}>All</button>
 <button onClick={() => setCommunityFilter('discussion')} className={communityFilter === 'discussion' ? 'btn-primary' : 'btn-secondary'} style={{ fontSize: '11px', padding: '6px 12px', borderRadius: '8px' }}>Discussions</button>
 <button onClick={() => setCommunityFilter('whistleblower')} className={communityFilter === 'whistleblower' ? 'btn-primary' : 'btn-secondary'} style={{ fontSize: '11px', padding: '6px 12px', borderRadius: '8px', color: communityFilter === 'whistleblower' ? '#fff' : '#ff4444' }}> Whistleblower</button>
 </div>
 </div>
 {communityLoading ? (
 <div style={{ padding: '40px', textAlign: 'center', color: 'rgba(255,255,255,0.40)', fontSize: '13px' }}>Loading board...</div>
 ) : (
 <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
 {communityPosts.filter(p => (communityFilter === 'all' || p.post_type === communityFilter) && p.post_type !== 'channel').map((post) => {
 const isExpanded = expandedPostIds.includes(post.id);
 const comments = activePostComments[post.id] || [];
 return (
 <div key={post.id} className="glass-panel" style={{ padding: '16px', borderLeft: post.post_type === 'whistleblower' ? '3px solid #ff4444' : '3px solid rgba(192,192,192,0.5)' }}>
 <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
 <span style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.06em', color: post.post_type === 'whistleblower' ? '#ff4444' : 'var(--accent-cyan)' }}>{post.post_type === 'whistleblower' ? ' Whistleblower' : ' Discussion'}</span>
 <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.35)' }}>{new Date(post.created_at).toLocaleString()}</span>
 </div>
 <h4 style={{ fontSize: '14px', fontWeight: 600, color: '#fff', marginBottom: '6px' }}>{post.title}</h4>
 <p style={{ color: 'rgba(255,255,255,0.65)', fontSize: '12px', lineHeight: '1.5', marginBottom: '10px' }}>{post.content}</p>
 <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '11px', color: 'rgba(255,255,255,0.50)' }}>
 <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
 <button onClick={() => handleVotePost(post.id, 'up')} style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}></button>
 <span style={{ color: '#fff', fontWeight: 600 }}>{post.votes}</span>
 <button onClick={() => handleVotePost(post.id, 'down')} style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}></button>
 </div>
 <button onClick={() => handleToggleComments(post.id)} style={{ background: 'none', border: 'none', color: 'var(--accent-cyan)', cursor: 'pointer', fontSize: '11px' }}>{isExpanded ? 'Hide' : ` ${post.comment_count} replies`}</button>
 <span style={{ marginLeft: 'auto' }}>by {post.is_anonymous ? 'Anonymous' : (post.user?.email || 'System')}</span>
 </div>
 {isExpanded && (
 <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.08)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
 {comments.map((c: any) => (
 <div key={c.id} style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.04)', borderRadius: '8px' }}>
 <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.35)', marginBottom: '3px' }}>{c.is_anonymous ? 'Anonymous' : (c.user?.email || 'User')} · {new Date(c.created_at).toLocaleTimeString()}</div>
 <div style={{ fontSize: '12px', color: '#fff' }}>{c.content}</div>
 </div>
 ))}
 <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
 <input type="text" className="input-field" placeholder="Reply..." value={newCommentText[post.id] || ''} onChange={e => setNewCommentText(prev => ({ ...prev, [post.id]: e.target.value }))} style={{ flex: 1, fontSize: '12px', padding: '8px 12px' }} />
 <button onClick={() => handleSubmitComment(post.id)} className="btn-secondary" style={{ fontSize: '11px', padding: '8px 14px', borderRadius: '10px' }}>Reply</button>
 </div>
 </div>
 )}
 </div>
 );
 })}
 </div>
 )}
 </div>
 )}
 </div>

 {/* RIGHT SIDEBAR: Post composer (board view) or Channel info (chat view) */}
 <div style={{ width: '260px', flexShrink: 0, background: 'rgba(255,255,255,0.05)', backdropFilter: 'blur(40px)', borderLeft: '1px solid rgba(255,255,255,0.10)', display: 'flex', flexDirection: 'column', padding: '16px', gap: '14px', overflowY: 'auto' }}>
 {chatView === 'chat' ? (
 <>
 <div>
 <div style={{ fontSize: '11px', fontWeight: 700, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>Channel Info</div>
 {activeChannel ? (
 <div style={{ padding: '12px', background: 'rgba(255,255,255,0.06)', borderRadius: '12px' }}>
 <div style={{ fontSize: '14px', fontWeight: 600, color: '#fff', marginBottom: '4px' }}>{activeChannel.title}</div>
 <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.55)', lineHeight: '1.5' }}>{activeChannel.content}</div>
 <div style={{ marginTop: '10px', fontSize: '11px', color: 'rgba(255,255,255,0.35)' }}> All messages are anonymous</div>
 </div>
 ) : (
 <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.35)', lineHeight: '1.6' }}>Select a channel to see its info here.</div>
 )}
 </div>
 <div>
 <div style={{ fontSize: '11px', fontWeight: 700, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>Your Identity</div>
 <div style={{ padding: '10px 12px', background: chatAnon ? 'rgba(128,128,128,0.10)' : 'rgba(160,160,160,0.10)', borderRadius: '10px', border: `1px solid ${chatAnon ? 'rgba(128,128,128,0.25)' : 'rgba(160,160,160,0.25)'}` }}>
 <div style={{ fontSize: '13px', fontWeight: 600, color: '#fff', marginBottom: '3px' }}>{chatAnon ? ' Anonymous' : ' Identified'}</div>
 <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.50)' }}>{chatAnon ? 'Your identity is hidden' : user?.email}</div>
 </div>
 </div>
 {showCreateChannel && (
 <form onSubmit={handleCreateChannel} style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: '12px', background: 'rgba(255,255,255,0.06)', borderRadius: '12px' }}>
 <div style={{ fontSize: '12px', fontWeight: 600, color: '#fff' }}>New Channel</div>
 <input className="input-field" placeholder="channel-name" value={newChannelName} onChange={e => setNewChannelName(e.target.value)} style={{ fontSize: '12px', padding: '8px 10px' }} />
 <input className="input-field" placeholder="Short description" value={newChannelDesc} onChange={e => setNewChannelDesc(e.target.value)} style={{ fontSize: '12px', padding: '8px 10px' }} />
 <div style={{ display: 'flex', gap: '6px' }}>
 <button type="submit" className="btn-primary" style={{ flex: 1, justifyContent: 'center', fontSize: '11px', padding: '7px' }}>Create</button>
 <button type="button" onClick={() => setShowCreateChannel(false)} className="btn-secondary" style={{ flex: 1, justifyContent: 'center', fontSize: '11px', padding: '7px' }}>Cancel</button>
 </div>
 </form>
 )}
 </>
 ) : (
 /* Board: Post composer */
 <form onSubmit={handleCreatePost} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
 <div style={{ fontSize: '12px', fontWeight: 700, color: '#fff' }}>Share to Board</div>
 <select className="input-field" value={newPostType} onChange={e => setNewPostType(e.target.value)} style={{ fontSize: '12px', padding: '8px' }}>
 <option value="discussion">Anonymous Discussion</option>
 <option value="whistleblower">Whistleblower Leak</option>
 </select>
 <input type="text" required className="input-field" placeholder="Title..." value={newPostTitle} onChange={e => setNewPostTitle(e.target.value)} style={{ fontSize: '12px', padding: '8px 10px' }} />
 <textarea required className="input-field" placeholder="Details..." value={newPostContent} onChange={e => setNewPostContent(e.target.value)} style={{ fontSize: '12px', padding: '8px 10px', minHeight: '90px', resize: 'vertical' }} />
 {newPostType !== 'whistleblower' && (
 <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'rgba(255,255,255,0.55)', cursor: 'pointer' }}>
 <input type="checkbox" checked={newPostIsAnonymous} onChange={e => setNewPostIsAnonymous(e.target.checked)} />
 Post anonymously
 </label>
 )}
 <button type="submit" className="btn-primary" style={{ justifyContent: 'center', fontSize: '12px', padding: '10px', borderRadius: '10px' }}>Publish</button>
 </form>
 )}
 </div>

 </div>
 )}

 {/* TAB 10: DEVELOPER SOFTWARE & SERVICES MARKETPLACE STORE */}
 {activeTab === 'marketplace' && (
 <div className="animate-fade-in" style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px', alignItems: 'start' }}>
 
 {/* Left Column: Products Listing Store */}
 <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
 
 <div>
 <h2 style={{ fontSize: '20px', color: '#fff', fontWeight: 600 }}>ATLAS Integrations & Services Marketplace</h2>
 <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '4px' }}>
 Acquire custom scripts, plugins, and recruiting services published by verified third-party developers.
 </p>
 </div>

 {marketplaceLoading ? (
 <div className="glass-panel pulse-glow" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
 Loading marketplace store modules...
 </div>
 ) : (
 <div>
 <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '16px', fontWeight: 600 }}>Available Products</h3>
 <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
 {marketplaceProducts.map((prod) => {
 const isBought = marketplacePurchases.some(p => p.product_id === prod.id);
 return (
 <div key={prod.id} className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '200px' }}>
 <div>
 <div style={{ display: 'flex', justifyItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
 <span style={{ fontSize: '10px', background: 'rgba(255,255,255,0.04)', padding: '3px 8px', borderRadius: '12px', color: 'var(--accent-cyan)' }}>
 {prod.category === 'software' ? ' Software integration' : ' Hiring Service'}
 </span>
 <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#fff' }}>
 ${prod.price.toFixed(2)}
 </span>
 </div>

 <h4 style={{ fontSize: '15px', color: '#fff', fontWeight: 'bold', marginBottom: '6px' }}>
 {prod.name}
 </h4>

 <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.4', marginBottom: '16px' }}>
 {prod.description}
 </p>
 </div>

 <div>
 <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginBottom: '8px' }}>
 Publisher: {prod.author_email}
 </div>
 
 {isBought ? (
 <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
 <div style={{ display: 'flex', gap: '6px', fontSize: '12px', color: '#22c55e', fontWeight: 'bold', alignItems: 'center' }}>
 Purchased & Unlocked
 </div>
 {prod.download_url && (
 <a 
 href={prod.download_url} 
 target="_blank" 
 rel="noreferrer" 
 className="btn-primary lining-settings" 
 style={{ justifyContent: 'center', fontSize: '12px', padding: '6px 12px', textDecoration: 'none' }}
 >
 Access / Download Resource
 </a>
 )}
 </div>
 ) : (
 <button 
 onClick={() => handlePurchaseProduct(prod.id)}
 className="btn-primary" 
 style={{ width: '100%', justifyContent: 'center', fontSize: '12px', padding: '8px' }}
 >
 Buy & Unlock
 </button>
 )}
 </div>
 </div>
 );
 })}
 </div>
 </div>
 )}

 {/* My Purchased Inventory */}
 <div>
 <h3 style={{ fontSize: '16px', color: '#fff', marginBottom: '16px', fontWeight: 600 }}>My Purchased Inventory</h3>
 
 {marketplacePurchases.length === 0 ? (
 <div className="glass-panel" style={{ padding: '24px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '13px' }}>
 You have not acquired any software integrations or services yet.
 </div>
 ) : (
 <div className="glass-panel" style={{ padding: '0 20px' }}>
 {marketplacePurchases.map((purch, idx) => (
 <div key={purch.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 0', borderBottom: idx < marketplacePurchases.length - 1 ? '1px solid var(--border-glass)' : 'none' }}>
 <div>
 <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#fff' }}>
 {purch.product?.name || "Unknown Product"}
 </div>
 <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
 Acquired on {new Date(purch.purchased_at).toLocaleString()}
 </div>
 </div>

 {purch.product?.download_url && (
 <a 
 href={purch.product.download_url} 
 target="_blank" 
 rel="noreferrer" 
 className="btn-secondary" 
 style={{ fontSize: '11px', padding: '6px 12px', textDecoration: 'none' }}
 >
 Download Link
 </a>
 )}
 </div>
 ))}
 </div>
 )}
 </div>

 </div>

 {/* Right Column: Publish New Product Form */}
 <div className="glass-panel" style={{ padding: '24px' }}>
 <h3 style={{ fontSize: '18px', color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
 <ShoppingBag size={16} style={{ color: 'var(--accent-cyan)' }} /> Publish to Store
 </h3>
 
 <form onSubmit={handleCreateProduct} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Item Name / Title</label>
 <input 
 type="text" 
 required 
 className="input-field" 
 placeholder="e.g. ATLAS Slack Notification Plugin" 
 value={newProductName} 
 onChange={e => setNewProductName(e.target.value)} 
 style={{ width: '100%' }}
 />
 </div>

 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Description</label>
 <textarea 
 required 
 className="input-field" 
 placeholder="Detailed explanation of the utility, benefits, and support options..." 
 value={newProductDescription} 
 onChange={e => setNewProductDescription(e.target.value)} 
 style={{ width: '100%', minHeight: '80px', resize: 'vertical' }}
 />
 </div>

 <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Price (USD)</label>
 <input 
 type="number" 
 step="0.01" 
 required 
 className="input-field" 
 placeholder="e.g. 29.99" 
 value={newProductPrice} 
 onChange={e => setNewProductPrice(e.target.value)} 
 style={{ width: '100%' }}
 />
 </div>

 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Category</label>
 <select 
 className="input-field" 
 value={newProductCategory} 
 onChange={e => setNewProductCategory(e.target.value)}
 style={{ width: '100%', padding: '10px' }}
 >
 <option value="software">Software / Script</option>
 <option value="service">Recruiting Service</option>
 </select>
 </div>
 </div>

 <div>
 <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Resource Download / Support URL (Optional)</label>
 <input 
 type="url" 
 className="input-field" 
 placeholder="e.g. https://github.com/my-plugin-repo" 
 value={newProductDownloadUrl} 
 onChange={e => setNewProductDownloadUrl(e.target.value)} 
 style={{ width: '100%' }}
 />
 </div>

 <button type="submit" className="btn-primary lining-settings" style={{ width: '100%', justifyContent: 'center', marginTop: '8px' }}>
 List Item For Sale
 </button>
 </form>
 </div>

 </div>
 )}
 </main>

 {/* Footer */}
 <footer style={{ borderTop: '1px solid var(--border-glass)', padding: '24px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.1em', marginTop: 'auto' }}>
 DEVELOPED AND DESIGNED BY ATLAS WORK INTELLIGENCE TEAM
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
 <div style={{ fontWeight: 'bold', color: '#fff', fontSize: '14px' }}> India Local Payment</div>
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
 <div style={{ fontWeight: 'bold', color: '#fff', fontSize: '14px' }}> Global Cards & Wallets</div>
 <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>Pay in USD via Visa, Mastercard, Apple Pay</div>
 </div>
 <div style={{ fontWeight: 'bold', color: 'var(--accent-gold-deep)', fontSize: '14px' }}>$79 / yr</div>
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
 <input type="text" readOnly className="input-field" value="4242 4242 4242 4242" style={{ letterSpacing: '2px', fontFamily: 'monospace' }} />
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
 <span style={{ fontSize: '24px', marginBottom: '4px' }}></span>
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
 <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--accent-gold)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', fontWeight: 'bold' }}>R</div>
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

 {/* INCOMING CALL MODAL DIALOG */}
 {incomingCall && (
 <div style={{ position: 'fixed', top: '0', left: '0', width: '100%', height: '100%', background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(10px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 3000, padding: '16px' }}>
 <div className="glass-panel animate-fade-in" style={{ width: '100%', maxWidth: '360px', padding: '32px', textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '20px' }}>
 <div style={{ display: 'inline-flex', alignSelf: 'center', padding: '16px', background: 'rgba(128, 128, 128, 0.1)', borderRadius: '50%', color: '#808080' }} className="pulse-glow">
 <Phone size={36} />
 </div>
 <div>
 <span style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-dim)', letterSpacing: '0.1em' }}>INCOMING CALL</span>
 <h3 style={{ fontSize: '18px', color: '#fff', marginTop: '6px' }}>{incomingCall.callerName}</h3>
 </div>
 <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
 <button 
 onClick={handleRejectCall} 
 className="btn-secondary" 
 style={{ flex: 1, color: '#808080', border: '1px solid rgba(255,45,85,0.2)', padding: '12px', justifyContent: 'center' }}
 >
 Reject
 </button>
 <button 
 onClick={handleAcceptCall} 
 className="btn-primary" 
 style={{ flex: 1, padding: '12px', justifyContent: 'center' }}
 >
 Accept
 </button>
 </div>
 </div>
 </div>
 )}

 {/* ACTIVE CALL DESK MODAL OVERLAY */}
 {activeCall && (
 <div style={{ position: 'fixed', top: '0', left: '0', width: '100%', height: '100%', background: 'rgba(0,0,0,0.92)', backdropFilter: 'blur(16px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 3000, padding: '16px' }}>
 <div className="glass-panel animate-fade-in" style={{ width: '100%', maxWidth: '720px', padding: '24px', position: 'relative', display: 'flex', flexDirection: 'column', gap: '16px' }}>
 
 {/* Call Header info */}
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px' }}>
 <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
 <span className="pulse-glow" style={{ width: '8px', height: '8px', borderRadius: '50%', background: activeCall.status === 'connected' ? '#84cc16' : '#eab308' }} />
 <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
 {activeCall.status === 'connected' ? 'Live Call Connected' : 'Dialing / Connecting...'}
 </span>
 </div>
 <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#fff' }}>
 {activeCall.peerName}
 </div>
 </div>

 {/* Video Streams Canvas Area */}
 <div style={{ position: 'relative', width: '100%', height: '360px', background: '#09090b', borderRadius: '4px', overflow: 'hidden', border: '1px solid var(--border-glass)' }}>
 {activeCall.status === 'connected' && !videoDisabled ? (
 // Remote/Loopback stream video
 <video 
 ref={remoteVideoRef} 
 autoPlay 
 playsInline 
 style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
 />
 ) : (
 <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%', color: 'var(--text-dim)' }}>
 <Users size={48} />
 <span style={{ fontSize: '13px', marginTop: '12px' }}>
 {videoDisabled ? 'Camera Disabled' : 'Waiting for participant to join...'}
 </span>
 </div>
 )}

 {/* Local picture-in-picture stream preview bubble */}
 {localStream && !videoDisabled && (
 <div style={{ position: 'absolute', bottom: '16px', right: '16px', width: '140px', height: '105px', borderRadius: '4px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.15)', background: '#111', boxShadow: '0 8px 24px rgba(0,0,0,0.5)' }}>
 <video 
 ref={localVideoRef} 
 autoPlay 
 muted 
 playsInline 
 style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
 />
 </div>
 )}
 </div>

 {/* Calling control deck actions */}
 <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginTop: '8px' }}>
 <button 
 onClick={handleToggleMic} 
 className={micMuted ? "btn-secondary" : "btn-primary"}
 style={{ padding: '12px', borderRadius: '50%', color: micMuted ? '#808080' : 'inherit' }}
 title={micMuted ? "Unmute Mic" : "Mute Mic"}
 >
 {micMuted ? <MicOff size={18} /> : <Mic size={18} />}
 </button>
 
 <button 
 onClick={handleToggleVideo} 
 className={videoDisabled ? "btn-secondary" : "btn-primary"}
 style={{ padding: '12px', borderRadius: '50%', color: videoDisabled ? '#808080' : 'inherit' }}
 title={videoDisabled ? "Enable Video" : "Disable Video"}
 >
 {videoDisabled ? <VideoOff size={18} /> : <Video size={18} />}
 </button>

 <button 
 onClick={() => handleEndCall(activeCall.candidateId)} 
 className="btn-primary"
 style={{ padding: '12px 18px', background: '#808080', border: 'none', color: '#fff', display: 'flex', gap: '8px', alignItems: 'center' }}
 title="Hang Up"
 >
 <PhoneOff size={18} />
 <span>Hang Up</span>
 </button>
 </div>

 </div>
 </div>
 )}
 </div>
 );
}
