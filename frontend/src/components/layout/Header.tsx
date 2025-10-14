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
    <header className="bg-card border-b border-border px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Logo avec icône de cible - simple mais efficace */}
          <div className="h-8 w-8 bg-primary rounded-lg flex items-center justify-center">
            <Target className="h-5 w-5 text-primary-foreground" />
          </div>
          <h1 className="text-xl font-bold text-foreground">KovaaK's AI Personal Trainer</h1>
        </div>
        {/* Status et informations */}
        <div className="flex items-center gap-4">
          <StatusIndicator />
          {/* <div className="text-sm text-muted-foreground">
            KovaaK's AI Personal Trainer
          </div> */}
        </div>
      </div>
    </header>
  )
}
