import { KovaaksApiClient } from 'kovaaks-api-client';

/**
 * Script pour trouver TOUS les joueurs de Martinique et leur position dans le top global
 */
class AllMartiniquePlayersFinder {
  private client: KovaaksApiClient;

  constructor() {
    this.client = new KovaaksApiClient();
  }

  async findAllMartiniquePlayers(): Promise<void> {
    console.log('Recherche de TOUS les joueurs de Martinique (MQ)...');
    console.log('=' .repeat(60));

    let foundPlayers: any[] = [];
    let page = 1;
    let totalPlayersChecked = 0;
    const maxPages = 5000; // Aller jusqu'au top 500,000 (5000 pages x 100 joueurs)

    while (page <= maxPages) {
      try {
        // Afficher la progression tous les 10 pages
        if (page % 10 === 1 || page <= 10) {
          console.log(`\nPage ${page} - Vérification des positions ${totalPlayersChecked + 1} à ${totalPlayersChecked + 100}...`);
        }
        
        const leaderboard = await this.client.getGlobalLeaderboard({
          page,
          max: 100
        });

        // Chercher les joueurs de Martinique sur cette page
        leaderboard.data.forEach((player: any, index: number) => {
          if (player.country && player.country.toLowerCase() === 'mq') {
            const globalPosition = totalPlayersChecked + index + 1;
            foundPlayers.push({
              ...player,
              globalPosition
            });
            console.log(`🎯 TROUVÉ! Position ${globalPosition}: ${player.webappUsername || player.steamAccountName}`);
          }
        });

        totalPlayersChecked += leaderboard.data.length;

        // Si on a moins de 100 joueurs, on a atteint la fin
        if (leaderboard.data.length < 100) {
          console.log('Fin des données atteinte');
          break;
        }

        page++;
        
        // Afficher la progression tous les 50 pages
        if (page % 50 === 0) {
          console.log(`📊 Progression: ${page}/5000 pages (${totalPlayersChecked} joueurs vérifiés) - ${foundPlayers.length} joueur(s) de Martinique trouvé(s)`);
        }
        
        // Pause plus courte pour aller plus vite
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.log(`Erreur page ${page}: ${error}`);
        break;
      }
    }

    console.log(`\n${'='.repeat(60)}`);
    console.log(`RÉSULTATS FINAUX`);
    console.log(`=${'='.repeat(59)}`);
    console.log(`Pages analysées: ${page - 1}`);
    console.log(`Joueurs vérifiés: ${totalPlayersChecked}`);
    console.log(`Joueurs de Martinique trouvés: ${foundPlayers.length}`);

    if (foundPlayers.length > 0) {
      console.log(`\n🏆 TOUS LES JOUEURS DE MARTINIQUE TROUVÉS:`);
      console.log(`${'='.repeat(60)}`);
      
      // Trier par position globale
      foundPlayers.sort((a, b) => a.globalPosition - b.globalPosition);
      
      foundPlayers.forEach((player, index) => {
        console.log(`\n${index + 1}. 🥇 Position globale: #${player.globalPosition}`);
        console.log(`   Nom: ${player.webappUsername || player.steamAccountName}`);
        console.log(`   Points: ${parseInt(player.points).toLocaleString()}`);
        console.log(`   Scénarios joués: ${player.scenariosCount}`);
        console.log(`   Completions: ${player.completionsCount}`);
        console.log(`   Pays: ${player.country}`);
        console.log(`   Kovaaks Plus: ${player.kovaaksPlusActive ? 'Oui' : 'Non'}`);
        console.log(`   Changement de rang: ${player.rankChange > 0 ? '+' : ''}${player.rankChange}`);
      });

      // Statistiques
      const bestPosition = Math.min(...foundPlayers.map(p => p.globalPosition));
      const worstPosition = Math.max(...foundPlayers.map(p => p.globalPosition));
      const totalPoints = foundPlayers.reduce((sum, p) => sum + parseInt(p.points), 0);
      const avgPoints = Math.round(totalPoints / foundPlayers.length);

      console.log(`\n📊 STATISTIQUES:`);
      console.log(`${'='.repeat(30)}`);
      console.log(` Meilleure position: #${bestPosition}`);
      console.log(` Pire position: #${worstPosition}`);
      console.log(` Moyenne des points: ${avgPoints.toLocaleString()}`);
      console.log(` Total des points: ${totalPoints.toLocaleString()}`);

    } else {
    console.log(`\n❌ Aucun joueur de Martinique trouvé dans les ${totalPlayersChecked} premiers joueurs.`);
    console.log(`\n💡 Possibilités:`);
    console.log(`   - Les joueurs de Martinique sont au-delà de la position ${totalPlayersChecked}`);
    console.log(`   - Ils utilisent un autre code pays (ex: FR pour France)`);
    console.log(`   - Ils ne sont pas dans le top global`);
    console.log(`   - Ils ne jouent pas à KovaaK's`);
    }
  }

  async searchAlternativeCountryCodes(): Promise<void> {
    console.log(`\n🔍 Recherche avec d'autres codes pays possibles...`);
    console.log(`${'='.repeat(50)}`);
    
    const alternativeCodes = ['fr', 'gp', 'gf']; // France, Guadeloupe, Guyane française
    let page = 1;
    const maxPages = 5;

    for (const countryCode of alternativeCodes) {
      console.log(`\nRecherche avec le code: ${countryCode.toUpperCase()}`);
      let found = 0;
      page = 1;

      while (page <= maxPages) {
        try {
          const leaderboard = await this.client.getGlobalLeaderboard({
            page,
            max: 100
          });

          const players = leaderboard.data.filter((player: any) => 
            player.country && player.country.toLowerCase() === countryCode.toLowerCase()
          );

          if (players.length > 0) {
            found += players.length;
            console.log(`  Page ${page}: ${players.length} joueur(s) trouvé(s)`);
          }

          page++;
          await new Promise(resolve => setTimeout(resolve, 100));
          
        } catch (error) {
          break;
        }
      }

      console.log(`  Total pour ${countryCode.toUpperCase()}: ${found} joueur(s)`);
    }
  }
}

async function main(): Promise<void> {
  const finder = new AllMartiniquePlayersFinder();
  
  await finder.findAllMartiniquePlayers();
  await finder.searchAlternativeCountryCodes();
  
  console.log(`\n✅ Recherche terminée!`);
}

// Gestion des erreurs
process.on('unhandledRejection', (reason, promise) => {
  console.log('Erreur non gérée:', reason);
  process.exit(1);
});

// Lancer la recherche
if (require.main === module) {
  main().catch(console.error);
}
