import { IsNotEmpty, IsNumber, IsOptional, IsString } from "class-validator"



export class CreateProductItemDto {
    @IsString()
    @IsNotEmpty()
    name: string

    @IsOptional()
    @IsNumber()
    rating: number

    @IsOptional()
    @IsString()
    originalPrice: string

    @IsOptional()
    @IsString()
    salePrice:string

    @IsOptional()
    @IsString()
    shippingFee: string
    @IsOptional()
    @IsString()
    productInfo:string
    @IsString()
    @IsNotEmpty()
    productUrl:string


}


