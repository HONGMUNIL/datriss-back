import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { User } from '../../../entities/user/user.entity';
import { Repository } from 'typeorm';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
  ) {}

  async findByEmail(email: string): Promise<User | null> {
    return this.userRepository.findOne({
      where: { email },
    });
  }

  async createUser(email: string, password: string, name?: string): Promise<User> {
    const user = this.userRepository.create({
      email,
      password,
      name: name ?? null,
    });
    
    return this.userRepository.save(user);
  }

  async findById(id: number){
    const user = await this.userRepository.findOne({
      where: {id},
    });
    if(!user){
      throw new NotFoundException('유저를 찾을 수 없습니다.');
    }
    return user;
  }
}