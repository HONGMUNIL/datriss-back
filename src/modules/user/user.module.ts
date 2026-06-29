import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from '../../entities/user/user.entity';
import { UserService } from './service/user.service';
import { UserMeController } from './controllers/user.me.controller';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UserMeController],
  providers: [UserService],
  exports: [UserService],
})
export class UserModule {}