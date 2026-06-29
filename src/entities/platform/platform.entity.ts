import { Column, Entity, Index, PrimaryGeneratedColumn } from "typeorm";
import { OneToMany } from "typeorm/browser";
import { Product } from "../product/product.entity";
import { CreateDateColumn } from "typeorm/browser";
import { UpdateDateColumn } from "typeorm/browser";

@Entity("platforms")
@Index(["code"], {unique: true})
export class Platform {
    @PrimaryGeneratedColumn()
    id: number;

    @Column({ length: 50})
    code: string;

    @Column({length:100})
    name: string;
    @Column({name:"base_url", length:255})
    baseUrl: string;
    @OneToMany(() => Product, (product) => product.platform)    
    products: Product[];


    @CreateDateColumn({ name: "created_at" })
    createdAt: Date;

    @UpdateDateColumn({ name: "updated_at" })
    updatedAt: Date;

    }
    







