"use client"

import { Target } from "lucide-react"
import { StatusIndicator } from "@/components/StatusIndicator"

/**
 * Composant Header - En-tête de l'application
 * Affiche le logo et le titre de l'application
 * 
 * TODO: Ajouter un menu déroulant pour les paramètres utilisateur
 * FIXME: Le logo pourrait être plus stylé, peut-être avec une animation
 */
export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-black/20 backdrop-blur-xl supports-[backdrop-filter]:bg-black/20">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-3">
          {/* Logo avec icône de cible */}
          <div className="h-9 w-9 bg-gradient-to-br from-[hsl(var(--harvest-orange))] to-orange-600 rounded-xl flex items-center justify-center shadow-[0_0_15px_rgba(255,120,0,0.3)]">
            <Target className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/80">
            KovaaK's <span className="text-[hsl(var(--harvest-orange))]">AI Trainer</span>
          </h1>
        </div>
        {/* Status et informations */}
        <div className="flex items-center gap-4">
          <StatusIndicator />
        </div>
      </div>
    </header>
  )
}
