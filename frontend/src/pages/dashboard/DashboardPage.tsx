import { Users, Briefcase, Search, Bot, TrendingUp, Clock, CheckCircle, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'

const stats = [
  { name: 'Total Candidates', value: '1,234', change: '+12%', icon: Users, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  { name: 'Active Jobs', value: '56', change: '+3', icon: Briefcase, color: 'text-green-500', bg: 'bg-green-500/10' },
  { name: 'Matches This Week', value: '89', change: '+23%', icon: Search, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  { name: 'AI Interactions', value: '1,456', change: '+45%', icon: Bot, color: 'text-orange-500', bg: 'bg-orange-500/10' },
]

const recentActivity = [
  { id: 1, type: 'candidate_match', title: 'New high match found', description: 'Sarah Chen matched with Senior React Developer (92%)', time: '2 min ago', icon: CheckCircle, color: 'text-green-500' },
  { id: 2, type: 'job_posted', title: 'Job posted', description: 'Senior Frontend Engineer position published', time: '15 min ago', icon: Briefcase, color: 'text-blue-500' },
  { id: 3, type: 'interview_scheduled', title: 'Interview scheduled', description: 'Technical interview with John Smith for Backend Role', time: '1 hour ago', icon: Clock, color: 'text-purple-500' },
  { id: 4, type: 'candidate_applied', title: 'New application', description: 'Emily Davis applied for Product Manager position', time: '2 hours ago', icon: Users, color: 'text-orange-500' },
  { id: 5, type: 'offer_extended', title: 'Offer extended', description: 'Offer sent to Michael Brown for DevOps Engineer', time: '3 hours ago', icon: CheckCircle, color: 'text-green-500' },
]

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Welcome back! Here's what's happening with your recruitment pipeline.</p>
        </div>
        <Button>Add Candidate</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.name}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.name}</CardTitle>
              <stat.icon className={cn('h-4 w-4', stat.color)} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.change} from last week</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start gap-3">
                  <div className={cn('p-2 rounded-lg', activity.color + '/10')}>
                    <activity.icon className={cn('h-4 w-4', activity.color)} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{activity.title}</p>
                    <p className="text-sm text-muted-foreground">{activity.description}</p>
                  </div>
                  <span className="text-xs text-muted-foreground whitespace-nowrap">{activity.time}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pipeline Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { stage: 'Sourced', count: 234, color: 'bg-blue-500' },
                { stage: 'Screening', count: 89, color: 'bg-yellow-500' },
                { stage: 'Interviewing', count: 45, color: 'bg-purple-500' },
                { stage: 'Offer', count: 12, color: 'bg-green-500' },
                { stage: 'Hired', count: 8, color: 'bg-emerald-500' },
              ].map((stage) => (
                <div key={stage.stage} className="flex items-center gap-4">
                  <div className="w-32 text-sm font-medium">{stage.stage}</div>
                  <div className="flex-1 h-3 bg-muted rounded-full overflow-hidden">
                    <div
                      className={cn('h-full rounded-full transition-all', stage.color)}
                      style={{ width: `${(stage.count / 234) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium w-12 text-right">{stage.count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Hiring Funnel (Last 30 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end justify-around gap-2">
              {[
                { label: 'Week 1', applications: 45, screens: 32, interviews: 18, offers: 5 },
                { label: 'Week 2', applications: 52, screens: 38, interviews: 22, offers: 8 },
                { label: 'Week 3', applications: 48, screens: 35, interviews: 20, offers: 7 },
                { label: 'Week 4', applications: 61, screens: 42, interviews: 25, offers: 10 },
              ].map((week, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <div className="flex gap-1 w-full h-full items-end">
                    <div className="flex-1 bg-blue-500 rounded-t" style={{ height: `${(week.applications / 61) * 100}%` }} title={`${week.applications} Applications`} />
                    <div className="flex-1 bg-yellow-500 rounded-t" style={{ height: `${(week.screens / 42) * 100}%` }} title={`${week.screens} Screenings`} />
                    <div className="flex-1 bg-purple-500 rounded-t" style={{ height: `${(week.interviews / 25) * 100}%` }} title={`${week.interviews} Interviews`} />
                    <div className="flex-1 bg-green-500 rounded-t" style={{ height: `${(week.offers / 10) * 100}%` }} title={`${week.offers} Offers`} />
                  </div>
                  <span className="text-xs text-muted-foreground">{week.label}</span>
                </div>
              ))}
            </div>
            <div className="flex gap-4 justify-center mt-4 text-sm">
              <div className="flex items-center gap-1"><div className="w-3 h-3 bg-blue-500 rounded" /> Applications</div>
              <div className="flex items-center gap-1"><div className="w-3 h-3 bg-yellow-500 rounded" /> Screenings</div>
              <div className="flex items-center gap-1"><div className="w-3 h-3 bg-purple-500 rounded" /> Interviews</div>
              <div className="flex items-center gap-1"><div className="w-3 h-3 bg-green-500 rounded" /> Offers</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button variant="outline" className="w-full justify-start gap-2">
              <Users className="h-4 w-4" /> Add Candidate
            </Button>
            <Button variant="outline" className="w-full justify-start gap-2">
              <Briefcase className="h-4 w-4" /> Create Job
            </Button>
            <Button variant="outline" className="w-full justify-start gap-2">
              <Search className="h-4 w-4" /> Find Matches
            </Button>
            <Button variant="outline" className="w-full justify-start gap-2">
              <Bot className="h-4 w-4" /> Ask Atlas One
            </Button>
            <Button variant="outline" className="w-full justify-start gap-2">
              <TrendingUp className="h-4 w-4" /> View Analytics
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}