# Deploying Stock Application on Render

This document provides step-by-step instructions for deploying the Stock Application on Render.

## Prerequisites

1. A Render account (sign up at [render.com](https://render.com))
2. Your repository pushed to GitHub or another Git provider
3. Authentication credentials (if using Clerk or other auth providers)

## Deployment Options

### Option 1: One-Click Deployment with Blueprint

1. Fork or clone this repository
2. Connect your Render account to your Git provider
3. Select the repository in Render
4. Click "Deploy with Blueprint"
5. Add the required environment variables:
   - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (if using Clerk auth)
   - `CLERK_SECRET_KEY` (if using Clerk auth)
   - Any other environment variables required by your application

### Option 2: Manual Deployment

#### Deploy the Frontend (Next.js)

1. Go to [render.com](https://render.com) and sign in
2. Click "New" and select "Web Service"
3. Connect your GitHub repository
4. Configure the following:
   - **Name**: `stock-frontend` (or your preferred name)
   - **Region**: Choose the region closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `frontend`
   - **Runtime**: `Node`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
   - **Plan**: Choose the appropriate plan (Free tier works for testing)
5. Add the following environment variables:
   - `NODE_ENV=production`
   - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key` (if using Clerk)
   - `CLERK_SECRET_KEY=your_clerk_secret_key` (if using Clerk)
   - `NEXT_PUBLIC_WHATSAPP_SCRAPER_URL=https://your-whatsapp-scraper-url.onrender.com`
   - `NEXT_PUBLIC_MCX_SCRAPER_URL=https://your-mcx-scraper-url.onrender.com`
   - `NEXT_PUBLIC_LME_SCRAPER_URL=https://your-lme-scraper-url.onrender.com`
6. Click "Create Web Service"

#### Deploy Backend Services

##### WhatsApp Scraper Service:

1. Click "New" and select "Web Service"
2. Connect your GitHub repository
3. Configure the following:
   - **Name**: `stock-whatsapp-scraper` (or your preferred name)
   - **Region**: Choose the region closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `Backend/Whatsapp-Scraping`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: Choose the appropriate plan (Free tier works for testing)
4. Add the environment variables:
   - `PORT=10000`
5. Click "Create Web Service"

##### MCX Aluminium Scraper Service:

1. Click "New" and select "Web Service"
2. Connect your GitHub repository
3. Configure the following:
   - **Name**: `stock-mcx-aluminium-scraper` (or your preferred name)
   - **Region**: Choose the same region as your other services
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `Backend/Scraping`
   - **Runtime**: `Python 3`
   - **Build Command**: `./render_build.sh`
   - **Start Command**: `python 3_months_MCX_aluminium_scrap.py`
   - **Plan**: Choose the appropriate plan
4. Add the environment variables:
   - `PORT=10001`
5. Click "Create Web Service"

##### LME Aluminium Scraper Service:

1. Click "New" and select "Web Service"
2. Connect your GitHub repository
3. Configure the following:
   - **Name**: `stock-lme-aluminium-scraper` (or your preferred name)
   - **Region**: Choose the same region as your other services
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `Backend/Scraping`
   - **Runtime**: `Python 3`
   - **Build Command**: `./render_build.sh`
   - **Start Command**: `python 3_months_LME_Aluminium_scrap.py`
   - **Plan**: Choose the appropriate plan
4. Add the environment variables:
   - `PORT=10002`
5. Click "Create Web Service"

## After Deployment

1. Once all services are deployed, update the frontend environment variables with the actual URLs of your backend services.
2. Test the application by navigating to your frontend URL.

## Troubleshooting

### CSS Build Issues

If you encounter the error "Import trace for requested module: ./app/globals.css > Build failed because of webpack errors", ensure that:

1. Your Next.js configuration is correct:
   - `next.config.js` should be a JavaScript file, not TypeScript
   - Ensure PostCSS and Tailwind configurations are properly set up

2. Make these changes before deploying:
   - Create or update `postcss.config.js` to include tailwindcss and autoprefixer
   - Update `tailwind.config.js` to include all content paths
   - Ensure package.json has the correct dependencies:
     ```json
     "devDependencies": {
       "autoprefixer": "^10.4.17",
       "postcss": "^8.4.35",
       "tailwindcss": "^3.4.1"
     }
     ```

### Other Common Issues

- **Selenium Issues**: For scrapers using Selenium, you may need to add additional build steps to install Chrome and ChromeDriver. Use the provided `render_build.sh` script for this purpose.

- **CORS Issues**: If you experience CORS issues, ensure that your backend services allow requests from your frontend domain.

- **Memory Issues**: For more intensive scraping operations, you may need to upgrade to a higher-tier plan on Render.

## Monitoring

Render provides built-in logging and monitoring. Access logs by clicking on your service and selecting the "Logs" tab. 