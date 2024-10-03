# cams_ver_viewer
Web app for navigating &amp; plotting CAMS verification results

## for dev
### go to /backend/api/ and run command 
>pip install -r requirements.txt

>fastapi dev VerisualiserAPI.py


### go to /frontend/ and run command 
>npm install 

(there might be an issue with plotly-dist types)

in which case you should run <br>

>npm install -D plotly.js-dist

and if doesn't work, run

>npm install plotly.js

go to /node_modules/@types
rename plotly.js to plotly.js-dist 
>(optionally also delete plotly.js module from node_modules)

## for dev
### go to /frontend/ <br>
>npm run dev 

## for deployment

### go to /frontend/ <br>
>npm run build <br>
>npm start
