from typing import List, Optional
from pydantic import BaseModel


# ──────────────────────────────────────────
# SITE INSPECTION REPORT
# ──────────────────────────────────────────

class IssueItem(BaseModel):
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    location: str


class ActionItem(BaseModel):
    task: str
    priority: str  # URGENT, HIGH, MEDIUM, LOW
    deadline: Optional[str] = None


class SiteInspectionReport(BaseModel):
    location: str
    inspector_name: Optional[str] = None
    inspection_date: str
    inspection_type: str
    findings: List[str] = []
    issues: List[IssueItem] = []
    action_items: List[ActionItem] = []
    safety_rating: str  # PASS, FAIL, CONDITIONAL
    follow_up_required: bool = False
    follow_up_date: Optional[str] = None
    overall_condition: str  # EXCELLENT, GOOD, FAIR, POOR
    additional_notes: Optional[str] = None


# ──────────────────────────────────────────
# SALES VISIT REPORT
# ──────────────────────────────────────────

class NextStep(BaseModel):
    action: str
    owner: Optional[str] = None
    deadline: Optional[str] = None


class SalesVisitReport(BaseModel):
    client_name: str
    contact_person: Optional[str] = None
    contact_role: Optional[str] = None
    meeting_date: str
    meeting_duration: Optional[str] = None
    discussion_points: List[str] = []
    pain_points: List[str] = []
    objections: List[str] = []
    next_steps: List[NextStep] = []
    deal_stage: str  # Prospect, Discovery, Proposal, Negotiation, Closed Won, Closed Lost
    deal_value: Optional[str] = None
    follow_up_date: Optional[str] = None
    sentiment: str  # POSITIVE, NEUTRAL, NEGATIVE
    notes: Optional[str] = None


# ──────────────────────────────────────────
# DELIVERY LOG REPORT
# ──────────────────────────────────────────

class DeliveryStop(BaseModel):
    stop_number: int
    location: str
    status: str  # Delivered, Failed, Partial
    notes: Optional[str] = None


class DeliveryIssue(BaseModel):
    type: str  # Vehicle, Route, Customer, Package, Other
    description: str
    severity: str  # HIGH, MEDIUM, LOW


class DeliveryLogReport(BaseModel):
    driver_name: Optional[str] = None
    vehicle_id: Optional[str] = None
    delivery_date: str
    route: Optional[str] = None
    stops: List[DeliveryStop] = []
    total_stops: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    issues: List[DeliveryIssue] = []
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    mileage: Optional[str] = None
    fuel_used: Optional[str] = None
    completion_rate: Optional[str] = None
    notes: Optional[str] = None


# ──────────────────────────────────────────
# FIELD REPORT RESULT (wrapper)
# ──────────────────────────────────────────

class FieldReportResult(BaseModel):
    report_type: str  # site_inspection, sales_visit, delivery_log
    transcript: str
    transcript_confidence: float
    audio_duration_seconds: float
    report: dict
    word_count: int
    processing_time_seconds: float
    status: str = "success"  # success, error
    error_message: Optional[str] = None
