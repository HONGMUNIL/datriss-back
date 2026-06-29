import { ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);


  app.useGlobalPipes(
    new ValidationPipe({

      whitelist: true,
      forbidNonWhitelisted:true, //@IsEmail() 작동시키기 위함 안하면 Controller까지 들어옴
      transform: true,
    }),
  );


app.enableCors({
  origin: 'http://localhost:5173',
  credentials: true,
});

  await app.listen(process.env.PORT ?? 3000);
}

bootstrap();