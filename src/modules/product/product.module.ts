import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { Product } from "../../entities/product/product.entity";
import { Platform } from "../../entities/platform/platform.entity";
import { ProductController } from "./controllers/product.controller";
import { ProductService } from "./service/product.service";

@Module({
  imports: [TypeOrmModule.forFeature([Product, Platform])],
  controllers: [ProductController],
  providers: [ProductService],
})
export class ProductModule {}