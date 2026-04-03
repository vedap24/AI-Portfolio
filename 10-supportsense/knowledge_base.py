# ──────────────────────────────────────────
# FAKE SAAS PRODUCT KNOWLEDGE BASE
# Product: "FlowDesk" — a project management SaaS
#
# This is the RAG source of truth.
# The AI ONLY answers from this content.
# If it's not here, it says "I don't know."
# That's the anti-hallucination guarantee.
# ──────────────────────────────────────────

PRODUCT_NAME = "FlowDesk"

KNOWLEDGE_BASE_DOCS = [
    {
        "id": "kb_001",
        "category": "pricing",
        "title": "FlowDesk Pricing Plans",
        "content": (
            "FlowDesk offers three pricing plans. "
            "The Free plan costs $0/month and includes "
            "up to 3 projects, 5 team members, "
            "and 1GB storage. "
            "The Pro plan costs $12/user/month "
            "and includes unlimited projects, "
            "unlimited team members, 50GB storage, "
            "priority support, and API access. "
            "The Enterprise plan has custom pricing "
            "and includes everything in Pro plus "
            "SSO, audit logs, dedicated support, "
            "and SLA guarantees. "
            "All plans include a 14-day free trial. "
            "Annual billing gives a 20% discount."
        )
    },
    {
        "id": "kb_002",
        "category": "features",
        "title": "FlowDesk Core Features",
        "content": (
            "FlowDesk core features include: "
            "Kanban boards for visual task management, "
            "Gantt charts for timeline planning, "
            "time tracking built into every task, "
            "file attachments up to 100MB per file, "
            "real-time collaboration with live cursors, "
            "task comments and @mentions, "
            "recurring tasks and reminders, "
            "custom fields and tags, "
            "and reporting dashboards. "
            "The mobile app is available on "
            "iOS and Android."
        )
    },
    {
        "id": "kb_003",
        "category": "integrations",
        "title": "FlowDesk Integrations",
        "content": (
            "FlowDesk integrates with: "
            "Slack for notifications, "
            "GitHub and GitLab for dev workflows, "
            "Google Drive and Dropbox for files, "
            "Zoom for meeting links, "
            "Zapier for 5000+ app connections, "
            "and REST API for custom integrations. "
            "API access requires Pro plan or higher. "
            "Zapier integration is available "
            "on all paid plans."
        )
    },
    {
        "id": "kb_004",
        "category": "billing",
        "title": "Billing and Payments",
        "content": (
            "FlowDesk accepts Visa, Mastercard, "
            "American Express, and PayPal. "
            "Invoices are generated on the "
            "1st of each month. "
            "Billing can be monthly or annual. "
            "Annual plans are paid upfront. "
            "To cancel, go to Settings > Billing "
            "> Cancel Subscription. "
            "Cancellation takes effect at the "
            "end of the current billing period. "
            "No refunds are issued for partial months. "
            "Enterprise customers are invoiced "
            "separately with net-30 terms."
        )
    },
    {
        "id": "kb_005",
        "category": "account",
        "title": "Account and Team Management",
        "content": (
            "To add team members: "
            "go to Settings > Team > Invite Members. "
            "Free plan supports up to 5 members. "
            "Pro and Enterprise have unlimited members. "
            "Admins can set role permissions: "
            "Owner, Admin, Member, or Viewer. "
            "Owners can transfer ownership "
            "in Settings > Account. "
            "To delete an account permanently, "
            "contact support@flowdesk.com. "
            "Account data is retained for "
            "30 days after cancellation."
        )
    },
    {
        "id": "kb_006",
        "category": "technical",
        "title": "Technical Requirements and Limits",
        "content": (
            "FlowDesk works in Chrome, Firefox, "
            "Safari, and Edge. "
            "IE is not supported. "
            "Minimum browser version: "
            "Chrome 80+, Firefox 75+, Safari 13+. "
            "Free plan: 1GB storage, "
            "100 tasks per project. "
            "Pro plan: 50GB storage, "
            "unlimited tasks. "
            "API rate limit: 1000 requests/hour "
            "on Pro, 5000/hour on Enterprise. "
            "File upload limit: 100MB per file. "
            "Data is backed up every 6 hours."
        )
    },
    {
        "id": "kb_007",
        "category": "support",
        "title": "Support Channels and Response Times",
        "content": (
            "Free plan: community forum only. "
            "Pro plan: email support, "
            "response within 24 hours on weekdays. "
            "Enterprise plan: dedicated Slack channel, "
            "response within 4 hours, 24/7. "
            "Live chat is available Mon-Fri 9am-6pm EST "
            "for Pro and Enterprise users. "
            "Critical bug reports are escalated "
            "regardless of plan. "
            "Support email: support@flowdesk.com. "
            "Status page: status.flowdesk.com."
        )
    },
    {
        "id": "kb_008",
        "category": "security",
        "title": "Security and Compliance",
        "content": (
            "FlowDesk is SOC 2 Type II certified. "
            "Data is encrypted at rest (AES-256) "
            "and in transit (TLS 1.3). "
            "GDPR compliant — EU data stays in EU. "
            "Two-factor authentication available "
            "on all plans. "
            "SSO (SAML 2.0) available on "
            "Enterprise plan only. "
            "Audit logs available on Enterprise. "
            "DPA (Data Processing Agreement) "
            "available on request. "
            "HIPAA compliance: not currently supported."
        )
    },
    {
        "id": "kb_009",
        "category": "getting_started",
        "title": "Getting Started with FlowDesk",
        "content": (
            "To get started: "
            "1. Sign up at flowdesk.com/signup. "
            "2. Create your first workspace. "
            "3. Invite team members via email. "
            "4. Create your first project. "
            "5. Add tasks to the Kanban board. "
            "Video tutorials at help.flowdesk.com. "
            "Onboarding checklist in the dashboard. "
            "Templates available for "
            "software, marketing, and HR teams. "
            "Import from Asana, Trello, and Jira "
            "available in Settings > Import."
        )
    },
    {
        "id": "kb_010",
        "category": "troubleshooting",
        "title": "Common Issues and Troubleshooting",
        "content": (
            "Can't log in: check caps lock, "
            "try password reset at "
            "flowdesk.com/reset. "
            "Notifications not working: "
            "check browser permissions "
            "and notification settings in profile. "
            "Slow performance: clear browser cache, "
            "disable extensions, try incognito mode. "
            "File upload failing: "
            "check file size (max 100MB) "
            "and storage quota. "
            "Integration not syncing: "
            "disconnect and reconnect in "
            "Settings > Integrations. "
            "If issues persist, contact "
            "support@flowdesk.com with "
            "browser version and screenshot."
        )
    }
]