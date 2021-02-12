"""
Main Python Script of the 'Mistos' Microservice.

To start this app type

```uvicorn main:mistos --reload --workers 1 --host 0.0.0.0 --port 7777```

inside the src/-folder of this project.

Alternatively you can run the file main-py directly using

```python.exe main.py```

inside the src/-folder.

For debugging using VSCode or Pycharm see: https://fastapi.tiangolo.com/tutorial/debugging/

"""
# Delete old files from garbage collection before startup
from app.api import utils_garbage
if not utils_garbage.garbage_json.exists():
    utils_garbage.create_garbage_json()
    
utils_garbage.delete_garbage_file() 



import uvicorn

from app.api.com import hello, api_images, api_classifier, api_experiments
# from app.api.schemas import LoginException
from fastapi import FastAPI
from fastapi.logger import logger as log
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.database import SessionLocal, engine
from app import db_models

db_models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI
mistos = FastAPI()

# Configuration for CORS
origins = [
    "http://localhost",
    "http://localhost:4200",
    "*"
    # "http://<hostname>",
    # "http://<hostname>:80"
]

# Configuration for CORS
mistos.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@mistos.on_event("startup")
async def startup():
    """
    During startup of the fast-api this method is triggered.
    It can be used to prepare the system, e.g. fireing up database connection handler
    """
    pass

# Include the '/api/hello' route
mistos.include_router(hello.router)

'''
Image endpoints
'''
# Include the "/api/images" routes
mistos.include_router(api_images.router)


'''
Classifier endpoints
'''
# Include the "/api/classifier" routes
mistos.include_router(api_classifier.router)

'''
Experiment endpoints
'''
# Include the "/api/experiments" routes
mistos.include_router(api_experiments.router)

if __name__ == "__main__":
    uvicorn.run(mistos, host="0.0.0.0", port=7777)
