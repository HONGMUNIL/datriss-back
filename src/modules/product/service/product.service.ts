import { BadRequestException, Injectable } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { Product } from "../../../entities/product/product.entity";
import { Platform } from "../../../entities/platform/platform.entity";
import { BulkCreateProductsDto } from "../dto/bulk-create-products.dto";

@Injectable()
export class ProductService {
  constructor(
    @InjectRepository(Product)
    private readonly productRepository: Repository<Product>,

    @InjectRepository(Platform)
    private readonly platformRepository: Repository<Platform>
  ) {}

  async bulkCreateProducts(dto: BulkCreateProductsDto) {
    const platformCode = dto.platformCode.trim().toLowerCase();

    const platform = await this.platformRepository.findOne({
      where: {
        code: platformCode,
      },
    });

    if (!platform) {
      throw new BadRequestException("존재하지 않는 플랫폼입니다.");
    }

    let createdCount = 0;
    let updatedCount = 0;

    for (const item of dto.products) {
      const productUrl = item.productUrl.trim();

      const existingProduct = await this.productRepository.findOne({
        where: {
          platformId: platform.id,
          productUrl,
        },
      });

      if (existingProduct) {
        existingProduct.name = item.name.trim();
        existingProduct.rating = item.rating ?? null;
        existingProduct.originalPrice = item.originalPrice ?? null;
        existingProduct.salePrice = item.salePrice ?? null;
        existingProduct.shippingFee = item.shippingFee ?? null;
        existingProduct.productInfo = item.productInfo ?? null;

        await this.productRepository.save(existingProduct);
        updatedCount++;
      } else {
        const newProduct = this.productRepository.create({
          platformId: platform.id,
          name: item.name.trim(),
          rating: item.rating ?? null,
          originalPrice: item.originalPrice ?? null,
          salePrice: item.salePrice ?? null,
          shippingFee: item.shippingFee ?? null,
          productInfo: item.productInfo ?? null,
          productUrl,
        });

        await this.productRepository.save(newProduct);
        createdCount++;
      }
    }

    return {
      platform: platform.code,
      totalCount: dto.products.length,
      createdCount,
      updatedCount,
    };
  }

  async findAll(platformCode?: string) {
    const queryBuilder = this.productRepository
      .createQueryBuilder("product")
      .leftJoinAndSelect("product.platform", "platform")
      .orderBy("product.createdAt", "DESC");

    if (platformCode) {
      queryBuilder.andWhere("platform.code = :platformCode", {
        platformCode: platformCode.trim().toLowerCase(),
      });
    }

    return queryBuilder.getMany();
  }
}