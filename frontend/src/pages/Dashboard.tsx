import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuthStore } from "@/store/authStore";
import { listProducts } from "@/api/products";
import type { Product } from "@/types";
import { LayoutDashboard, LogOut, Plus, User } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { AddProductDialog } from "@/components/AddProductDialog";
import { EditProductDialog } from "@/components/EditProductDialog";
import { deleteProduct } from "@/api/products";
import { useToast } from "@/hooks/useToast";

export default function Dashboard() {
  const { email, role, logout, isAdmin } = useAuthStore();
  const { toast } = useToast();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [addOpen, setAddOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  async function handleDelete(p: Product) {
    if (!confirm(`Delete "${p.name}"?`)) return;
    try {
      await deleteProduct(p.id);
      toast({ title: "Product deleted", variant: "success" });
      loadProducts();
    } catch {
      toast({ title: "Failed to delete", variant: "destructive" });
    }
  }

  const loadProducts = async () => {
    try {
      const data = await listProducts();
      setProducts(data);
    } catch {
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  return (
    <div className="min-h-screen bg-muted/30">
      <header className="border-b bg-card">
        <div className="container mx-auto flex h-14 items-center justify-between px-4">
          <Link to="/dashboard" className="flex items-center gap-2 font-semibold">
            <LayoutDashboard className="h-6 w-6" />
            Primetrade
          </Link>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            {isAdmin() && (
              <Button onClick={() => setAddOpen(true)} size="sm">
                <Plus className="mr-2 h-4 w-4" />
                Add product
              </Button>
            )}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                  <User className="h-5 w-5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem disabled>
                  <span className="font-medium">{email}</span>
                  <span className="ml-2 text-muted-foreground">({role})</span>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/products">Products</Link>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={logout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle>Dashboard</CardTitle>
            <CardDescription>Product list. {isAdmin() && "You can add, edit, and delete products."}</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-muted-foreground">Loading…</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Price</TableHead>
                    {isAdmin() && <TableHead className="w-[120px]">Actions</TableHead>}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {products.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={isAdmin() ? 4 : 3} className="text-center text-muted-foreground">
                        No products yet.
                      </TableCell>
                    </TableRow>
                  ) : (
                    products.map((p) => (
                      <TableRow key={p.id}>
                        <TableCell className="font-medium">{p.name}</TableCell>
                        <TableCell>{p.description || "—"}</TableCell>
                        <TableCell>{new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(Number(p.price))}</TableCell>
                        {isAdmin() && (
                          <TableCell>
                            <div className="flex gap-2">
                              <Button variant="outline" size="sm" onClick={() => setEditingProduct(p)}>
                                Edit
                              </Button>
                              <Button variant="destructive" size="sm" onClick={() => handleDelete(p)}>
                                Delete
                              </Button>
                            </div>
                          </TableCell>
                        )}
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </main>

      <AddProductDialog open={addOpen} onOpenChange={setAddOpen} onSuccess={loadProducts} />
      <EditProductDialog
        product={editingProduct}
        open={!!editingProduct}
        onOpenChange={(open) => !open && setEditingProduct(null)}
        onSuccess={() => { setEditingProduct(null); loadProducts(); }}
      />
    </div>
  );
}
