import { NextRequest, NextResponse } from 'next/server';
import path from 'path';
import { addImage, getAllImages } from '@/app/lib/db';
import { renderFormula } from '@/app/lib/mathjax';
import { getUploadDir } from '@/app/lib/upload';
import cuid from 'cuid';


export async function GET() {
  try {
    const formulas = getAllImages();
    return NextResponse.json(formulas);
  } catch (error) {
    console.error('Error retrieving formulas:', error);
    return NextResponse.json(
      { error: 'Не получилось получить формулы' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const { name, description, latex, password } = await request.json();

    if (!name || !latex || !password) {
      return NextResponse.json(
        { error: 'Не заполнены обязательные поля' },
        { status: 400 }
      );
    }

    const createdAt = new Date();
    const filename = `formula_${cuid.slug()}.svg`;
    const filepath = path.join(getUploadDir(), filename);

    await renderFormula(latex, filepath);

    const imageId = addImage({
      name,
      description,
      filename,
      password: password || undefined,
      createdAt
    });

    return NextResponse.json({ success: true, id: imageId }, { status: 201 });
  } catch (error) {
    console.error('Error processing formula submission:', error);
    return NextResponse.json(
      { error: 'Не удалось добавить формулу' },
      { status: 500 }
    );
  }
}
