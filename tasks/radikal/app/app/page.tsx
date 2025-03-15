'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import '@/app/page.module.css';

interface Image {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

export default function Home() {
  const [images, setImages] = useState<Image[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState<number | null>(null);
  const [passwordInput, setPasswordInput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [formulaImage, setFormulaImage] = useState<string | null>(null);
  const passwordInputRef = useRef<HTMLInputElement>(null);
  const popupContentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(process.env.basePath + '/api/formulas')
      .then(response => response.json())
      .then(data => {
        setImages(data);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error fetching formulas:', error);
        setIsLoading(false);
      });
  }, []);

  useEffect(() => {
    if (selectedImage && passwordInputRef.current) {
      passwordInputRef.current.focus();
    }
  }, [selectedImage]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && selectedImage !== null) {
        closePopup();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [selectedImage]);

  const handleCardClick = (id: number) => {
    setSelectedImage(id);
    setPasswordInput('');
    setError(null);
    setFormulaImage(null);
  };

  const closePopup = () => {
    setSelectedImage(null);
    setPasswordInput('');
    setError(null);
    setFormulaImage(null);
  };

  const verifyPassword = async () => {
    if (!selectedImage || !passwordInput.trim()) return;

    try {
      const response = await fetch(process.env.basePath + '/api/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: selectedImage,
          password: passwordInput,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setFormulaImage(process.env.basePath + `/uploads/${data.filename}`);
        setError(null);
      } else {
        setError('Неверный пароль');
      }
    } catch (err) {
      setError('Failed to verify password');
      console.error('Error verifying password:', err);
    }
  };

  const handleOutsideClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (popupContentRef.current && !popupContentRef.current.contains(event.target as Node)) {
      closePopup();
    }
  };

  return (
    <div>
      <div style={{
        padding: '2rem',
        background: '#f7f7f7',
        borderRadius: 'var(--border-radius)',
        marginTop: '2rem'
      }}>
        <p style={{ marginBottom: '1rem' }}>
          Радикал-Формула - исторически первый и один из наиболее используемых в Рунете «однокликовых» хостингов формул. Начиная с 2005 года, на проект загружено более 600 млн. формул. Формулы с Радикал-Формула в той или иной мере используются на порядка 10 тыс. самых разнообразных статей.
        </p>
        <Link href="/add" style={{
          display: 'inline-block',
          marginTop: '1rem',
          padding: '0.5rem 1rem',
          background: 'var(--primary-color, #0070f3)',
          color: 'white',
          textDecoration: 'none',
          borderRadius: 'var(--border-radius)',
        }}>
          Добавить формулу
        </Link>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h3>Последние формулы</h3>
        {isLoading ? (
          <p>Загружаем формулы...</p>
        ) : images.length > 0 ? (
          <ul style={{
            listStyle: 'none',
            padding: 0,
            marginTop: '1rem'
          }}>
            {images.map((image) => (
              <li
                key={image.id}
                onClick={() => handleCardClick(image.id)}
                style={{
                  padding: '1rem',
                  marginBottom: '1rem',
                  border: '1px solid #eaeaea',
                  borderRadius: 'var(--border-radius)',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <h4 style={{ margin: '0 0 0.5rem 0' }}>{image.name}</h4>
                {image.description && (
                  <p style={{ margin: '0 0 0.5rem 0', color: '#666' }}>{image.description}</p>
                )}
                <p style={{ margin: 0, fontSize: '0.8rem', color: '#888' }} title={image.created_at}>
                  Создано: {new Date(image.created_at).toLocaleString()}
                </p>
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ marginTop: '1rem' }}>Создайте первую формулу!</p>
        )}
      </div>

      <p style={{ marginTop: '2rem' }}>
      Cервис позволяет легко и быстро публиковать ваши формулы на страницах любого интернет-форума, блога, чата, доске объявлений (необходимая подготовка выполняется автоматически). Вам нужно только РАЗРАБОТАТЬ формулу, нажать кнопку ЗАГРУЗИТЬ и затем скопировать ссылку на наш сервис в свое сообщение.
      </p>
      <p>Кроме того данный хостинг обладает множеством преимуществ:</p>
      <p>- Не требует регистрации<br/>
- Срок хранения неограничен*<br/>
- Максимальный объем формулы до 40 дробей и больше<br/>
- Загрузка радикалов без ограничений<br/>
- Возможность загрузки изображений с помощью:<br/>
   - новой Мобильной версии РАДИКАЛ – ФОРМУЛА<br/>
- Сервис полностью бесплатен</p>
      <p>*если к формуле не было обращения больше года, то данный контент считается потеряным и удаляется.</p>

      {selectedImage && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000,
          }}
          onClick={handleOutsideClick}
        >
          <div
            ref={popupContentRef}
            style={{
              background: 'white',
              padding: '2rem',
              borderRadius: 'var(--border-radius)',
              width: '90%',
              maxWidth: formulaImage ? '800px' : '400px',
              boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
              maxHeight: '90vh',
              overflow: 'auto',
            }}
          >
            {!formulaImage ? (
              <>
                <h3 style={{ marginTop: 0 }}>Введите пароль</h3>
                <p style={{marginBottom: '0.5rem'}}>Для доступа к этой формуле нужен пароль. Введите его:</p>

                {error && (
                  <div style={{
                    color: 'red',
                    marginBottom: '0.5rem',
                    padding: '0.5rem',
                    background: '#ffeeee',
                    borderRadius: 'var(--border-radius)'
                  }}>
                    {error}
                  </div>
                )}

                <input
                  ref={passwordInputRef}
                  type="password"
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ccc',
                    borderRadius: 'var(--border-radius)',
                    marginBottom: '1rem',
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') verifyPassword();
                  }}
                />

                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button
                    onClick={verifyPassword}
                    style={{
                      padding: '0.5rem 1rem',
                      background: 'var(--primary-color, #0070f3)',
                      color: 'white',
                      border: 'none',
                      borderRadius: 'var(--border-radius)',
                      cursor: 'pointer',
                    }}
                  >
                    Открыть
                  </button>

                  <button
                    onClick={closePopup}
                    style={{
                      padding: '0.5rem 1rem',
                      background: 'transparent',
                      border: '1px solid #ccc',
                      borderRadius: 'var(--border-radius)',
                      cursor: 'pointer',
                    }}
                  >
                    Закрыть
                  </button>
                </div>
              </>
            ) : (
              <>
                <div style={{ textAlign: 'center' }}>
                  <h3>Формула</h3>
                  <p>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={formulaImage}
                    alt="Формула"
                    style={{
                      width: '90%',
                      maxWidth: '100%',
                      maxHeight: '5rem',
                      margin: '1rem 0'
                    }}
                  />
                  </p>
                  <button
                    onClick={closePopup}
                    style={{
                      padding: '0.5rem 1rem',
                      background: 'var(--primary-color, #0070f3)',
                      color: 'white',
                      border: 'none',
                      borderRadius: 'var(--border-radius)',
                      cursor: 'pointer',
                    }}
                  >
                    Закрыть
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
