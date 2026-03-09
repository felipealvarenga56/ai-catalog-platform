from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ContractInitiative(str, Enum):
    BI = "BI"
    DEEP = "Deep"
    WIDE_N8N = "wide-n8n"
    WIDE_LOVABLE = "wide-lovable"
    WIDE_SUPERBLOCKS = "wide-superblocks"
    ALTERYX = "Alteryx"
    COPILOT = "Copilot"


class ContractStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEVELOPMENT = "development"
    STAGING = "staging"


class ContractCreate(BaseModel):
    business_map_id: str
    title: str
    area: str
    initiative: ContractInitiative
    version: str = "1.0.0"
    description: str
    owner: str
    status: ContractStatus = ContractStatus.ACTIVE
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    sec_approval: Optional[str] = None
    docs_link: Optional[str] = None
    cost: Optional[str] = None
    projected_return: Optional[str] = None
    usage: Optional[str] = None
    limitations: Optional[str] = None


class Contract(ContractCreate):
    id: int
    created_at: str
    updated_at: str


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1)


class ToolSolution(str, Enum):
    COPILOT = "copilot"
    LOVABLE = "lovable"
    N8N = "n8n"
    ALTERYX = "alteryx"
    BI_TEAM = "bi_team"
    DEEP_TEAM = "deep_team"
    SQUAD = "squad"
    NO_SOLUTION = "no_solution"


class WizardResponse(BaseModel):
    answer: str
    recommended_tool: Optional[ToolSolution] = None
    justification: Optional[str] = None
    similar_projects: list[Contract] = []


class DeliveryProcedure(BaseModel):
    tool_id: ToolSolution
    tool_name: str
    steps: list[str]
    documentation_path: Optional[str] = None
    contact_info: Optional[str] = None


class ExecutiveReport(BaseModel):
    total_projects: int
    by_source: dict[str, int]
    by_status: dict[str, int]
    summary: str


class IngestResult(BaseModel):
    total_processed: int
    total_inserted: int
    total_updated: int
    errors: list[str]


# --- Executive Dashboard Models (Requirement 6.1, 6.4) ---


class FilterOptions(BaseModel):
    areas: list[str]
    initiatives: list[str]
    statuses: list[str]
    owners: list[str]


class ComplianceMetrics(BaseModel):
    sec_approval_count: int
    sec_approval_percentage: float
    docs_link_count: int
    docs_link_percentage: float


class CrossTabEntry(BaseModel):
    row: str
    col: str
    count: int


class FinancialMetrics(BaseModel):
    cost_coverage_count: int
    cost_coverage_percentage: float
    return_coverage_count: int
    return_coverage_percentage: float
    cost_by_initiative: dict[str, str]      # initiative → representative cost string
    return_by_initiative: dict[str, str]    # initiative → representative return string


class ExecutiveDashboardReport(BaseModel):
    total_contracts: int
    by_status: dict[str, int]
    by_initiative: dict[str, int]
    by_area: dict[str, int]
    by_owner: dict[str, int]
    compliance: ComplianceMetrics
    financial: FinancialMetrics
    cross_area_initiative: list[CrossTabEntry]
    cross_area_status: list[CrossTabEntry]
    filter_options: FilterOptions
