import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { CheckCircle, ArrowRight, X, FileText, MessageSquare, BookOpen, Shield } from 'lucide-react';

const STEPS_DE = [
  {
    icon: FileText,
    title: 'Bewerbung eingereicht',
    desc: 'Deine Bewerbung und Dokumente wurden erfolgreich übermittelt. Unser Team prüft sie innerhalb von 24 Stunden.',
  },
  {
    icon: BookOpen,
    title: 'Kurs & Status verfolgen',
    desc: 'Im Menü findest du deinen Bewerbungsstatus, offene Aufgaben und nächste Schritte – immer aktuell.',
  },
  {
    icon: FileText,
    title: 'Dokumente verwalten',
    desc: 'Lade fehlende Dokumente hoch, prüfe den Status deiner eingereichten Unterlagen und reagiere auf Nachforderungen.',
  },
  {
    icon: MessageSquare,
    title: 'Nachrichten & Kommunikation',
    desc: 'Schreibe direkt an dein Betreuungsteam. Alle Nachrichten sind dokumentiert und jederzeit abrufbar.',
  },
  {
    icon: Shield,
    title: 'Datenschutz & Einwilligungen',
    desc: 'Unter Einwilligungen steuerst du, welche Daten an Lehrpersonal weitergegeben werden dürfen. Du hast jederzeit die volle Kontrolle.',
  },
];

const STEPS_EN = [
  {
    icon: FileText,
    title: 'Application Submitted',
    desc: 'Your application and documents have been submitted. Our team will review them within 24 hours.',
  },
  {
    icon: BookOpen,
    title: 'Track Your Status',
    desc: 'In the menu you can find your application status, open tasks and next steps – always up to date.',
  },
  {
    icon: FileText,
    title: 'Manage Documents',
    desc: 'Upload missing documents, check the status of your submissions and respond to document requests.',
  },
  {
    icon: MessageSquare,
    title: 'Messages & Communication',
    desc: 'Write directly to your support team. All messages are documented and available at any time.',
  },
  {
    icon: Shield,
    title: 'Privacy & Consents',
    desc: 'Under Consents you control which data may be shared with teaching staff. You have full control at all times.',
  },
];

export default function OnboardingTour({ onComplete }) {
  const { i18n } = useTranslation();
  const { user } = useAuth();
  const [step, setStep] = useState(0);
  const [visible, setVisible] = useState(false);

  const steps = i18n.language === 'en' ? STEPS_EN : STEPS_DE;
  const isLastStep = step === steps.length - 1;

  useEffect(() => {
    const key = `onboarding_done_${user?.id || 'anon'}`;
    if (!localStorage.getItem(key)) {
      setVisible(true);
    }
  }, [user?.id]);

  const handleComplete = () => {
    const key = `onboarding_done_${user?.id || 'anon'}`;
    localStorage.setItem(key, 'true');
    setVisible(false);
    onComplete?.();
  };

  const handleNext = () => {
    if (isLastStep) {
      handleComplete();
    } else {
      setStep(s => s + 1);
    }
  };

  if (!visible) return null;

  const current = steps[step];
  const Icon = current.icon;

  const labels = i18n.language === 'en'
    ? { welcome: `Welcome, ${user?.full_name?.split(' ')[0] || 'there'}!`, sub: 'A quick tour of your portal:', skip: 'Skip', next: 'Next', finish: 'Get Started', step: 'Step' }
    : { welcome: `Willkommen, ${user?.full_name?.split(' ')[0] || 'dort'}!`, sub: 'Eine kurze Tour durch dein Portal:', skip: 'Überspringen', next: 'Weiter', finish: 'Loslegen', step: 'Schritt' };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 animate-fade-in" data-testid="onboarding-tour">
      <div className="bg-white rounded-sm shadow-xl max-w-md w-full" data-testid="onboarding-modal">
        {/* Header */}
        <div className="bg-primary p-5 rounded-t-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-white font-heading font-bold text-lg">{labels.welcome}</h2>
              <p className="text-white/70 text-sm">{labels.sub}</p>
            </div>
            <button onClick={handleComplete} className="text-white/50 hover:text-white transition-colors" data-testid="onboarding-skip-x">
              <X size={20} />
            </button>
          </div>
          {/* Progress */}
          <div className="flex gap-1.5 mt-4">
            {steps.map((_, i) => (
              <div key={i} className={`h-1 flex-1 rounded-full transition-all ${i <= step ? 'bg-white' : 'bg-white/20'}`} />
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="flex items-start gap-4 mb-6">
            <div className="w-12 h-12 bg-primary/8 rounded-sm flex items-center justify-center shrink-0">
              <Icon size={24} className="text-primary" />
            </div>
            <div>
              <p className="text-xs text-slate-400 mb-1">{labels.step} {step + 1}/{steps.length}</p>
              <h3 className="font-semibold text-slate-800 text-base mb-2">{current.title}</h3>
              <p className="text-sm text-slate-600 leading-relaxed">{current.desc}</p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between">
            <button onClick={handleComplete} className="text-sm text-slate-400 hover:text-slate-600 transition-colors" data-testid="onboarding-skip-btn">
              {labels.skip}
            </button>
            <button onClick={handleNext} data-testid="onboarding-next-btn"
              className="bg-primary text-white px-5 py-2.5 rounded-sm text-sm font-medium hover:bg-primary-hover transition-all flex items-center gap-2">
              {isLastStep ? labels.finish : labels.next}
              {isLastStep ? <CheckCircle size={16} /> : <ArrowRight size={16} />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
