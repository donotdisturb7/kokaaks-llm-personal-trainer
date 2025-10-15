import express, { Request, Response } from 'express';
import cors from 'cors';
import { KovaaksApiClient } from 'kovaaks-api-client';

const app = express();
const PORT = process.env.PORT || 9000;

// Middleware
app.use(cors());
app.use(express.json());

// Client KovaaK's
const client = new KovaaksApiClient();

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'healthy', service: 'kovaaks-proxy' });
});

// GET profile by username
app.get('/api/profile/:username', async (req: Request, res: Response) => {
  try {
    const { username } = req.params;
    const profile = await client.getProfileByUsername({ username });
    res.json({ success: true, data: profile });
  } catch (error: any) {
    console.error(`Error fetching profile:`, error.message);
    res.status(404).json({ 
      success: false, 
      error: error.message || 'Profile not found' 
    });
  }
});

// GET scenarios played by username
app.get('/api/scenarios/:username', async (req: Request, res: Response) => {
  try {
    const { username } = req.params;
    const page = parseInt(req.query.page as string) || 1;
    const max = parseInt(req.query.max as string) || 100;
    const sort = req.query.sort as string || 'plays';
    
    const scenarios = await client.getScenariosPlayedByUsername({
      username,
      page,
      max,
      sort: sort as any
    });
    
    res.json({ success: true, data: scenarios });
  } catch (error: any) {
    console.error(`Error fetching scenarios:`, error.message);
    res.status(404).json({ 
      success: false, 
      error: error.message || 'Scenarios not found' 
    });
  }
});

// GET recent high scores
app.get('/api/highscores/:username', async (req: Request, res: Response) => {
  try {
    const { username } = req.params;
    const highscores = await client.getRecentHighScoresByUsername({ username });
    res.json({ success: true, data: highscores });
  } catch (error: any) {
    console.error(`Error fetching highscores:`, error.message);
    res.status(404).json({ 
      success: false, 
      error: error.message || 'Highscores not found' 
    });
  }
});

// GET benchmark progress
app.get('/api/benchmarks/:username', async (req: Request, res: Response) => {
  try {
    const { username } = req.params;
    const page = parseInt(req.query.page as string) || 1;
    const max = parseInt(req.query.max as string) || 100;
    
    const benchmarks = await client.getBenchmarkProgressForUsername({
      username,
      page,
      max
    });
    
    res.json({ success: true, data: benchmarks });
  } catch (error: any) {
    console.error(`Error fetching benchmarks:`, error.message);
    res.status(404).json({ 
      success: false, 
      error: error.message || 'Benchmarks not found' 
    });
  }
});

// GET favorite scenarios
app.get('/api/favorites/:username', async (req: Request, res: Response) => {
  try {
    const { username } = req.params;
    const favorites = await client.getFavoriteScenariosByUsername({ username });
    res.json({ success: true, data: favorites });
  } catch (error: any) {
    console.error(`Error fetching favorites:`, error.message);
    res.status(404).json({ 
      success: false, 
      error: error.message || 'Favorites not found' 
    });
  }
});

// GET last scores by scenario name
app.get('/api/scores/:username/:scenarioName', async (req: Request, res: Response) => {
  try {
    const { username, scenarioName } = req.params;
    const scores = await client.getLastScoresByScenarioName({ username, scenarioName });
    res.json({ success: true, data: scores });
  } catch (error: any) {
    console.error(`Error fetching scores:`, error.message);
    res.status(404).json({ 
      success: false, 
      error: error.message || 'Scores not found' 
    });
  }
});

// Search scenarios by name
app.get('/api/search/scenarios', async (req: Request, res: Response) => {
  try {
    const scenarioName = req.query.name as string;
    const page = parseInt(req.query.page as string) || 1;
    const max = parseInt(req.query.max as string) || 100;
    
    if (!scenarioName) {
      return res.status(400).json({ 
        success: false, 
        error: 'Scenario name is required' 
      });
    }
    
    const scenarios = await client.searchScenariosByName({
      scenarioName,
      page,
      max
    });
    
    res.json({ success: true, data: scenarios });
  } catch (error: any) {
    console.error(`Error searching scenarios:`, error.message);
    res.status(404).json({ 
      success: false, 
      error: error.message || 'Scenarios not found' 
    });
  }
});

// GET global leaderboard
app.get('/api/leaderboard/global', async (req: Request, res: Response) => {
  try {
    const page = parseInt(req.query.page as string) || 1;
    const max = parseInt(req.query.max as string) || 100;
    
    const leaderboard = await client.getGlobalLeaderboard({
      page,
      max
    });
    
    res.json({ success: true, data: leaderboard });
  } catch (error: any) {
    console.error(`Error fetching leaderboard:`, error.message);
    res.status(500).json({ 
      success: false, 
      error: error.message || 'Leaderboard not found' 
    });
  }
});

// Error handling
app.use((err: Error, req: Request, res: Response, next: any) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ 
    success: false, 
    error: 'Internal server error' 
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 KovaaK's Proxy Server running on http://localhost:${PORT}`);
  console.log(`📊 API: http://localhost:${PORT}/api`);
  console.log(`🏥 Health: http://localhost:${PORT}/health`);
});

