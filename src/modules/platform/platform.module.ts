import { Module } from "@nestjs/common";
import { platform } from "os";
import { PlatformService } from "./service/platform.service";
import { PlatformController } from "./controllers/platform.controller";
import { TypeOrmModule } from "@nestjs/typeorm";
import { Platform } from "src/entities/platform/platform.entity";

@Module({
    imports: [
        // ProductModule
        TypeOrmModule.forFeature([Platform])
    ],
    controllers: [
        PlatformController
    ],
    providers: [
        PlatformService
    ],
    exports: [PlatformService]
})
export class PlatformModule {}