import { fetchProducts } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function CatalogPage() {
  let error: string | null = null;
  let items: Awaited<ReturnType<typeof fetchProducts>>["items"] = [];

  try {
    const data = await fetchProducts();
    items = data.items;
  } catch (err) {
    error = err instanceof Error ? err.message : "Не удалось загрузить каталог";
  }

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
