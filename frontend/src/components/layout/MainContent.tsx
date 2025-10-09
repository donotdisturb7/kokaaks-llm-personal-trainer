"use client"

import { TabsContent } from "@/components/ui/tabs"
import { ChatInterface } from "@/components/chat/ChatInterface"
import { ExercisesTab } from "@/components/exercises/ExercisesTab"
import { BarChart3, Settings } from "lucide-react"

/**
 * Composant MainContent - Zone de contenu principal
 * Gère l'affichage du contenu selon l'onglet sélectionné
 */
export function MainContent() {
  return (
    <div className="flex-1 flex flex-col">
      <TabsContent value="chat" className="flex-1 m-0">
        <ChatInterface />
      </TabsContent>

      <TabsContent value="exercises" className="flex-1 m-0">
        <ExercisesTab />
      </TabsContent>

      <TabsContent value="stats" className="flex-1 m-0 p-6">
        <div className="h-full flex items-center justify-center">
          <div className="text-center">
            <BarChart3 className="h-16 w-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Tableau de Bord</h3>
            <p className="text-gray-400">
              Vos statistiques KovaaK's et suivi de progression apparaîtront ici.
            </p>
          </div>
        </div>
      </TabsContent>

      <TabsContent value="settings" className="flex-1 m-0 p-6">
        <div className="h-full flex items-center justify-center">
          <div className="text-center">
            <Settings className="h-16 w-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Paramètres</h3>
            <p className="text-gray-400">
              Configurez votre assistant IA et vos préférences d'entraînement.
            </p>
          </div>
        </div>
      </TabsContent>
    </div>
  )
}
