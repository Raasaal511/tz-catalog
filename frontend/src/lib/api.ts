export type Product = {
  id: number;
  title: string;
  image_url: string;
  created_at: string;
};

export type ProductList = {
  items: Product[];
  total: number;
};

function ensureScheme(url: string): string {
  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }
  if (url.includes("localhost") || url.includes("127.0.0.1")) {
    return `http://${url}`;
  }
  return `https://${url}`;
}

function getApiBaseUrl(): string {
  const raw =
    process.env.API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "http://localhost:8000";
  return ensureScheme(raw);
}

export async function fetchProducts(): Promise<ProductList> {
  const base = getApiBaseUrl().replace(/\/$/, "");
  const response = await fetch(`${base}/api/v1/products`, {
    next: { revalidate: 10 },
  });

  if (!response.ok) {
    throw new Error(`Failed to load products: ${response.status}`);
  }

  return response.json();
}
