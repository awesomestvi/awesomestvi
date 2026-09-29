export const navetTypographyTokens = {
  body: 'text-sm leading-6',
  bodyCompact: 'text-sm leading-[21px]',
  helper: 'text-sm leading-5',
  compactHelper: 'text-xs leading-4',
  label: 'text-sm font-medium',
  control: 'text-sm font-medium',
  fieldValue: 'text-sm font-normal leading-5',
  caption: 'text-xs leading-4',
  dense: 'text-xs leading-5',
  compactMetadata: 'text-xs leading-4',
  eyebrow: 'text-xs font-semibold uppercase tracking-[0.16em]',
  titleSm: 'text-sm font-semibold',
  titleMd: 'text-base font-semibold',
  sectionHeading: 'text-lg font-semibold',
  featureHeading: 'text-xl font-semibold tracking-tight',
  pageHeading: 'text-2xl font-semibold tracking-tight',
  // Primary metric displayed on a card (temperature, percentage, count, etc.)
  cardMetricSm: 'text-2xl font-bold leading-none', // small cards and compact metric surfaces
  cardMetricLg: 'text-3xl font-bold leading-none', // medium and standard large cards
  cardMetricXl: 'text-4xl font-semibold leading-none', // hero metric panels inside large cards
} as const;

export const navetRadiusTokens = {
  field: 'rounded-[22px]',
  action: 'rounded-[20px]',
  panelInset: 'rounded-[24px]',
  panel: 'rounded-[28px]',
  pill: 'rounded-full',
} as const;
