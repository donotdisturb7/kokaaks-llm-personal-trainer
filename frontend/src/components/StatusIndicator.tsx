"use client"

import { useState, useEffect } from "react"
import { api, HealthResponse } from "@/lib/api"
import { cn } from "@/lib/utils"

interface StatusIndicatorProps {
  className?: string
}

export function StatusIndicator({ className }: StatusIndicatorProps) {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const healthData = await api.healthCheck()
        setHealth(healthData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        setHealth(null)
      } finally {
        setIsLoading(false)
      }
    }

    checkHealth()

    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = () => {
    if (isLoading) return "bg-yellow-500"
    if (error || !health || health.status !== "healthy") return "bg-red-500"
    return "bg-green-500"
  }

  const getStatusText = () => {
    if (isLoading) return "Checking..."
    if (error) return "Offline"
    if (!health) return "Unknown"
    if (health.status !== "healthy") return "Unhealthy"
    return "Online"
  }

  return (
    <div className={cn("flex items-center gap-2 text-sm", className)}>
      <div className={cn(
        "w-2.5 h-2.5 rounded-full animate-pulse shadow-[0_0_8px_currentColor]",
        getStatusColor()
      )} />
      <span className="text-muted-foreground">
        Backend: {getStatusText()}
      </span>
      {health && health.status === "healthy" && (
        <span className="text-muted-foreground">
          ({health.llm_provider})
        </span>
      )}
    </div>
  )
}
