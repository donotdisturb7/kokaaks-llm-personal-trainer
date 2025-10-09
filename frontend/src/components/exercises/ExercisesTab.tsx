"use client"

import { useState } from "react"
import { ExerciseCard } from "./ExerciseCard"
import { Search, Filter } from "lucide-react"

// Exercices d'exemple - à remplacer par une vraie API plus tard
// Ces exercices sont basés sur les classiques de KovaaK's
const sampleExercises = [
  {
    id: "1",
    title: "1wall6targets TE",
    description: "Exercice de tracking classique axé sur les mouvements fluides de souris et l'acquisition de cibles. Parfait pour développer les compétences de tracking de base.",
    difficulty: "Beginner" as const,
    duration: "10-15 min",
    category: "Tracking"
  },
  {
    id: "2", 
    title: "Close Fast Strafes",
    description: "Exercice de changement de cibles à haute vitesse pour améliorer le temps de réaction et la précision des flicks. Parfait pour les scénarios compétitifs.",
    difficulty: "Intermediate" as const,
    duration: "5-10 min",
    category: "Flicking"
  },
  {
    id: "3",
    title: "Tile Frenzy 180",
    description: "Entraînement de précision avancé avec des rotations de 180 degrés. Défie à la fois la précision et la conscience spatiale.",
    difficulty: "Advanced" as const,
    duration: "15-20 min", 
    category: "Precision"
  },
  {
    id: "4",
    title: "Pasu Track",
    description: "Smooth tracking exercise with varying target speeds. Excellent for building consistent tracking muscle memory.",
    difficulty: "Beginner" as const,
    duration: "8-12 min",
    category: "Tracking"
  },
  {
    id: "5",
    title: "Bounce 180",
    description: "Dynamic target switching with unpredictable movement patterns. Tests both tracking and flicking abilities.",
    difficulty: "Advanced" as const,
    duration: "12-18 min",
    category: "Hybrid"
  },
  {
    id: "6",
    title: "Microshot Speed",
    description: "Ultra-precise clicking exercise for building pixel-perfect accuracy. Essential for long-range engagements.",
    difficulty: "Intermediate" as const,
    duration: "6-10 min",
    category: "Precision"
  }
]

export function ExercisesTab() {
  // États pour la recherche et le filtrage
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("All")
  
  // Catégories disponibles - pourrait venir d'une API
  const categories = ["All", "Tracking", "Flicking", "Precision", "Hybrid"]
  
  // Filtrage des exercices selon la recherche et la catégorie
  const filteredExercises = sampleExercises.filter(exercise => {
    const matchesSearch = exercise.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         exercise.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === "All" || exercise.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-800">
        <h2 className="text-2xl font-bold text-white mb-4">Aim Training Exercises</h2>
        
        {/* Search and Filter */}
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search exercises..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Exercises Grid */}
      <div className="flex-1 p-6 overflow-y-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredExercises.map((exercise) => (
            <ExerciseCard
              key={exercise.id}
              title={exercise.title}
              description={exercise.description}
              difficulty={exercise.difficulty}
              duration={exercise.duration}
              category={exercise.category}
              onSelect={() => {
                // TODO: Implement exercise selection logic
                console.log("Selected exercise:", exercise.title)
              }}
            />
          ))}
        </div>
        
        {filteredExercises.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg">No exercises found matching your criteria.</p>
          </div>
        )}
      </div>
    </div>
  )
}
