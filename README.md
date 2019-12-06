# Hand-Drawn-Images-Recognition
## Модуль генерации данных:
* Запускаем команду ниже. Получаем 50 сгенерированных картинок в папке data\.
```
python data_generator.py -n 50 -dst data/ --rewrite --noisy
```
К этому модулю есть требования.
* Необходимо установать пакеты `numpy, pillow`.
* Поставить `TexLive` и `ImageMagick`. 
* Для пользователей `Windows`
  нужно добавить в `PATH` бинарный файл `pdflatex`, а так же в корне `ImageMagick`
  найти файл `convert.exe` и переименовать в `imgconvert.exe`, потому что 
  разработчики не согласовали свои правки. По 
  [ссылке](https://www.ghostscript.com/) можно найти еще одну необходимую
  библиотеку.