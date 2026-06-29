import { Controller, Get } from "@nestjs/common";
import { PlatformService } from "../service/platform.service";

@Controller("platforms")
export class PlatformController{
    constructor(private readonly platformService: PlatformService){}

    @Get()
    async fildAll(){
        return this.platformService.findAll();
        
    }





}


