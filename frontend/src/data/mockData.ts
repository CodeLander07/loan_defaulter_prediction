export const NAV_ITEMS = [
  { label: 'New Prediction', path: '/new-prediction', icon: 'precision_manufacturing' },
  { label: 'Settings', path: '/settings', icon: 'settings' },
];

export const LOAN_TYPES = [
  'SME',
  'Home Loan',
  'Personal Loan',
  'Business Loan',
  'Agricultural Loan',
];

export const INDUSTRIES = [
  'Manufacturing',
  'IT Services',
  'Retail',
  'Healthcare',
  'Construction',
  'Education',
  'Transportation',
  'Energy',
];

export const EMPLOYMENT_SECTORS = ['Private', 'Govt', 'Self-Employed'];

export const REGION_OPTIONS = [
  'North America (NA-01)',
  'European Union (EU-27)',
  'Asia Pacific (APAC-02)',
  'South Asia (SA-03)',
];

export const RISK_TRIGGERS = [
  { label: 'Market Volatility', icon: 'warning', severity: 'Critical' as const },
  { label: 'Asset Liquidity', icon: 'trending_down', severity: 'Moderate' as const },
  { label: 'Regulatory Compliance', icon: 'gavel', severity: 'Healthy' as const },
];

export const INDUSTRY_CODES: Record<string, string> = {
  'Manufacturing': 'manufacturing',
  'IT Services': 'it_services',
  'Retail': 'retail',
  'Healthcare': 'healthcare',
  'Construction': 'construction',
  'Education': 'education',
  'Transportation': 'transportation',
  'Energy': 'energy',
};
