"use client"

import { MessageCircle, Target, BarChart3, Settings } from "lucide-react"
import { TabsList, TabsTrigger } from "@/components/ui/tabs"

/**
 * Composant Sidebar - Barre latérale de navigation
 * Contient les onglets de navigation principaux
 * 
 * NOTE: La largeur est fixée à w-64 (256px) - assez large pour être confortable
 * HACK: Utilise TabsList mais en mode vertical, pas très standard mais ça marche
 */
export function Sidebar() {
  return (
    <TabsList className="flex flex-col w-64 bg-gray-900 border-r border-gray-800 rounded-none h-full">
      {/* Onglet Chat - le plus utilisé probablement */}
      <TabsTrigger 
        value="chat" 
        className="flex items-center gap-3 justify-start px-4 py-3 w-full data-[state=active]:bg-gray-800 data-[state=active]:text-white"
      >
        <MessageCircle className="h-5 w-5" />
        Chat
      </TabsTrigger>
      
      {/* Onglet Exercices - bibliothèque d'exercices KovaaK's */}
      <TabsTrigger 
        value="exercises" 
        className="flex items-center gap-3 justify-start px-4 py-3 w-full data-[state=active]:bg-gray-800 data-[state=active]:text-white"
      >
        <Target className="h-5 w-5" />
        Exercices
      </TabsTrigger>
      
      {/* Onglet Stats - pour voir les progrès */}
      <TabsTrigger 
        value="stats" 
        className="flex items-center gap-3 justify-start px-4 py-3 w-full data-[state=active]:bg-gray-800 data-[state=active]:text-white"
      >
        <BarChart3 className="h-5 w-5" />
        Statistiques
      </TabsTrigger>
      
      {/* Onglet Paramètres - configuration de l'IA */}
      <TabsTrigger 
        value="settings" 
        className="flex items-center gap-3 justify-start px-4 py-3 w-full data-[state=active]:bg-gray-800 data-[state=active]:text-white"
      >
        <Settings className="h-5 w-5" />
        Paramètres
      </TabsTrigger>
    </TabsList>
  )
}
