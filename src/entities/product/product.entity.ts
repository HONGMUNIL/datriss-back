import {
  Column,
  CreateDateColumn,
  Entity,
  Index,
  JoinColumn,
  ManyToOne,
  PrimaryGeneratedColumn,
  UpdateDateColumn,
} from "typeorm";
import { Platform } from "../platform/platform.entity";

@Entity("products")
@Index(["platformId", "productUrl"], { unique: true })//같은 상품 URL은 한번만 저장가능
export class Product {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ name: "platform_id" })
  platformId: number;

  @ManyToOne(() => Platform, (platform) => platform.products, {
    //여러상품이 하나의 플랫폼에 들어감
    nullable: false,
    onDelete: "RESTRICT",
  })
  @JoinColumn({ name: "platform_id" })
  platform: Platform;

  @Column({ length: 500 })
  name: string;

  @Column({ type: "double precision", nullable: true })
  rating: number | null;

  @Column({ name: "original_price", length: 100, nullable: true })
  originalPrice: string | null;

  @Column({ name: "sale_price", length: 100, nullable: true })
  salePrice: string | null;

  @Column({ name: "shipping_fee", length: 100, nullable: true })
  shippingFee: string | null;

  @Column({ name: "product_info", type: "text", nullable: true })
  productInfo: string | null;

  @Column({ name: "product_url", length: 1000 })
  productUrl: string;

  @CreateDateColumn({ name: "created_at" })
  createdAt: Date;

  @UpdateDateColumn({ name: "updated_at" })
  updatedAt: Date;
}