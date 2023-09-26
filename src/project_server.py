from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import os

from ros2.ros_mgmt import ROS2CLIWrapper

# Get the ROS2 workspace directory from .env file
ROS2_WS_DIR = "/home/kat354/ros2_ws"
if not ROS2_WS_DIR:
    raise ValueError("ROS2_WS_DIR is not set in the environment or .env file")

app = FastAPI()
ros_cli = ROS2CLIWrapper(ROS2_WS_DIR)


class PackageInfo(BaseModel):
    package_name: str
    package_type: str = 'ament_python'


@app.post("/create_project/")
async def create_project(package_info: PackageInfo):
    return await ros_cli.create_project(package_info.package_name, package_info.package_type)


@app.get("/list_projects/")
async def list_projects():
    return await ros_cli.list_projects()


@app.get("/list_nodes/")
async def list_nodes():
    return await ros_cli.list_nodes()


@app.post("/build_package/{package_name}/")
async def build_package(package_name: str):
    return await ros_cli.build_package(package_name)


@app.post("/install_package/{package_name}/")
async def install_package(package_name: str):
    return await ros_cli.install_package(package_name)


@app.post("/run_package/{package_name}/{executable_name}/")
async def run_package(package_name: str, executable_name: str):
    return await ros_cli.run_package(package_name, executable_name)


@app.delete("/uninstall_package/{package_name}/")
async def uninstall_package(package_name: str):
    await ros_cli.uninstall_package(package_name)
    return {"message": f"Uninstalled {package_name}"}


@app.delete("/delete_package/{package_name}/")
async def delete_package(package_name: str):
    await ros_cli.delete_package(package_name)
    return {"message": f"Deleted {package_name}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
