"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID


# City schemas
class CityConfig(BaseModel):
    name: str
    display_name: str
    council_members: List[str]
    total_seats: int
    colors: Dict[str, str]


class CityListResponse(BaseModel):
    success: bool
    cities: Dict[str, CityConfig]
    total: int


# Session schemas
class SessionResponse(BaseModel):
    success: bool
    session_id: UUID
    created_at: datetime
    cities: List[str]


class UploadResponse(BaseModel):
    success: bool
    session_id: UUID
    city_key: str
    filename: str
    total_votes: int
    message: str


# Dashboard schemas
class VoteSummaryResponse(BaseModel):
    success: bool
    city_info: Dict[str, Any]
    vote_summary: Dict[str, Any]
    member_participation: List[Dict[str, Any]]
    total_members: int
    active_members: int


class MemberAnalysisResponse(BaseModel):
    success: bool
    city_info: Dict[str, Any]
    member_analysis: Dict[str, Any]
    alignment_data: Dict[str, Dict[str, float]]
    most_aligned: List[Dict[str, Any]]
    least_aligned: List[Dict[str, Any]]


class MemberProfileResponse(BaseModel):
    success: bool
    member_name: str
    member_stats: Dict[str, Any]
    city_info: Dict[str, Any]
    vote_history: List[Dict[str, Any]]
    agreements: List[tuple]


class AgendaItemsResponse(BaseModel):
    success: bool
    city_info: Dict[str, Any]
    meetings: Dict[str, Any]
    total_items: int


class AgendaItemDetailResponse(BaseModel):
    success: bool
    item: Dict[str, Any]
    member_votes: List[Dict[str, str]]
    city_info: Dict[str, Any]


class ComparisonResponse(BaseModel):
    success: bool
    comparison_data: Dict[str, Any]
    comparison_metrics: Dict[str, Any]
    cities_count: int


# Error response
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
