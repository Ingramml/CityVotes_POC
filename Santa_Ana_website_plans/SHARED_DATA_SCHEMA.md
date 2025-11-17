# Santa Ana Votes - Shared Data Schema

## **Overview**

This document defines the exact data schema shared between the Vercel website frontend and the backend data pipeline. This schema ensures seamless integration and allows the website to switch from fake to real data without code changes.

## **Core Principle**

**Single Source of Truth**: Both the website TypeScript interfaces and the backend API schemas must match exactly. Any changes to this schema require updates to both systems.

## **Data Entities**

### **Council Member Schema**

#### **TypeScript Interface (Website)**
```typescript
// lib/types.ts
export interface CouncilMember {
  id: string                    // Unique identifier (e.g., "phil-bacerra")
  name: string                  // Full name (e.g., "Phil Bacerra")
  role: 'Mayor' | 'Mayor Pro Tem' | 'Council Member'
  district?: number             // Council district (optional)
  termStart: string             // ISO date string (e.g., "2020-12-07")
  termEnd: string               // ISO date string (e.g., "2024-12-07")
  active: boolean               // Currently serving
  photoUrl: string              // URL to member photo
  contactInfo: ContactInfo      // Contact details
}

export interface ContactInfo {
  email?: string
  phone?: string
  website?: string
  socialMedia?: {
    twitter?: string
    facebook?: string
    instagram?: string
  }
}

export interface CouncilMemberStats {
  totalVotes: number            // Total votes participated in
  participationRate: number     // Percentage of votes attended
  agreementRate: Record<string, number> // Agreement % with other members
  votingPatterns: {
    aye: number
    no: number
    abstain: number
    absent: number
  }
}
```

#### **Backend Pydantic Schema (API)**
```python
# schemas/council.py
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    social_media: Optional[Dict[str, str]] = Field(alias="socialMedia", default=None)

class CouncilMember(BaseModel):
    id: str
    name: str
    role: str  # Validated to be one of the three roles
    district: Optional[int] = None
    term_start: str = Field(alias="termStart")  # ISO date string
    term_end: str = Field(alias="termEnd")      # ISO date string
    active: bool
    photo_url: str = Field(alias="photoUrl")
    contact_info: ContactInfo = Field(alias="contactInfo")

    class Config:
        allow_population_by_field_name = True

class CouncilMemberStats(BaseModel):
    total_votes: int = Field(alias="totalVotes")
    participation_rate: float = Field(alias="participationRate")
    agreement_rate: Dict[str, float] = Field(alias="agreementRate")
    voting_patterns: Dict[str, int] = Field(alias="votingPatterns")

    class Config:
        allow_population_by_field_name = True
```

### **Vote Schema**

#### **TypeScript Interface (Website)**
```typescript
// lib/types.ts
export interface Vote {
  id: string                    // Unique identifier (e.g., "vote-2024-01-16-7-1")
  meetingId: string             // Links to meeting (e.g., "meeting-2024-01-16")
  agendaItemNumber: string      // Item number (e.g., "7.1", "8.A")
  title: string                 // Vote title/topic
  description: string           // Detailed description
  outcome: 'Pass' | 'Fail' | 'Tie' | 'Continued'
  date: string                  // ISO date string

  // Vote tallies
  tallyAyes: number
  tallyNoes: number
  tallyAbstain: number
  tallyAbsent: number
  tallyRecused?: number

  // Individual member votes
  memberVotes: Record<string, MemberVote>

  // Optional metadata
  motionText?: string           // Full motion text
  mover?: string               // Member who made motion
  seconder?: string            // Member who seconded motion
  qualityScore: number         // Data extraction confidence (0-100)
}

export interface MemberVote {
  position: 'Aye' | 'No' | 'Abstain' | 'Absent' | 'Recused'
  memberId: string             // Links to council member
  memberName: string           // Display name
  recusalReason?: string       // If recused, why
}

export interface VoteFilters {
  dateRange?: {
    start: Date
    end: Date
  }
  members?: string[]           // Filter by member IDs
  outcome?: 'Pass' | 'Fail' | 'Tie' | 'Continued'
  search?: string              // Search in title/description
  meetingType?: string         // Filter by meeting type
}
```

#### **Backend Pydantic Schema (API)**
```python
# schemas/votes.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal
from datetime import datetime

class MemberVote(BaseModel):
    position: Literal["Aye", "No", "Abstain", "Absent", "Recused"]
    member_id: str = Field(alias="memberId")
    member_name: str = Field(alias="memberName")
    recusal_reason: Optional[str] = Field(alias="recusalReason", default=None)

    class Config:
        allow_population_by_field_name = True

class Vote(BaseModel):
    id: str
    meeting_id: str = Field(alias="meetingId")
    agenda_item_number: str = Field(alias="agendaItemNumber")
    title: str
    description: str
    outcome: Literal["Pass", "Fail", "Tie", "Continued"]
    date: str  # ISO date string

    # Vote tallies
    tally_ayes: int = Field(alias="tallyAyes")
    tally_noes: int = Field(alias="tallyNoes")
    tally_abstain: int = Field(alias="tallyAbstain")
    tally_absent: int = Field(alias="tallyAbsent")
    tally_recused: Optional[int] = Field(alias="tallyRecused", default=0)

    # Member votes
    member_votes: Dict[str, MemberVote] = Field(alias="memberVotes")

    # Optional metadata
    motion_text: Optional[str] = Field(alias="motionText", default=None)
    mover: Optional[str] = None
    seconder: Optional[str] = None
    quality_score: float = Field(alias="qualityScore", ge=0, le=100)

    class Config:
        allow_population_by_field_name = True

class VoteFilters(BaseModel):
    date_start: Optional[str] = None      # YYYY-MM-DD format
    date_end: Optional[str] = None        # YYYY-MM-DD format
    members: Optional[List[str]] = None   # List of member IDs
    outcome: Optional[str] = None         # Pass, Fail, Tie, Continued
    search: Optional[str] = None          # Search query
    meeting_type: Optional[str] = None    # Meeting type filter
```

### **Meeting Schema**

#### **TypeScript Interface (Website)**
```typescript
// lib/types.ts
export interface Meeting {
  id: string                    // Unique identifier (e.g., "meeting-2024-01-16")
  date: string                  // ISO date string
  type: 'regular' | 'special' | 'joint_housing' | 'emergency'
  agendaUrl?: string           // Link to original agenda
  minutesUrl?: string          // Link to original minutes
  totalVotes: number           // Number of votes in meeting
  duration?: number            // Meeting length in minutes
  status: 'completed' | 'processing' | 'pending'
}

export interface MeetingDetails extends Meeting {
  votes: Vote[]                // All votes from this meeting
  attendance: Record<string, boolean> // Member attendance
  summary?: string             // Meeting summary
}
```

#### **Backend Pydantic Schema (API)**
```python
# schemas/meetings.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal

class Meeting(BaseModel):
    id: str
    date: str  # ISO date string
    type: Literal["regular", "special", "joint_housing", "emergency"]
    agenda_url: Optional[str] = Field(alias="agendaUrl", default=None)
    minutes_url: Optional[str] = Field(alias="minutesUrl", default=None)
    total_votes: int = Field(alias="totalVotes")
    duration: Optional[int] = None  # minutes
    status: Literal["completed", "processing", "pending"]

    class Config:
        allow_population_by_field_name = True

class MeetingDetails(Meeting):
    votes: List[Vote] = []
    attendance: Dict[str, bool] = {}
    summary: Optional[str] = None
```

### **Analytics Schema**

#### **TypeScript Interface (Website)**
```typescript
// lib/types.ts
export interface AlignmentMatrix {
  matrix: Record<string, Record<string, number>>  // member_id -> member_id -> agreement %
  members: Array<{
    id: string
    name: string
  }>
  generatedAt: string          // ISO timestamp
}

export interface VotingTrends {
  trends: Array<{
    period: string             // YYYY-MM format
    totalVotes: number
    passRate: number           // Percentage
    unanimousRate: number      // Percentage
    contentiousRate: number    // Percentage
  }>
  generatedAt: string
}

export interface DashboardStats {
  totalVotes: number
  totalMeetings: number
  coveragePeriod: {
    start: string
    end: string
  }
  dataAccuracy: number         // Percentage
  lastUpdated: string
}

export interface IssueCategoryData {
  categories: Array<{
    name: string
    count: number
    percentage: number
  }>
  generatedAt: string
}
```

#### **Backend Pydantic Schema (API)**
```python
# schemas/analytics.py
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

class AlignmentMatrix(BaseModel):
    matrix: Dict[str, Dict[str, float]]
    members: List[Dict[str, str]]
    generated_at: str = Field(alias="generatedAt")

    class Config:
        allow_population_by_field_name = True

class VotingTrendPoint(BaseModel):
    period: str
    total_votes: int = Field(alias="totalVotes")
    pass_rate: float = Field(alias="passRate")
    unanimous_rate: float = Field(alias="unanimousRate")
    contentious_rate: float = Field(alias="contentiousRate")

    class Config:
        allow_population_by_field_name = True

class VotingTrends(BaseModel):
    trends: List[VotingTrendPoint]
    generated_at: str = Field(alias="generatedAt")

    class Config:
        allow_population_by_field_name = True

class DashboardStats(BaseModel):
    total_votes: int = Field(alias="totalVotes")
    total_meetings: int = Field(alias="totalMeetings")
    coverage_period: Dict[str, str] = Field(alias="coveragePeriod")
    data_accuracy: float = Field(alias="dataAccuracy")
    last_updated: str = Field(alias="lastUpdated")

    class Config:
        allow_population_by_field_name = True

class IssueCategory(BaseModel):
    name: str
    count: int
    percentage: float

class IssueCategoryData(BaseModel):
    categories: List[IssueCategory]
    generated_at: str = Field(alias="generatedAt")

    class Config:
        allow_population_by_field_name = True
```

## **API Endpoint Contracts**

### **Council Member Endpoints**
```
GET /api/v1/council/
Response: CouncilMember[]

GET /api/v1/council/{member_id}
Response: CouncilMember & CouncilMemberStats

GET /api/v1/council/{member_id}/votes
Response: Vote[]

GET /api/v1/council/{member_id}/alignments
Response: Record<string, number>  // other_member_id -> agreement_percentage
```

### **Vote Endpoints**
```
GET /api/v1/votes/
Query Params: date_start, date_end, members[], outcome, search, limit, offset
Response: Vote[]

GET /api/v1/votes/{vote_id}
Response: Vote

POST /api/v1/votes/search
Body: VoteFilters
Response: Vote[]
```

### **Meeting Endpoints**
```
GET /api/v1/meetings/
Response: Meeting[]

GET /api/v1/meetings/{meeting_id}
Response: MeetingDetails

GET /api/v1/meetings/{meeting_id}/votes
Response: Vote[]
```

### **Analytics Endpoints**
```
GET /api/v1/analytics/dashboard
Response: DashboardStats

GET /api/v1/analytics/alignment-matrix
Response: AlignmentMatrix

GET /api/v1/analytics/voting-trends
Response: VotingTrends

GET /api/v1/analytics/issue-categories
Response: IssueCategoryData
```

### **Export Endpoints**
```
POST /api/v1/export/votes/csv
Body: { vote_ids: string[] }
Response: CSV file download

POST /api/v1/export/member/pdf
Body: { member_id: string }
Response: PDF file download
```

## **Data Validation Rules**

### **Council Member Validation**
```python
# Validation rules enforced by both systems
COUNCIL_MEMBER_VALIDATION = {
    "id": {
        "pattern": r"^[a-z][a-z0-9-]*[a-z0-9]$",  # lowercase-with-hyphens
        "max_length": 50
    },
    "name": {
        "min_length": 2,
        "max_length": 100,
        "pattern": r"^[A-Za-z\s\-\.]+$"  # Letters, spaces, hyphens, periods
    },
    "role": {
        "enum": ["Mayor", "Mayor Pro Tem", "Council Member"]
    },
    "district": {
        "min": 1,
        "max": 10,  # Santa Ana has districts 1-6 typically
        "optional": True
    }
}
```

### **Vote Validation**
```python
VOTE_VALIDATION = {
    "id": {
        "pattern": r"^vote-\d{4}-\d{2}-\d{2}-[a-zA-Z0-9\-]+$"
    },
    "outcome": {
        "enum": ["Pass", "Fail", "Tie", "Continued"]
    },
    "tally_consistency": {
        "rule": "tally_ayes + tally_noes + tally_abstain + tally_absent + tally_recused >= 5",
        "description": "Total tallies should account for minimum council size"
    },
    "member_votes_consistency": {
        "rule": "len(member_votes) matches expected council size",
        "description": "Should have votes for active council members"
    },
    "quality_score": {
        "min": 0.0,
        "max": 100.0,
        "type": "float"
    }
}
```

## **Error Response Schema**

### **Standard Error Format**
```typescript
// Both website and backend use this error format
export interface APIError {
  error: {
    code: string              // Machine-readable error code
    message: string           // Human-readable error message
    details?: any            // Additional error context
    timestamp: string        // ISO timestamp
    path?: string           // API path where error occurred
  }
}
```

```python
# Backend error response
class ErrorResponse(BaseModel):
    error: ErrorDetail

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None
    timestamp: str
    path: Optional[str] = None
```

### **Common Error Codes**
```typescript
export const ERROR_CODES = {
  VALIDATION_ERROR: "VALIDATION_ERROR",
  NOT_FOUND: "NOT_FOUND",
  INTERNAL_ERROR: "INTERNAL_ERROR",
  RATE_LIMIT_EXCEEDED: "RATE_LIMIT_EXCEEDED",
  DATA_QUALITY_LOW: "DATA_QUALITY_LOW",
  EXTRACTION_FAILED: "EXTRACTION_FAILED"
} as const
```

## **Fake Data Generation Rules**

### **Realistic Data Requirements**
```typescript
// Fake data must match these realistic constraints
export const FAKE_DATA_CONSTRAINTS = {
  council_members: {
    count: 7,  // Santa Ana has 7 council members
    roles: {
      "Mayor": 1,
      "Mayor Pro Tem": 1,
      "Council Member": 5
    },
    term_overlap: true,  // Some members serve multiple terms
    districts: [1, 2, 3, 4, 5, 6]  // Santa Ana districts
  },

  votes: {
    per_meeting: { min: 8, max: 15 },
    pass_rate: 0.75,  // ~75% of votes pass (realistic)
    unanimous_rate: 0.40,  // ~40% are unanimous
    contentious_rate: 0.15,  // ~15% are close votes
    quality_score_distribution: {
      high: 0.60,    // 60% high quality (80-100)
      medium: 0.30,  // 30% medium quality (60-80)
      low: 0.10      // 10% low quality (40-60)
    }
  },

  meetings: {
    frequency: "bi_weekly",  // Every 2 weeks typically
    types: {
      "regular": 0.80,
      "special": 0.15,
      "joint_housing": 0.04,
      "emergency": 0.01
    }
  }
}
```

## **Migration Strategy**

### **Phase 1: Fake Data (POC)**
```typescript
// Website uses static JSON files
const API_BASE = '/data'  // Static files in public/data/

export async function getCouncilMembers(): Promise<CouncilMember[]> {
  const response = await fetch(`${API_BASE}/council-members.json`)
  return response.json()
}
```

### **Phase 2: Real Data (Production)**
```typescript
// Website switches to real API (same function signature!)
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL + '/api/v1'

export async function getCouncilMembers(): Promise<CouncilMember[]> {
  const response = await fetch(`${API_BASE}/council/`)
  if (!response.ok) {
    throw new APIError(await response.json())
  }
  return response.json()
}

// All other website code remains exactly the same!
```

## **Testing Strategy**

### **Schema Compatibility Tests**
```typescript
// tests/schema-compatibility.test.ts
describe('Schema Compatibility', () => {
  test('Council member from API matches TypeScript interface', async () => {
    const apiResponse = await fetch('/api/v1/council/phil-bacerra')
    const member: CouncilMember = await apiResponse.json()

    // This test will fail if schemas don't match exactly
    expect(member).toMatchSchema(CouncilMemberSchema)
  })

  test('Vote data structure matches between fake and real data', () => {
    const fakeVote = loadFakeVote()
    const realVote = loadRealVote()

    expect(Object.keys(fakeVote).sort()).toEqual(Object.keys(realVote).sort())
  })
})
```

### **Integration Tests**
```python
# tests/integration/test_website_integration.py
async def test_website_compatibility():
    """Test that API responses work with website code"""

    # Test council member endpoint
    response = await client.get("/api/v1/council/")
    members = response.json()

    # Verify it matches website expectations exactly
    for member in members:
        validate_council_member_schema(member)

    # Test vote filtering (website's main feature)
    response = await client.get("/api/v1/votes/?date_start=2024-01-01&limit=10")
    votes = response.json()

    for vote in votes:
        validate_vote_schema(vote)
```

## **Versioning Strategy**

### **API Versioning**
- **v1**: Initial release matching this schema
- **v2**: Future enhancements (maintain v1 compatibility)
- **Website Compatibility**: Website specifies API version in requests

### **Schema Evolution**
- **Additive Changes**: New optional fields allowed
- **Breaking Changes**: Require new API version
- **Deprecation**: 6-month notice for removed fields

## **Documentation Maintenance**

### **Change Management**
1. **Schema Change Proposal**: Document any changes
2. **Impact Assessment**: Check both website and backend
3. **Testing**: Verify compatibility
4. **Deployment**: Coordinate updates

### **Single Source of Truth**
This document serves as the authoritative reference for data structures. Any discrepancies between actual implementations and this document should be resolved by updating the implementations to match this schema.

## **Conclusion**

This shared schema ensures perfect compatibility between the Vercel website frontend and the backend data pipeline. By maintaining exact schema matching, the website can seamlessly transition from fake data POC to real data production without any code changes.

The schema is designed to be both comprehensive for full functionality and flexible for future enhancements, providing a solid foundation for the Santa Ana civic transparency platform.