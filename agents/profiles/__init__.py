from __future__ import annotations

from typing import TYPE_CHECKING

from agents.profiles.base import AgentProfile
from agents.profiles.business_analyst import PROFILE as BUSINESS_ANALYST
from agents.profiles.content_moderator import PROFILE as CONTENT_MODERATOR
from agents.profiles.contract_auditor import PROFILE as CONTRACT_AUDITOR
from agents.profiles.customer_service import PROFILE as CUSTOMER_SERVICE
from agents.profiles.hr_assistant import PROFILE as HR_ASSISTANT
from agents.profiles.it_helpdesk import PROFILE as IT_HELPDESK
from agents.profiles.market_specialist import PROFILE as MARKET_SPECIALIST
from agents.profiles.marketing_copywriter import PROFILE as MARKETING_COPYWRITER
from agents.profiles.sales_development import PROFILE as SALES_DEVELOPMENT
from agents.profiles.social_media import PROFILE as SOCIAL_MEDIA
from agents.profiles.technical_support import PROFILE as TECHNICAL_SUPPORT

if TYPE_CHECKING:
    from agents.core.registry import AgentRegistry

PROFILES: tuple[AgentProfile, ...] = (
    MARKETING_COPYWRITER,
    MARKET_SPECIALIST,
    SALES_DEVELOPMENT,
    SOCIAL_MEDIA,
    BUSINESS_ANALYST,
    CONTENT_MODERATOR,
    HR_ASSISTANT,
    IT_HELPDESK,
    CUSTOMER_SERVICE,
    TECHNICAL_SUPPORT,
    CONTRACT_AUDITOR,
)


def register_profiles(registry: AgentRegistry) -> None:
    for profile in PROFILES:
        registry.register(profile)
