from pydantic import BaseModel

from subprocess import getoutput
from ..api_router import api

class RunRequest(BaseModel):
    command: str

build_thread = None

@api.post("/command/run")
async def run_command(req: RunRequest):
    out = getoutput(f"{req.command}")
    print(out)
    return {"status": "success", "message": f"{out}"}
