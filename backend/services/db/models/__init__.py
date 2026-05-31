from services.db.models.activity import Activity
from services.db.models.ai_scores import (
    ChurnPrediction,
    CLVEstimate,
    CopilotSuggestion,
    LeadScore,
)
from services.db.models.cases import (
    Case,
    CaseComment,
    CaseEscalation,
    KnowledgeArticle,
    SLAPolicy,
    SupportQueue,
)
from services.db.models.inbox import AgentPresence, ConversationHandoff, InboxQueue
from services.db.models.workflows import WorkflowDefinition, WorkflowExecution, WorkflowStep
from services.db.models.partners import (
    DealRegistration,
    Partner,
    PartnerActivityLog,
    PartnerCommission,
)
from services.db.models.campaigns import (
    Campaign,
    CampaignConversion,
    CampaignSegment,
    CampaignSend,
    MessageTemplate,
)
from services.db.models.territories import Territory, TerritoryAssignment, TerritoryRule
from services.db.models.collections import Invoice, Payment, ReconciliationCase
from services.db.models.conversations import Conversation, ConversationMessage
from services.db.models.followup import FollowupEscalation, FollowupTask
from services.db.models.idempotency import IdempotencyRecord
from services.db.models.lead import Lead

__all__ = [
    "Activity",
    "ChurnPrediction",
    "CLVEstimate",
    "CopilotSuggestion",
    "LeadScore",
    "AgentPresence",
    "Campaign",
    "DealRegistration",
    "CampaignConversion",
    "CampaignSegment",
    "CampaignSend",
    "Case",
    "CaseComment",
    "CaseEscalation",
    "Conversation",
    "ConversationHandoff",
    "ConversationMessage",
    "FollowupEscalation",
    "FollowupTask",
    "IdempotencyRecord",
    "InboxQueue",
    "Invoice",
    "KnowledgeArticle",
    "Lead",
    "MessageTemplate",
    "Partner",
    "PartnerActivityLog",
    "PartnerCommission",
    "Payment",
    "ReconciliationCase",
    "SLAPolicy",
    "SupportQueue",
    "Territory",
    "TerritoryAssignment",
    "TerritoryRule",
    "WorkflowDefinition",
    "WorkflowExecution",
    "WorkflowStep",
]
