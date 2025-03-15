import { NextRequest, NextResponse } from 'next/server';
import { getImageById } from '@/app/lib/db';

export async function POST(request: NextRequest) {
  try {
    const { id, password } = await request.json();

    if (!id || !password) {
      return NextResponse.json({
        success: false,
        error: 'Не указаны обязательные поля'
      }, { status: 400 });
    }

    const image = getImageById(Number(id));

    if (!image) {
      return NextResponse.json({
        success: false,
        error: 'Формула не найдена'
      }, { status: 404 });
    }

    if (image.password !== password) {
      return NextResponse.json({
        success: false,
        error: 'Неверный пароль'
      }, { status: 403 });
    }

    return NextResponse.json({
      success: true,
      filename: image.filename
    });
  } catch (error) {
    console.error('Error verifying formula password:', error);
    return NextResponse.json(
      { success: false, error: 'Не получилось проверить пароль' },
      { status: 500 }
    );
  }
}
