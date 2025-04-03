import { NextResponse } from 'next/server';
import prisma from '../../utils/prisma';  // Adjust the import path if necessary
import { auth } from '@clerk/nextjs/server';

export async function POST(req: Request) {  
  try {
    const { userId } = await auth();  // Added await here

    if (!userId) {
      return new NextResponse('Unauthorized', { status: 401 });
    }

    const body = await req.json();
    const { companyName, businessType, role, phoneNumber, pincode, gstin, interestedMetals } = body;

    // Validate required fields
    if (!companyName || !businessType || !role || !phoneNumber || !pincode || !gstin) {
      return new NextResponse('Missing required fields', { status: 400 });
    }

    // Store data in the database
    const formEntry = await prisma.onboarding.create({
      data: {
        userId,
        companyName,
        businessType,
        role,
        phoneNumber,
        pincode,
        gstin,
        interestedMetals,
      },
    });

    return NextResponse.json({ success: true, data: formEntry });
  } catch (error) {
    console.error('Error saving form data:', error);
    return new NextResponse('Internal Server Error', { status: 500 });
  }
}
