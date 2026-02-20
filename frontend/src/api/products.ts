import { api } from "./client";
import type { Product, ProductCreate, ProductUpdate } from "@/types";

export async function listProducts(skip = 0, limit = 100): Promise<Product[]> {
  const res = await api.get<Product[]>("/api/v1/products", { params: { skip, limit } });
  return res.data;
}

export async function getProduct(id: number): Promise<Product> {
  const res = await api.get<Product>(`/api/v1/products/${id}`);
  return res.data;
}

export async function createProduct(data: ProductCreate): Promise<Product> {
  const res = await api.post<Product>("/api/v1/products", data);
  return res.data;
}

export async function updateProduct(id: number, data: ProductUpdate): Promise<Product> {
  const res = await api.put<Product>(`/api/v1/products/${id}`, data);
  return res.data;
}

export async function deleteProduct(id: number): Promise<void> {
  await api.delete(`/api/v1/products/${id}`);
}
