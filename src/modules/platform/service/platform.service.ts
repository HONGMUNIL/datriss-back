import { Injectable, OnModuleInit } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { Platform } from "../../../entities/platform/platform.entity";

@Injectable()
export class PlatformService implements OnModuleInit {
  constructor(
    @InjectRepository(Platform)
    private readonly platformRepository: Repository<Platform>
  ) {}

  async onModuleInit() {
    await this.seedDefaultPlatforms();
  }

  async seedDefaultPlatforms() {
    const defaultPlatforms = [
      {
        code: "amazon",
        name: "Amazon",
        baseUrl: "https://www.amazon.com",
      },
      {
        code: "ebay",
        name: "eBay",
        baseUrl: "https://www.ebay.com",
      },
    ];

    for (const platform of defaultPlatforms) {
      const existingPlatform = await this.platformRepository.findOne({
        where: {
          code: platform.code,
        },
      });

      if (!existingPlatform) {
        await this.platformRepository.save(platform);
      }
    }
  }

  async findAll() {
    return this.platformRepository.find({
      order: {
        id: "ASC",
      },
    });
  }
}