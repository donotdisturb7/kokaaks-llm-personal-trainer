"use client"

import { useState } from "react"
import { FileText, Download, Plus, Search, Filter, Calendar, User, Target } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"

interface Artifact {
  id: string
  title: string
  type: 'training_program' | 'exercise_plan' | 'analysis_report' | 'custom'
  description: string
  createdAt: Date
  content: string
  tags: string[]
  generatedBy: string
}

const ArtifactsTab: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [filterTag, setFilterTag] = useState<string>('all')

  const [artifacts] = useState<Artifact[]>([
    {
      id: '1',
      title: 'Beginner Aim Training Program',
      type: 'training_program',
      description: 'A comprehensive 4-week program designed for beginners to improve their aim fundamentals',
      createdAt: new Date('2024-01-15'),
      content: `# Beginner Aim Training Program

## Week 1: Foundation Building
- **Day 1-2**: Basic tracking exercises (Smoothbot, Air Angelic)
- **Day 3-4**: Flicking fundamentals (Tile Frenzy, 1wall6targets)
- **Day 5-6**: Precision training (Thin Gauntlet, Microshot)
- **Day 7**: Rest and review

## Week 2: Skill Development
- **Day 1-2**: Advanced tracking (Close Fast Strafes, FuglaaXYLongstrafes)
- **Day 3-4**: Speed flicking (1wall5targets_pasu, Bounce 180)
- **Day 5-6**: Precision under pressure (Popcorn, Ground Plaza)
- **Day 7**: Assessment and adjustment

## Week 3: Integration
- **Day 1-2**: Mixed scenarios (Voltaic, Aimer7 routines)
- **Day 3-4**: Game-specific training
- **Day 5-6**: Endurance building
- **Day 7**: Performance review

## Week 4: Mastery
- **Day 1-2**: Advanced scenarios
- **Day 3-4**: Competition preparation
- **Day 5-6**: Final assessment
- **Day 7**: Program completion and next steps`,
      tags: ['beginner', 'tracking', 'flicking', 'precision'],
      generatedBy: 'GPT-4'
    },
    {
      id: '2',
      title: 'Wrist Pain Prevention Guide',
      type: 'analysis_report',
      description: 'Comprehensive analysis of wrist pain causes and prevention strategies for aim training',
      createdAt: new Date('2024-01-10'),
      content: `# Wrist Pain Prevention Guide

## Common Causes
1. **Overuse**: Excessive training without proper rest
2. **Poor posture**: Incorrect arm and wrist positioning
3. **High sensitivity**: Training with sensitivity too high
4. **Inadequate warm-up**: Starting intense training cold

## Prevention Strategies
1. **Proper warm-up routine** (5-10 minutes)
2. **Ergonomic setup** recommendations
3. **Training schedule** with adequate rest
4. **Stretching exercises** for wrist flexibility

## Warning Signs
- Persistent pain during or after training
- Reduced range of motion
- Tingling or numbness
- Weakness in grip strength

## Recovery Protocol
1. Immediate rest from training
2. Ice therapy (15-20 minutes)
3. Gentle stretching
4. Gradual return to training`,
      tags: ['health', 'prevention', 'wrist', 'ergonomics'],
      generatedBy: 'Claude-3'
    },
    {
      id: '3',
      title: 'Advanced Flicking Routine',
      type: 'exercise_plan',
      description: 'High-intensity flicking routine for experienced players looking to push their limits',
      createdAt: new Date('2024-01-08'),
      content: `# Advanced Flicking Routine

## Warm-up (10 minutes)
1. **1wall6targets TE** - 2 minutes
2. **Tile Frenzy** - 2 minutes
3. **1wall5targets_pasu** - 3 minutes
4. **Bounce 180** - 3 minutes

## Main Training (30 minutes)
1. **1wall6targets TE** - 5 minutes
2. **Tile Frenzy** - 5 minutes
3. **1wall5targets_pasu** - 5 minutes
4. **Bounce 180** - 5 minutes
5. **1wall6targets TE** - 5 minutes
6. **Tile Frenzy** - 5 minutes

## Cool-down (5 minutes)
1. **Smoothbot** - 3 minutes
2. **Air Angelic** - 2 minutes

## Tips for Success
- Focus on accuracy over speed initially
- Maintain consistent crosshair placement
- Take breaks between sets
- Track your progress daily`,
      tags: ['advanced', 'flicking', 'intensive', 'routine'],
      generatedBy: 'GPT-4'
    }
  ])

  const filteredArtifacts = artifacts.filter(artifact => {
    const matchesSearch = artifact.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         artifact.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = filterType === 'all' || artifact.type === filterType
    const matchesTag = filterTag === 'all' || artifact.tags.includes(filterTag)
    return matchesSearch && matchesType && matchesTag
  })

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'training_program': return 'bg-red-500/20 text-red-400 border-red-500/50'
      case 'exercise_plan': return 'bg-orange-500/20 text-orange-400 border-orange-500/50'
      case 'analysis_report': return 'bg-blue-500/20 text-blue-400 border-blue-500/50'
      case 'custom': return 'bg-purple-500/20 text-purple-400 border-purple-500/50'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/50'
    }
  }

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'training_program': return 'Training Program'
      case 'exercise_plan': return 'Exercise Plan'
      case 'analysis_report': return 'Analysis Report'
      case 'custom': return 'Custom'
      default: return type
    }
  }

  const handleDownload = (artifact: Artifact) => {
    const blob = new Blob([artifact.content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${artifact.title.replace(/\s+/g, '_')}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleGenerateNew = () => {
    // This would open a modal or navigate to a generation form
    console.log('Generate new artifact')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">AI Artifacts</h2>
          <p className="text-muted-foreground">
            Generated training programs, exercise plans, and analysis reports
          </p>
        </div>
        <Button onClick={handleGenerateNew} className="bg-primary hover:bg-primary/90">
          <Plus className="w-4 h-4 mr-2" />
          Generate New
        </Button>
      </div>

      {/* Filters */}
      <Card className="bg-card border-border">
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search artifacts..."
                className="pl-10"
              />
            </div>
            <select 
              value={filterType} 
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full sm:w-[180px] h-9 px-3 py-2 bg-input border border-border rounded-md text-sm"
            >
              <option value="all">All Types</option>
              <option value="training_program">Training Program</option>
              <option value="exercise_plan">Exercise Plan</option>
              <option value="analysis_report">Analysis Report</option>
              <option value="custom">Custom</option>
            </select>
            <select 
              value={filterTag} 
              onChange={(e) => setFilterTag(e.target.value)}
              className="w-full sm:w-[180px] h-9 px-3 py-2 bg-input border border-border rounded-md text-sm"
            >
              <option value="all">All Tags</option>
              <option value="beginner">Beginner</option>
              <option value="advanced">Advanced</option>
              <option value="tracking">Tracking</option>
              <option value="flicking">Flicking</option>
              <option value="precision">Precision</option>
              <option value="health">Health</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Artifacts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredArtifacts.map((artifact) => (
          <Card key={artifact.id} className="bg-card border-border hover:border-primary/50 transition-colors">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-5 h-5 text-primary" />
                    <CardTitle className="text-lg">{artifact.title}</CardTitle>
                  </div>
                  <CardDescription className="text-muted-foreground">
                    {artifact.description}
                  </CardDescription>
                </div>
                <Badge className={`${getTypeColor(artifact.type)} border`}>
                  {getTypeLabel(artifact.type)}
                </Badge>
              </div>
              <div className="flex flex-wrap gap-1 mt-3">
                {artifact.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      <span>{artifact.createdAt.toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <User className="w-4 h-4" />
                      <span>{artifact.generatedBy}</span>
                    </div>
                  </div>
                </div>
                
                <ScrollArea className="h-32 w-full">
                  <div className="text-sm text-muted-foreground whitespace-pre-wrap">
                    {artifact.content.substring(0, 200)}...
                  </div>
                </ScrollArea>
                
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleDownload(artifact)}
                    className="flex-1"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    <Target className="w-4 h-4 mr-2" />
                    Use Template
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredArtifacts.length === 0 && (
        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">No artifacts found</h3>
              <p className="text-muted-foreground mb-4">
                {searchQuery || filterType !== 'all' || filterTag !== 'all'
                  ? 'Try adjusting your search or filters'
                  : 'Generate your first AI artifact to get started'
                }
              </p>
              <Button onClick={handleGenerateNew} className="bg-primary hover:bg-primary/90">
                <Plus className="w-4 h-4 mr-2" />
                Generate New Artifact
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default ArtifactsTab
