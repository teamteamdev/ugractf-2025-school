import Database from 'better-sqlite3';
import path from 'node:path';
import { ensureDirectory } from '@/app/lib/fs';

import { headers, UnsafeUnwrappedHeaders } from 'next/headers'; // -
const dbCache = new Map<string, Database.Database>(); // -
const DB_PATH = process.env.DATABASE_PATH || process.cwd();
// + let db: Database.Database | null = null;

const initializeDatabase = (): Database.Database => {
  // + if (db) return db;
  const token = (headers()  as unknown as UnsafeUnwrappedHeaders).get('x-token') || ''; // -
  const cachedDb = dbCache.get(token); // -
  if (cachedDb) { // -
    return cachedDb; // -
  } // -

  ensureDirectory(DB_PATH);
  // + db = new Database(path.join(DB_PATH, 'db.sqlite'));
  const db = new Database(path.join(DB_PATH, `${token}.sqlite`)); // -
  dbCache.set(token, db); // -

  db.exec(`
    CREATE TABLE IF NOT EXISTS images (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT,
      filename TEXT NOT NULL,
      password TEXT NOT NULL,
      created_at TEXT NOT NULL
    )
  `);

  return db;
};

export interface ImageListItem {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

export const getAllImages = (): ImageListItem[] => {
  const db = initializeDatabase();
  return db.prepare(`
    SELECT id, name, description, created_at
    FROM images
    ORDER BY created_at DESC
  `).all() as ImageListItem[];
};

export interface ImageRecord {
  id: number;
  name: string;
  description: string | null;
  filename: string;
  password: string;
  created_at: string;
}

export const getImageById = (id: number): ImageRecord | undefined => {
  const db = initializeDatabase();
  return db.prepare('SELECT * FROM images WHERE id = ?').get(id) as ImageRecord | undefined;
};

export interface NewImage {
  name: string;
  description?: string;
  filename: string;
  password: string;
  createdAt: Date;
}

export const addImage = (image: NewImage): number => {
  const db = initializeDatabase();
  const stmt = db.prepare(
    'INSERT INTO images (name, description, filename, password, created_at) VALUES (?, ?, ?, ?, ?)'
  );

  const info = stmt.run(
    image.name,
    image.description || null,
    image.filename,
    image.password,
    image.createdAt.toISOString(),
  );

  return info.lastInsertRowid as number;
};

export const deleteImage = (id: number, password?: string): boolean => {
  const db = initializeDatabase();
  const image = getImageById(id);

  if (!image) return false;
  if (image.password && image.password !== password) return false;

  const info = db.prepare('DELETE FROM images WHERE id = ?').run(id);
  return info.changes > 0;
};
