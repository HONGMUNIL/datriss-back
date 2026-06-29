import { join } from "path";
import {
    TypeOrmModuleAsyncOptions,
    TypeOrmModuleOptions,
} from '@nestjs/typeorm';
import { ConfigService } from '@nestjs/config';


class TypeOrmConfig {
    static getConfig(configService: ConfigService): TypeOrmModuleOptions{
        return{
            type:'postgres',
            host: configService.get('DB_HOST'),
            port: configService.get<number>('DB_PORT'),
            username: configService.get('DB_USERNAME'),
            password: configService.get('DB_PASSWORD'),
            database: configService.get('DB_DATABASE'),
            entities: [join(__dirname, '../**/entities/**/*.entity{.ts}')],
            synchronize: false,
            logging: true,
            autoLoadEntities: true,
            extra: {
                connectionTimeoutMillis: 50000,
            },

        };
    }
}

export const typeormConfigAsync: TypeOrmModuleAsyncOptions = {
    useFactory: async (configService: ConfigService) =>
        TypeOrmConfig.getConfig(configService),
    inject: [ConfigService],
};