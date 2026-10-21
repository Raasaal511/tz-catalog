import { Catalog } from "@/components/Catalog";
import { fetchProducts } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function CatalogPage() {
  let initialError: string | null = null;
  let initialItems: Awaited<ReturnType<typeof fetchProducts>>["items"] = [];

  try {
    const data = await fetchProducts();
    initialItems = data.items;
  } catch (err) {
    initialError = err instanceof Error ? err.message : "Не удалось загрузить каталог";
  }

  return <Catalog initialItems={initialItems} initialError={initialError} />;
}
