import { INDUSTRY_CODES } from '../data/mockData';

export interface FinancialParams {
  annualRevenue: string;
  liquidityRatio: string;
  operatingMargin: string;
  roa: string;
  profitMargin: string;
  industryCode: string;
}

interface FinancialParamsSectionProps {
  value: FinancialParams;
  onChange: (v: FinancialParams) => void;
}

function FinancialParamsSection({ value, onChange }: FinancialParamsSectionProps) {
  const update = (key: keyof FinancialParams, val: string) => {
    onChange({ ...value, [key]: val });
  };

  const codes = Object.entries(INDUSTRY_CODES);

  return (
    <section className="bg-surface-container border border-outline-variant/10 rounded-lg p-6 shadow-sm animate-entrance delay-3 transition-all duration-300 hover:shadow-lg hover:border-primary/10 hover:-translate-y-0.5">
      <div className="flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-primary text-[20px]">account_balance_wallet</span>
        <h3 className="font-headline-sm text-headline-sm text-on-surface">Financial Parameters</h3>
      </div>
      <div className="grid grid-cols-3 gap-6">
        <div className="space-y-1 animate-entrance delay-3">
          <label className="text-label-sm text-on-surface-variant px-1">Annual Revenue (USD)</label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant/40">$</span>
            <input
              type="number"
              value={value.annualRevenue}
              onChange={e => update('annualRevenue', e.target.value)}
              placeholder="0"
              className="w-full bg-surface-container-lowest border border-outline-variant/20 rounded-full pl-7 pr-4 py-2 text-body-md transition-all duration-300 hover:border-outline-variant/50 focus:border-primary/50 focus:ring-0 focus:shadow-[0_0_20px_rgba(221,183,255,0.1)] focus:scale-[1.01] placeholder:text-on-surface-variant/30"
            />
          </div>
        </div>
        <div className="space-y-1 animate-entrance delay-4">
          <label className="text-label-sm text-on-surface-variant px-1">Liquidity Ratio</label>
          <input
            type="text"
            value={value.liquidityRatio}
            onChange={e => update('liquidityRatio', e.target.value)}
            placeholder="0.00"
            className="w-full bg-surface-container-lowest border border-outline-variant/20 rounded-full px-4 py-2 text-body-md transition-all duration-300 hover:border-outline-variant/50 focus:border-primary/50 focus:ring-0 focus:shadow-[0_0_20px_rgba(221,183,255,0.1)] focus:scale-[1.01] placeholder:text-on-surface-variant/30"
          />
        </div>
        <div className="space-y-1 animate-entrance delay-5">
          <label className="text-label-sm text-on-surface-variant px-1">Operating Margin</label>
          <input
            type="text"
            value={value.operatingMargin}
            onChange={e => update('operatingMargin', e.target.value)}
            placeholder="0.00"
            className="w-full bg-surface-container-lowest border border-outline-variant/20 rounded-full px-4 py-2 text-body-md transition-all duration-300 hover:border-outline-variant/50 focus:border-primary/50 focus:ring-0 focus:shadow-[0_0_20px_rgba(221,183,255,0.1)] focus:scale-[1.01] placeholder:text-on-surface-variant/30"
          />
        </div>
        <div className="space-y-1 animate-entrance delay-4">
          <label className="text-label-sm text-on-surface-variant px-1">ROA (Return on Assets)</label>
          <input
            type="text"
            value={value.roa}
            onChange={e => update('roa', e.target.value)}
            placeholder="0.00"
            className="w-full bg-surface-container-lowest border border-outline-variant/20 rounded-full px-4 py-2 text-body-md transition-all duration-300 hover:border-outline-variant/50 focus:border-primary/50 focus:ring-0 focus:shadow-[0_0_20px_rgba(221,183,255,0.1)] focus:scale-[1.01] placeholder:text-on-surface-variant/30"
          />
        </div>
        <div className="space-y-1 animate-entrance delay-5">
          <label className="text-label-sm text-on-surface-variant px-1">Profit Margin</label>
          <input
            type="text"
            value={value.profitMargin}
            onChange={e => update('profitMargin', e.target.value)}
            placeholder="0.00"
            className="w-full bg-surface-container-lowest border border-outline-variant/20 rounded-full px-4 py-2 text-body-md transition-all duration-300 hover:border-outline-variant/50 focus:border-primary/50 focus:ring-0 focus:shadow-[0_0_20px_rgba(221,183,255,0.1)] focus:scale-[1.01] placeholder:text-on-surface-variant/30"
          />
        </div>
        <div className="space-y-1 animate-entrance delay-5">
          <label className="text-label-sm text-on-surface-variant px-1">Industry Code</label>
          <select
            value={value.industryCode}
            onChange={e => update('industryCode', e.target.value)}
            className="w-full bg-surface-container-lowest border border-outline-variant/20 rounded-full px-4 py-2 text-body-md transition-all duration-300 hover:border-outline-variant/50 focus:border-primary/50 focus:ring-0 focus:shadow-[0_0_20px_rgba(221,183,255,0.1)] focus:scale-[1.01]"
          >
            {codes.map(([label, code]) => (
              <option key={code} value={code}>{label}</option>
            ))}
          </select>
        </div>
      </div>
    </section>
  );
}

export default FinancialParamsSection;
