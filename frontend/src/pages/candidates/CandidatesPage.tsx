import { useState } from 'react'
import { Search, Filter, Plus, Download, MoreHorizontal } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu'
import { Badge } from '../components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar'
import { cn } from '../lib/utils'

const candidates = [
  { id: '1', name: 'Sarah Chen', email: 'sarah.chen@email.com', phone: '+1-555-0123', location: 'San Francisco, CA', skills: ['React', 'TypeScript', 'Node.js', 'AWS'], status: 'screening', experience: 'Senior', appliedDate: '2024-01-15', matchScore: 92 },
  { id: '2', name: 'Michael Rodriguez', email: 'm.rodriguez@email.com', phone: '+1-555-0456', location: 'Austin, TX', skills: ['Python', 'Django', 'PostgreSQL', 'Docker'], status: 'interviewing', experience: 'Mid', appliedDate: '2024-01-12', matchScore: 87 },
  { id: '3', name: 'Emily Watson', email: 'emily.watson@email.com', phone: '+1-555-0789', location: 'New York, NY', skills: ['Java', 'Spring Boot', 'Kubernetes', 'Microservices'], status: 'offer', experience: 'Senior', appliedDate: '2024-01-10', matchScore: 95 },
  { id: '4', name: 'David Park', email: 'david.park@email.com', phone: '+1-555-0321', location: 'Seattle, WA', skills: ['Go', 'gRPC', 'Redis', 'GraphQL'], status: 'screening', experience: 'Lead', appliedDate: '2024-01-08', matchScore: 89 },
  { id: '5', name: 'Lisa Thompson', email: 'lisa.thompson@email.com', phone: '+1-555-0654', location: 'Remote', skills: ['React Native', 'Expo', 'Firebase', 'TypeScript'], status: 'new', experience: 'Mid', appliedDate: '2024-01-05', matchScore: 78 },
]

const statusConfig = {
  new: { label: 'New', color: 'bg-gray-100 text-gray-800' },
  screening: { label: 'Screening', color: 'bg-blue-100 text-blue-800' },
  interviewing: { label: 'Interviewing', color: 'bg-purple-100 text-purple-800' },
  offer: { label: 'Offer', color: 'bg-green-100 text-green-800' },
  hired: { label: 'Hired', color: 'bg-emerald-100 text-emerald-800' },
  rejected: { label: 'Rejected', color: 'bg-red-100 text-red-800' },
  withdrawn: { label: 'Withdrawn', color: 'bg-orange-100 text-orange-800' },
}

export function CandidatesPage() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [experienceFilter, setExperienceFilter] = useState('all')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Candidates</h1>
          <p className="text-muted-foreground">Manage and track your candidate pipeline</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm"><Download className="h-4 w-4 mr-2" /> Export</Button>
          <Button><Plus className="h-4 w-4 mr-2" /> Add Candidate</Button>
        </div>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search candidates..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="new">New</SelectItem>
                <SelectItem value="screening">Screening</SelectItem>
                <SelectItem value="interviewing">Interviewing</SelectItem>
                <SelectItem value="offer">Offer</SelectItem>
                <SelectItem value="hired">Hired</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>
            <Select value={experienceFilter} onValueChange={setExperienceFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Experience" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Levels</SelectItem>
                <SelectItem value="entry">Entry</SelectItem>
                <SelectItem value="junior">Junior</SelectItem>
                <SelectItem value="mid">Mid</SelectItem>
                <SelectItem value="senior">Senior</SelectItem>
                <SelectItem value="lead">Lead</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm"><Filter className="h-4 w-4" /></Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">Candidate</TableHead>
                <TableHead>Contact</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Skills</TableHead>
                <TableHead className="w-36">Experience</TableHead>
                <TableHead className="w-36">Status</TableHead>
                <TableHead className="w-32">Match Score</TableHead>
                <TableHead className="w-36">Applied</TableHead>
                <TableHead className="w-12"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {candidates.map((candidate) => {
                const status = statusConfig[candidate.status as keyof typeof statusConfig]
                return (
                  <TableRow key={candidate.id} className="hover:bg-muted/50">
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-10 w-10">
                          <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${candidate.name}`} alt={candidate.name} />
                          <AvatarFallback>{candidate.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium">{candidate.name}</p>
                          <p className="text-sm text-muted-foreground">{candidate.email}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{candidate.phone}</TableCell>
                    <TableCell>{candidate.location}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {candidate.skills.slice(0, 3).map((skill) => (
                          <Badge key={skill} variant="secondary" className="text-xs">{skill}</Badge>
                        ))}
                        {candidate.skills.length > 3 && (
                          <Badge variant="outline" className="text-xs">+{candidate.skills.length - 3}</Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{candidate.experience}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={cn(status.color, 'capitalize')}>{status.label}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-green-500 rounded-full transition-all"
                            style={{ width: `${candidate.matchScore}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-green-600">{candidate.matchScore}%</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(candidate.appliedDate).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" className="h-8 w-8 p-0">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>View Profile</DropdownMenuItem>
                          <DropdownMenuItem>Edit Candidate</DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem>Schedule Interview</DropdownMenuItem>
                          <DropdownMenuItem>Send Email</DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem className="text-red-600">Reject Candidate</DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">Showing 5 of 234 candidates</p>
        <nav className="flex gap-1">
          <Button variant="outline" size="sm" disabled>Previous</Button>
          <Button variant="outline" size="sm">1</Button>
          <Button variant="default" size="sm">2</Button>
          <Button variant="outline" size="sm">3</Button>
          <Button variant="outline" size="sm">Next</Button>
        </nav>
      </div>
    </div>
  )
}