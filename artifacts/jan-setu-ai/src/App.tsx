import { type ReactNode, useEffect, useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ErrorBoundary } from '@/components/error-boundary';
import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';
import NotFound from '@/pages/not-found';
import {
  ArrowRight,
  Activity,
  AlertTriangle,
  BarChart3,
  Check,
  ChevronRight,
  Clock3,
  CircleHelp,
  ExternalLink,
  FileText,
  Globe2,
  Headphones,
  Landmark,
  Lightbulb,
  Map,
  MapPin,
  Menu,
  Mic,
  MessageSquare,
  Network,
  Play,
  Quote,
  Send,
  ShieldCheck,
  Sparkles,
  Target,
  Users,
  Volume2,
  X,
} from 'lucide-react';
import {
  type CitizenRequest,
  type DashboardSummary,
  type RequestAnalysis,
  getDashboardSummary,
  listRequests,
  previewRequest,
  saveRequest,
} from '@/lib/api';
import {
  Link,
  Route,
  Switch,
  useLocation,
  Router as WouterRouter,
} from 'wouter';

const queryClient = new QueryClient();

const navItems = [
  { href: '/', label: 'Overview' },
  { href: '/citizen', label: 'Share a request' },
  { href: '/dashboard', label: 'Policymaker view' },
];

function Brand({ dark = false }: { dark?: boolean }) {
  return (
    <Link href="/" className="flex items-center gap-3" data-testid="link-brand">
      <span className={`grid h-10 w-10 place-items-center rounded-xl ${dark ? 'bg-[#f7c75d] text-[#17383e]' : 'bg-[#17383e] text-[#f7c75d]'}`}>
        <Network size={21} strokeWidth={2.4} />
      </span>
      <span className="leading-none">
        <span className={`block font-serif text-[17px] font-bold tracking-[-.04em] ${dark ? 'text-[#f8f0df]' : 'text-[#17383e]'}`}>JanSetu</span>
        <span className={`mt-1 block text-[10px] font-semibold uppercase tracking-[.22em] ${dark ? 'text-[#b7cbc5]' : 'text-[#62817a]'}`}>AI / citizen intelligence</span>
      </span>
    </Link>
  );
}

function Header() {
  const [open, setOpen] = useState(false);
  const [location] = useLocation();
  return (
    <header className="relative z-20 border-b border-[#d9d2c4]/80 bg-[#f9f5ed]/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-[1240px] items-center justify-between px-5 py-4 lg:px-8">
        <Brand />
        <nav className="hidden items-center gap-8 md:flex" aria-label="Primary navigation">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} data-testid={`link-nav-${item.label.toLowerCase().replaceAll(' ', '-')}`} className={`relative py-2 text-[13px] font-semibold transition-colors ${location === item.href ? 'text-[#17383e]' : 'text-[#68817b] hover:text-[#17383e]'}`}>
              {item.label}
              {location === item.href && <span className="absolute -bottom-[18px] left-0 right-0 h-0.5 rounded-full bg-[#e4a83c]" />}
            </Link>
          ))}
          <Link href="/citizen" data-testid="link-header-start" className="group flex items-center gap-2 rounded-full bg-[#17383e] px-5 py-2.5 text-[13px] font-bold text-[#f9f5ed] transition-transform hover:-translate-y-0.5">
            Start with your voice <ArrowRight size={15} className="transition-transform group-hover:translate-x-0.5" />
          </Link>
        </nav>
        <button type="button" aria-label="Open navigation" data-testid="button-open-menu" onClick={() => setOpen(true)} className="rounded-lg p-2 text-[#17383e] md:hidden">
          <Menu size={23} />
        </button>
      </div>
      {open && (
        <div className="absolute inset-x-0 top-full border-b border-[#d9d2c4] bg-[#f9f5ed] p-5 shadow-lg md:hidden">
          <div className="mb-4 flex justify-between"><span className="text-xs font-bold uppercase tracking-widest text-[#68817b]">Navigate</span><button type="button" aria-label="Close navigation" data-testid="button-close-menu" onClick={() => setOpen(false)}><X size={19} /></button></div>
          <div className="grid gap-1">
            {navItems.map((item) => <Link key={item.href} href={item.href} onClick={() => setOpen(false)} data-testid={`link-mobile-${item.label.toLowerCase().replaceAll(' ', '-')}`} className="rounded-lg px-3 py-3 font-semibold text-[#17383e] hover:bg-[#ece5d8]">{item.label}</Link>)}
          </div>
        </div>
      )}
    </header>
  );
}

function PageFrame({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`min-h-[100dvh] bg-[#f9f5ed] text-[#17383e] ${className}`}><Header />{children}</div>;
}

function Home() {
  return (
    <PageFrame>
      <main>
        <section className="relative overflow-hidden border-b border-[#d9d2c4]">
          <div className="pointer-events-none absolute -right-32 -top-32 h-[500px] w-[500px] rounded-full border border-[#e4a83c]/25" />
          <div className="pointer-events-none absolute right-10 top-20 h-[315px] w-[315px] rounded-full border border-[#e4a83c]/20" />
          <div className="mx-auto grid max-w-[1240px] gap-12 px-5 pb-20 pt-16 md:pt-24 lg:grid-cols-[1.05fr_.95fr] lg:items-center lg:px-8 lg:pb-28">
            <div className="relative z-10 max-w-[650px]">
              <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-[#c7d3cd] bg-[#eef2eb] px-3.5 py-2 text-[11px] font-bold uppercase tracking-[.17em] text-[#52736c]">
                <span className="h-2 w-2 rounded-full bg-[#4c9a7c]" /> A civic signal, not a complaint box
              </div>
              <h1 className="font-serif text-[clamp(3.25rem,7vw,6.5rem)] font-bold leading-[.93] tracking-[-.075em] text-[#17383e]">
                Your voice.<br /><span className="text-[#c77a52]">Better decisions.</span>
              </h1>
              <p className="mt-8 max-w-[540px] text-[17px] leading-8 text-[#5a706b]">
                JanSetu AI helps citizens turn everyday development needs into a clear public signal — and helps decision-makers see what matters, where it matters.
              </p>
              <div className="mt-9 flex flex-wrap items-center gap-4">
                <Link href="/citizen" data-testid="link-hero-share" className="group flex items-center gap-3 rounded-full bg-[#e4a83c] px-6 py-3.5 text-sm font-bold text-[#17383e] shadow-[0_8px_24px_rgba(187,131,39,.18)] transition-transform hover:-translate-y-0.5">
                  Share a development need <ArrowRight size={17} className="transition-transform group-hover:translate-x-1" />
                </Link>
                <Link href="/dashboard" data-testid="link-hero-dashboard" className="flex items-center gap-2 rounded-full border border-[#c5cfc6] px-5 py-3.5 text-sm font-bold text-[#315a58] hover:border-[#17383e] hover:bg-[#f0eadf]">
                  <Play size={14} fill="currentColor" /> See the demo
                </Link>
              </div>
              <div className="mt-12 flex items-center gap-3 text-xs text-[#6b827c]">
                <div className="flex -space-x-2">
                  {['A', 'क', 'M', 'S'].map((letter, index) => <span key={letter} className={`grid h-8 w-8 place-items-center rounded-full border-2 border-[#f9f5ed] text-[11px] font-bold ${['bg-[#dae7df] text-[#326555]', 'bg-[#f3d8ae] text-[#9b6126]', 'bg-[#d7e2eb] text-[#345c72]', 'bg-[#ead5ce] text-[#8b4e42]'][index]}`}>{letter}</span>)}
                </div>
                <span>Built for India’s many languages, places and priorities</span>
              </div>
            </div>
            <div className="relative mx-auto w-full max-w-[510px] lg:ml-auto">
              <div className="relative overflow-hidden rounded-[2rem] bg-[#17383e] p-4 shadow-[0_28px_70px_rgba(23,56,62,.2)]">
                <div className="rounded-[1.45rem] border border-[#5e7c78]/45 bg-[#21494d] p-5 sm:p-7">
                  <div className="mb-9 flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-[.2em] text-[#b8d0c6]">Live signal / demo view</span>
                    <span className="flex items-center gap-1.5 text-[10px] font-semibold text-[#f7c75d]"><span className="h-1.5 w-1.5 rounded-full bg-[#f7c75d]" /> synthetic data</span>
                  </div>
                  <div className="mb-8">
                    <div className="text-[12px] text-[#b8d0c6]">Most requested this month</div>
                    <div className="mt-2 font-serif text-4xl font-bold tracking-tight text-[#f8f0df]">Safe water access</div>
                    <div className="mt-3 flex items-center gap-2 text-xs text-[#b8d0c6]"><span className="rounded-full bg-[#f7c75d]/15 px-2 py-1 font-semibold text-[#f7c75d]">+18.4%</span> across 6 wards in Nashik</div>
                  </div>
                  <div className="flex h-32 items-end gap-2 border-b border-[#5e7c78]/50 pb-0">
                    {[38, 47, 42, 65, 56, 79, 68, 94, 82, 100, 91, 108].map((height, index) => <div key={index} className={`flex-1 rounded-t-sm ${index > 8 ? 'bg-[#f7c75d]' : 'bg-[#77a89a]'}`} style={{ height: `${height}px` }} />)}
                  </div>
                  <div className="mt-4 flex justify-between text-[10px] text-[#9ab9ae]"><span>01 May</span><span>31 May</span></div>
                </div>
                <div className="absolute -bottom-5 -left-5 flex items-center gap-3 rounded-2xl border border-[#d9d2c4] bg-[#fbf7ef] px-4 py-3 shadow-xl">
                  <span className="grid h-9 w-9 place-items-center rounded-full bg-[#f0d99f] text-[#90631c]"><Target size={18} /></span>
                  <div><div className="text-[11px] font-bold text-[#17383e]">Priority mapped</div><div className="text-[10px] text-[#6b827c]">Ward-level clarity</div></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-[1240px] px-5 py-20 lg:px-8 lg:py-28">
          <div className="grid gap-12 lg:grid-cols-[.72fr_1.28fr]">
            <div>
              <p className="text-xs font-bold uppercase tracking-[.2em] text-[#c77a52]">One bridge, two sides</p>
              <h2 className="mt-5 max-w-[380px] font-serif text-4xl font-bold leading-tight tracking-[-.05em] text-[#17383e] sm:text-5xl">From lived experience to public action.</h2>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <FeatureCard icon={<MessageSquare size={21} />} number="01" title="Listen in the language people use" body="Text-first, voice-ready intake that makes it easy to share a need in your own words." />
              <FeatureCard icon={<BarChart3 size={21} />} number="02" title="Find the signal in the noise" body="Themes, urgency and location are structured into a view teams can actually act on." />
              <FeatureCard icon={<Map size={21} />} number="03" title="See the need, ward by ward" body="Transparent hotspots reveal where demand is rising and which voices are being heard." />
              <FeatureCard icon={<ShieldCheck size={21} />} number="04" title="Keep the public in the loop" body="A clear trail from request to priority builds trust in the decisions that follow." />
            </div>
          </div>
        </section>

        <section className="bg-[#e8eee7]">
          <div className="mx-auto grid max-w-[1240px] gap-10 px-5 py-20 lg:grid-cols-[1fr_1.2fr] lg:items-center lg:px-8 lg:py-24">
            <div>
              <p className="text-xs font-bold uppercase tracking-[.2em] text-[#52736c]">Designed for the ground reality</p>
              <h2 className="mt-5 font-serif text-4xl font-bold leading-tight tracking-[-.05em] text-[#17383e] sm:text-5xl">A better signal starts with a better question.</h2>
              <p className="mt-5 max-w-[470px] leading-7 text-[#5a706b]">No forms that feel like paperwork. No black box that asks for blind trust. JanSetu is a simple, human front door to a more responsive development process.</p>
              <Link href="/citizen" data-testid="link-section-citizen" className="mt-8 inline-flex items-center gap-2 text-sm font-bold text-[#17383e] underline decoration-[#e4a83c] decoration-2 underline-offset-8">Try the citizen experience <ArrowRight size={16} /></Link>
            </div>
            <div className="relative min-h-[320px] overflow-hidden rounded-[1.75rem] bg-[#17383e] p-7 text-[#f8f0df] sm:p-10">
              <div className="absolute right-8 top-8 text-[#f7c75d]"><Quote size={36} fill="currentColor" strokeWidth={0} /></div>
              <p className="relative max-w-[490px] font-serif text-3xl font-semibold leading-[1.15] tracking-[-.04em]">“The handpump near our anganwadi has been dry for three weeks. We need a reliable water point before summer gets harder.”</p>
              <div className="absolute bottom-8 left-7 flex items-center gap-3 text-xs text-[#b8d0c6] sm:left-10"><span className="grid h-9 w-9 place-items-center rounded-full bg-[#315c5e] font-bold text-[#f7c75d]">RK</span><span>Resident voice · Nashik, Maharashtra</span></div>
              <div className="absolute -bottom-16 -right-8 h-48 w-48 rounded-full border-[24px] border-[#f7c75d]/25" />
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-[1240px] px-5 py-20 lg:px-8 lg:py-24">
          <div className="flex flex-col justify-between gap-6 border-b border-[#d9d2c4] pb-8 sm:flex-row sm:items-end">
            <div><p className="text-xs font-bold uppercase tracking-[.2em] text-[#c77a52]">Built for a credible demo</p><h2 className="mt-4 font-serif text-4xl font-bold tracking-[-.05em] text-[#17383e]">Make the signal visible.</h2></div>
            <Link href="/dashboard" data-testid="link-cta-dashboard" className="flex items-center gap-2 text-sm font-bold text-[#315a58]">Open policymaker view <ChevronRight size={17} /></Link>
          </div>
          <div className="grid gap-8 pt-9 sm:grid-cols-3">
            <StatBlock value="8" label="languages ready for the roadmap" icon={<Globe2 size={18} />} />
            <StatBlock value="6 wards" label="mapped in our synthetic demo" icon={<Map size={18} />} />
            <StatBlock value="1 clear" label="path from voice to priority" icon={<Lightbulb size={18} />} />
          </div>
        </section>
      </main>
      <Footer />
    </PageFrame>
  );
}

function FeatureCard({ icon, number, title, body }: { icon: ReactNode; number: string; title: string; body: string }) {
  return <div className="group rounded-2xl border border-[#d9d2c4] bg-[#fcf8f1] p-6 transition-all hover:-translate-y-1 hover:border-[#b4c5bb] hover:shadow-[0_14px_28px_rgba(23,56,62,.07)]"><div className="flex items-center justify-between text-[#52736c]"><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#e6eee8]">{icon}</span><span className="font-mono text-xs font-bold text-[#9baea5]">{number}</span></div><h3 className="mt-7 font-serif text-xl font-bold leading-tight tracking-[-.025em]">{title}</h3><p className="mt-3 text-sm leading-6 text-[#698079]">{body}</p></div>;
}

function StatBlock({ value, label, icon }: { value: string; label: string; icon: ReactNode }) {
  return <div className="flex gap-4 border-l-2 border-[#e4a83c] pl-5"><span className="mt-1 text-[#c77a52]">{icon}</span><div><div className="font-serif text-3xl font-bold tracking-[-.04em]">{value}</div><div className="mt-1 text-sm leading-5 text-[#698079]">{label}</div></div></div>;
}

function Footer() {
  return <footer className="border-t border-[#d9d2c4] bg-[#f0eadf]"><div className="mx-auto flex max-w-[1240px] flex-col gap-6 px-5 py-8 sm:flex-row sm:items-center sm:justify-between lg:px-8"><Brand /><div className="text-xs text-[#68817b]">A hackathon prototype for more responsive public development.</div></div></footer>;
}

function AnalysisDetails({ analysis, compact = false }: { analysis: RequestAnalysis; compact?: boolean }) {
  const severityTone = analysis.severity === 'High'
    ? 'bg-[#f4ddd4] text-[#994e3d]'
    : analysis.severity === 'Medium'
      ? 'bg-[#fcf2d8] text-[#765821]'
      : 'bg-[#e8eee7] text-[#52736c]';

  return (
    <div className={compact ? 'space-y-4' : 'space-y-5'} data-testid="card-ai-analysis-details">
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-xl bg-[#e8eee7] p-4">
          <p className="text-[10px] font-bold uppercase tracking-[.16em] text-[#52736c]">What JanSetu understood</p>
          <p className="mt-2 text-sm leading-6 text-[#315a58]" data-testid="text-understanding">{analysis.understanding}</p>
        </div>
        <div className="rounded-xl bg-[#f0eadf] p-4">
          <p className="text-[10px] font-bold uppercase tracking-[.16em] text-[#c77a52]">Internal translation</p>
          <p className="mt-2 text-sm leading-6 text-[#315a58]" data-testid="text-translated-request">{analysis.translated_text}</p>
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <DetailItem icon={<LanguagesIcon />} label="Language detected" value={analysis.language === 'hi' ? 'Hindi' : 'English'} testId="text-detected-language" />
        <DetailItem icon={<MapPin size={15} />} label="Location extracted" value={analysis.location} testId="text-extracted-location" />
        <div className="rounded-xl border border-[#d9d2c4] bg-[#fcf8f1] p-3">
          <p className="text-[10px] font-bold uppercase tracking-[.14em] text-[#8ba098]">Urgency</p>
          <p className="mt-2 flex items-center gap-2 text-sm font-bold text-[#17383e]" data-testid="text-urgency"><Clock3 size={15} className="text-[#c77a52]" />{analysis.urgency}</p>
        </div>
        <div className="rounded-xl border border-[#d9d2c4] bg-[#fcf8f1] p-3">
          <p className="text-[10px] font-bold uppercase tracking-[.14em] text-[#8ba098]">Severity</p>
          <p className={`mt-2 inline-flex rounded-full px-2.5 py-1 text-xs font-bold ${severityTone}`} data-testid="text-severity">{analysis.severity}</p>
        </div>
      </div>
      <div className="rounded-xl border border-[#d9d2c4] bg-[#fcf8f1] p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[.16em] text-[#c77a52]">Development category</p>
            <div className="mt-2 flex flex-wrap gap-2" data-testid="list-development-categories">
              {analysis.categories.map((category) => <span key={category} className="rounded-full bg-[#dce9df] px-3 py-1 text-xs font-bold text-[#315a58]">{category}</span>)}
            </div>
          </div>
          <div className="min-w-[150px]">
            <div className="flex items-center justify-between text-xs font-bold text-[#52736c]"><span>Priority score</span><span data-testid="text-priority-score">{analysis.priority_score}/100</span></div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-[#e7e1d6]"><div className="h-full rounded-full bg-[#e4a83c] transition-all" style={{ width: `${analysis.priority_score}%` }} /></div>
          </div>
        </div>
        <p className="mt-3 text-xs text-[#698079]">Confidence: {Math.round(analysis.confidence * 100)}% · {analysis.priority_label}</p>
      </div>
    </div>
  );
}

function DetailItem({ icon, label, value, testId }: { icon: ReactNode; label: string; value: string; testId: string }) {
  return <div className="rounded-xl border border-[#d9d2c4] bg-[#fcf8f1] p-3"><p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-[.14em] text-[#8ba098]">{icon}{label}</p><p className="mt-2 truncate text-sm font-bold text-[#17383e]" data-testid={testId}>{value}</p></div>;
}

function LanguagesIcon() {
  return <Globe2 size={15} />;
}

type SpeechResultEvent = {
  results: ArrayLike<ArrayLike<{ transcript: string }>>;
};

type SpeechRecognizer = {
  lang: string;
  interimResults: boolean;
  maxAlternatives: number;
  start: () => void;
  onresult: ((event: SpeechResultEvent) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
};

function Citizen() {
  const [text, setText] = useState('');
  const [location, setLocation] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [analysis, setAnalysis] = useState<RequestAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [apiError, setApiError] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [voiceInfo, setVoiceInfo] = useState(false);
  const sample = 'The streetlights on our lane have not worked for two weeks.';

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setIsAnalyzing(true);
    setApiError('');
    try {
      const nextAnalysis = await previewRequest({ text: text.trim(), location: location.trim() || undefined });
      setAnalysis(nextAnalysis);
    } catch (error) {
      setApiError(error instanceof Error ? error.message : 'The AI analysis service is unavailable.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSave = async () => {
    if (!text.trim()) return;
    setIsSaving(true);
    setApiError('');
    try {
      const savedRequest = await saveRequest({ text: text.trim(), location: location.trim() || undefined });
      setAnalysis(savedRequest);
      setSubmitted(true);
    } catch (error) {
      setApiError(error instanceof Error ? error.message : 'The request could not be saved.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleVoice = () => {
    const speechWindow = window as Window & {
      SpeechRecognition?: new () => SpeechRecognizer;
      webkitSpeechRecognition?: new () => SpeechRecognizer;
    };
    const Recognition = speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition;
    if (!Recognition) {
      setVoiceInfo(true);
      return;
    }
    const recognition = new Recognition();
    recognition.lang = 'hi-IN';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = (event) => {
      setText(event.results[0][0].transcript);
      setVoiceInfo(false);
    };
    recognition.onerror = () => {
      setVoiceInfo(true);
      setIsListening(false);
    };
    recognition.onend = () => setIsListening(false);
    setIsListening(true);
    recognition.start();
  };

  const editRequest = () => {
    setSubmitted(false);
    setAnalysis(null);
    setApiError('');
  };

  return (
    <PageFrame>
      <main className="mx-auto max-w-[1080px] px-5 py-12 lg:px-8 lg:py-20">
        <div className="mb-12 flex items-center gap-3 text-xs font-bold uppercase tracking-[.17em] text-[#6b827c]"><span className="grid h-7 w-7 place-items-center rounded-full bg-[#e4a83c] text-[#17383e]">{submitted ? <Check size={14} /> : analysis ? <Check size={14} /> : '1'}</span><span className="h-px w-12 bg-[#d9d2c4]" /><span className={analysis ? 'text-[#17383e]' : 'opacity-50'}>2. Review</span><span className="h-px w-12 bg-[#d9d2c4]" /><span className={submitted ? 'text-[#17383e]' : 'opacity-50'}>3. Shared</span></div>
        <div className="grid gap-12 lg:grid-cols-[.76fr_1.24fr] lg:items-start">
          <div>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-[#e8eee7] px-3 py-2 text-[11px] font-bold uppercase tracking-[.16em] text-[#52736c]"><MessageSquare size={14} /> Citizen intake</div>
            <h1 className="font-serif text-5xl font-bold leading-[.96] tracking-[-.06em] text-[#17383e] sm:text-6xl">What should improve where you live?</h1>
            <p className="mt-6 max-w-[410px] text-[16px] leading-7 text-[#5a706b]">Tell us in your own words. A useful request can be about a road, a school, water, safety, health or anything your community needs.</p>
            <div className="mt-8 flex gap-3 rounded-xl border border-[#d9d2c4] bg-[#f0eadf] p-4 text-xs leading-5 text-[#698079]"><ShieldCheck size={17} className="mt-0.5 shrink-0 text-[#52736c]" /><span>Your words stay yours. This demo does not send data anywhere.</span></div>
          </div>
          <div className="rounded-[1.5rem] border border-[#d9d2c4] bg-[#fcf8f1] p-5 shadow-[0_18px_45px_rgba(23,56,62,.06)] sm:p-8">
            {!submitted && !analysis ? (
              <>
                <div className="mb-5 flex items-start justify-between"><div><label htmlFor="request" className="text-lg font-bold text-[#17383e]">Share your request</label><p className="mt-1 text-xs text-[#698079]">Write as much or as little as you like.</p></div><span className="rounded-full bg-[#e8eee7] px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-[#52736c]">Step 1 of 3</span></div>
                <textarea id="request" value={text} maxLength={500} onChange={(event) => setText(event.target.value)} data-testid="input-citizen-request" placeholder="For example: The handpump near our anganwadi has been dry for three weeks..." className="min-h-[180px] w-full resize-none rounded-xl border border-[#cfd8d0] bg-[#f9f5ed] p-4 text-[15px] leading-7 text-[#17383e] outline-none transition-colors placeholder:text-[#9aaea5] focus:border-[#52736c] focus:ring-4 focus:ring-[#dce9df]" />
                <div className="mt-4"><label htmlFor="location" className="text-xs font-bold uppercase tracking-[.14em] text-[#52736c]">Where is this happening? <span className="font-normal normal-case tracking-normal text-[#8ba098]">(optional)</span></label><div className="mt-2 flex items-center gap-2 rounded-xl border border-[#cfd8d0] bg-[#f9f5ed] px-3 focus-within:border-[#52736c]"><MapPin size={16} className="text-[#8ba098]" /><input id="location" value={location} onChange={(event) => setLocation(event.target.value)} data-testid="input-citizen-location" placeholder="Ward, village, block or landmark" className="w-full bg-transparent py-3 text-sm text-[#17383e] outline-none placeholder:text-[#9aaea5]" /></div></div>
                <div className="mt-3 flex flex-wrap items-center justify-between gap-3"><button type="button" data-testid="button-use-example" onClick={() => setText(sample)} className="text-xs font-bold text-[#52736c] underline underline-offset-4">Use a sample request</button><span className="text-[11px] text-[#91a49d]">{text.length}/500</span></div>
                <div className="mt-6 grid gap-3 sm:grid-cols-[1fr_auto]"><button type="button" data-testid="button-voice-input" onClick={handleVoice} className={`flex items-center justify-center gap-2 rounded-xl border px-4 py-3 text-sm font-bold transition-colors ${isListening ? 'border-[#e4a83c] bg-[#fcf2d8] text-[#765821]' : 'border-[#cfd8d0] text-[#315a58] hover:border-[#52736c] hover:bg-[#eef2eb]'}`}><Mic size={17} /> {isListening ? 'Listening…' : 'Add by voice'}</button><button type="button" disabled={!text.trim() || isAnalyzing} data-testid="button-continue-request" onClick={handleAnalyze} className="group flex items-center justify-center gap-2 rounded-xl bg-[#17383e] px-6 py-3 text-sm font-bold text-[#f8f0df] transition-all hover:bg-[#28565a] disabled:cursor-not-allowed disabled:opacity-40">{isAnalyzing ? 'Understanding…' : 'Continue'} {!isAnalyzing && <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />}</button></div>
                {voiceInfo && <div className="mt-4 flex items-start gap-3 rounded-xl border border-[#ead2a0] bg-[#fcf2d8] p-4 text-xs leading-5 text-[#765821]" role="status" data-testid="status-voice-support"><Volume2 size={16} className="mt-0.5 shrink-0" /><span><strong className="font-bold">Voice capture is not available in this browser.</strong> You can type your request instead.</span><button type="button" aria-label="Dismiss voice information" data-testid="button-dismiss-voice-info" onClick={() => setVoiceInfo(false)} className="ml-auto"><X size={15} /></button></div>}
              </>
            ) : analysis && !submitted ? (
              <div className="py-2" data-testid="state-request-review">
                <div className="mb-6 flex items-start justify-between"><div><p className="text-xs font-bold uppercase tracking-[.17em] text-[#52736c]">Step 2 of 3</p><h2 className="mt-2 font-serif text-3xl font-bold tracking-[-.04em]">Here is what JanSetu understood.</h2></div><Activity size={23} className="text-[#e4a83c]" /></div>
                <AnalysisDetails analysis={analysis} />
                {apiError && <p className="mt-4 rounded-xl bg-[#f4ddd4] p-3 text-xs leading-5 text-[#994e3d]" role="alert" data-testid="status-api-error">{apiError}</p>}
                <div className="mt-6 flex flex-wrap justify-end gap-3"><button type="button" data-testid="button-edit-analysis" onClick={editRequest} className="rounded-xl border border-[#cfd8d0] px-4 py-3 text-sm font-bold text-[#315a58] hover:bg-[#eef2eb]">Edit request</button><button type="button" data-testid="button-confirm-request" onClick={handleSave} disabled={isSaving} className="flex items-center gap-2 rounded-xl bg-[#17383e] px-5 py-3 text-sm font-bold text-[#f8f0df] disabled:opacity-50">{isSaving ? 'Sharing…' : 'Confirm and share'} {!isSaving && <Send size={15} />}</button></div>
              </div>
            ) : (
              <div className="py-2" data-testid="status-request-ready">
                <div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-[#e0eee5] text-[#398066]"><Check size={30} strokeWidth={2.5} /></div>
                <p className="mt-6 text-xs font-bold uppercase tracking-[.18em] text-[#52736c]">Step 3 of 3 · Shared</p>
                <h2 className="mt-3 font-serif text-3xl font-bold tracking-[-.04em]">Your request is now a public signal.</h2>
                <p className="mx-auto mt-3 max-w-[380px] text-sm leading-6 text-[#698079]">The AI analysis is stored in the demo dataset and is ready for the policymaker view.</p>
                <div className="mt-7 rounded-xl bg-[#f0eadf] p-4 text-left text-sm leading-6 text-[#315a58]">“{text}”</div>
                {analysis && <div className="mt-6 text-left"><AnalysisDetails analysis={analysis} compact /></div>}
                {apiError && <p className="mt-4 rounded-xl bg-[#f4ddd4] p-3 text-xs leading-5 text-[#994e3d]" role="alert" data-testid="status-api-error">{apiError}</p>}
                <div className="mt-7 flex flex-wrap justify-center gap-3"><button type="button" data-testid="button-start-over" onClick={editRequest} className="rounded-xl border border-[#cfd8d0] px-4 py-3 text-sm font-bold text-[#315a58] hover:bg-[#eef2eb]">Share another request</button><Link href="/dashboard" data-testid="link-view-analysis" className="flex items-center gap-2 rounded-xl bg-[#17383e] px-4 py-3 text-sm font-bold text-[#f8f0df]">Open policymaker view <ExternalLink size={15} /></Link></div>
              </div>
            )}
          </div>
        </div>
        <div className="mt-20 grid gap-4 border-t border-[#d9d2c4] pt-8 sm:grid-cols-3">
          {[[<FileText size={18} />, 'Say it plainly', 'No official language or department knowledge needed.'], [<Globe2 size={18} />, 'Language-ready', 'Designed to meet people in the language they use.'], [<Headphones size={18} />, 'Voice is coming', 'Speech input is part of the product roadmap.']].map(([icon, title, body], index) => <div key={index} className="flex gap-3"><span className="text-[#c77a52]">{icon}</span><div><div className="text-sm font-bold">{title}</div><div className="mt-1 text-xs leading-5 text-[#698079]">{body}</div></div></div>)}
        </div>
      </main>
    </PageFrame>
  );
}

const priorities = [
  { name: 'Water access', share: '28.6%', count: '1,284 requests', color: '#e4a83c' },
  { name: 'Roads & mobility', share: '22.1%', count: '993 requests', color: '#c77a52' },
  { name: 'Street safety', share: '17.4%', count: '782 requests', color: '#5d9a85' },
  { name: 'Public health', share: '13.8%', count: '620 requests', color: '#6b91a5' },
];

function Dashboard() {
  const [activePriority, setActivePriority] = useState('Water access');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [requests, setRequests] = useState<CitizenRequest[]>([]);
  const [selectedRequestId, setSelectedRequestId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [dashboardError, setDashboardError] = useState('');

  useEffect(() => {
    let mounted = true;
    Promise.all([getDashboardSummary(), listRequests()])
      .then(([nextSummary, nextRequests]) => {
        if (!mounted) return;
        setSummary(nextSummary);
        setRequests(nextRequests);
        setSelectedRequestId(nextRequests[0]?.id ?? null);
        setActivePriority(nextRequests[0]?.category ?? 'Water access');
      })
      .catch((error: unknown) => {
        if (mounted) setDashboardError(error instanceof Error ? error.message : 'Live analysis is unavailable.');
      })
      .finally(() => {
        if (mounted) setIsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const livePriorities = requests.length
    ? Object.entries(
      requests.reduce<Record<string, number>>((counts, request) => {
        counts[request.category] = (counts[request.category] ?? 0) + 1;
        return counts;
      }, {}),
    )
      .sort(([, countA], [, countB]) => countB - countA)
      .map(([name, count], index) => ({
        name,
        share: `${Math.round((count / requests.length) * 100)}%`,
        count: `${count} request${count === 1 ? '' : 's'}`,
        color: ['#e4a83c', '#c77a52', '#5d9a85', '#6b91a5'][index % 4],
      }))
    : priorities;
  const selectedRequest = requests.find((request) => request.id === selectedRequestId) ?? requests[0];

  return (
    <PageFrame>
      <main className="mx-auto max-w-[1240px] px-5 py-10 lg:px-8 lg:py-14">
        <div className="mb-10 flex flex-col justify-between gap-5 sm:flex-row sm:items-end"><div><div className="mb-3 inline-flex items-center gap-2 rounded-full border border-[#ead2a0] bg-[#fcf2d8] px-3 py-1.5 text-[10px] font-bold uppercase tracking-[.16em] text-[#765821]"><Sparkles size={13} /> Prototype workspace</div><h1 className="font-serif text-4xl font-bold tracking-[-.055em] sm:text-5xl">Development intelligence</h1><p className="mt-3 text-sm text-[#698079]">A transparent view of what residents are asking for across Nashik, Maharashtra.</p></div><button type="button" data-testid="button-dashboard-help" className="flex items-center gap-2 self-start rounded-full border border-[#cfd8d0] px-4 py-2.5 text-xs font-bold text-[#315a58] hover:bg-[#eef2eb] sm:self-auto"><CircleHelp size={15} /> About this demo</button></div>
        <div className="mb-7 flex items-start gap-3 rounded-xl border border-[#bcd1c4] bg-[#e9f1eb] p-4 text-sm text-[#315a58]" data-testid="status-demo-banner"><Sparkles size={18} className="mt-0.5 shrink-0 text-[#5d9a85]" /><div><strong className="font-bold">Synthetic demo data.</strong> This view uses the local SQLite analysis feed. No government system is connected.</div></div>
        {dashboardError && <div className="mb-7 flex items-start gap-3 rounded-xl border border-[#ead2a0] bg-[#fcf2d8] p-4 text-xs leading-5 text-[#765821]" role="status" data-testid="status-dashboard-api"><AlertTriangle size={16} className="mt-0.5 shrink-0" /><span>Live AI analysis is not connected yet. Start the FastAPI backend to load saved citizen signals.</span></div>}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Kpi label="Requests received" value={isLoading ? '…' : summary ? String(summary.total_requests) : '—'} trend={summary ? 'from SQLite feed' : 'waiting for API'} icon={<MessageSquare size={18} />} />
          <Kpi label="Active hotspots" value={isLoading ? '…' : summary ? String(summary.active_hotspots) : '—'} trend={summary ? 'high-demand clusters' : 'waiting for API'} icon={<Map size={18} />} />
          <Kpi label="High priority" value={isLoading ? '…' : summary ? String(summary.high_priority_requests) : '—'} trend={summary ? 'transparent score ≥ 75' : 'waiting for API'} icon={<Target size={18} />} />
          <Kpi label="Top category" value={isLoading ? '…' : summary?.top_category ?? '—'} trend={summary ? 'most repeated signal' : 'waiting for API'} icon={<Globe2 size={18} />} />
        </div>
        <div className="mt-4 grid gap-4 lg:grid-cols-[1.15fr_.85fr]">
          <section className="rounded-2xl border border-[#d9d2c4] bg-[#fcf8f1] p-5 sm:p-7" data-testid="card-priority-signals">
            <div className="flex items-start justify-between"><div><p className="text-[10px] font-bold uppercase tracking-[.18em] text-[#c77a52]">What people need</p><h2 className="mt-2 font-serif text-2xl font-bold tracking-[-.04em]">Priority signals</h2></div><button type="button" data-testid="button-export-priorities" className="rounded-lg p-2 text-[#698079] hover:bg-[#f0eadf]" aria-label="Export priority signals"><BarChart3 size={18} /></button></div>
            <div className="mt-8 space-y-5">{livePriorities.map((priority) => <button type="button" key={priority.name} onClick={() => setActivePriority(priority.name)} data-testid={`button-priority-${priority.name.toLowerCase().replaceAll(' ', '-')}`} className={`block w-full text-left ${activePriority === priority.name ? '' : 'opacity-65'} transition-opacity`}><div className="mb-2 flex items-end justify-between"><span className="text-sm font-bold">{priority.name}</span><span className="text-xs text-[#698079]">{priority.share} <span className="ml-1 hidden sm:inline">{priority.count}</span></span></div><div className="h-3 overflow-hidden rounded-full bg-[#e7e1d6]"><div className="h-full rounded-full transition-all duration-500" style={{ width: priority.share, backgroundColor: priority.color }} /></div></button>)}</div>
            <div className="mt-7 flex items-center gap-2 border-t border-[#e5ded1] pt-5 text-xs text-[#698079]"><span className="h-2 w-2 rounded-full" style={{ backgroundColor: livePriorities.find((p) => p.name === activePriority)?.color }} /> Showing {activePriority.toLowerCase()} as the active signal <ChevronRight size={13} className="ml-auto" /></div>
          </section>
          <section className="rounded-2xl bg-[#17383e] p-5 text-[#f8f0df] sm:p-7" data-testid="card-hotspots">
            <div className="flex items-start justify-between"><div><p className="text-[10px] font-bold uppercase tracking-[.18em] text-[#f7c75d]">Where demand is rising</p><h2 className="mt-2 font-serif text-2xl font-bold tracking-[-.04em]">Hotspots</h2></div><Map size={21} className="text-[#f7c75d]" /></div>
            <div className="relative mt-7 h-[212px] overflow-hidden rounded-xl border border-[#5e7c78]/45 bg-[#21494d]">
              <div className="absolute inset-0 opacity-35" style={{ backgroundImage: 'linear-gradient(32deg, transparent 48%, #a6c7b9 49%, transparent 51%), linear-gradient(118deg, transparent 48%, #a6c7b9 49%, transparent 51%), linear-gradient(76deg, transparent 48%, #a6c7b9 49%, transparent 51%)', backgroundSize: '110px 80px' }} />
              {[['Panchavati', 'water', 'left-[22%] top-[28%]', 'bg-[#f7c75d]'], ['Satpur', 'roads', 'left-[62%] top-[23%]', 'bg-[#e78d67]'], ['Nashik Road', 'safety', 'left-[47%] top-[67%]', 'bg-[#7db49e]']].map(([area, issue, position, color]) => <button type="button" key={area} data-testid={`button-hotspot-${area.toLowerCase().replaceAll(' ', '-')}`} className={`absolute ${position} group`}><span className={`relative grid h-9 w-9 place-items-center rounded-full ${color} text-[#17383e] shadow-lg ring-4 ring-white/10`}><span className="absolute inset-0 animate-ping rounded-full bg-inherit opacity-25" /><span className="relative h-2 w-2 rounded-full bg-[#17383e]" /></span><span className="absolute left-1/2 top-11 hidden -translate-x-1/2 whitespace-nowrap rounded-md bg-[#f8f0df] px-2 py-1 text-[10px] font-bold text-[#17383e] group-hover:block">{area} · {issue}</span></button>)}
              <div className="absolute bottom-3 left-3 rounded-md bg-[#17383e]/80 px-2 py-1 text-[9px] uppercase tracking-widest text-[#b8d0c6]">Illustrative ward map</div>
            </div>
            <div className="mt-5 flex justify-between text-xs"><span className="text-[#b8d0c6]">3 emerging clusters</span><span className="font-bold text-[#f7c75d]">View all wards <ArrowRight size={13} className="ml-1 inline" /></span></div>
          </section>
        </div>
        <section className="mt-4 rounded-2xl border border-[#d9d2c4] bg-[#fcf8f1] p-5 sm:p-7" data-testid="card-ai-analysis-ledger">
          <div className="flex flex-col justify-between gap-4 border-b border-[#e5ded1] pb-5 sm:flex-row sm:items-end">
            <div><p className="text-[10px] font-bold uppercase tracking-[.18em] text-[#c77a52]">AI analysis ledger</p><h2 className="mt-2 font-serif text-2xl font-bold tracking-[-.04em]">What the system understood</h2><p className="mt-2 max-w-[640px] text-sm leading-6 text-[#698079]">Every request is made explainable: language, internal translation, location, development category, urgency and severity stay visible to the policy team.</p></div>
            <span className="inline-flex items-center gap-2 rounded-full bg-[#e8eee7] px-3 py-2 text-[11px] font-bold text-[#52736c]"><Activity size={14} /> {requests.length} analyzed signals</span>
          </div>
          <div className="mt-5 grid gap-4 lg:grid-cols-[.75fr_1.25fr]">
            <div className="space-y-2" data-testid="list-analyzed-requests">
              {isLoading && <div className="rounded-xl bg-[#f0eadf] p-4 text-sm text-[#698079]">Loading analyzed requests…</div>}
              {!isLoading && !requests.length && <div className="rounded-xl bg-[#f0eadf] p-4 text-sm text-[#698079]">No analyzed citizen requests yet.</div>}
              {requests.map((request) => <button type="button" key={request.id} onClick={() => setSelectedRequestId(request.id)} data-testid={`button-analyzed-request-${request.id}`} className={`w-full rounded-xl border p-4 text-left transition-colors ${selectedRequest?.id === request.id ? 'border-[#52736c] bg-[#e8eee7]' : 'border-[#e5ded1] bg-[#f9f5ed] hover:border-[#b4c5bb]'}`}><div className="flex items-start justify-between gap-3"><span className="line-clamp-2 text-sm font-bold leading-5 text-[#17383e]">{request.issue}</span><span className={`shrink-0 rounded-full px-2 py-1 text-[10px] font-bold ${request.severity === 'High' ? 'bg-[#f4ddd4] text-[#994e3d]' : 'bg-[#fcf2d8] text-[#765821]'}`}>{request.severity}</span></div><div className="mt-3 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-[#698079]"><span>{request.location}</span><span>·</span><span>{request.urgency}</span><span>·</span><span>{request.priority_score}/100</span></div></button>)}
            </div>
            <div className="rounded-xl border border-[#d9d2c4] bg-[#f0eadf] p-4 sm:p-5">
              {selectedRequest ? <AnalysisDetails analysis={selectedRequest} compact /> : <div className="grid min-h-[230px] place-items-center text-center text-sm text-[#698079]"><div><AlertTriangle size={22} className="mx-auto mb-3 text-[#c77a52]" /><p>Select an analyzed request to inspect its details.</p></div></div>}
            </div>
          </div>
        </section>
        <section className="mt-4 grid gap-4 lg:grid-cols-[.8fr_1.2fr]">
          <div className="rounded-2xl border border-[#d9d2c4] bg-[#fcf8f1] p-5 sm:p-7"><p className="text-[10px] font-bold uppercase tracking-[.18em] text-[#c77a52]">Signal quality</p><h2 className="mt-2 font-serif text-2xl font-bold tracking-[-.04em]">The context behind the count</h2><div className="mt-7 flex items-center gap-6"><div className="relative grid h-32 w-32 place-items-center rounded-full" style={{ background: 'conic-gradient(#5d9a85 0 76%, #e7e1d6 76% 100%)' }}><div className="grid h-24 w-24 place-items-center rounded-full bg-[#fcf8f1]"><span className="font-serif text-2xl font-bold">76%</span></div></div><div className="space-y-3 text-xs text-[#698079]"><div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#5d9a85]" /> Specific enough to act</div><div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#e7e1d6]" /> Needs more context</div></div></div></div>
          <div className="rounded-2xl border border-[#d9d2c4] bg-[#f0eadf] p-5 sm:p-7"><div className="flex items-start justify-between"><div><p className="text-[10px] font-bold uppercase tracking-[.18em] text-[#52736c]">Recent requests</p><h2 className="mt-2 font-serif text-2xl font-bold tracking-[-.04em]">A sample of the voice</h2></div><span className="text-xs font-bold text-[#52736c]">{summary?.top_location ?? 'Live feed'}</span></div><div className="mt-5 divide-y divide-[#d9d2c4]">{requests.slice(0, 3).map((request) => <div key={request.id} className="flex gap-3 py-4 first:pt-2"><span className="mt-1 grid h-7 w-7 shrink-0 place-items-center rounded-full bg-[#dbe7df] text-[#52736c]"><MessageSquare size={13} /></span><div><p className="text-sm leading-5 text-[#315a58]">“{request.text}”</p><p className="mt-1 text-[10px] font-bold uppercase tracking-wider text-[#8ba098]">{request.location} · {request.category}</p></div></div>)}{!requests.length && <p className="py-4 text-sm text-[#698079]">Start the backend to load recent analyzed requests.</p>}</div></div>
        </section>
        <p className="mt-8 text-center text-[11px] text-[#8ba098]">Prototype only · Values are synthetic and illustrative · JanSetu AI is not connected to any government system</p>
      </main>
    </PageFrame>
  );
}

function Kpi({ label, value, trend, icon }: { label: string; value: string; trend: string; icon: ReactNode }) {
  return <div className="rounded-2xl border border-[#d9d2c4] bg-[#fcf8f1] p-5"><div className="flex items-center justify-between text-[#c77a52]"><span className="text-xs font-bold uppercase tracking-[.12em] text-[#698079]">{label}</span>{icon}</div><div className="mt-5 font-serif text-3xl font-bold tracking-[-.05em]">{value}</div><div className="mt-1 text-xs font-semibold text-[#5d9a85]">{trend}</div></div>;
}

function Router() {
  return <RoutedErrorBoundary><Switch><Route path="/" component={Home} /><Route path="/citizen" component={Citizen} /><Route path="/dashboard" component={Dashboard} /><Route component={NotFound} /></Switch></RoutedErrorBoundary>;
}

function RoutedErrorBoundary({ children }: { children: ReactNode }) {
  const [location] = useLocation();
  return <ErrorBoundary resetKey={location}>{children}</ErrorBoundary>;
}

function App() {
  return <QueryClientProvider client={queryClient}><TooltipProvider><WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}><Router /></WouterRouter><Toaster /></TooltipProvider></QueryClientProvider>;
}

export default App;