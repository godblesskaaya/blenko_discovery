// framework.js
// Sprint 1: Framework content hardcoded here.
// Future: All content fetched from backend DB keyed by framework_version.

export const FRAMEWORK_VERSION = '1.0.0'

export const DIMENSION_META = {
  competitive_awareness: {
    key: 'competitive_awareness',
    label: 'Competitive Awareness',
    shortLabel: 'D1',
    index: 1,
    maxScore: 10,
    tiers: [
      { key: 'low', label: 'Low Awareness', range: [0, 3], color: 'red' },
      { key: 'emerging', label: 'Emerging Awareness', range: [4, 6], color: 'amber' },
      { key: 'high', label: 'High Awareness', range: [7, 10], color: 'green' },
    ],
    openingQuestion:
      'How would you describe your position in the market right now — are you where you want to be, or is there ground you feel you should be gaining?',
    positioningMoment:
      'Businesses that close competitive gaps address brand and systems together — no single lever moves the needle as fast as both.',
  },
  brand_gap: {
    key: 'brand_gap',
    label: 'Brand Perception Gap',
    shortLabel: 'D2',
    index: 2,
    maxScore: 12,
    tiers: [
      { key: 'low', label: 'No Perceived Gap', range: [0, 4], color: 'red' },
      { key: 'emerging', label: 'Emerging Gap Awareness', range: [5, 8], color: 'amber' },
      { key: 'high', label: 'Clear Gap Recognition', range: [9, 12], color: 'green' },
    ],
    openingQuestion:
      "If a potential customer encountered your business for the first time — what impression do you think they'd walk away with?",
    positioningMoment:
      'Craftsmanship differentiator: when quality gaps appear, the solution is a single integrated standard, not patchwork suppliers.',
  },
  is_maturity: {
    key: 'is_maturity',
    label: 'Operational & IS Maturity',
    shortLabel: 'D3',
    index: 3,
    maxScore: 14,
    tiers: [
      { key: 'low', label: 'Low IS Maturity Awareness', range: [0, 4], color: 'red' },
      { key: 'emerging', label: 'Emerging IS Pain', range: [5, 9], color: 'amber' },
      { key: 'high', label: 'Active IS Pain / Readiness', range: [10, 14], color: 'green' },
    ],
    openingQuestion:
      'On the operational side — how well do your current tools and systems support the way your team actually works day to day? Are they an asset or getting in the way?',
    positioningMoment:
      'IS infrastructure directly affects brand experience — customers feel slow responses, broken portals, and inconsistent communication as a reflection of how you run your business.',
  },
  cost_of_status_quo: {
    key: 'cost_of_status_quo',
    label: 'Cost of Status Quo',
    shortLabel: 'D4',
    index: 4,
    maxScore: 14,
    tiers: [
      { key: 'low', label: 'Low Cost Awareness', range: [0, 4], color: 'red' },
      { key: 'emerging', label: 'Emerging Urgency', range: [5, 9], color: 'amber' },
      { key: 'high', label: 'Genuine Urgency Established', range: [10, 14], color: 'green' },
    ],
    openingQuestion:
      "Based on everything you've shared — if nothing changes over the next 12 months, what do you think that looks like for your business?",
    positioningMoment:
      "ROI framing: brand and IS addressed together generates compounding returns — not isolated wins from isolated fixes.",
  },
}

export const SIGNALS = {
  competitive_awareness: [
    {
      id: 'S1_competitor_awareness',
      label: 'S1: Competitor Awareness',
      description: 'Prospect can name competitors and describe what they are doing.',
    },
    {
      id: 'S2_brand_perception_sensitivity',
      label: 'S2: Brand Perception Sensitivity',
      description: 'Prospect shows awareness that customer perception matters to outcomes.',
    },
    {
      id: 'S3_loss_attribution',
      label: 'S3: Loss Attribution',
      description: 'Prospect can identify why they have lost business or opportunities.',
    },
    {
      id: 'S4_is_competitive_awareness',
      label: 'S4: IS Competitive Awareness',
      description: 'Prospect recognises IS/infrastructure as a competitive lever.',
    },
    {
      id: 'S5_emotional_engagement',
      label: 'S5: Emotional Engagement',
      description: 'Prospect shows emotional investment in their competitive position.',
    },
  ],
  brand_gap: [
    {
      id: 'S1_self_awareness_brand_gap',
      label: 'S1: Self-Awareness of Brand Gap',
      description: 'Prospect acknowledges a gap between intended and perceived brand.',
    },
    {
      id: 'S2_physical_presentation_concern',
      label: 'S2: Physical Presentation Concern',
      description: 'Prospect expresses concern about physical/apparel brand presentation.',
    },
    {
      id: 'S3_digital_presence_dissatisfaction',
      label: 'S3: Digital Presence Dissatisfaction',
      description: 'Prospect is dissatisfied with their digital presence or website.',
    },
    {
      id: 'S4_cross_touchpoint_consistency',
      label: 'S4: Cross-Touchpoint Consistency',
      description: 'Prospect recognises inconsistency across brand touchpoints.',
    },
    {
      id: 'S5_customer_feedback_awareness',
      label: 'S5: Customer Feedback Awareness',
      description: 'Prospect references customer feedback related to brand perception.',
    },
    {
      id: 'S6_emotional_response_gap',
      label: 'S6: Emotional Response to Gap',
      description: 'Prospect shows emotional engagement when brand gap is surfaced.',
    },
  ],
  is_maturity: [
    {
      id: 'S1_operational_friction',
      label: 'S1: Operational Friction',
      description: 'Prospect describes day-to-day friction caused by current tools.',
    },
    {
      id: 'S2_business_management_maturity',
      label: 'S2: Business Management Maturity',
      description: 'Prospect\'s current business management systems are adequate.',
    },
    {
      id: 'S3_web_digital_health',
      label: 'S3: Web & Digital Health',
      description: 'Digital presence and web infrastructure are working well.',
    },
    {
      id: 'S4_network_security_confidence',
      label: 'S4: Network & Security Confidence',
      description: 'Prospect expresses concern or lack of confidence in security.',
    },
    {
      id: 'S5_scalability_concern',
      label: 'S5: Scalability Concern',
      description: 'Prospect questions whether systems will scale with growth.',
    },
    {
      id: 'S6_support_reliability_pain',
      label: 'S6: Support & Reliability Pain',
      description: 'Prospect has experienced unreliable vendor support.',
    },
    {
      id: 'S7_openness_to_is_investment',
      label: 'S7: Openness to IS Investment',
      description: 'Prospect signals willingness to invest in IS improvements.',
    },
  ],
  cost_of_status_quo: [
    {
      id: 'S1_revenue_impact_brand_gap',
      label: 'S1: Revenue Impact of Brand Gap',
      description: 'Prospect links brand gap to lost or at-risk revenue.',
    },
    {
      id: 'S2_productivity_operational_cost',
      label: 'S2: Productivity & Operational Cost',
      description: 'Prospect can quantify operational cost or time lost.',
    },
    {
      id: 'S3_competitive_erosion',
      label: 'S3: Competitive Erosion',
      description: 'Prospect acknowledges competitors are gaining ground over time.',
    },
    {
      id: 'S4_trust_reputation_erosion',
      label: 'S4: Trust & Reputation Erosion',
      description: 'Prospect identifies trust or reputation risk of staying put.',
    },
    {
      id: 'S5_opportunity_cost_delay',
      label: 'S5: Opportunity Cost of Delayed Action',
      description: 'Prospect can articulate what delay is costing them.',
    },
    {
      id: 'S6_emotional_urgency',
      label: 'S6: Emotional Urgency',
      description: 'Prospect expresses genuine urgency — not just intellectual acknowledgement.',
    },
    {
      id: 'S7_timeline_commitment',
      label: 'S7: Timeline Commitment',
      description: 'Prospect references a specific timeframe for action.',
    },
  ],
}

export const PROBES = {
  competitive_awareness: [
    {
      id: 'probe_a',
      label: 'Probe A: Competitor Visibility',
      text: "When you think about competitors in your space — who are they, and what are they doing that you're noticing?",
    },
    {
      id: 'probe_b',
      label: 'Probe B: Decision Influence',
      text: "When a potential customer is deciding between you and a competitor — what do you think influences that decision most?",
    },
    {
      id: 'probe_c',
      label: 'Probe C: Lost Opportunity',
      text: "Have there been opportunities you felt you should have won but didn't? What happened there?",
    },
    {
      id: 'probe_d',
      label: 'Probe D: IS Competitive Awareness',
      text: "On the systems and infrastructure side — do you think that gives you an advantage, or is it more just keeping the lights on?",
    },
  ],
  brand_gap: [
    {
      id: 'probe_a',
      label: 'Probe A: Physical Presentation',
      text: "When a customer or prospect sees your team in person — uniforms, vehicle wraps, signage — what impression does that give them?",
    },
    {
      id: 'probe_b',
      label: 'Probe B: Print & Collateral',
      text: "When you hand someone a business card, a brochure, or a quote — does that material reflect the quality of what you actually deliver?",
    },
    {
      id: 'probe_c',
      label: 'Probe C: Digital Presence',
      text: "If someone searched for your business right now and landed on your website and socials — what would they find?",
    },
    {
      id: 'probe_d',
      label: 'Probe D: Cross-Touchpoint Consistency',
      text: "If someone experienced your business across three different touchpoints — the website, your team in person, a document you sent — would those all feel like the same brand?",
    },
    {
      id: 'probe_e',
      label: 'Probe E: Customer Feedback Awareness',
      text: "Have you ever had a customer comment — positively or negatively — on how your business looks or feels?",
    },
  ],
  is_maturity: [
    {
      id: 'probe_a',
      label: 'Probe A: Communication & Collaboration',
      text: "How does your team communicate day-to-day — what tools are you using and is that working?",
    },
    {
      id: 'probe_b',
      label: 'Probe B: Business Management Systems',
      text: "When it comes to managing quotes, jobs, invoicing, and customer records — what does that process look like?",
    },
    {
      id: 'probe_c',
      label: 'Probe C: Digital Presence & Web',
      text: "Is your website actively generating leads or enquiries, or is it more of a digital brochure?",
    },
    {
      id: 'probe_d',
      label: 'Probe D: Network & Security',
      text: "On the IT infrastructure side — are you confident your systems and data are secure and reliable?",
    },
    {
      id: 'probe_e',
      label: 'Probe E: Scalability',
      text: "If the business doubled in size in the next two years — would your current systems handle that, or would they become a bottleneck?",
    },
    {
      id: 'probe_f',
      label: 'Probe F: Vendor & Support Dependency',
      text: "When something goes wrong with your tech or systems — who do you call, and how does that usually go?",
    },
  ],
  cost_of_status_quo: [
    {
      id: 'probe_a',
      label: 'Probe A: Revenue Impact of Brand Gap',
      text: "If the brand gap we talked about earlier is costing you even one or two contracts a year — what does that represent in revenue?",
    },
    {
      id: 'probe_b',
      label: 'Probe B: Productivity & Operational Cost',
      text: "If you had to put a number on the hours your team loses each week to workarounds or system friction — what would that add up to?",
    },
    {
      id: 'probe_c',
      label: 'Probe C: Competitive Erosion',
      text: "Over the next twelve months — if competitors continue investing in brand and systems while you stay where you are — where does that leave you?",
    },
    {
      id: 'probe_d',
      label: 'Probe D: Trust & Reputation Erosion',
      text: "Is there a risk that the perception gap compounds over time — that customers who haven't experienced your quality yet form a view before they give you the chance?",
    },
    {
      id: 'probe_e',
      label: 'Probe E: Opportunity Cost of Delayed Action',
      text: "If you address this in eighteen months rather than now — what's the cost of that gap in time?",
    },
  ],
}

export const REFRAMES = {
  competitive_awareness: [
    {
      id: 'rf_ca_1',
      label: 'Prospect dismisses competition',
      text: "Competition often works silently — customers make decisions based on perception before they even engage. It's rarely about the product alone.",
    },
    {
      id: 'rf_ca_2',
      label: 'Prospect thinks brand is fine',
      text: "We're often the last ones to see the gap because we're too close to it. What customers experience versus what we intend can be quite different.",
    },
    {
      id: 'rf_ca_3',
      label: 'Prospect dismisses IS',
      text: "Internal systems create an external experience — slow responses, inconsistent communication, limited digital presence — customers feel all of that.",
    },
  ],
  brand_gap: [
    {
      id: 'rf_bg_1',
      label: 'Brand gap as success problem',
      text: "The businesses with the biggest perception gaps are often the ones delivering the highest quality — they've invested in the work and the brand hasn't kept pace. It's a sign of a good business that outgrew its branding.",
    },
    {
      id: 'rf_bg_2',
      label: 'Physical branding undervalued',
      text: "People make trust judgments in seconds — before a word is spoken. Physical presentation is doing silent work at every interaction, whether you're managing it or not.",
    },
    {
      id: 'rf_bg_3',
      label: 'Digital treated as separate',
      text: "Customers don't experience your website and physical brand as separate things. They move between them and form a single impression. A disconnect erodes trust subtly.",
    },
    {
      id: 'rf_bg_4',
      label: 'Inconsistency accepted',
      text: "Inconsistency sends an unintended message — it suggests different parts of the business operate independently, which makes customers wonder which version of you they'll actually get.",
    },
  ],
  is_maturity: [
    {
      id: 'rf_is_1',
      label: 'Systems are fine',
      text: "Systems feel fine until they don't — and by the time the problem is obvious, it's usually costing more to fix than it would have to prevent.",
    },
    {
      id: 'rf_is_2',
      label: 'Disconnected tools',
      text: "Disconnected systems create invisible costs — time spent moving data manually, errors from duplicate records, decisions made on incomplete pictures.",
    },
    {
      id: 'rf_is_3',
      label: 'IS not a competitive factor',
      text: "Competitors operating on integrated systems are responding faster, deciding on better data, and spending less time on administration. That gap compounds over time.",
    },
    {
      id: 'rf_is_4',
      label: 'Fear of disruption',
      text: "The fear of disruption from upgrading is completely understandable. But what causes the horror stories is poorly managed implementation, not implementation itself. A well-planned transition is far less disruptive than people expect.",
    },
    {
      id: 'rf_is_5',
      label: 'Brand-IS connection missing',
      text: "IS infrastructure directly affects brand experience — slow email responses, a website that breaks, a portal that doesn't work — customers experience all of that as a reflection of how you run your business.",
    },
  ],
  cost_of_status_quo: [
    {
      id: 'rf_csq_1',
      label: 'Minimising inaction cost',
      text: "Status quo costs are invisible on the balance sheet but very real in the business. You won't see a line item for lost trust or missed opportunities — but they're there.",
    },
    {
      id: 'rf_csq_2',
      label: 'Will address eventually',
      text: "Every month of delay is a month where competitors are gaining ground. Eventually has a cost that's easy to underestimate because it accumulates quietly.",
    },
    {
      id: 'rf_csq_3',
      label: 'Investment framed as cost',
      text: "The more useful frame is rate of return. If addressing these gaps generates even a 10% improvement in conversion, retention, or operational efficiency — what does that return look like against the investment?",
    },
    {
      id: 'rf_csq_4',
      label: 'Overwhelmed by where to start',
      text: "You don't have to solve everything at once. The most effective approach is to identify the highest-cost gap first, address that with precision, then build from there. Small strategic moves compound over time.",
    },
  ],
}

export const SCORE_TRIGGERS = {
  competitive_awareness: {
    low: {
      label: 'Low Awareness — Deploy Reframes',
      instruction:
        'Deploy Reframes 1 & 2. Do not advance to deep qualification. Flag for longer sales cycle. Awareness-building is the priority.',
    },
    emerging: {
      label: 'Emerging Awareness — Probe Deeper',
      instruction:
        'Probe C and D are high priority if not yet used. Transition to D2 — brand gap will deepen urgency.',
    },
    high: {
      label: 'High Awareness — Strong Foundation',
      instruction:
        'Strong foundation. Move efficiently. Flag cross-sell opportunity. Prospect is open to both branding and IS interventions.',
    },
  },
  brand_gap: {
    low: {
      label: 'No Perceived Gap — Redirect',
      instruction:
        'Do not push on brand gap. Deploy Reframe 1. Return to this dimension after D3 — IS pain may be the better entry point.',
    },
    emerging: {
      label: 'Emerging Gap Awareness — High Leverage',
      instruction:
        'High leverage moment. Probe D if not yet asked. Transition to D3 with momentum.',
    },
    high: {
      label: 'Clear Gap Recognition — Strong Signal',
      instruction:
        'Strong signal. Flag embroidery, print, and digital services. Probe E if not yet asked. Advance to D3 with high confidence.',
    },
  },
  is_maturity: {
    low: {
      label: 'Low IS Maturity Awareness',
      instruction:
        'Do not push IS solutions. Deploy Reframe 1 (preventive thinking) and Reframe 3 (competitive angle). Flag for IS education track.',
    },
    emerging: {
      label: 'Emerging IS Pain — High Potential',
      instruction:
        'High-potential IS opportunity. Probe B and F highest priority. Flag ERP/CRM and IT consulting. Use Reframe 2 to make invisible costs visible.',
    },
    high: {
      label: 'Active IS Pain / Readiness — Strong IS Qualification',
      instruction:
        'Strong IS qualification. Flag full IS assessment. Schedule technical discovery follow-up alongside commercial conversation.',
    },
  },
  cost_of_status_quo: {
    low: {
      label: 'Low Cost Awareness — Do Not Advance',
      instruction:
        'Do not advance to recommendation. Deploy Reframes 1 and 3. Propose complimentary brand and IS audit as low-risk next step. Flag as medium-term nurture.',
    },
    emerging: {
      label: 'Emerging Urgency — Critical Moment',
      instruction:
        "Probe E is critical if not yet used. Deploy Reframe 2 if in 'eventually' mode. If urgency solidifies, advance to D5. Flag as high-potential short window.",
    },
    high: {
      label: 'Genuine Urgency — Prospect Ready',
      instruction:
        "Prospect is psychologically ready. Note highest-cost areas as anchors for D5. Do not linger — urgency at this level needs forward momentum. Flag as hot.",
    },
  },
}

export const QUALIFICATION_GRADES = [
  { key: 'unqualified', label: 'Unqualified', range: [0, 12], stage: 'Lead — Awareness' },
  { key: 'developing', label: 'Developing', range: [13, 25], stage: 'Opportunity — Qualification' },
  { key: 'qualified', label: 'Qualified', range: [26, 40], stage: 'Opportunity — Needs Analysis' },
  { key: 'hot', label: 'Hot', range: [41, 50], stage: 'Opportunity — Proposal' },
]

export function getQualificationGrade(score) {
  for (const grade of QUALIFICATION_GRADES) {
    if (score >= grade.range[0] && score <= grade.range[1]) return grade.key
  }
  return 'unqualified'
}

export function getDimensionTier(dimensionKey, score) {
  const meta = DIMENSION_META[dimensionKey]
  if (!meta) return null
  for (const tier of meta.tiers) {
    if (score >= tier.range[0] && score <= tier.range[1]) return tier
  }
  return meta.tiers[0]
}

export const DIMENSIONS_ORDER = [
  'competitive_awareness',
  'brand_gap',
  'is_maturity',
  'cost_of_status_quo',
]

export const BUSINESS_TYPES = [
  { value: 'service', label: 'Service' },
  { value: 'trade', label: 'Trade' },
  { value: 'retail', label: 'Retail' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'hospitality', label: 'Hospitality' },
  { value: 'professional', label: 'Professional' },
  { value: 'other', label: 'Other' },
]

export const SIZE_TIERS = [
  { value: 'micro', label: 'Micro', description: '1–5 employees' },
  { value: 'small', label: 'Small', description: '6–25 employees' },
  { value: 'medium', label: 'Medium', description: '26–100 employees' },
  { value: 'large', label: 'Large', description: '100+ employees' },
]

export const GROWTH_STAGES = [
  { value: 'early_growth', label: 'Early Growth' },
  { value: 'active_growth', label: 'Active Growth' },
  { value: 'scaling', label: 'Scaling' },
  { value: 'established', label: 'Established' },
  { value: 'consolidating', label: 'Consolidating' },
]

export const GEOGRAPHIC_SCOPES = [
  { value: 'local', label: 'Local' },
  { value: 'regional', label: 'Regional' },
  { value: 'national', label: 'National' },
  { value: 'multi_site', label: 'Multi-Site' },
]

export const VENDOR_STATUSES = [
  { value: 'none', label: 'No Current Vendors' },
  { value: 'ad_hoc', label: 'Ad Hoc / Sporadic' },
  { value: 'established', label: 'Established (Happy)' },
  { value: 'unhappy', label: 'Established (Unhappy)' },
]

export const GROWTH_AMBITIONS = [
  { value: 'high', label: 'High Growth Target' },
  { value: 'moderate', label: 'Moderate / Steady' },
  { value: 'maintenance', label: 'Maintenance Mode' },
]

export const TRIGGER_CATEGORIES = [
  { value: 'new_contract', label: 'New Contract Won' },
  { value: 'rebranding', label: 'Rebranding Initiative' },
  { value: 'system_failure', label: 'System / Tech Failure' },
  { value: 'competitor_move', label: 'Competitor Move' },
  { value: 'new_hire', label: 'New Hire / Leadership Change' },
  { value: 'upcoming_event', label: 'Upcoming Event / Deadline' },
  { value: 'growth_pressure', label: 'Growth Pressure' },
  { value: 'vendor_dissatisfaction', label: 'Vendor Dissatisfaction' },
  { value: 'referral', label: 'Referral / Recommendation' },
  { value: 'other', label: 'Other' },
]
