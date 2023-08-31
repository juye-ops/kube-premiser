from fastapi import APIRouter

from database import *
from routers import ProjectCreate, ProjectEdit
from utils import dind, ide

router = APIRouter(
    prefix="/project",
)


@router.get("/list")
def _list():
    return ProjectDB.get_list()

@router.get("/info")
def _info(name):
    return ProjectDB.get_info(name)[0]

@router.get("/len")
def _len(name):
    return ProjectDB.get_len(name)[0]["count(*)"]


@router.post("/create")
def _create(info: ProjectCreate):
    info = info.dict()

    project_name = info["name"]
    project_desc = info["description"]

    net_info = dind.Network.create(info["name"])

    ProjectDB.create(project_name, project_desc, net_info["subnet"])

    return 200

@router.post("/edit")
def _edit(res: ProjectEdit):
    res = res.dict()

    old_name = res["old_name"]
    new_name = res["new_name"]
    project_desc = res["description"]
    
    container_list = ProjectDB.get_containers(old_name)

    dind.Network.disconnect_all(res["old_name"])
    dind.Network.remove(res["old_name"])
    net_info = dind.Network.create(res["new_name"])
    dind.Network.connect_containers(new_name, container_list)
    
    ProjectDB.edit(old_name, new_name, project_desc, net_info["subnet"])
    for c in container_list:
        container_ip = dind.Container.get_info(c["name"])["NetworkSettings"]["Networks"][new_name]["IPAddress"]
        ContainerDB.update_ip(c["name"], container_ip)

    return 200

@router.delete("/remove")
def _remove(name: str):
    container_list = ProjectDB.get_containers(name)

    for c in container_list:
        dind.Container.remove(c["name"])
        ide.rm_proxy(name)

    dind.Network.remove(name)

    ProjectDB.remove(name)
