from enum import Enum


class AuditLogAction(Enum):
    DELETE = "DELETE"
    UPDATE = "UPDATE"


class AccountType(str, Enum):
    TFSA = "TFSA"
    FHSA = "FHSA"
    Cash = "Cash"
    RRSP = "RRSP"
    RRSP_Spousal = "RRSP-Spousal"
    LIRA = "LIRA"
    RESP_Family = "RESP-Family"
    RIF_Spousal = "RIF-Spousal"
    RESP_Single = "RESP-Single"
    RRIF = "RRIF"
    GRSP = "GRSP"
    LRSP = "LRSP"
    LIF = "LIF"
    PRIF = "PRIF"
    GTFSA = "GTFSA"
    LRIF = "LRIF"
    RLIF = "RLIF"
    GSRSP = "GSRSP"


class SubscriptionTier(Enum):
    TRIAL = "Trial"
    PROFESSIONAL = "Professional"
    GROWTH = "Growth"
    SCALE = "Scale"
    ENTERPRISE = "Enterprise"


class PaymentStatus(Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"


class FeatureType(Enum):
    PDF_BROKERAGE_DOCS = "PDF Brokerage Docs"
    PDF_ESTATE_DOCS = "PDF Estate Docs"
    PORTFOLIO_REVIEW_SLIDES = "Portfolio Review Slides"
    IMAGE_SCANS = "Image / Scans"
    MEETINGS = "Meetings"


class SubscriptionStatus(Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"
    PAUSED = "paused"


class ScanStatus(Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"


class Role(Enum):
    ADMIN = "Admin"
    ADVISOR = "Advisor"
    PROSPECT = "Prospect"
