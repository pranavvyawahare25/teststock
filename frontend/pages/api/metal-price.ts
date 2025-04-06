import { NextApiRequest, NextApiResponse } from 'next';

interface PriceData {
  spot_price: number;
  price_change: number;
  change_percentage: number;
  last_updated: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {
    const response = await fetch('https://591c-2401-4900-57a3-b6fb-69c5-cc00-b7cb-2af0.ngrok-free.app/api/price-data');
    
    if (!response.ok) {
      throw new Error('Failed to fetch price data');
    }
    
    const data: PriceData = await response.json();
    
    // Transform the data to match the frontend's expected format
    const transformedData = {
      spotPrice: data.spot_price,
      change: data.price_change,
      changePercent: data.change_percentage,
      lastUpdated: data.last_updated
    };
    
    res.status(200).json(transformedData);
  } catch (error) {
    console.error('Error fetching price data:', error);
    res.status(500).json({ error: 'Failed to fetch price data' });
  }
} 