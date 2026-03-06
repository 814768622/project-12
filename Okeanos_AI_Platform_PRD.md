# Okeanos AI Platform — Product Requirements Document

**Product Name:** Okeanos AI Platform — Marketing Module
**Version:** 1.0
**Date:** March 2, 2026
**Owner:** Okeanos Ontario Inc.

## Vision Statement

Automate the creation, deployment, optimization, and reporting of marketing campaigns across all digital channels to continuously drive qualified leads at or below the target CPA of $1,000–$2,000 per lead, while reducing manual marketing effort to near-zero — enabling Okeanos Ontario to scale toward 200 pool installations per year through precision targeting, instant engagement, and data-driven budget allocation.

## Feature List

1. [Campaign Creation & Management](#1-campaign-creation--management)
2. [Budget Allocation & Optimization](#2-budget-allocation--optimization)
3. [Audience Targeting & Segmentation](#3-audience-targeting--segmentation)
4. [SEO & Content Automation](#4-seo--content-automation)
5. [Email & SMS Marketing Automation](#5-email--sms-marketing-automation)
6. [Performance Reporting & Analytics](#6-performance-reporting--analytics)

---

# 1. Campaign Creation & Management

## 1. Business Goal (Context)

Eliminate the manual effort of creating, testing, and managing ad campaigns across Google Ads, Meta (Facebook + Instagram), and TikTok by automating creative generation, A/B testing, and posting — so that Joe can focus on closing deals rather than managing ads.

## 2. Roles & Permissions

- **AI System (automated):** Generates ad creatives, runs A/B tests, schedules posts, and manages campaign lifecycle. All actions operate within pre-approved budget limits and brand guidelines.
- **Joe / Owner (human):** Approves total marketing budget, reviews campaign performance, approves or rejects proposed campaign changes above a configurable spend threshold. Can manually pause, start, or edit any campaign.
- **Admin (human):** Configures platform API connections, sets brand guidelines, manages creative asset library, and defines approval workflows.

## 3. Functional Requirements

- [ ] Generate targeted ad creatives (headlines, body copy, CTAs) aligned to ICP segments and seasonal trends
- [ ] Build and deploy campaigns across Google Ads, Meta (Facebook + Instagram), and TikTok from a single interface
- [ ] Auto-create A/B test variants: minimum 2 variants per campaign for headlines, images, and CTAs
- [ ] Declare a winning variant when statistical significance is reached (95% confidence) and auto-pause the loser
- [ ] Schedule posts based on algorithm-driven optimal timing for the target audience (GTA homeowners aged 35–55)
- [ ] Align all ad messaging with the Okeanos brand voice: confident, helpful, straight-talking, no fluff, focus on value (speed + affordability + quality)
- [ ] Support the three pricing tiers in ad messaging: DIY ($20K–$35K), Assisted ($30K–$45K), Full Install ($45K–$75K) — always with "starting from" language and "+HST" disclaimer
- [ ] Tag all campaigns with ICP segment, season, and objective for downstream attribution
- [ ] Maintain a creative asset library with approved pool model photos, 3D renders, installation videos, brochure excerpts, and customer testimonials
- [ ] Auto-rotate creatives every 14 days to prevent ad fatigue, or sooner if CTR drops > 20% from 7-day average
- [ ] Support seasonal campaign templates: spring urgency ("Book now for summer install"), summer showcase ("See our latest installs"), fall planning ("Get ahead for next year"), winter promo ("Early bird pricing")

## 4. Business Rules

- All ad creatives must align with approved brand messaging — no mention of exact pricing without "subject to site review & final scope" disclaimer
- Competitor mentions in ads are prohibited
- No campaign may launch without at least one approved creative variant
- All campaigns must include a clear CTA directing to either the website contact form or the Calendly booking link (`https://calendly.com/joe-okeanos/30min`)
- Ad copy must never promise specific timelines, guarantees, or binding commitments
- A/B tests must run for a minimum of 72 hours before declaring a winner, regardless of statistical significance

## 5. Data Schema

- **Campaign:** { campaign_id, platform [google|meta|tiktok], campaign_name, objective [lead_gen|brand_awareness|retargeting|seasonal_promo], status [active|paused|draft|completed|ab_testing], daily_budget, total_budget, cpa_target, start_date, end_date, icp_segment [residential|landscaper|builder], season_tag, created_by [ai|human], created_at, updated_at }
- **AdCreative:** { creative_id, campaign_id (FK), headline (max 40 chars for Google, max 125 chars for Meta), body_text, image_url, video_url, cta_text, cta_url, variant_label [A|B|C], impressions, clicks, conversions, ctr, cpa, status [active|paused|winner|loser], rotation_started_at, fatigue_flagged (bool) }
- **CreativeAsset:** { asset_id, asset_type [photo|render|video|testimonial|brochure_excerpt], pool_model, file_url, approved (bool), approved_by, tags[], uploaded_at }

## 6. MVP Scope vs Future Expansion

- **MVP:** Manual campaign creation with AI-suggested headlines and body copy; creative asset library; basic A/B testing with manual winner selection; seasonal campaign templates; single-platform launch (Meta first, then Google).
- **Future:** Full API integration with Google Ads, Meta Ads Manager, and TikTok Ads for automated campaign deployment; AI-generated image creatives using pool model renders; video ad auto-generation from installation footage; cross-platform campaign orchestration; automated fatigue detection and creative rotation.

---

# 2. Budget Allocation & Optimization

## 1. Business Goal (Context)

Maximize return on ad spend by dynamically allocating marketing budget across platforms based on real-time CPA and lead quality data, ensuring Okeanos hits the target CPA of $1,000–$2,000 per lead while eliminating wasted spend on underperforming channels.

## 2. Roles & Permissions

- **AI System (automated):** Monitors platform performance in real-time, reallocates budget between platforms, pauses underperformers, and scales high performers — all within pre-set guardrails.
- **Joe / Owner (human):** Sets total weekly/monthly marketing budget. Approves any budget reallocation that exceeds a configurable threshold (e.g., > 20% shift between platforms). Receives alerts on budget anomalies.
- **Admin (human):** Configures budget guardrails, CPA targets by season, and approval thresholds.

## 3. Functional Requirements

- [ ] Set and enforce budget guardrails: minimum and maximum daily spend per platform (e.g., Google min $50/day, Meta min $50/day, TikTok min $25/day)
- [ ] Define CPA targets by season: Spring/Summer (March–August) target $1,000–$1,500; Fall/Winter (September–February) tolerance up to $2,000
- [ ] Monitor CPA per platform in real-time (updated at minimum every 6 hours)
- [ ] Auto-pause campaigns on any platform when CPA exceeds 2x the seasonal target for 3 consecutive days
- [ ] Reallocate budget from paused/underperforming campaigns to top performers within 24 hours
- [ ] Alert Joe via email when any platform CPA exceeds 1.5x target for > 2 consecutive days (early warning)
- [ ] Alert Joe via SMS + email when total weekly spend exceeds 90% of the weekly budget cap
- [ ] Track spend pacing: flag if weekly spend is on track to exceed budget by > 10%, or underperform by > 25%
- [ ] Provide weekly budget optimization recommendations: suggested platform mix for the coming week based on trailing 14-day performance
- [ ] Support manual budget overrides by Joe at any time
- [ ] Log all budget changes (automated and manual) with timestamps, amounts, and reason

## 4. Business Rules

- Total marketing spend must never exceed the approved weekly budget without Joe's explicit written approval
- No single platform may receive more than 60% of total budget unless manually overridden by Joe
- Budget reallocation must preserve minimum daily spend on each active platform (no platform goes to $0 without explicit pause)
- CPA calculations include all ad platform costs but exclude agency or tool fees
- Budget is calculated in CAD
- Seasonal CPA targets auto-switch on March 1 (spring) and September 1 (fall) each year

## 5. Data Schema

- **BudgetAllocation:** { allocation_id, period_type [daily|weekly|monthly], period_start, period_end, platform [google|meta|tiktok|total], allocated_amount_cad, spent_amount_cad, remaining_cad, cpa_actual, cpa_target, status [on_track|over_budget|under_pacing|paused], updated_at }
- **BudgetChange:** { change_id, platform, previous_amount, new_amount, change_type [auto_reallocation|manual_override|auto_pause|auto_scale], reason_text, triggered_by [ai|joe|admin], timestamp }
- **BudgetAlert:** { alert_id, alert_type [cpa_warning|cpa_critical|spend_cap|pacing], platform, threshold_value, current_value, triggered_at, acknowledged_by, acknowledged_at }

## 6. MVP Scope vs Future Expansion

- **MVP:** Manual budget setting per platform with weekly CPA tracking; email alerts when CPA exceeds targets; weekly optimization recommendations generated from platform reporting data; budget change logging.
- **Future:** Real-time API-driven budget reallocation across all platforms; predictive budget optimization using historical conversion data; automated seasonal target switching; multi-currency support; integration with QuickBooks for marketing ROI tracking against revenue.

---

# 3. Audience Targeting & Segmentation

## 1. Business Goal (Context)

Ensure every marketing dollar targets the right prospects by building and maintaining audience segments aligned to Okeanos's four Ideal Customer Profiles — continuously refining targeting based on which leads actually convert, so that lead quality improves over time while CPA decreases.

## 2. Roles & Permissions

- **AI System (automated):** Builds audience segments, creates lookalikes, manages retargeting lists, and refines targeting based on conversion data.
- **Joe / Owner (human):** Reviews audience performance, approves new segment definitions, provides input on ICP changes.
- **Admin (human):** Configures segment parameters, manages platform pixel/tracking setup, and controls data sharing between platforms.

## 3. Functional Requirements

- [ ] Build and maintain primary audience segments based on ICP profiles:
  - **Residential Homeowners:** GTA/Golden Horseshoe, ages 35–55, household income $150K+, homeowners with detached/semi/townhomes, interests in home improvement, outdoor living, family recreation
  - **Empty Nesters:** Same geography, ages 55+, interests in property value, lifestyle upgrades, wellness
  - **Landscaping Companies:** Southern Ontario, business owners/managers at companies with $500K–$5M revenue, interests in landscaping, outdoor construction, subcontracting
  - **Pool Builders:** Southern Ontario, small-medium pool builders, interests in fiberglass pools, pool equipment, supplier partnerships
- [ ] Create lookalike audiences on Meta and Google based on Won leads from CRM data (minimum seed list: 50 Won leads)
- [ ] Build retargeting audiences:
  - Website visitors who viewed pool model pages but did not submit a form (7-day, 14-day, 30-day windows)
  - Form abandoners who started but did not complete the contact form
  - Engaged leads (score 30–49) who were not yet qualified
  - Past customers for referral program promotions
- [ ] Exclude audiences: existing Won leads (active customers), Lost leads marked "Not Interested", and leads outside service area
- [ ] Refresh audience lists weekly from CRM data sync
- [ ] Track and report audience performance: conversion rate, CPA, and lead quality score by segment
- [ ] Identify emerging audience patterns: if a new demographic or geography is converting at above-average rates, flag for review

## 4. Business Rules

- Residential homeowner targeting is the primary segment — must always receive the largest budget share unless manually overridden
- B2B segments (landscapers, builders) require separate ad creatives and landing pages — never mixed with residential messaging
- Lookalike audiences require a minimum seed list of 50 records; do not build lookalikes from fewer records
- Retargeting audiences must respect CASL opt-outs — exclude any prospects who have unsubscribed from communications
- Audience data from CRM must be hashed before uploading to ad platforms (email/phone SHA-256)
- No audience segment may target users under age 25 (pool buyers skew 35+)

## 5. Data Schema

- **AudienceSegment:** { segment_id, segment_name, platform [google|meta|tiktok|all], icp_type [residential|empty_nester|landscaper|builder], targeting_criteria_json, seed_list_size, lookalike_size, status [active|paused|draft], created_at, last_refreshed_at }
- **RetargetingList:** { list_id, list_name, trigger [page_view|form_abandon|engaged_not_qualified|past_customer], lookback_days [7|14|30|90], platform, audience_size, exclusions_applied[], updated_at }
- **AudiencePerformance:** { perf_id, segment_id (FK), period_start, period_end, impressions, clicks, conversions, cpa, avg_lead_score, conversion_rate }

## 6. MVP Scope vs Future Expansion

- **MVP:** Manual audience definition on Meta and Google based on ICP demographics; basic website retargeting (all visitors, 30-day window); manual CRM list upload for lookalikes quarterly.
- **Future:** Automated weekly CRM-to-platform audience sync; dynamic lookalike audience building from fresh conversion data; AI-driven segment discovery; form abandoner retargeting; cross-platform audience suppression; geo-fencing for service area targeting; weather-triggered campaign activation (target prospects during heat waves).

---

# 4. SEO & Content Automation

## 1. Business Goal (Context)

Improve organic search visibility and website engagement for Okeanos Ontario so that a growing share of leads come from unpaid search traffic — reducing dependence on paid ads and lowering overall CPA. Also optimize for LLM-based search (AI overviews, ChatGPT recommendations) which is increasingly driving consumer discovery.

## 2. Roles & Permissions

- **AI System (automated):** Analyzes SEO performance, generates content suggestions, drafts blog posts, and monitors competitor rankings. Content is published either automatically with a 24-hour review window or after manual approval.
- **Joe / Owner (human):** Reviews and approves blog content before publication (or within the 24-hour review window for auto-published content). Provides input on priority topics.
- **Admin (human):** Manages WordPress publishing credentials, configures content calendar, and sets auto-publish rules.

## 3. Functional Requirements

- [ ] Perform monthly SEO audit of okeanosontario.com: page rankings, keyword positions, page speed scores, mobile usability, time-on-site, click-through rates from search
- [ ] Identify top 20 target keywords for Okeanos (e.g., "fiberglass pool Ontario", "pool installer GTA", "affordable pool Toronto", "backyard pool cost Ontario")
- [ ] Monitor rankings for all target keywords weekly; alert when any keyword drops > 5 positions
- [ ] Generate and publish 2–4 SEO-optimized blog posts per month based on: trending keywords, seasonal relevance, competitor content gaps, and common prospect questions from the Knowledge Base
- [ ] Blog post requirements: 800–1,500 words, include target keyword in title and first 100 words, include at least 1 internal link and 1 pool model image, include a CTA to the contact form or Calendly booking
- [ ] Optimize website metadata (title tags, meta descriptions, H1/H2 structure) for top 20 target keywords across all main pages
- [ ] Monitor competitor online positioning: track top 5 competitors' keyword rankings, content output, and backlink profiles monthly
- [ ] Generate monthly competitor analysis report with actionable recommendations (e.g., "Competitor X ranks #1 for 'pool cost Ontario' — recommended action: publish a pricing guide blog post targeting this keyword")
- [ ] Optimize for LLM-based search: ensure website content uses structured data (FAQ schema, LocalBusiness schema, Product schema) to increase visibility in AI overviews and conversational search results
- [ ] Auto-generate social media posts (Instagram, Facebook) from published blog content: extract key points, create 2–3 social posts per blog with images and hashtags

## 4. Business Rules

- All blog content must be factually accurate and consistent with Okeanos product information, pricing, and warranty details
- Blog posts must never include competitor names or comparative pricing
- Auto-published content can be retracted by Joe within 24 hours; after 24 hours, edits require a new post
- SEO changes to existing website pages (metadata, headings) require Joe's approval before implementation
- Social media posts must use the Okeanos brand voice and include the company handle/tag
- No AI-generated content may claim to be written by a specific person (e.g., "By Joe") — use "Okeanos Team" as author

## 5. Data Schema

- **SEOAudit:** { audit_id, audit_date, overall_score, page_speed_desktop, page_speed_mobile, keywords_tracked, keywords_in_top_10, keywords_in_top_3, avg_time_on_site_seconds, bounce_rate, recommendations_json }
- **KeywordRanking:** { ranking_id, keyword, current_position, previous_position, position_change, search_volume_monthly, difficulty_score, tracked_since, last_checked_at }
- **BlogPost:** { post_id, title, slug, target_keyword, word_count, status [draft|review|published|retracted], wordpress_post_id, published_at, page_views, avg_time_on_page, conversions_attributed, author_display_name }
- **CompetitorReport:** { report_id, report_month, competitors_analyzed[], keyword_gaps_json, content_gaps_json, backlink_comparison_json, recommendations_text, generated_at }

## 6. MVP Scope vs Future Expansion

- **MVP:** One-time SEO audit with recommendations document; manual keyword tracking via free tools (Google Search Console); 1–2 blog posts per month drafted by AI and manually reviewed/published; monthly competitor keyword check.
- **Future:** Automated weekly keyword tracking with position alerts; auto-publishing to WordPress with 24-hour review window; AI-generated social media posts from blog content; structured data auto-implementation; competitor monitoring with automated alerts; backlink opportunity identification; video SEO optimization for YouTube/TikTok content.

---

# 5. Email & SMS Marketing Automation

## 1. Business Goal (Context)

Nurture leads that are not yet qualified (score < 50) through automated, personalized email and SMS sequences that educate prospects, build trust, and bring them back when they are ready to buy — while also maintaining engagement with existing customers for referrals and repeat business.

## 2. Roles & Permissions

- **AI System (automated):** Manages sequence enrollment, sends scheduled messages, personalizes content based on lead data, and tracks engagement metrics.
- **Joe / Owner (human):** Approves all email/SMS templates before activation. Can manually enroll or remove leads from sequences. Reviews engagement reports.
- **Admin (human):** Configures sequences, manages template library, sets sending schedules, and ensures CASL compliance settings.

## 3. Functional Requirements

### 5.1 Nurture Sequences (Leads Score < 50)
- [ ] **Budget Education Sequence:** Triggered when a lead is tagged "budget-mismatch." Send planning guide (Day 0), seasonal promo notification (Day 7), financing options overview (Day 14), re-engagement offer (Day 30)
- [ ] **General Nurture Sequence:** For new leads not yet qualified. Pool buying guide (Day 1), Okeanos story + differentiators (Day 3), customer testimonial spotlight (Day 7), pool model showcase (Day 14), "Ready to talk?" invitation (Day 21)
- [ ] **Seasonal Re-Engagement:** November 1 annual email to all unconverted leads: "Plan ahead for next summer" + early bird promotion
- [ ] **Lost Lead Reactivation:** For leads marked Lost > 90 days ago. "Things have changed" email with updated pricing or new models, sent once per quarter

### 5.2 Pipeline-Stage Sequences (Leads Score >= 50)
- [ ] **Post-First-Contact:** Confirmation of next steps + link to pool model gallery + FAQ document (sent within 1 hour of first contact)
- [ ] **Discovery Confirmation:** Date/time confirmation + request for site photos + "what to expect" guide (sent immediately upon Calendly booking)
- [ ] **Discovery Reminder:** 24-hour and 1-hour reminders with rescheduling link
- [ ] **Post-Discovery:** Summary of discussion + next steps + preparation checklist (sent within 2 hours of call completion)
- [ ] **Post-Quote Follow-Up:** Day 2 (recap + key highlights), Day 5 (testimonial video + customer story), Day 10 (installation video + "what to expect" guide + calendar spot hold offer)
- [ ] **No-Reply Sequence:** Day 1, Day 3, Day 7, Day 14 follow-ups with escalating urgency but always respectful tone

### 5.3 Post-Sale Sequences (Won Leads / Customers)
- [ ] **Pre-Install:** Pool school scheduling reminder + site preparation checklist (sent 7 days before install date)
- [ ] **Post-Install:** Day 1 (congratulations + maintenance quick-start guide), Day 7 (pool school follow-up + chemical tips), Day 30 (how's it going check-in + Google review request)
- [ ] **Referral Program:** "Know someone who wants a pool?" email with referral incentive, sent 60 days post-install
- [ ] **Seasonal Maintenance:** Spring opening tips (March), summer maintenance reminders (June), fall closing guide (September), winter care checklist (November)

### 5.4 SMS Automation
- [ ] **Initial SMS (Web Lead):** "Hi [Name], it's Joe from Okeanos Fiberglass Pools! Thank you for your inquiry! We look forward to helping you with your request. Do you mind if I ask 3 quick questions to check access, budget, and timing, then schedule you in with a call?" — sent within 5 minutes of form submission
- [ ] **Appointment Reminder SMS:** "Hi [Name], just a reminder about your Okeanos discovery call tomorrow at [Time]. Looking forward to speaking with you! If you need to reschedule: [Reschedule Link]"
- [ ] **Quote Follow-Up SMS (Day 5):** "Checking in on your quote — any questions about models, timelines, or access? I can walk you through trade-offs live and lock a tentative spot on the install calendar."
- [ ] All SMS messages must include CASL-compliant opt-out instruction: "Reply STOP to unsubscribe"
- [ ] SMS sending window: 9 AM – 8 PM ET only (no messages outside business hours)
- [ ] Maximum 1 SMS per lead per 48-hour period (to avoid spamming)

### 5.5 Personalization & Template Variables
- [ ] Support dynamic variables in all templates: [Name], [First Name], [Date/Time], [Pool Model], [Budget Range], [Calendly Link], [Reschedule Link], [Referral Link]
- [ ] Personalize pool model images based on lead's stated interest (if known)
- [ ] Adjust messaging tone for B2B leads (landscapers, builders) vs residential consumers

## 4. Business Rules

- All email/SMS templates must be approved by Joe before being activated in any sequence
- CASL compliance is mandatory: every email includes an unsubscribe link; every SMS includes "Reply STOP"; all opt-outs are honored within 24 hours
- A lead who unsubscribes from one channel (email or SMS) is only removed from that channel — not both — unless they request removal from all communications
- No lead may receive more than 3 emails per week from all sequences combined
- SMS is reserved for high-value touchpoints only: initial contact, appointment reminders, and quote follow-ups
- All sent communications are logged in the CRM as activities on the lead record
- Sequences pause automatically when a lead advances to the next pipeline stage (to avoid conflicting messages)

## 5. Data Schema

- **Sequence:** { sequence_id, sequence_name, trigger [budget_mismatch|general_nurture|seasonal|lost_reactivation|post_contact|discovery_confirm|post_discovery|post_quote|no_reply|post_sale|referral|maintenance], target_segment, status [active|paused|draft], created_at }
- **SequenceStep:** { step_id, sequence_id (FK), step_order, delay_days, channel [email|sms], template_id (FK), send_time_preference [morning|afternoon|any] }
- **Template:** { template_id, template_name, channel [email|sms], subject_line (email only), body_text, variables_used[], version, approved_by, approved_at, status [draft|approved|active|retired] }
- **SequenceEnrollment:** { enrollment_id, lead_id (FK), sequence_id (FK), enrolled_at, current_step, status [active|completed|paused|unenrolled], unenrolled_reason }
- **MessageSent:** { message_id, enrollment_id (FK), step_id (FK), channel, sent_at, delivered (bool), opened (bool), clicked (bool), replied (bool), bounced (bool), unsubscribed (bool) }

## 6. MVP Scope vs Future Expansion

- **MVP:** General nurture sequence (5-step email), post-quote follow-up (3-step), discovery confirmation + reminders, initial SMS for web leads, appointment reminder SMS. All templates manually created and approved. Basic open/click tracking.
- **Future:** AI-personalized content based on lead behavior and preferences; dynamic send-time optimization per recipient; multi-language templates (French); WhatsApp/Instagram DM integration; advanced engagement scoring (email engagement → lead score boost); automated template A/B testing; drip campaign builder UI for Joe to create custom sequences.

---

# 6. Performance Reporting & Analytics

## 1. Business Goal (Context)

Create predictability in the marketing function by providing real-time visibility into campaign performance, spend efficiency, lead flow, and conversion metrics — enabling data-driven decisions, continuous optimization, and accountability toward the 200 installs/year target.

## 2. Roles & Permissions

- **AI System (automated):** Collects data from all ad platforms and communication tools, computes metrics, generates reports, and surfaces anomaly alerts.
- **Joe / Owner (human):** Views all dashboards and reports. Receives weekly summaries and real-time alerts for critical metrics.
- **Admin (human):** Configures dashboard layouts, metric definitions, alert thresholds, and report schedules.

## 3. Functional Requirements

### 6.1 Marketing KPI Tracking
- [ ] **CPA by Platform:** Cost per lead acquisition broken down by Google, Meta, TikTok (target: $1,000–$2,000 seasonally adjusted)
- [ ] **Total Marketing Spend:** Daily, weekly, and monthly totals with platform breakdown
- [ ] **Lead Volume by Source:** New leads per day/week/month by acquisition channel (paid search, paid social, organic search, direct, referral)
- [ ] **Lead Quality Distribution:** Leads by score bracket (0–29, 30–49, 50–79, 80–100) per source
- [ ] **Creative Performance:** CTR, conversion rate, and CPA per ad creative variant
- [ ] **Email Engagement:** Open rate, click rate, reply rate, unsubscribe rate per sequence and per template
- [ ] **SMS Engagement:** Delivery rate, response rate, opt-out rate
- [ ] **Website Traffic:** Sessions, page views, bounce rate, time-on-site, top landing pages, conversion rate (form submissions / sessions)
- [ ] **SEO Performance:** Keyword rankings (top 20 tracked), organic traffic volume, organic conversion rate
- [ ] **Funnel Conversion Rates:** Lead → Contacted → Qualified → Discovery Booked → Quoted → Won (conversion % at each step, by source)

### 6.2 Weekly Marketing Report
- [ ] Auto-generate and email to Joe every Monday at 8 AM ET:
  - Total spend by platform vs budget
  - CPA by platform vs target
  - Total new leads by source
  - Lead quality distribution
  - Top 3 performing ad creatives (by CPA)
  - Bottom 3 performing ad creatives (flagged for pause/replacement)
  - Email sequence engagement summary
  - Website traffic and conversion highlights
  - SEO keyword movement summary
  - AI-generated recommendations for the coming week (budget shifts, creative refreshes, audience adjustments)
- [ ] Include trend comparisons: week-over-week and month-over-month for all key metrics
- [ ] Format as a clean, scannable email with visual charts/graphs where possible

### 6.3 Predictive Analytics
- [ ] Estimate expected lead volume for the next 4 weeks based on current ad spend, seasonal patterns, and trailing conversion rates
- [ ] Forecast expected discoveries and bookings based on current pipeline and historical stage-conversion rates
- [ ] Alert when projected lead volume is below the weekly target needed to maintain the 200 installs/year trajectory (approximately 4–5 qualified leads per week)
- [ ] Identify optimal budget allocation for the coming month based on historical platform performance by season

### 6.4 Anomaly Alerts
- [ ] Alert Joe immediately (SMS + email) when:
  - CPA on any platform exceeds 2x the seasonal target for > 2 consecutive days
  - Daily lead volume drops > 30% compared to the 7-day average
  - Total weekly spend exceeds 90% of budget cap
  - Email bounce rate exceeds 5% on any send (possible list quality issue)
  - Website conversion rate drops > 25% week-over-week (possible landing page issue)
  - Any tracked SEO keyword drops > 10 positions (possible penalty or competitor move)

### 6.5 Attribution & ROI
- [ ] Track end-to-end attribution: which campaign/creative/audience generated each lead
- [ ] Calculate marketing ROI: (Revenue from Won leads attributed to marketing) / (Total marketing spend) — reported monthly
- [ ] Identify highest-ROI channels and recommend budget shifts accordingly
- [ ] Track customer acquisition cost (CAC) including all marketing and sales costs per Won deal

## 4. Business Rules

- All metrics are calculated from ad platform APIs and CRM data — no manual data entry required
- Reports are retained for 24 months for historical trend analysis
- Predictive models must be recalculated weekly using the latest 90 days of conversion data
- Anomaly alert thresholds are seasonally adjusted: relaxed in off-season (September–February), tightened in peak season (March–August)
- Attribution uses last-click model by default; first-touch attribution available as a secondary view
- All financial figures are in CAD

## 5. Data Schema

- **MetricSnapshot:** { snapshot_id, metric_name, metric_value, dimension_json (e.g., {platform: "meta", segment: "residential", creative_id: "xyz"}), period_type [daily|weekly|monthly], period_start, period_end, computed_at }
- **WeeklyReport:** { report_id, period_start, period_end, total_spend_cad, avg_cpa_cad, total_leads, leads_by_platform_json, leads_by_quality_json, top_creatives_json, bottom_creatives_json, email_summary_json, seo_summary_json, recommendations_text, generated_at, delivered_to }
- **Alert:** { alert_id, alert_type [cpa_spike|lead_drop|spend_cap|bounce_rate|conversion_drop|seo_drop], platform, threshold_value, current_value, triggered_at, acknowledged_by, acknowledged_at }
- **Forecast:** { forecast_id, metric_name [lead_volume|discoveries|revenue], forecast_period_start, forecast_period_end, predicted_value, confidence_interval_low, confidence_interval_high, model_version, generated_at }
- **Attribution:** { attribution_id, lead_id (FK), campaign_id (FK), creative_id (FK), segment_id (FK), attribution_model [last_click|first_touch], revenue_attributed_cad, attributed_at }

## 6. MVP Scope vs Future Expansion

- **MVP:** Weekly email report compiled manually from platform data exports with AI-generated summary and recommendations; basic CPA and lead volume tracking in a spreadsheet; email open/click rates from email tool; manual Google Search Console keyword check.
- **Future:** Real-time dashboard with live API feeds from Google Ads, Meta, TikTok, Mailchimp/SendGrid, and Google Analytics; automated anomaly detection with configurable thresholds; predictive lead volume forecasting; multi-touch attribution modeling; ROI tracking with QuickBooks integration; interactive dashboard with drill-down by platform/segment/creative/date.
