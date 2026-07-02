import React, { useMemo, useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Search, ArrowRight, BookOpen, FileText, Globe, CreditCard, Plane, AlertCircle } from 'lucide-react';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import SEOHead from '../../components/shared/SEOHead';

const CATEGORY_ICONS = { Visa: Plane, Dokumente: FileText, Studienkolleg: BookOpen, Sprachkurse: Globe, Zahlung: CreditCard, Anreise: Plane };
const FILTERS = ['Visa', 'Dokumente', 'Studienkolleg', 'Sprachkurse', 'Zahlung', 'Anreise'];

const ARTICLES = [
  { id: 'anabin', category: 'Dokumente', titleDE: 'Wie laeuft die Anerkennungspruefung ueber Anabin?', titleEN: 'How does the Anabin recognition process work?', summaryDE: 'Welche Unterlagen wir zuerst sehen, wie Kategorien gelesen werden und wann eine manuelle Pruefung noetig ist.', summaryEN: 'Which documents we review first, how categories are read, and when a manual review is needed.' },
  { id: 'visa', category: 'Visa', titleDE: 'Welche Unterlagen braucht das Visum wirklich?', titleEN: 'What documents does the visa really require?', summaryDE: 'Checkliste fuer Finanzierungsnachweis, Einladung, Kursbezug und typische Rueckfragen der Botschaft.', summaryEN: 'Checklist for proof of funding, invitation letter, course reference, and common embassy questions.' },
  { id: 'fees', category: 'Zahlung', titleDE: 'Wofuer steht eine Rechnung im Portal?', titleEN: 'What does an invoice in the portal mean?', summaryDE: 'Bedeutung, Faelligkeit, rechtliche Angaben und was nach dem Zahlungseingang passiert.', summaryEN: 'Meaning, due date, legal details, and what happens after payment is received.' },
  { id: 'arrival', category: 'Anreise', titleDE: 'Was passiert nach der Ankunft in Aachen?', titleEN: 'What happens after arrival in Aachen?', summaryDE: 'Erste Schritte mit Meldung, Orientierung, Unterrichtsbeginn und Support-Kanaelen.', summaryEN: 'First steps including registration, orientation, start of classes, and support channels.' },
  { id: 'language', category: 'Sprachkurse', titleDE: 'Welches Sprachlevel ist fuer welchen Weg sinnvoll?', titleEN: 'Which language level makes sense for which path?', summaryDE: 'A1 bis C1 sauber eingeordnet – inklusive Anschlusslogik zum Studienkolleg.', summaryEN: 'A1 to C1 clearly explained – including the connection to the Studienkolleg.' },
  { id: 'docs', category: 'Dokumente', titleDE: 'Warum wurde ein Dokument abgelehnt?', titleEN: 'Why was a document rejected?', summaryDE: 'Haeufige Ablehnungsgruende, Qualitaetskriterien und wie eine Korrektur hochgeladen wird.', summaryEN: 'Common rejection reasons, quality criteria, and how to upload a correction.' },
  { id: 'fsp', category: 'Studienkolleg', titleDE: 'Was ist die Feststellungspruefung (FSP)?', titleEN: 'What is the Feststellungspruefung (FSP)?', summaryDE: 'Die externe Abschlusspruefung des Studienkollegs – Ablauf, Anmeldung, Tipps zur Vorbereitung.', summaryEN: 'The external final exam of the Studienkolleg – process, registration, and preparation tips.' },
  { id: 'insurance', category: 'Anreise', titleDE: 'Welche Krankenversicherung brauche ich?', titleEN: 'Which health insurance do I need?', summaryDE: 'Gesetzlich vs. privat, Nachweispflicht und guenstige Optionen fuer Studienkolleg-Teilnehmer.', summaryEN: 'Public vs. private, proof requirements, and affordable options for Studienkolleg participants.' },
];

function useInView(threshold = 0.1) {
  const ref = useRef(null);
  const [vis, setVis] = useState(false);
  useEffect(() => {
    const el = ref.current; if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setVis(true); obs.unobserve(el); } }, { threshold });
    obs.observe(el); return () => obs.disconnect();
  }, [threshold]);
  return [ref, vis];
}
const stagger = (vis) => `transition-all duration-700 ${vis ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'}`;
const staggerDelay = (idx) => ({ transitionDelay: `${idx * 80}ms` });

export default function KnowledgeCenterPage() {
  const { i18n } = useTranslation();
  const isEN = i18n.language === 'en';
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('Alle');
  const [heroRef, heroVis] = useInView(0.1);
  const [gridRef, gridVis] = useInView(0.1);

  const filteredArticles = useMemo(() => ARTICLES.filter((a) => {
    const matchesFilter = filter === 'Alle' || a.category === filter;
    const q = search.toLowerCase();
    const title = isEN ? a.titleEN : a.titleDE;
    const summary = isEN ? a.summaryEN : a.summaryDE;
    const matchesSearch = !q || title.toLowerCase().includes(q) || summary.toLowerCase().includes(q);
    return matchesFilter && matchesSearch;
  }), [filter, search, isEN]);

  return (
    <div className="min-h-screen bg-white">
      <SEOHead titleKey="seo.knowledge_title" descKey="seo.knowledge_desc" path="/knowledge" />
      <PublicNav />
      <main className="pt-16">

        {/* Hero */}
        <section ref={heroRef} className="relative overflow-hidden py-[72px] lg:py-[96px]"
          style={{ background: 'linear-gradient(170deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)' }}>
          <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, white 1px, transparent 1px)', backgroundSize: '48px 48px' }} />
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12 relative z-10">
            <div className={`max-w-[640px] ${stagger(heroVis)}`}>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-6 h-[2px]" style={{ background: 'var(--color-accent)' }} />
                <span className="text-[11px] font-semibold tracking-[0.2em] uppercase" style={{ color: 'var(--color-accent)' }}>
                  {isEN ? 'Knowledge Center' : 'Wissenscenter'}
                </span>
              </div>
              <h1 className="text-[32px] sm:text-[44px] lg:text-[56px] font-extrabold text-white leading-[1.08] tracking-[-0.03em] mb-6"
                style={{ fontFamily: 'var(--font-heading)' }} data-testid="knowledge-center-page">
                {isEN ? 'Knowledge Center & FAQ' : 'Wissenscenter & FAQ'}
              </h1>
              <p className="text-[15px] lg:text-[17px] text-white/40 leading-[1.7] max-w-[520px] mb-8">
                {isEN
                  ? 'Clear answers about visas, documents, courses, payments, and arrival – organized and immediately usable.'
                  : 'Klare Antworten zu Visa, Dokumenten, Kurswegen, Zahlung und Anreise – sauber gruppiert und direkt nutzbar.'}
              </p>
              {/* Search */}
              <div className="relative max-w-[480px]">
                <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/30" />
                <input value={search} onChange={(e) => setSearch(e.target.value)}
                  className="w-full h-[48px] pl-11 pr-4 text-[14px] text-white bg-white/10 border border-white/10 rounded-[4px] placeholder-white/25 focus:outline-none focus:border-white/25 transition-colors"
                  placeholder={isEN ? 'Search knowledge base...' : 'Im Wissenscenter suchen...'}
                  data-testid="knowledge-search-input" />
              </div>
            </div>
          </div>
        </section>

        {/* Filter + Articles */}
        <section ref={gridRef} className="py-[48px] lg:py-[72px]">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">

            {/* Filter Pills */}
            <div className="flex flex-wrap gap-2 mb-8 lg:mb-12" data-testid="knowledge-filters">
              {['Alle', ...FILTERS].map((item) => (
                <button key={item} type="button" onClick={() => setFilter(item)}
                  className={`px-4 py-2 text-[12px] font-semibold rounded-full transition-all ${
                    filter === item
                      ? 'text-[var(--color-primary-dark)]' : 'border border-[rgba(10,25,47,0.1)] text-[var(--color-text-secondary)] hover:border-[rgba(10,25,47,0.25)] hover:text-[var(--color-primary-dark)]'
                  }`}
                  style={filter === item ? { background: 'var(--color-accent)', color: 'var(--color-primary-dark)' } : {}}
                  data-testid={`knowledge-filter-${item.toLowerCase()}`}>
                  {item === 'Alle' ? (isEN ? 'All' : 'Alle') : item}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
              {/* Articles */}
              <div className="lg:col-span-8 space-y-4" data-testid="knowledge-list-column">
                {filteredArticles.length === 0 ? (
                  <div className="text-center py-16">
                    <AlertCircle size={32} className="mx-auto mb-4" style={{ color: 'var(--color-accent)' }} />
                    <p className="text-[15px] font-semibold text-[var(--color-primary-dark)] mb-1">{isEN ? 'No results found' : 'Keine Ergebnisse'}</p>
                    <p className="text-[13px] text-[var(--color-text-secondary)]">{isEN ? 'Try a different search term or filter.' : 'Versuche einen anderen Suchbegriff oder Filter.'}</p>
                  </div>
                ) : (
                  filteredArticles.map((article, idx) => {
                    const Icon = CATEGORY_ICONS[article.category] || BookOpen;
                    return (
                      <article key={article.id}
                        className={`group p-6 lg:p-8 rounded-[8px] border border-[rgba(10,25,47,0.08)] transition-all duration-300 hover:border-[rgba(10,25,47,0.15)] ${stagger(gridVis)}`}
                        style={{ ...staggerDelay(idx), boxShadow: '0 2px 12px rgba(17,54,85,0.04)' }}
                        data-testid={`knowledge-article-${article.id}`}>
                        <div className="flex items-start gap-4">
                          <div className="w2g-icon-wrap shrink-0">
                            <Icon size={20} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-[2px]"
                                style={{ background: 'rgba(212,175,55,0.1)', color: 'var(--color-accent)' }}>
                                {article.category}
                              </span>
                            </div>
                            <h2 className="text-[17px] font-bold text-[var(--color-primary-dark)] mb-2 leading-[1.3]" style={{ fontFamily: 'var(--font-heading)' }}>
                              {isEN ? article.titleEN : article.titleDE}
                            </h2>
                            <p className="text-[14px] text-[var(--color-text-secondary)] leading-[1.7] mb-4">
                              {isEN ? article.summaryEN : article.summaryDE}
                            </p>
                            <button type="button"
                              className="text-[13px] font-semibold flex items-center gap-1.5 transition-all hover:gap-2.5"
                              style={{ color: 'var(--color-primary)' }}
                              data-testid={`knowledge-read-${article.id}`}>
                              {isEN ? 'Read full article' : 'Vollstaendig lesen'} <ArrowRight size={13} />
                            </button>
                          </div>
                        </div>
                      </article>
                    );
                  })
                )}
              </div>

              {/* Sidebar */}
              <aside className="lg:col-span-4 space-y-5" data-testid="knowledge-sidepanel">
                {/* Popular Topics */}
                <div className="p-6 rounded-[8px] border border-[rgba(10,25,47,0.08)]" style={{ boxShadow: '0 2px 12px rgba(17,54,85,0.04)' }}>
                  <h3 className="text-[11px] font-semibold tracking-[0.15em] uppercase mb-4" style={{ color: 'var(--color-accent)' }}>
                    {isEN ? 'Popular Topics' : 'Beliebte Themen'}
                  </h3>
                  <div className="space-y-3">
                    {[
                      isEN ? 'Document quality & re-upload' : 'Dokumentenqualitaet und Re-Upload',
                      isEN ? 'Semester dates & deadlines' : 'Semesterstarts und Fristen',
                      isEN ? 'Invoice, payment, proof' : 'Rechnung, Zahlung, Nachweis',
                      isEN ? 'FSP exam preparation' : 'FSP-Pruefungsvorbereitung',
                    ].map((topic, i) => (
                      <div key={i} className="flex items-center gap-2.5 text-[13px] text-[var(--color-text-secondary)]">
                        <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: 'var(--color-accent)' }} />
                        {topic}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Direct Help */}
                <div className="p-6 rounded-[8px] border border-[rgba(10,25,47,0.08)]" style={{ boxShadow: '0 2px 12px rgba(17,54,85,0.04)' }}>
                  <h3 className="text-[11px] font-semibold tracking-[0.15em] uppercase mb-3" style={{ color: 'var(--color-accent)' }}>
                    {isEN ? 'Direct Help' : 'Direkte Hilfe'}
                  </h3>
                  <p className="text-[14px] text-[var(--color-text-secondary)] leading-[1.7] mb-4">
                    {isEN
                      ? 'For individual cases, direct contact is the fastest way.'
                      : 'Fuer individuelle Faelle ist der direkte Kontakt der schnellste Weg.'}
                  </p>
                  <Link to="/contact" className="inline-flex items-center gap-2 h-[40px] px-5 text-[13px] font-semibold rounded-full border-2 border-[var(--color-primary)] text-[var(--color-primary)] transition-all hover:bg-[var(--color-primary-dark)] hover:text-white hover:border-[var(--color-primary-dark)]"
                    data-testid="knowledge-contact-button">
                    {isEN ? 'Contact us' : 'Kontakt aufnehmen'}
                  </Link>
                </div>

                {/* Apply CTA */}
                <div className="p-6 rounded-[4px]" style={{ background: 'linear-gradient(170deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)', boxShadow: '0 16px 48px rgba(17,54,85,0.15)' }}>
                  <h3 className="text-[15px] font-bold text-white mb-2" style={{ fontFamily: 'var(--font-heading)' }}>
                    {isEN ? 'Start your application' : 'Bewerbung direkt starten'}
                  </h3>
                  <p className="text-[13px] text-white/40 leading-[1.7] mb-5">
                    {isEN
                      ? 'If your path is clear, go directly to the structured application.'
                      : 'Wenn dein Weg schon klar ist, geh direkt in die strukturierte Bewerbung.'}
                  </p>
                  <Link to="/apply"
                    className="inline-flex items-center justify-center gap-2 w-full h-[44px] text-[13px] font-bold rounded-full transition-all hover:scale-[1.02] group"
                    style={{ background: 'var(--color-accent)', color: 'var(--color-primary-dark)' }}
                    data-testid="knowledge-apply-button">
                    {isEN ? 'Apply Now' : 'Jetzt bewerben'} <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
                  </Link>
                </div>
              </aside>
            </div>
          </div>
        </section>

      </main>
      <PublicFooter />
    </div>
  );
}
