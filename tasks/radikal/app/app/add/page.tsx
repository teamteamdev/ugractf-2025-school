'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import '@/app/page.module.css';

export default function AddFormula() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [latex, setLatex] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    if (!name || !latex || !password) {
      setError('Не заполнены обязательные поля');
      setIsSubmitting(false);
      return;
    }

    try {
      const response = await fetch(process.env.basePath + '/api/formulas', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          description,
          latex,
          password,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Не получилось добавить формулу');
      }

      router.push('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Что-то пошло не так');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <h2>Добавить новую формулу</h2>

      <form onSubmit={handleSubmit} style={{ marginTop: '1.5rem' }}>
        {error && (
          <div style={{ color: 'red', marginBottom: '1rem', padding: '0.5rem', background: '#ffeeee', borderRadius: 'var(--border-radius)' }}>
            {error}
          </div>
        )}

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="name" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
            Название*
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ccc',
              borderRadius: 'var(--border-radius)',
            }}
          />
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="description" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
            Описание (необязательно)
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ccc',
              borderRadius: 'var(--border-radius)',
              font: 'inherit'
            }}
          ></textarea>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="latex" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
            Формула в формате LaTeX*
          </label>
          <textarea
            id="latex"
            value={latex}
            onChange={(e) => setLatex(e.target.value)}
            required
            rows={5}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ccc',
              borderRadius: 'var(--border-radius)',
              fontFamily: 'monospace',
            }}
            placeholder="Например: \frac{-b \pm \sqrt{b^2-4ac}}{2a}"
          ></textarea>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
            Пароль*
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ccc',
              borderRadius: 'var(--border-radius)',
            }}
          />
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              padding: '0.5rem 1rem',
              background: 'var(--primary-color, #0070f3)',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--border-radius)',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              opacity: isSubmitting ? 0.7 : 1,
            }}
          >
            {isSubmitting ? 'Сохраняется...' : 'Загрузить'}
          </button>

          <button
            type="button"
            onClick={() => router.push('/')}
            style={{
              padding: '0.5rem 1rem',
              background: 'transparent',
              border: '1px solid #ccc',
              borderRadius: 'var(--border-radius)',
              cursor: 'pointer',
            }}
          >
            Отменить
          </button>
        </div>
      </form>
    </div>
  );
}
