import os
import subprocess
import time
from pynput.mouse import Button, Controller

class LDPlayerManager:
    def __init__(self, ldconsole_path, dnconsole_path):
        self.ldconsole_path = ldconsole_path
        self.dnconsole_path = dnconsole_path

    def run_command(self, cmd):
        if cmd[0] == "touch":
            # Format the command as a string
            cmd_str = " ".join(cmd)
            # Use the dnconsole_path to run the command
            os.system(f"{self.dnconsole_path} {cmd_str}")
        else:
            # Use the ldconsole_path to run the command
            result = subprocess.run([self.ldconsole_path] + cmd, capture_output=True, text=True)
            return result.stdout

    def list_instances(self):
        cmd = ["list2"]
        result = subprocess.run([self.dnconsole_path] + cmd, capture_output=True, text=True)
        instances = [line.split(",")[1] for line in result.stdout.splitlines()[1:] if line]
        #print(f"list_instances output: {result.stdout}")  # debug print
        return instances

    def get_all_instances_status(self):
        cmd = ['list2']
        result = subprocess.run([self.dnconsole_path] + cmd, capture_output=True, text=True)
        instances = {}
        for line in result.stdout.splitlines():
            data = line.split(',')
            if len(data) >= 6:
                name = data[1].strip()
                started = data[4].strip()
                if started == '1':
                    status = 'running'
                else:
                    status = 'stopped'
            else:
                status = 'unknown'
            instances[name] = status
        return instances

    def print_instance_table(self, instance_statuses, status_filter=None):
        print("\nInstance Dashboard:")
        print("ID".ljust(5), "Instance Name".ljust(30), "Status")
        running_instances = []
        stopped_instances = []
        unknown_instances = []
        for instance, status in instance_statuses.items():
            if status == "running":
                running_instances.append(instance)
            elif status == "stopped":
                stopped_instances.append(instance)
            else:
                unknown_instances.append(instance)
        if status_filter == "running":
            instances = running_instances
        elif status_filter == "stopped":
            instances = stopped_instances
        else:
            instances = running_instances + stopped_instances + unknown_instances
        for idx, instance in enumerate(instances, start=1):
            status = instance_statuses[instance]
            print(str(idx).ljust(5), instance.ljust(30), status)
        print("\nSummary:")
        print(f"{len(running_instances)} instances running")
        print(f"{len(stopped_instances)} instances stopped")
        print(f"{len(unknown_instances)} instances in an unknown state")

    def start_instance(self, instance_name):
        cmd = ["launch", "--name", instance_name]
        self.run_command(cmd)
        # Wait for the instance to start up
        time.sleep(5)
        # Start the Roblox app
        cmd = ["runapp", "--name", instance_name, "--packagename", "com.roblox.client"]
        self.run_command(cmd)
        # Wait for the app to start up
        time.sleep(10)
        # Simulate a click on a specific coordinate
        mouse = Controller()
        mouse.position = (130, 482)
        mouse.press(Button.left)
        mouse.release(Button.left)

    def stop_instance(self, instance_name):
        cmd = ["quit", "--name", instance_name]
        self.run_command(cmd)

    def restart_instance(self, instance_name):
        self.stop_instance(instance_name)
        self.start_instance(instance_name)
                # Wait for the instance to start up
        time.sleep(5)
        # Start the Roblox app
        cmd = ["runapp", "--name", instance_name, "--packagename", "com.roblox.client"]
        self.run_command(cmd)
                # Wait for the app to start up
        time.sleep(10)
        # Click on a specific coordinate
        cmd = ["input", "touch", str(130), str(482), str(1000)]
        self.run_command(cmd)


ldconsole_path = r"C:\LDPlayer\LDPlayer9\ldconsole.exe"  # Replace with the path to your ldconsole.exe
dnconsole_path = r"C:\LDPlayer\LDPlayer9\dnconsole.exe"  # Replace with the path to your dnconsole.exe
manager = LDPlayerManager(ldconsole_path, dnconsole_path)

instances = manager.list_instances()


def print_instance_table(instance_statuses):
    print("\nInstance Dashboard:")
    print("ID\tInstance Name\tStatus")
    for idx, (instance, status) in enumerate(instance_statuses.items(), start=1):
        print(f"{idx}\t{instance}\t{status}")


def get_action():
    print("\nActions:")
    print("1. Start instance")
    print("2. Stop instance")
    print("3. Restart instance")
    print("4. Refresh dashboard")
    print("5. Exit")


instance_statuses = manager.get_all_instances_status()
manager.print_instance_table(instance_statuses)

while True:
    get_action()
    choice = input("Enter your choice: ")
    if choice in ["1", "2", "3"]:
        if choice == "1":
            action = "start"
            valid_instances = [instance for instance, status in instance_statuses.items() if status == "stopped"]
        elif choice == "2":
            action = "stop"
            valid_instances = [instance for instance, status in instance_statuses.items() if status == "running"]
        else:
            action = "restart"
            valid_instances = [instance for instance, status in instance_statuses.items() if status == "running"]
        if not valid_instances:
            print(f"No valid instances to {action}.")
            continue
        print("Instances:")
        for idx, instance in enumerate(valid_instances, start=1):
            print(f"{idx}. {instance}")
        instance_index = int(input("Enter the index of the instance: ")) - 1
        instance_name = valid_instances[instance_index]
        status = instance_statuses[instance_name]
        try:
            if instance_index < 0 or instance_index >= len(valid_instances):
                print("Invalid instance index.")
                continue
            instance_name = valid_instances[instance_index]
            status = instance_statuses[instance_name]
        except ValueError:
            print("Invalid instance index.")
            continue
    if choice == "1":
        if status == "stopped":
            manager.start_instance(instance_name)
            instance_statuses[instance_name] = "running"
            print(f"Started instance {instance_name}")
        else:
            print("Instance is already running.")
    elif choice == "2":
        if status == "running":
            manager.stop_instance(instance_name)
            instance_statuses[instance_name] = "stopped"
            print(f"Stopped instance {instance_name}")
        else:
            print("Instance is not running.")
    elif choice == "3":
        if status == "running":
            manager.restart_instance(instance_name)
            print(f"Restarted instance {instance_name}")
        else:
            print("Instance is not running.")
    elif choice == "4":
        instance_statuses = manager.get_all_instances_status()
        manager.print_instance_table(instance_statuses)
    elif choice == "5":
        print("Exiting LDPlayer Dashboard...")
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 5.")
