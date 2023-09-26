import asyncio
import shutil
import os


class ROS2CLIWrapper:
    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir

    async def run_command(self, command):
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.workspace_dir,
            executable='/bin/bash')

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Command failed with error: {stderr.decode()}")
        return stdout.decode()

    async def create_project(self, package_name, package_type='ament_python'):
        command = f"ros2 pkg create {package_name} --build-type {package_type}"
        return await self.run_command(command)

    async def list_projects(self):
        command = "ros2 pkg list"
        return await self.run_command(command)

    async def list_nodes(self):
        command = "ros2 node list"
        return await self.run_command(command)

    async def build_package(self, package_name):
        command = f"colcon build --packages-select {package_name}"
        return await self.run_command(command)

    async def install_package(self, package_name):
        command = f"colcon build --packages-select {package_name}"
        return await self.run_command(command)

    async def run_package(self, package_name, executable_name):
        command = f"source install/setup.bash && ros2 run {package_name} {executable_name}"
        return await self.run_command(command)

    async def uninstall_package(self, package_name):
        # Remove build, install, and log directories
        shutil.rmtree(os.path.join(self.workspace_dir, 'build', package_name))
        shutil.rmtree(os.path.join(self.workspace_dir, 'install', package_name))
        print(f"Uninstalled {package_name}")

    async def delete_package(self, package_name):
        # Remove package source code
        shutil.rmtree(os.path.join(self.workspace_dir, package_name))
        print(f"Deleted {package_name}")


# Example usage
async def main():
    workspace_dir = "/home/kat354/ros2_ws"
    ros2_cli = ROS2CLIWrapper(workspace_dir)

    # Create a new package
    await ros2_cli.create_project('my_package')
    #
    # # List all packages
    # packages = await ros2_cli.list_projects()
    # print(packages)
    #
    # # List all running nodes
    # nodes = await ros2_cli.list_nodes()
    # print(nodes)
    #
    # # Build a package
    # await ros2_cli.build_package('my_package')
    #
    # # Install a package
    # await ros2_cli.install_package('my_package')
    #
    # # Run a package
    # # await ros2_cli.run_package('my_package', 'my_executable')
    #
    # # Uninstall a package
    # await ros2_cli.uninstall_package('my_package')
    #
    # # Delete a package
    # await ros2_cli.delete_package('my_package')


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
