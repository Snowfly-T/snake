import importlib
from typing import cast

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(redoc_url=None)

importlib.import_module('fastapi_snake_app.db')
importlib.import_module('fastapi_snake_app.ws')
importlib.import_module('fastapi_snake_app.game')
importlib.import_module('fastapi_snake_app.user')
importlib.import_module('fastapi_snake_app.stage')
importlib.import_module('fastapi_snake_app.play')
importlib.import_module('fastapi_snake_app.login')
importlib.import_module('fastapi_snake_app.logout')
importlib.import_module('fastapi_snake_app.register')
importlib.import_module('fastapi_snake_app.update')
importlib.import_module('fastapi_snake_app.make_review')
importlib.import_module('fastapi_snake_app.review')
importlib.import_module('fastapi_snake_app.chatter')

# Import all routes
importlib.import_module('fastapi_snake_app.note')

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

with open('./fastapi_snake_app/game.html', 'r', encoding='utf-8') as f:
    demo_html = f.read()


@app.get('/', include_in_schema=False)
async def index() -> HTMLResponse:
    return HTMLResponse(demo_html)


def start_dev() -> None:
    """
    Launched with `poetry run start` or `poetry run start:dev` at root level.
    """

    uvicorn.run('fastapi_snake_app.main:app',
                reload=True, host='127.0.0.1')


def start_prod() -> None:
    """
    Launched with `poetry run start:prod` at root level.
    """

    uvicorn.run('fastapi_snake_app.main:app', host='0.0.0.0')


def get_redoc_html(
    *,
    openapi_url: str,
    title: str,
    redoc_favicon_url: str = 'https://fastapi.tiangolo.com/img/favicon.png',
    with_google_fonts: bool = True,
) -> HTMLResponse:
    """
    Used to add “Try it out” support to ReDoc.
    """

    html = f'''
      <!DOCTYPE html>
      <html>
      <head>
        <title>{title}</title>
        <!-- needed for adaptive design -->
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    '''

    if with_google_fonts:
        html += '''
          <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        '''

    html += f'''
        <link rel="shortcut icon" href="{redoc_favicon_url}">
        <!-- ReDoc doesn't change outer page styles -->
        <style>
          body {{
            margin: 0;
            padding: 0;
          }}
        </style>
      </head>
      <body>
        <div id="redoc-container"></div>
        <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0-rc.55/bundles/redoc.standalone.min.js"></script>
        <script src="https://cdn.jsdelivr.net/gh/wll8/redoc-try@1.4.1/dist/try.js"></script>
        <script>
          initTry({{
            openApi: `{openapi_url}`,
            redocOptions: {{scrollYOffset: 50}},
          }})
        </script>
      </body>
      </html>
    '''

    return HTMLResponse(html)


@app.get('/redoc', include_in_schema=False)
async def redoc_try_it_out() -> HTMLResponse:
    """
    Add “Try it out” support to ReDoc.
    """

    title = f'{app.title} Redoc'
    return get_redoc_html(openapi_url=cast(str, app.openapi_url), title=title)


@app.get('/echo')
async def echo(text: str) -> str:
    return text
