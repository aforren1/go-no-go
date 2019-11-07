rm drop.spec
@RD /S /Q "dist"
pyinstaller --noconsole --onefile --paths "./dlls" --add-data "gonogo/resources/fonts/*.ttf;gonogo/resources/fonts/" --add-data "gonogo/resources/images/*.png;gonogo/resources/images/" --add-data "dlls/freetype.dll;." --add-data "gonogo/resources/sound/*.wav;gonogo/resources/sound/" --add-data "gonogo/resources/themes/*.json;gonogo/resources/themes/" main.py --name gonogo

cp -r tables dist\tables
cp -r recipes dist\recipes
