# Santa Ana Votes Website - Vercel Deployment Roadmap (Proof of Concept)

## **Executive Overview**

This roadmap details the development of a Vercel-optimized Santa Ana City Council voting analysis website using Next.js 14+ with fake data for proof of concept demonstration. The website showcases civic transparency features while preparing for seamless integration with real data from the backend pipeline.

## **Project Vision & Goals**

### **Primary Mission**
Create a fast, modern, and accessible proof-of-concept website demonstrating Santa Ana's voting transparency platform, optimized for Vercel's edge network and serverless architecture.

### **Target Deployment Platform**
- **Vercel Edge Network**: Global CDN with sub-100ms response times
- **Serverless Functions**: API routes for dynamic functionality
- **Static Generation**: Pre-built pages for maximum performance
- **Edge Runtime**: Optimal performance at the network edge

### **Key Features**
- **Static Site Generation**: Pre-rendered pages with fake data
- **Interactive Analytics**: Client-side visualizations with Chart.js
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Search & Filtering**: Client-side search with instant results
- **Export Functionality**: CSV/PDF generation via serverless functions

## **Technology Stack**

### **Core Technologies**
```javascript
// Frontend Framework
Next.js 14+ (App Router)
TypeScript 5+
Tailwind CSS 3+
React 18+

// Data Visualization
Chart.js 4+
React Chart.js 2

// UI Components
Headless UI (for accessible components)
Heroicons (for consistent iconography)

// Development Tools
ESLint + Prettier
Husky (git hooks)
TypeScript strict mode
```

### **Vercel-Specific Features**
```javascript
// Vercel Functions
export default function handler(req, res) {
  // Serverless API endpoints
}

// Edge Functions (when needed)
export const config = {
  runtime: 'edge',
}

// Image Optimization
import Image from 'next/image'

// Performance Monitoring
import { Analytics } from '@vercel/analytics/react'
```

## **Application Architecture**

### **Project Structure**
```
santa-ana-votes/
├── app/                           # Next.js 14 App Router
│   ├── globals.css               # Global styles with Tailwind
│   ├── layout.tsx                # Root layout component
│   ├── page.tsx                  # Homepage dashboard
│   ├── council/
│   │   ├── page.tsx              # Council overview
│   │   └── [member]/page.tsx     # Individual member pages
│   ├── votes/
│   │   ├── page.tsx              # Vote search interface
│   │   └── [id]/page.tsx         # Individual vote details
│   ├── meetings/
│   │   ├── page.tsx              # Meeting browser
│   │   └── [id]/page.tsx         # Meeting details
│   ├── analytics/
│   │   └── page.tsx              # Analytics dashboard
│   └── api/                      # Serverless API routes
│       ├── votes/route.ts        # Vote search API
│       ├── export/route.ts       # Data export API
│       └── analytics/route.ts    # Analytics data API
├── components/
│   ├── ui/                       # Reusable UI components
│   ├── charts/                   # Chart.js wrapper components
│   ├── layout/                   # Layout components
│   └── features/                 # Feature-specific components
├── lib/
│   ├── fake-data.ts             # Fake data generation
│   ├── types.ts                 # TypeScript interfaces
│   ├── utils.ts                 # Utility functions
│   └── api.ts                   # API client functions
├── public/
│   ├── data/                    # Static JSON files
│   │   ├── council-members.json
│   │   ├── votes.json
│   │   ├── meetings.json
│   │   └── analytics.json
│   └── images/                  # Optimized images
└── styles/
    └── components.css           # Component-specific styles
```

### **Data Strategy - Fake Data for POC**

#### **Fake Data Generation System**
```typescript
// lib/fake-data.ts
export interface CouncilMember {
  id: string
  name: string
  role: 'Mayor' | 'Mayor Pro Tem' | 'Council Member'
  district?: number
  termStart: string
  termEnd: string
  active: boolean
  photoUrl: string
  contactInfo: ContactInfo
}

export interface Vote {
  id: string
  meetingId: string
  agendaItemNumber: string
  title: string
  description: string
  outcome: 'Pass' | 'Fail' | 'Tie' | 'Continued'
  tallyAyes: number
  tallyNoes: number
  tallyAbstain: number
  tallyAbsent: number
  memberVotes: Record<string, VotePosition>
  date: string
  motionText?: string
  mover?: string
  seconder?: string
}

// Realistic fake data generation
export function generateFakeVotes(count: number): Vote[] {
  const topics = [
    'Budget Amendment - Public Safety Funding',
    'Zoning Change - Downtown Development',
    'Parks and Recreation Expansion',
    'Housing Development Approval',
    'Transportation Infrastructure Update',
    'Environmental Impact Assessment',
    'Business License Regulation Update'
  ]

  return Array.from({ length: count }, (_, i) => ({
    id: `vote-${i + 1}`,
    meetingId: `meeting-${Math.floor(i / 8) + 1}`,
    title: topics[i % topics.length],
    // ... realistic fake data generation
  }))
}
```

#### **Static Data Files**
```json
// public/data/council-members.json
[
  {
    "id": "phil-bacerra",
    "name": "Phil Bacerra",
    "role": "Council Member",
    "district": 4,
    "termStart": "2020-12-07",
    "termEnd": "2024-12-07",
    "active": true,
    "photoUrl": "/images/council/bacerra.jpg",
    "contactInfo": {
      "email": "pbacerra@santa-ana.org",
      "phone": "(714) 647-5400"
    }
  }
  // ... more fake member data
]

// public/data/meetings.json
[
  {
    "id": "meeting-2024-01-16",
    "date": "2024-01-16",
    "type": "regular",
    "agendaUrl": "#",
    "minutesUrl": "#",
    "totalVotes": 12,
    "duration": 165
  }
  // ... more fake meeting data
]
```

## **Development Phases**

### **Phase 1: Foundation & Core UI (Week 1)**

#### **Setup & Configuration**
```bash
# Project initialization
npx create-next-app@latest santa-ana-votes --typescript --tailwind --app
cd santa-ana-votes
npm install @headlessui/react @heroicons/react chart.js react-chartjs-2

# Vercel CLI setup
npm install -g vercel
vercel login
vercel init
```

#### **Core Layout & Routing**
```typescript
// app/layout.tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  )
}

// components/layout/Navigation.tsx
export function Navigation() {
  return (
    <nav className="bg-blue-900 text-white">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="text-xl font-bold">
            Santa Ana Votes
          </Link>
          <div className="flex space-x-6">
            <Link href="/council">Council</Link>
            <Link href="/votes">Votes</Link>
            <Link href="/meetings">Meetings</Link>
            <Link href="/analytics">Analytics</Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
```

#### **Fake Data Integration**
```typescript
// lib/api.ts
export async function getCouncilMembers(): Promise<CouncilMember[]> {
  // In POC: load from static JSON
  const response = await fetch('/data/council-members.json')
  return response.json()

  // In production: will call backend API
  // const response = await fetch('/api/council-members')
  // return response.json()
}

export async function getVotes(filters?: VoteFilters): Promise<Vote[]> {
  // In POC: load and filter static JSON
  const response = await fetch('/data/votes.json')
  const votes = await response.json()

  if (!filters) return votes

  return votes.filter(vote => {
    if (filters.dateRange) {
      const voteDate = new Date(vote.date)
      if (voteDate < filters.dateRange.start || voteDate > filters.dateRange.end) {
        return false
      }
    }
    if (filters.members && !filters.members.includes(vote.memberVotes)) {
      return false
    }
    if (filters.outcome && vote.outcome !== filters.outcome) {
      return false
    }
    return true
  })
}
```

**Week 1 Deliverables:**
- Next.js 14 project with App Router configured
- Tailwind CSS styling system implemented
- Basic routing structure for all main sections
- Fake data generation system
- Static JSON data files with realistic Santa Ana data

### **Phase 2: Core Features & Functionality (Week 2)**

#### **Homepage Dashboard**
```typescript
// app/page.tsx
export default async function HomePage() {
  const stats = await getDashboardStats()
  const recentVotes = await getRecentVotes(5)
  const councilMembers = await getCouncilMembers()

  return (
    <div className="space-y-8">
      <DashboardStats stats={stats} />
      <CouncilComposition members={councilMembers} />
      <RecentActivity votes={recentVotes} />
      <QuickSearch />
    </div>
  )
}

// components/dashboard/DashboardStats.tsx
export function DashboardStats({ stats }: { stats: DashboardStats }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
      <StatCard
        title="Total Votes"
        value={stats.totalVotes}
        icon={<ChartBarIcon className="w-6 h-6" />}
      />
      <StatCard
        title="Meetings"
        value={stats.totalMeetings}
        icon={<CalendarIcon className="w-6 h-6" />}
      />
      <StatCard
        title="Coverage Period"
        value="2021-2024"
        icon={<ClockIcon className="w-6 h-6" />}
      />
      <StatCard
        title="Data Accuracy"
        value="90%+"
        icon={<CheckCircleIcon className="w-6 h-6" />}
      />
    </div>
  )
}
```

#### **Council Member Profiles**
```typescript
// app/council/[member]/page.tsx
export default async function MemberProfile({
  params,
}: {
  params: { member: string }
}) {
  const member = await getCouncilMember(params.member)
  const memberVotes = await getMemberVotes(params.member)
  const alignments = await getMemberAlignments(params.member)

  return (
    <div className="space-y-8">
      <MemberHeader member={member} />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <VotingPatternChart votes={memberVotes} />
          <VoteHistory votes={memberVotes} />
        </div>
        <div>
          <MemberStats member={member} votes={memberVotes} />
          <AlignmentAnalysis alignments={alignments} />
        </div>
      </div>
    </div>
  )
}
```

#### **Vote Search Interface**
```typescript
// app/votes/page.tsx
'use client'

export default function VotesPage() {
  const [votes, setVotes] = useState<Vote[]>([])
  const [filters, setFilters] = useState<VoteFilters>({})
  const [loading, setLoading] = useState(false)

  const handleSearch = async (newFilters: VoteFilters) => {
    setLoading(true)
    setFilters(newFilters)
    const results = await getVotes(newFilters)
    setVotes(results)
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <VoteSearchForm onSearch={handleSearch} />
      <SearchResults
        votes={votes}
        loading={loading}
        filters={filters}
      />
    </div>
  )
}

// components/votes/VoteSearchForm.tsx
export function VoteSearchForm({ onSearch }: { onSearch: (filters: VoteFilters) => void }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <DateRangePicker onChange={(range) => /* update filters */} />
        <MemberMultiSelect onChange={(members) => /* update filters */} />
        <OutcomeFilter onChange={(outcome) => /* update filters */} />
      </div>
      <div className="mt-4 flex justify-between">
        <SearchInput placeholder="Search votes by topic..." />
        <div className="flex space-x-2">
          <ExportButton format="csv" />
          <ExportButton format="pdf" />
        </div>
      </div>
    </div>
  )
}
```

**Week 2 Deliverables:**
- Complete homepage dashboard with fake statistics
- Council member profile pages with voting data
- Vote search interface with real-time filtering
- Meeting browser with fake meeting data

### **Phase 3: Analytics & Visualizations (Week 3)**

#### **Interactive Analytics Dashboard**
```typescript
// app/analytics/page.tsx
export default async function AnalyticsPage() {
  const alignmentData = await getMemberAlignmentMatrix()
  const trendData = await getVotingTrends()
  const issueData = await getIssueCategoryBreakdown()

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <AlignmentHeatmap data={alignmentData} />
        <VotingTrendsChart data={trendData} />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <IssueCategoryChart data={issueData} />
        <ParticipationChart data={trendData} />
      </div>
    </div>
  )
}

// components/analytics/AlignmentHeatmap.tsx
'use client'

import { Chart as ChartJS, CategoryScale, LinearScale, Title, Tooltip, Legend } from 'chart.js'
import { Matrix } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, Title, Tooltip, Legend)

export function AlignmentHeatmap({ data }: { data: AlignmentMatrix }) {
  const chartData = {
    labels: data.members,
    datasets: [{
      label: 'Agreement Rate (%)',
      data: data.matrix,
      backgroundColor: (context: any) => {
        const value = context.parsed.v
        return `rgba(31, 78, 121, ${value / 100})` // Santa Ana blue
      },
    }]
  }

  const options = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Council Member Voting Alignment'
      },
      tooltip: {
        callbacks: {
          title: (context: any) => {
            return `${context[0].label}`
          },
          label: (context: any) => {
            return `Agreement: ${context.parsed.v}%`
          }
        }
      }
    },
    scales: {
      x: {
        type: 'category',
        position: 'bottom'
      },
      y: {
        type: 'category'
      }
    }
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <Matrix data={chartData} options={options} />
    </div>
  )
}
```

#### **Export Functionality**
```typescript
// app/api/export/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  const { format, data, type } = await request.json()

  if (format === 'csv') {
    const csv = generateCSV(data, type)
    return new NextResponse(csv, {
      headers: {
        'Content-Type': 'text/csv',
        'Content-Disposition': `attachment; filename=santa-ana-${type}.csv`
      }
    })
  }

  if (format === 'pdf') {
    const pdf = await generatePDF(data, type)
    return new NextResponse(pdf, {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `attachment; filename=santa-ana-${type}.pdf`
      }
    })
  }

  return NextResponse.json({ error: 'Unsupported format' }, { status: 400 })
}
```

**Week 3 Deliverables:**
- Interactive analytics dashboard with Chart.js visualizations
- Member alignment heatmap with expansion capability
- Voting trends timeline charts
- CSV/PDF export functionality via serverless functions

### **Phase 4: Optimization & Deployment (Week 4)**

#### **Performance Optimization**
```typescript
// Performance optimizations
import dynamic from 'next/dynamic'

// Lazy load heavy chart components
const AlignmentHeatmap = dynamic(() => import('@/components/analytics/AlignmentHeatmap'), {
  loading: () => <ChartSkeleton />,
  ssr: false
})

// Image optimization
import Image from 'next/image'

export function CouncilMemberCard({ member }: { member: CouncilMember }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <Image
        src={member.photoUrl}
        alt={member.name}
        width={100}
        height={100}
        className="rounded-full"
        priority={false}
        placeholder="blur"
        blurDataURL="data:image/jpeg;base64,..."
      />
    </div>
  )
}
```

#### **Vercel Configuration**
```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "functions": {
    "app/api/export/route.ts": {
      "maxDuration": 30
    }
  },
  "redirects": [
    {
      "source": "/council",
      "destination": "/council/overview",
      "permanent": false
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "s-maxage=60, stale-while-revalidate"
        }
      ]
    }
  ]
}

// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['via.placeholder.com'], // For fake profile images
  },
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dashboard',
        permanent: false,
      },
    ]
  },
}

module.exports = nextConfig
```

#### **SEO & Accessibility**
```typescript
// app/layout.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Santa Ana Votes - City Council Transparency',
  description: 'Track Santa Ana City Council voting records, member alignment, and civic decision-making patterns.',
  keywords: 'Santa Ana, city council, voting records, civic transparency, government accountability',
  authors: [{ name: 'Santa Ana Votes Team' }],
  openGraph: {
    title: 'Santa Ana Votes',
    description: 'Complete transparency into Santa Ana City Council voting patterns',
    url: 'https://santa-ana-votes.vercel.app',
    siteName: 'Santa Ana Votes',
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Santa Ana Votes',
    description: 'Track Santa Ana City Council voting records and transparency',
  },
}

// Accessibility improvements
export function SearchInput({ label, ...props }: SearchInputProps) {
  const id = useId()

  return (
    <div className="space-y-1">
      <label htmlFor={id} className="sr-only">
        {label}
      </label>
      <input
        id={id}
        aria-label={label}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        {...props}
      />
    </div>
  )
}
```

**Week 4 Deliverables:**
- Fully optimized Next.js application for Vercel deployment
- Performance optimizations (lazy loading, image optimization)
- Complete SEO implementation with metadata
- WCAG 2.1 AA accessibility compliance
- Production deployment on Vercel

## **Data Integration Strategy**

### **Current State: Fake Data**
```typescript
// lib/fake-data.ts - Used during POC phase
export const FAKE_COUNCIL_MEMBERS = [
  {
    id: 'phil-bacerra',
    name: 'Phil Bacerra',
    role: 'Council Member',
    // ... realistic fake data
  }
  // ... 7 total members to match Santa Ana
]

export const FAKE_VOTES = generateRealisticVotes(150) // Match current extraction results
```

### **Future State: Real Data Integration**
```typescript
// lib/api.ts - Will be updated when backend is ready
export async function getCouncilMembers(): Promise<CouncilMember[]> {
  // Development: fake data
  if (process.env.NODE_ENV === 'development') {
    return FAKE_COUNCIL_MEMBERS
  }

  // Production: real backend API
  const response = await fetch(`${process.env.API_BASE_URL}/council-members`, {
    headers: {
      'Authorization': `Bearer ${process.env.API_TOKEN}`
    }
  })

  if (!response.ok) {
    throw new Error('Failed to fetch council members')
  }

  return response.json()
}
```

### **Shared Data Schema**
```typescript
// This schema will be shared between website and backend pipeline
export interface StandardizedVote {
  id: string                    // Unique identifier
  meetingId: string            // Links to meeting data
  agendaItemNumber: string     // e.g., "7.1", "8.A"
  title: string                // Vote title/topic
  description: string          // Detailed description
  outcome: 'Pass' | 'Fail' | 'Tie' | 'Continued'
  date: string                 // ISO date string

  // Vote tallies
  tallyAyes: number
  tallyNoes: number
  tallyAbstain: number
  tallyAbsent: number
  tallyRecused?: number

  // Individual member votes
  memberVotes: Record<string, {
    position: 'Aye' | 'No' | 'Abstain' | 'Absent' | 'Recused'
    memberId: string
    memberName: string
    recusalReason?: string
  }>

  // Additional metadata
  motionText?: string
  mover?: string
  seconder?: string
  qualityScore: number         // Data extraction confidence (0-100)
}
```

## **Performance Targets**

### **Vercel-Optimized Metrics**
- **Core Web Vitals**:
  - Largest Contentful Paint (LCP): < 2.5s
  - First Input Delay (FID): < 100ms
  - Cumulative Layout Shift (CLS): < 0.1
  - First Contentful Paint (FCP): < 1.5s

- **Page Speed**:
  - Homepage: < 1.5s initial load
  - Search results: < 800ms response time
  - Chart rendering: < 2s for complex visualizations
  - Export generation: < 10s for large datasets

- **Bundle Size**:
  - Initial JavaScript bundle: < 250KB gzipped
  - Total page weight: < 1MB
  - Image optimization: WebP format, lazy loading

## **SEO Strategy**

### **URL Structure**
```
https://santa-ana-votes.vercel.app/
├── /                           # Homepage
├── /council                    # Council overview
├── /council/phil-bacerra       # Individual member pages
├── /votes                      # Vote search
├── /votes/vote-2024-01-16-7-1  # Individual vote pages
├── /meetings                   # Meeting browser
├── /meetings/2024-01-16        # Individual meeting pages
├── /analytics                  # Analytics dashboard
└── /about                      # About page
```

### **Structured Data**
```typescript
// Structured data for government entities
export function generateStructuredData(member: CouncilMember) {
  return {
    "@context": "http://schema.org",
    "@type": "Person",
    "name": member.name,
    "jobTitle": member.role,
    "worksFor": {
      "@type": "GovernmentOrganization",
      "name": "Santa Ana City Council",
      "url": "https://www.santa-ana.org/government/city-council"
    },
    "url": `https://santa-ana-votes.vercel.app/council/${member.id}`,
    "sameAs": member.socialLinks
  }
}
```

## **Security & Privacy**

### **Data Protection**
```typescript
// No sensitive data handling in POC
// All data is fake and publicly displayable
export const PRIVACY_POLICY = {
  dataCollection: 'No personal data collected from users',
  cookies: 'Only essential analytics cookies',
  publicRecords: 'All voting data is public record',
  fakeData: 'POC uses realistic but fabricated data'
}
```

### **Content Security Policy**
```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self' vercel.live",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline' vercel.live",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https://via.placeholder.com",
      "font-src 'self'",
    ].join('; ')
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  }
]
```

## **Success Metrics**

### **Technical KPIs**
- **Lighthouse Score**: 90+ across all categories
- **Vercel Function Duration**: < 5s average
- **Build Time**: < 3 minutes
- **Deployment Success Rate**: 99%+

### **User Experience KPIs**
- **Time to Interactive**: < 2 seconds
- **Search Response Time**: < 500ms
- **Mobile Performance**: 85+ mobile Lighthouse score
- **Accessibility Score**: 95+ accessibility Lighthouse score

### **Business KPIs (POC Validation)**
- **Demo Success Rate**: Positive feedback from 80%+ of stakeholders
- **Feature Completeness**: All planned features functional
- **Data Accuracy**: Fake data realistic enough for meaningful demos
- **Integration Readiness**: Easy switch to real data pipeline

## **Deployment Process**

### **Development Workflow**
```bash
# Local development
npm run dev              # Start development server
npm run lint             # Run ESLint
npm run type-check       # TypeScript validation
npm run test             # Run test suite (if implemented)

# Vercel deployment
vercel --prod           # Deploy to production
vercel domains add      # Configure custom domain
vercel env add          # Configure environment variables
```

### **Environment Configuration**
```bash
# .env.local
NEXT_PUBLIC_SITE_URL=https://santa-ana-votes.vercel.app
NEXT_PUBLIC_API_BASE_URL=http://localhost:3000/api  # POC phase
# NEXT_PUBLIC_API_BASE_URL=https://api.santa-ana-votes.com  # Future production

# Vercel environment variables
VERCEL_URL              # Automatically set
NEXT_PUBLIC_VERCEL_ENV  # Automatically set
```

## **Future Migration Path**

### **Phase 1: POC with Fake Data** (This roadmap)
- Static JSON files with realistic fake data
- Client-side filtering and search
- Serverless functions for exports
- Full UI/UX demonstration

### **Phase 2: Real Data Integration** (After backend pipeline)
- Replace fake data API calls with real backend calls
- Add authentication if needed
- Implement real-time data updates
- Add data validation and error handling

### **Code Changes for Migration**
```typescript
// Only these functions need updating for real data:
// lib/api.ts - Update API endpoints
// lib/fake-data.ts - Remove (will be unused)
// app/*/page.tsx - No changes needed (uses api.ts functions)
// components/* - No changes needed (props stay the same)

// Migration is literally changing a few API endpoints:
const API_BASE = process.env.NODE_ENV === 'development'
  ? '/fake-data'  // Current POC
  : process.env.BACKEND_API_URL  // Future real data
```

## **Risk Management**

### **Technical Risks**
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-------------|
| Vercel build failures | Low | Medium | Comprehensive CI/CD testing |
| Performance degradation | Medium | High | Performance monitoring, bundle analysis |
| Fake data insufficient for demos | Low | High | Realistic data generation with domain expert review |

### **Timeline Risks**
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-------------|
| Chart.js integration complexity | Medium | Low | Start with simple charts, progressive enhancement |
| Responsive design challenges | Low | Medium | Mobile-first development approach |
| Vercel platform limitations | Low | High | Research Vercel capabilities upfront |

## **Conclusion**

This roadmap delivers a production-ready, Vercel-optimized proof-of-concept website in 4 weeks. The fake data strategy allows immediate demonstration of all features while maintaining the exact same architecture that will seamlessly integrate with real data from the backend pipeline.

The Next.js 14 App Router architecture, combined with Vercel's edge network, provides optimal performance and scalability. The modular component design ensures easy maintenance and future enhancements.

Most importantly, the clean separation between data layer and presentation layer means that switching from fake to real data requires minimal code changes, making this POC a true foundation for the production system.