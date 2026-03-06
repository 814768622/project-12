-- Okeanos MVP P0 schema
-- Generated from docs/architecture.md and docs/tech_design.md

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('owner', 'admin', 'system')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS leads (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(120),
    last_name VARCHAR(120),
    email VARCHAR(255),
    phone VARCHAR(50),
    source VARCHAR(100) NOT NULL DEFAULT 'website_cf7',
    status VARCHAR(50) NOT NULL DEFAULT 'new',
    score INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lead_stage_history (
    id BIGSERIAL PRIMARY KEY,
    lead_id BIGINT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    previous_stage VARCHAR(50),
    new_stage VARCHAR(50) NOT NULL,
    changed_by VARCHAR(100),
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lead_tags (
    id BIGSERIAL PRIMARY KEY,
    lead_id BIGINT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    tag VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (lead_id, tag)
);

CREATE TABLE IF NOT EXISTS campaigns (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('meta', 'google', 'tiktok')),
    campaign_name VARCHAR(255) NOT NULL,
    objective VARCHAR(50) NOT NULL CHECK (objective IN ('lead_gen', 'brand_awareness', 'retargeting', 'seasonal_promo')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'paused', 'draft', 'completed', 'ab_testing')),
    daily_budget NUMERIC(12, 2),
    total_budget NUMERIC(12, 2),
    cpa_target NUMERIC(12, 2),
    start_date DATE,
    end_date DATE,
    icp_segment VARCHAR(50) CHECK (icp_segment IN ('residential', 'landscaper', 'builder', 'empty_nester')),
    season_tag VARCHAR(50),
    created_by VARCHAR(20) NOT NULL DEFAULT 'human' CHECK (created_by IN ('ai', 'human')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ad_creatives (
    id BIGSERIAL PRIMARY KEY,
    campaign_id BIGINT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    headline VARCHAR(255),
    body_text TEXT,
    image_url TEXT,
    video_url TEXT,
    cta_text VARCHAR(255),
    cta_url TEXT,
    variant_label VARCHAR(10),
    impressions BIGINT NOT NULL DEFAULT 0,
    clicks BIGINT NOT NULL DEFAULT 0,
    conversions BIGINT NOT NULL DEFAULT 0,
    ctr NUMERIC(10, 4),
    cpa NUMERIC(12, 2),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'winner', 'loser')),
    rotation_started_at TIMESTAMPTZ,
    fatigue_flagged BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS creative_assets (
    id BIGSERIAL PRIMARY KEY,
    asset_type VARCHAR(30) NOT NULL CHECK (asset_type IN ('photo', 'render', 'video', 'testimonial', 'brochure_excerpt')),
    pool_model VARCHAR(255),
    file_url TEXT NOT NULL,
    approved BOOLEAN NOT NULL DEFAULT FALSE,
    approved_by VARCHAR(255),
    tags_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ad_metrics_hourly (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('meta', 'google', 'tiktok')),
    external_campaign_id VARCHAR(255) NOT NULL,
    external_ad_id VARCHAR(255),
    hour_bucket TIMESTAMPTZ NOT NULL,
    impressions BIGINT NOT NULL DEFAULT 0,
    clicks BIGINT NOT NULL DEFAULT 0,
    spend_cad NUMERIC(12, 2) NOT NULL DEFAULT 0,
    conversions BIGINT NOT NULL DEFAULT 0,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (platform, external_campaign_id, hour_bucket)
);

CREATE TABLE IF NOT EXISTS budget_guardrails (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('meta', 'google', 'tiktok', 'total')),
    season_name VARCHAR(20) NOT NULL,
    min_daily_spend NUMERIC(12, 2),
    max_daily_spend NUMERIC(12, 2),
    max_platform_share_pct NUMERIC(5, 2),
    cpa_target_low NUMERIC(12, 2),
    cpa_target_high NUMERIC(12, 2),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS budget_allocations (
    id BIGSERIAL PRIMARY KEY,
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly')),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('meta', 'google', 'tiktok', 'total')),
    allocated_amount_cad NUMERIC(12, 2) NOT NULL,
    spent_amount_cad NUMERIC(12, 2) NOT NULL DEFAULT 0,
    remaining_cad NUMERIC(12, 2) NOT NULL DEFAULT 0,
    cpa_actual NUMERIC(12, 2),
    cpa_target NUMERIC(12, 2),
    status VARCHAR(20) NOT NULL CHECK (status IN ('on_track', 'over_budget', 'under_pacing', 'paused')),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS budget_changes (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('meta', 'google', 'tiktok', 'total')),
    previous_amount NUMERIC(12, 2),
    new_amount NUMERIC(12, 2),
    change_type VARCHAR(30) NOT NULL CHECK (change_type IN ('auto_reallocation', 'manual_override', 'auto_pause', 'auto_scale')),
    reason_text TEXT,
    triggered_by VARCHAR(20) NOT NULL CHECK (triggered_by IN ('ai', 'joe', 'admin')),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audience_segments (
    id BIGSERIAL PRIMARY KEY,
    segment_name VARCHAR(255) NOT NULL,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('meta', 'google', 'tiktok', 'all')),
    icp_type VARCHAR(30) NOT NULL CHECK (icp_type IN ('residential', 'empty_nester', 'landscaper', 'builder')),
    targeting_criteria_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    seed_list_size INTEGER,
    lookalike_size INTEGER,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'paused', 'draft')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_refreshed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS retargeting_lists (
    id BIGSERIAL PRIMARY KEY,
    list_name VARCHAR(255) NOT NULL,
    trigger VARCHAR(30) NOT NULL CHECK (trigger IN ('page_view', 'form_abandon', 'engaged_not_qualified', 'past_customer')),
    lookback_days INTEGER NOT NULL,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('meta', 'google', 'tiktok', 'all')),
    audience_size INTEGER,
    exclusions_applied_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS templates (
    id BIGSERIAL PRIMARY KEY,
    template_name VARCHAR(255) NOT NULL,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('email', 'sms')),
    subject_line VARCHAR(255),
    body_text TEXT NOT NULL,
    variables_used_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    version INTEGER NOT NULL DEFAULT 1,
    approved_by VARCHAR(255),
    approved_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL CHECK (status IN ('draft', 'approved', 'active', 'retired')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sequences (
    id BIGSERIAL PRIMARY KEY,
    sequence_name VARCHAR(255) NOT NULL,
    trigger VARCHAR(50) NOT NULL CHECK (trigger IN (
        'budget_mismatch', 'general_nurture', 'seasonal', 'lost_reactivation', 'post_contact',
        'discovery_confirm', 'post_discovery', 'post_quote', 'no_reply', 'post_sale',
        'referral', 'maintenance'
    )),
    target_segment VARCHAR(100),
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'paused', 'draft')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sequence_steps (
    id BIGSERIAL PRIMARY KEY,
    sequence_id BIGINT NOT NULL REFERENCES sequences(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    delay_days INTEGER NOT NULL DEFAULT 0,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('email', 'sms')),
    template_id BIGINT NOT NULL REFERENCES templates(id) ON DELETE RESTRICT,
    send_time_preference VARCHAR(20) NOT NULL DEFAULT 'any' CHECK (send_time_preference IN ('morning', 'afternoon', 'any')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (sequence_id, step_order)
);

CREATE TABLE IF NOT EXISTS sequence_enrollments (
    id BIGSERIAL PRIMARY KEY,
    lead_id BIGINT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    sequence_id BIGINT NOT NULL REFERENCES sequences(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    current_step INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'completed', 'paused', 'unenrolled')),
    next_run_at TIMESTAMPTZ,
    unenrolled_reason TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages_sent (
    id BIGSERIAL PRIMARY KEY,
    enrollment_id BIGINT REFERENCES sequence_enrollments(id) ON DELETE SET NULL,
    step_id BIGINT REFERENCES sequence_steps(id) ON DELETE SET NULL,
    lead_id BIGINT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('email', 'sms')),
    external_message_id VARCHAR(255),
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    delivered BOOLEAN NOT NULL DEFAULT FALSE,
    opened BOOLEAN NOT NULL DEFAULT FALSE,
    clicked BOOLEAN NOT NULL DEFAULT FALSE,
    replied BOOLEAN NOT NULL DEFAULT FALSE,
    bounced BOOLEAN NOT NULL DEFAULT FALSE,
    unsubscribed BOOLEAN NOT NULL DEFAULT FALSE,
    error_text TEXT,
    UNIQUE (channel, external_message_id)
);

CREATE TABLE IF NOT EXISTS channel_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    lead_id BIGINT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('email', 'sms')),
    subscribed BOOLEAN NOT NULL DEFAULT TRUE,
    unsubscribed_at TIMESTAMPTZ,
    source VARCHAR(100),
    UNIQUE (lead_id, channel)
);

CREATE TABLE IF NOT EXISTS approvals (
    id BIGSERIAL PRIMARY KEY,
    approval_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    payload_hash VARCHAR(128) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'approved', 'rejected', 'expired', 'executed')),
    requested_by VARCHAR(100) NOT NULL,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decided_by VARCHAR(100),
    decided_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    decision_note TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('cpa_spike', 'lead_drop', 'spend_cap', 'bounce_rate', 'conversion_drop', 'seo_drop')),
    platform VARCHAR(20),
    threshold_value NUMERIC(12, 2),
    current_value NUMERIC(12, 2),
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'acknowledged', 'resolved'))
);

CREATE TABLE IF NOT EXISTS metric_snapshots (
    id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC(18, 4) NOT NULL,
    dimension_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly')),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS weekly_reports (
    id BIGSERIAL PRIMARY KEY,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_spend_cad NUMERIC(12, 2),
    avg_cpa_cad NUMERIC(12, 2),
    total_leads INTEGER,
    report_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    recommendations_text TEXT,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    delivered_to_json JSONB NOT NULL DEFAULT '[]'::jsonb
);

CREATE TABLE IF NOT EXISTS sync_runs (
    id BIGSERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    platform VARCHAR(20),
    status VARCHAR(20) NOT NULL CHECK (status IN ('running', 'success', 'failed', 'partial')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    duration_ms INTEGER,
    error_message TEXT,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    actor VARCHAR(100),
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score);
CREATE INDEX IF NOT EXISTS idx_lead_stage_history_lead_id ON lead_stage_history(lead_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_platform_status ON campaigns(platform, status);
CREATE INDEX IF NOT EXISTS idx_ad_metrics_hourly_hour_platform ON ad_metrics_hourly(hour_bucket, platform);
CREATE INDEX IF NOT EXISTS idx_budget_allocations_period ON budget_allocations(period_start, period_type);
CREATE INDEX IF NOT EXISTS idx_sequence_enrollments_status_next_run ON sequence_enrollments(status, next_run_at);
CREATE INDEX IF NOT EXISTS idx_messages_sent_sent_at_channel ON messages_sent(sent_at, channel);
CREATE INDEX IF NOT EXISTS idx_alerts_triggered_type ON alerts(triggered_at, alert_type);
CREATE INDEX IF NOT EXISTS idx_sync_runs_job_started ON sync_runs(job_name, started_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
