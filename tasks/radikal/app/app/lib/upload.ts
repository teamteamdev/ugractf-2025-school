import path from 'path';
import { ensureDirectory } from '@/app/lib/fs';

import { headers, UnsafeUnwrappedHeaders } from 'next/headers'; // -
// + // In dev server `/public/` will be handled by Next.js, in production we handle it by web server.
// + const UPLOAD_DIR = process.env.UPLOAD_DIR || path.join(process.cwd(), 'public', 'uploads');

export function getUploadDir() {
  const token = (headers()  as unknown as UnsafeUnwrappedHeaders).get('x-token') || ''; // -
  const UPLOAD_DIR = path.join(process.env.UPLOAD_DIR || path.join(process.cwd(), 'public', 'uploads'), token); // -
  ensureDirectory(UPLOAD_DIR);
  return UPLOAD_DIR;
}
