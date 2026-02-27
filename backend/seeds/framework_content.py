"""
Blenko Discovery Framework Content Seed Script.
Seeds all 4 scored dimensions with:
  - Dimension metadata (opening question, positioning moment, tier thresholds)
  - Signals (S1–S7 per dimension)
  - Probes (A–F per dimension)
  - Reframes (from Appendix 12.1)
  - Trigger instructions (per tier per dimension)

Run: python -m seeds.framework_content
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from sqlalchemy.orm import Session
from database import SessionLocal
from models.database import (
    FrameworkDimension, FrameworkSignal,
    FrameworkProbe, FrameworkReframe, FrameworkTrigger,
)


VERSION = "1.0.0"


DIMENSIONS = [
    {
        "dimension_name": "competitive_awareness",
        "dimension_label": "Dimension 1 — Competitive Awareness",
        "max_score": 10,
        "opening_question": (
            "How would you describe your position in the market right now — "
            "are you where you want to be, or is there ground you feel you should be gaining?"
        ),
        "positioning_moment": (
            "Businesses that close competitive gaps address brand and systems together."
        ),
        "tier_thresholds": {
            "low": [0, 3],
            "emerging": [4, 6],
            "high": [7, 10],
        },
    },
    {
        "dimension_name": "brand_gap",
        "dimension_label": "Dimension 2 — Brand Perception Gap",
        "max_score": 12,
        "opening_question": (
            "If a potential customer encountered your business for the first time — "
            "what impression do you think they'd walk away with?"
        ),
        "positioning_moment": (
            "Craftsmanship differentiator on quality gap. "
            "Integration differentiator on cross-touchpoint inconsistency."
        ),
        "tier_thresholds": {
            "low": [0, 4],
            "emerging": [5, 8],
            "high": [9, 12],
        },
    },
    {
        "dimension_name": "is_maturity",
        "dimension_label": "Dimension 3 — Operational & IS Maturity",
        "max_score": 14,
        "opening_question": (
            "On the operational side — how well do your current tools and systems support "
            "the way your team actually works day to day? Are they an asset or getting in the way?"
        ),
        "positioning_moment": (
            "When IS maturity gap surfaces — unexpected capability reveal."
        ),
        "tier_thresholds": {
            "low": [0, 4],
            "emerging": [5, 9],
            "high": [10, 14],
        },
    },
    {
        "dimension_name": "cost_of_status_quo",
        "dimension_label": "Dimension 4 — Cost of Status Quo",
        "max_score": 14,
        "opening_question": (
            "Based on everything you've shared — if nothing changes over the next 12 months, "
            "what do you think that looks like for your business?"
        ),
        "positioning_moment": (
            "ROI framing of multi-pillar approach — 'brand and IS addressed together "
            "generates compounding returns rather than isolated ones.'"
        ),
        "tier_thresholds": {
            "low": [0, 4],
            "emerging": [5, 9],
            "high": [10, 14],
        },
    },
    {
        "dimension_name": "solution_routing",
        "dimension_label": "Dimension 5 — Solution Routing & Next Steps",
        "max_score": 0,
        "opening_question": None,
        "positioning_moment": (
            "Based on everything we've covered today — the competitive gaps, the brand "
            "presentation opportunities, the IS infrastructure picture — I don't think you "
            "need a vendor. I think you need a strategic partner who can look at all of this "
            "together and build a roadmap that's integrated. That's specifically what we're "
            "structured to do."
        ),
        "tier_thresholds": None,
    },
]


SIGNALS = {
    "competitive_awareness": [
        ("S1", "competitor_awareness",
         "Prospect articulates who their competitors are and what they are doing"),
        ("S2", "brand_perception_sensitivity",
         "Prospect shows awareness that customer perception of their brand matters"),
        ("S3", "loss_attribution",
         "Prospect can identify why they have lost business to competitors"),
        ("S4", "is_competitive_awareness",
         "Prospect recognises information systems or infrastructure as a competitive factor"),
        ("S5", "emotional_engagement",
         "Prospect shows emotional investment in their competitive position"),
    ],
    "brand_gap": [
        ("S1", "self_awareness_of_brand_gap",
         "Prospect acknowledges a gap between how they present and how they want to be seen"),
        ("S2", "physical_presentation_concern",
         "Concern or dissatisfaction with physical brand elements (uniforms, signage, apparel)"),
        ("S3", "digital_presence_dissatisfaction",
         "Dissatisfaction with website, social media presence, or digital identity"),
        ("S4", "cross_touchpoint_consistency",
         "Awareness that different touchpoints give different impressions of the business"),
        ("S5", "customer_feedback_awareness",
         "Prospect references customer feedback or observations about their brand"),
        ("S6", "emotional_response_to_gap",
         "Emotional reaction when brand gap is surfaced — frustration, embarrassment, urgency"),
    ],
    "is_maturity": [
        ("S1", "operational_friction",
         "Specific examples of operational inefficiency caused by current tools"),
        ("S2", "business_management_maturity",
         "Awareness of gap in business management systems (ERP, CRM, quoting, inventory)"),
        ("S3", "web_and_digital_health",
         "Concern about website performance, hosting reliability, or digital infrastructure"),
        ("S4", "network_and_security_confidence",
         "Concerns about network security, data protection, or IT reliability"),
        ("S5", "scalability_concern",
         "Awareness that current systems will not scale with business growth"),
        ("S6", "support_and_reliability_pain",
         "Frustration with current IT support or vendor reliability"),
        ("S7", "openness_to_is_investment",
         "Prospect signals willingness to invest in IS improvement"),
    ],
    "cost_of_status_quo": [
        ("S1", "revenue_impact_awareness",
         "Prospect connects brand gap or IS issues to lost revenue or missed deals"),
        ("S2", "productivity_cost_awareness",
         "Prospect acknowledges time or labour cost of working around broken systems"),
        ("S3", "competitive_erosion_concern",
         "Prospect fears falling further behind competitors if nothing changes"),
        ("S4", "trust_and_reputation_risk",
         "Awareness that current gaps are eroding customer trust or business reputation"),
        ("S5", "opportunity_cost_of_delay",
         "Prospect recognises that delayed action has a compounding cost"),
        ("S6", "quantification_willingness",
         "Prospect is willing to assign numbers to the cost of inaction"),
        ("S7", "urgency_expression",
         "Prospect expresses genuine urgency to act — unprompted or after light probing"),
    ],
}


PROBES = {
    "competitive_awareness": [
        ("A", "Competitor Visibility",
         "Who do you see as your main competitors right now — and how would you compare where you are versus where they are?",
         "Tell me more about how you're monitoring what they're doing.",
         None),
        ("B", "Decision Influence",
         "When you lose a piece of business — or when a customer chooses someone else — what reason do they usually give?",
         "And what do you think the real reason is, underneath that?",
         ["executive_sponsor", "champion"]),
        ("C", "Lost Opportunity",
         "Have there been situations recently where you felt you should have won business but didn't — and looking back, what do you think the gap was?",
         None,
         ["executive_sponsor"]),
        ("D", "IS Competitive Awareness",
         "Do you think your competitors' internal systems — how they manage operations, communicate with customers, handle their digital presence — give them any advantage over you?",
         None,
         None),
    ],
    "brand_gap": [
        ("A", "Physical Presentation",
         "When your team is out in the field — at a client site, at an event, in your own premises — what impression do you think your physical presentation gives?",
         "How consistent is that across different contexts?",
         None),
        ("B", "Print & Collateral",
         "What printed materials are you currently using — brochures, business cards, quotes, signage — and how do you feel about the quality and consistency of those?",
         None,
         None),
        ("C", "Digital Presence",
         "If someone Googled your business right now — found your website, maybe your social media — what would they think? Does the digital impression match the quality of what you actually deliver?",
         None,
         None),
        ("D", "Cross-Touchpoint Consistency",
         "If a customer experienced your business across different touchpoints — your team in person, your website, your paperwork — do you think they'd get a consistent impression of who you are?",
         None,
         ["executive_sponsor", "champion"]),
        ("E", "Customer Feedback Awareness",
         "Have customers ever given you direct or indirect feedback about your presentation — either positive or areas where they noticed a gap?",
         None,
         None),
    ],
    "is_maturity": [
        ("A", "Communication & Collaboration",
         "How does your team currently communicate and collaborate — internally and with clients? Are there any friction points there?",
         None,
         None),
        ("B", "Business Management Systems",
         "What are you using to manage the business side — quoting, invoicing, job tracking, inventory? Is that working well or are there gaps?",
         "How much time does your team spend on manual processes that probably shouldn't need to be manual?",
         ["executive_sponsor", "champion"]),
        ("C", "Digital Presence & Web",
         "On the website and digital infrastructure side — is your site performing well, is it easy to update, does it reflect where the business is now?",
         None,
         None),
        ("D", "Network & Security",
         "How confident are you in your network infrastructure and data security? Is that something you've had formally assessed or is it more ad hoc?",
         None,
         ["executive_sponsor"]),
        ("E", "Scalability",
         "If your business grew by 50% over the next two years — would your current systems and infrastructure scale with that, or would they become a bottleneck?",
         None,
         ["executive_sponsor", "champion"]),
        ("F", "Vendor & Support Dependency",
         "Who looks after your IT currently — internal team, external provider, or a bit of both? And how responsive and proactive are they when something goes wrong?",
         None,
         None),
    ],
    "cost_of_status_quo": [
        ("A", "Revenue Impact of Brand Gap",
         "Based on what we've covered on the brand side — how many deals or relationships do you think that perception gap might be costing you per year?",
         "Even a rough figure — if 10% of enquiries dropped off because the first impression didn't match the quality of your actual work, what would that translate to?",
         ["executive_sponsor"]),
        ("B", "Productivity & Operational Cost",
         "If we think about the time your team spends working around your current systems — the manual steps, the double-handling, the things that should be automatic — what's your rough estimate of hours per week?",
         "And what does that translate to in cost?",
         ["executive_sponsor", "champion"]),
        ("C", "Competitive Erosion",
         "If nothing changes over the next 12 months — same brand presentation, same systems — and your competitors continue to invest in theirs, where does that leave you?",
         None,
         None),
        ("D", "Trust & Reputation Erosion",
         "Are there situations where you've felt the gap between your actual quality and how you're perceived has cost you credibility — even subtly?",
         None,
         None),
        ("E", "Opportunity Cost of Delayed Action",
         "If you'd addressed the brand and IS gaps 12 months ago, where do you think the business would be today?",
         None,
         ["executive_sponsor", "champion"]),
    ],
}


REFRAMES = {
    "competitive_awareness": [
        ("Reframe 1", "Prospect dismisses competition",
         "Competition often works silently — customers make decisions based on perception "
         "before they even engage. It's rarely about the product alone."),
        ("Reframe 2", "Prospect thinks brand is fine",
         "We're often the last ones to see the gap because we're too close to it. "
         "What customers experience versus what we intend can be quite different."),
        ("Reframe 3", "Prospect dismisses IS",
         "Internal systems create an external experience — slow responses, inconsistent "
         "communication, limited digital presence — customers feel all of that."),
    ],
    "brand_gap": [
        ("Reframe 1", "Brand gap as success problem",
         "The businesses with the biggest perception gaps are often the ones delivering the "
         "highest quality — they've invested in the work and the brand hasn't kept pace. "
         "It's a sign of a good business that outgrew its branding."),
        ("Reframe 2", "Physical branding undervalued",
         "People make trust judgments in seconds — before a word is spoken. Physical "
         "presentation is doing silent work at every interaction, whether you're managing it or not."),
        ("Reframe 3", "Digital treated as separate",
         "Customers don't experience your website and physical brand as separate things. "
         "They move between them and form a single impression. A disconnect erodes trust subtly."),
        ("Reframe 4", "Inconsistency accepted",
         "Inconsistency sends an unintended message — it suggests different parts of the "
         "business operate independently, which makes customers wonder which version of you "
         "they'll actually get."),
    ],
    "is_maturity": [
        ("Reframe 1", "Systems are fine",
         "Systems feel fine until they don't — and by the time the problem is obvious, it's "
         "usually costing more to fix than it would have to prevent."),
        ("Reframe 2", "Disconnected tools",
         "Disconnected systems create invisible costs — time spent moving data manually, "
         "errors from duplicate records, decisions made on incomplete pictures."),
        ("Reframe 3", "IS not a competitive factor",
         "Competitors operating on integrated systems are responding faster, deciding on "
         "better data, and spending less time on administration. That gap compounds over time."),
        ("Reframe 4", "Fear of disruption",
         "The fear of disruption from upgrading is completely understandable. But what causes "
         "the horror stories is poorly managed implementation, not implementation itself. "
         "A well-planned transition is far less disruptive than people expect."),
        ("Reframe 5", "Brand-IS connection missing",
         "IS infrastructure directly affects brand experience — slow email responses, a website "
         "that breaks, a portal that doesn't work — customers experience all of that as a "
         "reflection of how you run your business."),
    ],
    "cost_of_status_quo": [
        ("Reframe 1", "Minimising inaction cost",
         "Status quo costs are invisible on the balance sheet but very real in the business. "
         "You won't see a line item for lost trust or missed opportunities — but they're there."),
        ("Reframe 2", "Will address eventually",
         "Every month of delay is a month where competitors are gaining ground. Eventually "
         "has a cost that's easy to underestimate because it accumulates quietly."),
        ("Reframe 3", "Investment framed as cost",
         "The more useful frame is rate of return. If addressing these gaps generates even a "
         "10% improvement in conversion, retention, or operational efficiency — what does that "
         "return look like against the investment?"),
        ("Reframe 4", "Overwhelmed by where to start",
         "You don't have to solve everything at once. The most effective approach is to identify "
         "the highest-cost gap first, address that with precision, then build from there. "
         "Small strategic moves compound over time."),
    ],
}


TRIGGERS = {
    "competitive_awareness": {
        "low": {
            "text": (
                "Deploy Reframes 1 & 2. Do not advance to deep qualification. "
                "Flag for longer sales cycle. Awareness-building is the priority."
            ),
            "persona_addendums": {
                "executive_sponsor": "Frame as strategic risk — ask what it would mean if a competitor closes this gap before they do.",
                "champion": "Help them build an internal case around competitive standing. Give them language.",
                "gatekeeper": "Lead with credibility. Avoid pushing — focus on opening doors to pain owners.",
                "end_user": "Extract specific daily friction. Map path to Champion or Exec Sponsor.",
            },
        },
        "emerging": {
            "text": (
                "Probe C and D are high priority if not yet used. "
                "Transition to D2 — brand gap will deepen urgency."
            ),
            "persona_addendums": {
                "executive_sponsor": "Move to ROI framing. Connect competitive standing to business outcomes.",
                "champion": "Give them concrete data points to use internally.",
                "gatekeeper": None,
                "end_user": None,
            },
        },
        "high": {
            "text": (
                "Strong foundation. Move efficiently. Flag cross-sell opportunity. "
                "Prospect is open to both branding and IS interventions."
            ),
            "persona_addendums": {
                "executive_sponsor": "Move to D4 quickly — urgency is there. Keep building.",
                "champion": "Equip them. Ask who else needs to hear this.",
                "gatekeeper": None,
                "end_user": None,
            },
        },
    },
    "brand_gap": {
        "low": {
            "text": (
                "Do not push on brand gap. Deploy Reframe 1. "
                "Return to this dimension after D3 — IS pain may be the better entry point."
            ),
            "persona_addendums": {},
        },
        "emerging": {
            "text": (
                "High leverage moment. Probe D if not yet asked. "
                "Transition to D3 with momentum."
            ),
            "persona_addendums": {},
        },
        "high": {
            "text": (
                "Strong signal. Flag embroidery, print, and digital services. "
                "Probe E if not yet asked. Advance to D3 with high confidence."
            ),
            "persona_addendums": {},
        },
    },
    "is_maturity": {
        "low": {
            "text": (
                "Do not push IS solutions. Deploy Reframe 1 (preventive thinking) and "
                "Reframe 3 (competitive angle). Flag for IS education track."
            ),
            "persona_addendums": {},
        },
        "emerging": {
            "text": (
                "High-potential IS opportunity. Probe B and F highest priority. "
                "Flag ERP/CRM and IT consulting. Use Reframe 2 to make invisible costs visible."
            ),
            "persona_addendums": {},
        },
        "high": {
            "text": (
                "Strong IS qualification. Flag full IS assessment. "
                "Schedule technical discovery follow-up alongside commercial conversation."
            ),
            "persona_addendums": {},
        },
    },
    "cost_of_status_quo": {
        "low": {
            "text": (
                "Do not advance to recommendation. Deploy Reframes 1 and 3. "
                "Propose complimentary brand and IS audit as low-risk next step. "
                "Flag as medium-term nurture."
            ),
            "persona_addendums": {},
        },
        "emerging": {
            "text": (
                "Probe E is critical if not yet used. Deploy Reframe 2 if in 'eventually' mode. "
                "If urgency solidifies, advance to D5. Flag as high-potential short window."
            ),
            "persona_addendums": {},
        },
        "high": {
            "text": (
                "Prospect is psychologically ready. Note highest-cost areas as anchors for D5. "
                "Do not linger — urgency at this level needs forward momentum. Flag as hot."
            ),
            "persona_addendums": {},
        },
    },
}


def seed_all(db: Session):
    print("Seeding framework content...")

    # Wipe existing framework content (idempotent re-seed)
    for model in [FrameworkTrigger, FrameworkReframe, FrameworkProbe, FrameworkSignal, FrameworkDimension]:
        db.query(model).delete()
    db.flush()

    dim_map = {}

    # Seed dimensions
    for dim_data in DIMENSIONS:
        dim = FrameworkDimension(
            dimension_id=uuid.uuid4(),
            framework_version=VERSION,
            **dim_data,
        )
        db.add(dim)
        db.flush()
        dim_map[dim_data["dimension_name"]] = dim
        print(f"  ✓ Dimension: {dim_data['dimension_label']}")

    # Seed signals
    for dim_name, signals in SIGNALS.items():
        dim = dim_map[dim_name]
        for order, (code, name, desc) in enumerate(signals, 1):
            db.add(FrameworkSignal(
                signal_id=uuid.uuid4(),
                dimension_id=dim.dimension_id,
                signal_code=code,
                signal_name=name,
                signal_description=desc,
                max_signal_score=2,
                display_order=order,
                framework_version=VERSION,
            ))
        print(f"  ✓ {len(signals)} signals for {dim_name}")

    # Seed probes
    for dim_name, probes in PROBES.items():
        dim = dim_map[dim_name]
        for order, (label, title, text, follow_up, personas) in enumerate(probes, 1):
            db.add(FrameworkProbe(
                probe_id=uuid.uuid4(),
                dimension_id=dim.dimension_id,
                probe_label=label,
                probe_text=text,
                follow_up_text=follow_up,
                priority_personas=personas,
                display_order=order,
                framework_version=VERSION,
            ))
        print(f"  ✓ {len(probes)} probes for {dim_name}")

    # Seed reframes
    for dim_name, reframes in REFRAMES.items():
        dim = dim_map[dim_name]
        for order, (label, condition, text) in enumerate(reframes, 1):
            db.add(FrameworkReframe(
                reframe_id=uuid.uuid4(),
                dimension_id=dim.dimension_id,
                reframe_label=label,
                reframe_text=text,
                trigger_condition=condition,
                display_order=order,
                framework_version=VERSION,
            ))
        print(f"  ✓ {len(reframes)} reframes for {dim_name}")

    # Seed triggers
    for dim_name, tiers in TRIGGERS.items():
        dim = dim_map[dim_name]
        for tier, content in tiers.items():
            db.add(FrameworkTrigger(
                trigger_id=uuid.uuid4(),
                dimension_id=dim.dimension_id,
                tier=tier,
                trigger_text=content["text"],
                persona_addendums=content.get("persona_addendums", {}),
                framework_version=VERSION,
            ))
        print(f"  ✓ {len(tiers)} triggers for {dim_name}")

    db.commit()
    print("\n✅ Framework content seeded successfully.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_all(db)
    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()
