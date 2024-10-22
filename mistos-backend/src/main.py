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
import uvicorn

from app.api.com import hello, api_images, api_classifier, api_experiments, api_deepflash
# from app.api.schemas import LoginException
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.database import engine
from app import db_models
from app.api import utils_garbage
from app.api.utils_import import start_jvm, kill_jvm


db_models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI
mistos = FastAPI(
    title="Mistos-Backend",
    description="The backend service of the Mistos app",
)

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
    # initialize javabridge
    start_jvm()



@mistos.on_event("shutdown")
def shutdown_event():
    kill_jvm()
    # with open("log.txt", mode="a") as log:
    #     log.write("Application shutdown")

# Mount Fileserverfolder as static files
# mistos.mount("/static", StaticFiles(directory="static"), name="static") #utils_paths.fileserver.as_posix()


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

'''
Deepflash endpoints
'''
# Include the "/api/deepflash" routes
mistos.include_router(api_deepflash.router)

if __name__ == "__main__":
    uvicorn.run(mistos, host="0.0.0.0", port=7777)
