"use client"

import { TabsContent } from "@/components/ui/tabs"
import { ChatInterface } from "@/components/chat/ChatInterface"
import ArtifactsTab from "@/components/artifacts/ArtifactsTab"
import PdfUploaderTab from "@/components/rag/PdfUploaderTab"
import { BarChart3, Settings } from "lucide-react"

/**
 * Composant MainContent - Zone de contenu principal
 * Gère l'affichage du contenu selon l'onglet sélectionné
 */
export function MainContent() {
  return (
    <>
      <TabsContent value="chat" className="m-0 flex-1 h-full overflow-hidden data-[state=active]:flex data-[state=active]:flex-col">
        <ChatInterface />
      </TabsContent>

      <TabsContent value="artifacts" className="m-0 flex-1 h-full overflow-auto p-6 data-[state=active]:flex data-[state=active]:flex-col">
        <ArtifactsTab />
      </TabsContent>

      <TabsContent value="pdf" className="m-0 flex-1 h-full overflow-auto p-6 data-[state=active]:flex data-[state=active]:flex-col">
        <PdfUploaderTab />
      </TabsContent>

      <TabsContent value="stats" className="m-0 flex-1 h-full overflow-auto p-6 data-[state=active]:flex data-[state=active]:flex-col">
        <div className="h-full flex items-center justify-center">
          <div className="text-center p-8 rounded-2xl bg-black/20 backdrop-blur-sm border border-white/5">
            <div className="h-20 w-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-[hsl(var(--harvest-orange))] to-orange-600 flex items-center justify-center shadow-[0_0_20px_rgba(255,120,0,0.3)]">
              <BarChart3 className="h-10 w-10 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">Tableau de Bord</h3>
            <p className="text-white/60 max-w-md mx-auto">
              Vos statistiques KovaaK's et suivi de progression apparaîtront ici.
            </p>
          </div>
        </div>
      </TabsContent>

      <TabsContent value="settings" className="m-0 flex-1 h-full overflow-auto p-6 data-[state=active]:flex data-[state=active]:flex-col">
        <div className="h-full flex items-center justify-center">
          <div className="text-center p-8 rounded-2xl bg-black/20 backdrop-blur-sm border border-white/5">
            <div className="h-20 w-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-[hsl(var(--harvest-orange))] to-orange-600 flex items-center justify-center shadow-[0_0_20px_rgba(255,120,0,0.3)]">
              <Settings className="h-10 w-10 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">Paramètres</h3>
            <p className="text-white/60 max-w-md mx-auto">
              Configurez votre assistant IA et vos préférences d'entraînement.
            </p>
          </div>
        </div>
      </TabsContent>
    </>
  )
}
