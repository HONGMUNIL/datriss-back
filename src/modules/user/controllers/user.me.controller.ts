import { Controller, Get, Request, UseGuards } from "@nestjs/common";
import { UserService } from "../service/user.service";
import { JwtAuthGuard } from "src/modules/auth/guard/jwt-auth.guard";


@Controller('users')
@UseGuards(JwtAuthGuard)
export class UserMeController {
    constructor(private readonly userService: UserService){}

    @Get('me')
    async findMe(@Request() req){
        const { id, email } = req.user;
        console.log('id : ', id);
        console.log('email : ', email);
        const user = await this.userService.findById(id);
        const {password, ...userInfo} = user;
        return userInfo;
        
    }
}