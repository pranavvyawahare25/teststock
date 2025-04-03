import { NextRequest, NextResponse } from 'next/server';
import prisma from '../../utils/prisma';
import { auth } from '@clerk/nextjs/server';

export async function POST(req: NextRequest) {
  try {
    const { userId } = await auth();

    if (!userId) {
      return new NextResponse('Unauthorized', { status: 401 });
    }

    const body = await req.json();
    const { companyName, businessType, role, phoneNumber, pincode, gstin, interestedMetals } = body;

    // Validate required fields
    if (!companyName || !businessType || !role || !phoneNumber || !pincode || !gstin) {
      return new NextResponse('Missing required fields', { status: 400 });
    }

    // Store or update data in the database
    const formEntry = await prisma.onboarding.upsert({
      where: {
        userId: userId
      },
      update: {
        companyName,
        businessType,
        role,
        phoneNumber,
        pincode,
        gstin,
        interestedMetals,
      },
      create: {
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
