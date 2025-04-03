import type { NextApiRequest, NextApiResponse } from "next";

interface RateData {
  date: string;
  rbi_reference_rate: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {
    const response = await fetch("http://127.0.0.1:5000/api/rbi_rates"); // Flask API URL
    const data: RateData[] = await response.json();

    res.status(200).json(data);
  } catch (error) {
    console.error("Error fetching data:", error);
    res.status(500).json({ message: "Failed to fetch RBI reference rates" });
  }
}