from pydantic import BaseModel
class DeveloperOutput(BaseModel):
    models_py: str
    main_py: str