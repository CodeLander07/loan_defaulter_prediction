import type { MacroRiskResult, FinancialRiskResult, DocumentRiskResult } from '../types';

interface ResultsPanelProps {
  show: boolean;
  loading: boolean;
  macro: MacroRiskResult | null;
  financial: FinancialRiskResult | null;
  document: DocumentRiskResult | null;
}

const GAUGE_RADIUS = 88;
const GAUGE_CIRCUMFERENCE = 2 * Math.PI * GAUGE_RADIUS;

function scoreColor(score: number): string {
  if (score > 70) return 'text-error';
  if (score > 40) return 'text-tertiary';
  return 'text-primary';
}

function scoreLabel(score: number): string {
  if (score > 70) return 'HIGH RISK';
  if (score > 40) return 'MODERATE';
  return 'LOW RISK';
}

const SEVERITY_ICONS: Record<string, string> = {
  Inflation: 'trending_up',
  RepoRate: 'account_balance',
  GDPGrowth: 'bar_chart',
  UnemploymentRate: 'groups',
  HousingIndex: 'home',
  IndustryGrowth: 'factory',
  FuelPrices: 'local_gas_station',
};

function ResultsPanel({ show, loading, macro, financial, document }: ResultsPanelProps) {
  if (!show && !loading) {
    return (
      <section className="bg-surface-container border border-outline-variant/10 rounded-lg p-6 shadow-sm animate-scale-in min-h-[400px] flex flex-col items-center justify-center text-center transition-all duration-300 hover:shadow-lg hover:border-primary/10">
        <span className="material-symbols-outlined text-5xl text-on-surface-variant/20 mb-3 animate-float">psychiatry</span>
        <p className="font-label-md text-label-md text-on-surface-variant/40">Submit a prediction to see results</p>
      </section>
    );
  }

  const gaugeValue = macro?.macro_risk_score ?? 0;
  const gaugeOffset = GAUGE_CIRCUMFERENCE * (1 - gaugeValue / 100);
  const macroConfidence = macro ? (macro.confidence * 100).toFixed(1) : '--';
  const riskTier = financial?.risk_tier ?? '--';
  const factors = macro?.contributing_factors ?? {};
  const factorEntries = Object.entries(factors).slice(0, 3);

  return (
    <div className="space-y-6">
      <section className="bg-surface-container-high border border-outline-variant/10 rounded-lg p-6 shadow-lg relative overflow-hidden animate-scale-in transition-all duration-300 hover:shadow-xl hover:border-primary/10">
        <div className="absolute -top-12 -right-12 w-32 h-32 bg-primary/10 blur-3xl rounded-full animate-float" style={{ animationDuration: '6s' }} />
        <h3 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest text-center mb-6">Real-time Risk Score</h3>
        <div className="relative w-48 h-48 mx-auto flex items-center justify-center">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center z-10">
              <svg className="animate-spin h-8 w-8 text-primary" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
            </div>
          )}
          <svg className={`w-full h-full transform -rotate-90 ${loading ? 'opacity-30' : ''}`} viewBox="0 0 192 192">
            <circle className="text-surface-container-lowest" cx="96" cy="96" fill="transparent" r={GAUGE_RADIUS} stroke="currentColor" strokeWidth="8" />
            {macro && (
              <circle
                cx="96" cy="96" fill="transparent" r={GAUGE_RADIUS}
                stroke="currentColor"
                strokeDasharray={GAUGE_CIRCUMFERENCE}
                strokeDashoffset={gaugeOffset}
                strokeWidth="8"
                className={scoreColor(gaugeValue)}
                style={{ filter: `drop-shadow(0 0 8px ${gaugeValue > 70 ? 'rgba(255, 0, 0, 0.6)' : gaugeValue > 40 ? 'rgba(255, 183, 0, 0.6)' : 'rgba(221, 183, 255, 0.6)'})`, transition: 'stroke-dashoffset 1.5s ease-out' }}
              />
            )}
          </svg>
          <div className={`absolute inset-0 flex flex-col items-center justify-center text-center ${loading ? 'opacity-30' : 'animate-scale-in delay-2'}`}>
            <span className="text-[42px] font-bold text-on-surface leading-none">
              {macro ? gaugeValue : <span className="text-2xl">--</span>}
              {macro && <span className="text-headline-sm font-medium text-on-surface-variant/60" />}
            </span>
            {macro && (
              <span className={`text-label-sm font-bold px-3 py-0.5 rounded-full mt-2 ${gaugeValue > 70 ? 'bg-error/20 text-error' : gaugeValue > 40 ? 'bg-tertiary/20 text-tertiary' : 'bg-primary/20 text-primary'}`}>
                {scoreLabel(gaugeValue)}
              </span>
            )}
          </div>
        </div>
        <div className="mt-8 grid grid-cols-2 gap-4">
          <div className="p-3 bg-surface-container-lowest rounded-lg border border-outline-variant/10 transition-all duration-300 hover:border-primary/30 hover:shadow-md hover:-translate-y-0.5 animate-entrance delay-3">
            <p className="text-label-sm text-on-surface-variant mb-1">Confidence</p>
            <p className="text-headline-sm font-bold text-on-surface">{macroConfidence}%</p>
          </div>
          <div className="p-3 bg-surface-container-lowest rounded-lg border border-outline-variant/10 transition-all duration-300 hover:border-tertiary/30 hover:shadow-md hover:-translate-y-0.5 animate-entrance delay-4">
            <p className="text-label-sm text-on-surface-variant mb-1">Impact Tier</p>
            <p className={`text-headline-sm font-bold ${riskTier.includes('High') || riskTier.includes('Very') ? 'text-error' : riskTier.includes('Moderate') ? 'text-tertiary' : 'text-primary'}`}>{riskTier}</p>
          </div>
        </div>
      </section>

      {macro && (
        <section className="bg-surface-container border border-outline-variant/10 rounded-lg p-6 shadow-sm animate-entrance delay-3 transition-all duration-300 hover:shadow-lg hover:border-primary/10">
          <h3 className="font-headline-sm text-headline-sm text-on-surface mb-4">Contributing Factors</h3>
          <div className="space-y-3">
            {factorEntries.length > 0 ? factorEntries.map(([name, weight], i) => {
              const isWarning = weight > 0.15;
              const isModerate = weight > 0.05;
              const icon = SEVERITY_ICONS[name] || 'analytics';

              return (
                <div
                  key={name}
                  className="flex items-center justify-between p-3 bg-surface-container-lowest rounded-full border border-outline-variant/5 group transition-all duration-300 hover:border-primary/20 hover:shadow-md hover:-translate-y-0.5 cursor-default"
                  style={{ animationDelay: `${0.4 + i * 0.15}s` }}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 group-hover:scale-125 group-hover:rotate-6 ${
                      isWarning ? 'bg-error/10 text-error' : isModerate ? 'bg-tertiary/10 text-tertiary' : 'bg-primary/10 text-primary'
                    }`}>
                      <span className="material-symbols-outlined text-[18px]">{icon}</span>
                    </div>
                    <span className="text-body-md font-medium text-on-surface">{name}</span>
                  </div>
                  <span className={`text-label-sm px-2 py-0.5 border border-outline-variant/20 rounded-full transition-all duration-300 ${
                    isWarning ? 'text-error border-error/30' : isModerate ? 'text-tertiary border-tertiary/30' : 'text-on-surface-variant'
                  }`}>
                    {(weight * 100).toFixed(1)}%
                  </span>
                </div>
              );
            }) : (
              <p className="text-label-md text-on-surface-variant/40 text-center py-4">No contributing factors available</p>
            )}
          </div>
          <p className="mt-4 text-body-sm text-on-surface-variant/60 leading-relaxed px-1">{macro.explainable_summary}</p>
          <button className="w-full mt-4 text-label-md text-primary font-bold transition-all duration-300 hover:tracking-wider hover:underline decoration-2 underline-offset-4 active:scale-[0.98]">
            View Full Parameter Map
          </button>
        </section>
      )}

      {document && (
        <section className="bg-surface-container border border-outline-variant/10 rounded-lg p-6 shadow-sm animate-entrance delay-4 transition-all duration-300 hover:shadow-lg hover:border-primary/10">
          <h3 className="font-headline-sm text-headline-sm text-on-surface mb-3">Document Risk</h3>
          <div className="flex items-center justify-between mb-2">
            <span className="text-label-sm text-on-surface-variant">Score</span>
            <span className="text-label-sm font-bold text-on-surface">{document.score}/100</span>
          </div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-label-sm text-on-surface-variant">Fraud Probability</span>
            <span className="text-label-sm text-on-surface">{(document.fraud_probability * 100).toFixed(1)}%</span>
          </div>
          <p className="text-body-sm text-on-surface-variant/60 mt-2">{document.explainable_summary}</p>
        </section>
      )}

      <div className="bg-surface-container-lowest/50 rounded-lg p-4 border border-outline-variant/5 animate-entrance delay-5 transition-all duration-300 hover:border-primary/20 hover:shadow-md">
        <div className="flex items-center justify-between mb-2">
          <span className="text-label-sm text-on-surface-variant">Last Engine Pulse</span>
          <span className="text-label-sm text-on-surface flex items-center gap-2">
            <span className="indicator-dot" />
            {macro ? 'Live' : '--'}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-label-sm text-on-surface-variant">Model Version</span>
          <span className="text-label-sm text-on-surface">Aegis-v4.2.b-stable</span>
        </div>
      </div>
    </div>
  );
}

export default ResultsPanel;
