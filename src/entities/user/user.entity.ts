import {  Column, Entity, PrimaryGeneratedColumn } from "typeorm";
import { BaseEntity } from "../abstract/base.entity";

@Entity('users')
export class User extends BaseEntity{


@Column({ length: 100})
email: string;

@Column({length: 255})
password: string;

@Column({ type: 'varchar', length: 255, nullable: true })
name: string | null;

// @Column({ name: 'created_at'})
// createdAt!: Date;

// @Column({ name: 'updated_at'})
// updatedAt!: Date;


}


