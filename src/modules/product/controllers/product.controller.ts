import { Body, Controller, Get, Post, Query } from "@nestjs/common";
import { ProductService } from "../service/product.service";
import { BulkCreateProductsDto } from "../dto/bulk-create-products.dto";

@Controller("products")
export class ProductController {
  constructor(private readonly productService: ProductService) {}

  @Post("bulk")
  async bulkCreateProducts(@Body() dto: BulkCreateProductsDto) {
    return this.productService.bulkCreateProducts(dto);
  }

  @Get()
  async findAll(@Query("platform") platformCode?: string) {
    return this.productService.findAll(platformCode);
  }
}