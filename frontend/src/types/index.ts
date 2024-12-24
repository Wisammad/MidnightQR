export interface MenuItem {
  id: number;
  name: string;
  price: number;
  category: string;
  description: string;
  stock?: number;
  track_stock: boolean;
}

export interface OrderItem {
  id: number;
  name: string;
  quantity: number;
  price: number;
}

export interface Order {
  id: number;
  table_number: number;
  items: OrderItem[];
  total_price: number;
  status: string;
  created_at: string;
  updated_at: string;
  is_service: boolean;
  staff_id: number | null;
  staff_name: string | null;
}

export interface User {
  id: number;
  username: string;
  role: string;
  table_number?: number;
}

export interface AnalyticsItem {
  name: string;
  count: number;
}

export interface StaffPerformance {
  name: string;
  completed: number;
  refunded: number;
  totalOrders: number;
}

export interface OrderStatus {
  status: string;
  count: number;
}

export interface OrderTrend {
  date: string;
  count: number;
}

export interface AnalyticsState {
  totalOrders: number;
  totalRevenue: number;
  totalRefunds: number;
  popularItems: AnalyticsItem[];
  staffPerformance: StaffPerformance[];
  ordersByStatus: OrderStatus[];
  orderTrends: OrderTrend[];
} 