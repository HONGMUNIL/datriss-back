import { Type } from "class-transformer";
import { ArrayMinSize, IsArray, IsNotEmpty, IsString, ValidateNested } from "class-validator";
import { CreateProductItemDto } from "./create-product-item.dto";

export class BulkCreateProductsDto{
    @IsString()
    @IsNotEmpty()
    platformCode: string;

    @IsArray()
    @ArrayMinSize(1)
    @ValidateNested({ each: true })
    @Type(() => CreateProductItemDto)
    products: CreateProductItemDto[];




}




