"use client"

import { Target, Clock, TrendingUp } from "lucide-react"
import { cn } from "@/lib/utils"

interface ExerciseCardProps {
  title: string
  description: string
  difficulty: "Beginner" | "Intermediate" | "Advanced"
  duration: string
  category: string
  onSelect?: () => void
}

export function ExerciseCard({ 
  title, 
  description, 
  difficulty, 
  duration, 
  category,
  onSelect 
}: ExerciseCardProps) {
  const difficultyColors = {
    Beginner: "bg-green-600",
    Intermediate: "bg-yellow-600", 
    Advanced: "bg-red-600"
  }

  return (
    <div 
      className="bg-gray-900 border border-gray-800 rounded-lg p-4 hover:border-gray-700 transition-colors cursor-pointer"
      onClick={onSelect}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <Target className="h-5 w-5 text-blue-500" />
          <h3 className="font-semibold text-white">{title}</h3>
        </div>
        <span className={cn(
          "px-2 py-1 rounded-full text-xs font-medium text-white",
          difficultyColors[difficulty]
        )}>
          {difficulty}
        </span>
      </div>
      
      <p className="text-gray-300 text-sm mb-3 leading-relaxed">
        {description}
      </p>
      
      <div className="flex items-center justify-between text-xs text-gray-400">
        <div className="flex items-center gap-1">
          <Clock className="h-4 w-4" />
          <span>{duration}</span>
        </div>
        <div className="flex items-center gap-1">
          <TrendingUp className="h-4 w-4" />
          <span>{category}</span>
        </div>
      </div>
    </div>
  )
}
