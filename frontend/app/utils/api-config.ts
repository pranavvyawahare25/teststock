// API configuration for different environments

interface ApiConfig {
  whatsappScraperUrl: string;
  mcxAluminiumScraperUrl: string;
  lmeAluminiumScraperUrl: string;
}

// Default to local development URLs
const localConfig: ApiConfig = {
  whatsappScraperUrl: 'http://localhost:3232',
  mcxAluminiumScraperUrl: 'http://localhost:5002',
  lmeAluminiumScraperUrl: 'http://localhost:5003',
};

// Production URLs from environment variables
const productionConfig: ApiConfig = {
  whatsappScraperUrl: process.env.NEXT_PUBLIC_WHATSAPP_SCRAPER_URL || '',
  mcxAluminiumScraperUrl: process.env.NEXT_PUBLIC_MCX_SCRAPER_URL || '',
  lmeAluminiumScraperUrl: process.env.NEXT_PUBLIC_LME_SCRAPER_URL || '',
};

// Determine which config to use
const isProduction = process.env.NODE_ENV === 'production';
const config: ApiConfig = isProduction ? productionConfig : localConfig;

export default config; 