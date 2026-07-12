import { REGION_OPTIONS, LOAN_TYPES, INDUSTRIES, EMPLOYMENT_SECTORS } from '../data/mockData';

export interface ApplicantInfo {
  entityName: string;
  applicationId: string;
  region: string;
  loanType: string;
  industry: string;
  employmentSector: string;
}

interface ApplicantInfoSectionProps {
  value: ApplicantInfo;
  onChange: (v: ApplicantInfo) => void;
}

function ApplicantInfoSection({ value, onChange }: ApplicantInfoSectionProps) {
  const update = (key: keyof ApplicantInfo, val: string) => {
    onChange({ ...value, [key]: val });
  };

  return (
    <section className="bg-surface-container border border-outline-variant/10 rounded-lg p-6 shadow-sm animate-entrance delay-2 transition-all duration-300 hover:shadow-lg hover:border-primary/10 hover:-translate-y-0.5">
      <div className="flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-primary text-[20px]">person_pin_circle</span>
        <h3 className="font-headline-sm text-headline-sm text-on-surface">Applicant Information</h3>
      </div>
      <div className="grid grid-cols-2 gap-x-6 gap-y-4">
        <div className="space-y-1 animate-entrance delay-2">
          <label className="text-label-sm text-on-surface-variant px-1">Legal Entity Name</label>
          <input
            type="text"
            value={value.entityName}
            onChange={e => update('entityName', e.target.value)}
            placeholder="Enter legal entity name"
            className="w-full bg-surface-container-lowest border border-outline-variant/20 rounded-full px-4 py-2 text-body-md transition-all duration-300 hover:border-outline-variant/50 focus:border-primary/50 focus:ring-0 focus:shadow-[0_0_20px_rgba(221,183,255,0.1)] focus:scale-[1.01] placeholder:text-on-surface-variant/30"
          />
        </div>
        <div className="space-y-1 animate-entrance delay-3">
          <label className="text-label-sm text-on-surface-variant px-1">Application ID</label>
          <input
            type="text"
            value={value.applicationId}
            readOnly
            className="w-full bg-surface-container-lowest/50 border border-outline-variant/10 rounded-full px-4 py-2 text-body-md text-on-surface-variant/60 cursor-default"
          />
        </div>
        <div className="space-y-1 animate-entrance delay-4">
          <label className="text-label-sm text-on-surface-variant px-1">Region Jurisdiction</label>
          <select
            value={value.region}
            onChange={e => update('region', e.target.value)}
            className="w-full bg-surface-container-lowest border border-outline-variant/20 rounded-full px-4 py-2 text-body-md transition-all duration-300 hover:border-outline-variant/50 focus:border-primary/50 focus:ring-0 focus:shadow-[0_0_20px_rgba(221,183,255,0.1)] focus:scale-[1.01]"
          >
            {REGION_OPTIONS.map(r => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>
        <div className="space-y-1 animate-entrance delay-5">
          <label className="text-label-sm text-on-surface-variant px-1">Loan Type</label>
          <select
            value={value.loanType}
            onChange={e => update('loanType', e.target.value)}
            className="w-full bg-surface-container-lowest border border-outline-variant/20 rounded-full px-4 py-2 text-body-md transition-all duration-300 hover:border-outline-variant/50 focus:border-primary/50 focus:ring-0 focus:shadow-[0_0_20px_rgba(221,183,255,0.1)] focus:scale-[1.01]"
          >
            {LOAN_TYPES.map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div className="space-y-1 animate-entrance delay-5">
          <label className="text-label-sm text-on-surface-variant px-1">Industry Sector</label>
          <select
            value={value.industry}
            onChange={e => update('industry', e.target.value)}
            className="w-full bg-surface-container-lowest border border-outline-variant/20 rounded-full px-4 py-2 text-body-md transition-all duration-300 hover:border-outline-variant/50 focus:border-primary/50 focus:ring-0 focus:shadow-[0_0_20px_rgba(221,183,255,0.1)] focus:scale-[1.01]"
          >
            {INDUSTRIES.map(ind => (
              <option key={ind} value={ind}>{ind}</option>
            ))}
          </select>
        </div>
        <div className="space-y-1 animate-entrance delay-5">
          <label className="text-label-sm text-on-surface-variant px-1">Employment Sector</label>
          <select
            value={value.employmentSector}
            onChange={e => update('employmentSector', e.target.value)}
            className="w-full bg-surface-container-lowest border border-outline-variant/20 rounded-full px-4 py-2 text-body-md transition-all duration-300 hover:border-outline-variant/50 focus:border-primary/50 focus:ring-0 focus:shadow-[0_0_20px_rgba(221,183,255,0.1)] focus:scale-[1.01]"
          >
            {EMPLOYMENT_SECTORS.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>
    </section>
  );
}

export default ApplicantInfoSection;
