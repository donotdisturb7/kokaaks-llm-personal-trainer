"use client"

import { Target } from "lucide-react"

/**
 * Composant Header - En-tête de l'application
 * Affiche le logo et le titre de l'application
 * 
 * TODO: Ajouter un menu déroulant pour les paramètres utilisateur
 * FIXME: Le logo pourrait être plus stylé, peut-être avec une animation
 */
export function Header() {
  return (
    <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Logo avec icône de cible - simple mais efficace */}
          <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Target className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-xl font-bold text-white">Aim Training AI</h1>
        </div>
        {/* Sous-titre informatif - pourrait être dynamique selon l'utilisateur */}
        <div className="text-sm text-gray-400">
          Aim Training AI - Your personal aim training assistant
        </div>
      </div>
    </header>
  )
}
