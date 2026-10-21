"use client";

import { useCallback, useEffect, useState } from "react";

import { getPublicApiBaseUrl, type Product } from "@/lib/api";

const POLL_MS = 2000;

type CatalogProps = {
  initialItems: Product[];
  initialError: string | null;
};

export function Catalog({ initialItems, initialError }: CatalogProps) {
  const [items, setItems] = useState<Product[]>(initialItems);
  const [error, setError] = useState<string | null>(initialError);

  const load = useCallback(async () => {
    try {
      const base = getPublicApiBaseUrl();
      const response = await fetch(`${base}/api/v1/products`, {
        cache: "no-store",
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = (await response.json()) as { items: Product[] };
      setItems(data.items);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось загрузить каталог");
    }
  }, []);

  useEffect(() => {
    const id = window.setInterval(() => {
      void load();
    }, POLL_MS);
    return () => window.clearInterval(id);
  }, [load]);

  return (
    <main>
      <h1>Каталог</h1>

      {error ? <p className="error">{error}</p> : null}

      {!error && items.length === 0 ? (
        <p className="empty">Товаров пока нет</p>
      ) : null}

      {!error && items.length > 0 ? (
        <ul className="catalog">
          {items.map((product) => (
            <li key={product.id}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={product.image_url} alt={product.title} />
              <div className="title">{product.title}</div>
            </li>
          ))}
        </ul>
      ) : null}
    </main>
  );
}
