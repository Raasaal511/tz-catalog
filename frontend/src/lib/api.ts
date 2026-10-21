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

/** Browser / client: only NEXT_PUBLIC_* is available. */
export function getPublicApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  return ensureScheme(raw).replace(/\/$/, "");
}

/** Server: prefer internal Docker URL, fall back to public. */
export function getServerApiBaseUrl(): string {
  const raw =
    process.env.API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "http://localhost:8000";
  return ensureScheme(raw).replace(/\/$/, "");
}

export async function fetchProducts(baseUrl?: string): Promise<ProductList> {
  const base = (baseUrl || getServerApiBaseUrl()).replace(/\/$/, "");
  const response = await fetch(`${base}/api/v1/products`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to load products: ${response.status}`);
  }

  return response.json();
}
