#!/usr/bin/python3

import os
import subprocess
import sys
import argparse
import json
from datetime import datetime

BOLD = "\x1b[22m"
BRIGHT = "\x1b[1m"
RESET = "\x1b[0m"

RED = f"{BOLD}\x1b[31m{BRIGHT}"
GREEN = f"{BOLD}\x1b[32m{BRIGHT}"
YELLOW = f"{BOLD}\x1b[33m{BRIGHT}"
BLUE = f"{BOLD}\x1b[36m{BRIGHT}"
GREY = "\x1b[90m"


def config_file_exists():
    return os.path.exists('.qs')


def get_config():
    with open(".qs", "r") as config_file:
        return json.load(config_file)


def get_timestamp():
    now = datetime.now()
    return f"{GREY}[{now.strftime('%H:%M:%S.%f')[:-3]}]{RESET}"


def print_info(message):
    print(f"{get_timestamp()} [{YELLOW}INFO{RESET}] {message}")


def print_warning(message):
    print(f"{get_timestamp()} [{BLUE}WARN{RESET}] {message}")


def print_error(message):
    print(f"{get_timestamp()} [{RED}FAIL{RESET}] {message}")
    sys.exit(1)


def print_success(message):
    print(f"{get_timestamp()} [{GREEN} OK {RESET}] {message}")


def get_application_name():
    name = os.getcwd().split('/')[-1]
    if config_file_exists():
        config = get_config()
        if "name" in config:
            name = config["name"]
    return name


def is_docker_running():
    result = subprocess.run(["docker", "info"], capture_output=True)
    if result.returncode != 0:
        print_error(
            "Unable to reach Docker - is it running? Do you need to run quickstack as root?")


def create_network():
    result = subprocess.run(["docker", "network", "inspect",
                            "quickstack-platform-interconnect"], capture_output=True)

    if result.returncode != 0:
        print_warning("Container network doesn't exist yet...")
        result = subprocess.run(["docker", "network", "create", "-d", "bridge",
                                "quickstack-platform-interconnect"], capture_output=True)
        if (result.returncode != 0):
            print_error("Failed to create container network!")
        else:
            print_success("Container network created!")


def build_compose_stack(args):
    print_info(f"Building application images...")
    build_args = ["docker", "compose", "build"]
    if args.clean:
        print_warning("Building without cache")
        build_args.append("--no-cache")
    result = subprocess.run(build_args, capture_output=not args.debug)
    if result.returncode != 0:
        print_error(
            f"Failed to build application images! Try running with --debug for more details")
    print_success(f"Successfully built application images!")


def start_compose_stack(args):
    print_info(f"Starting stack...")
    result = subprocess.run(
        ["docker", "compose", "up", "-d"], capture_output=not args.debug)
    if result.returncode != 0:
        print_error(f"Failed to start stack!")
    print_success(f"Successfully started stack!")
    if (args.attach):
        subprocess.run(["docker", "compose", "logs", "--follow",
                       get_application_name()], capture_output=False)


def restart_compose_stack(args):
    print_info(f"Restarting stack...")
    result = subprocess.run(
        ["docker", "compose", "restart"], capture_output=not args.debug)
    if result.returncode != 0:
        print_error(f"Failed to restart stack!")
    print_success(f"Successfully restarted stack!")
    if (args.attach):
        subprocess.run(["docker", "compose", "logs", "--follow",
                       get_application_name()], capture_output=False)


def stop_compose_stack(args):
    print_info(f"Stopping stack...")
    result = subprocess.run(["docker", "compose", "stop"],
                            capture_output=not args.debug)
    if result.returncode != 0:
        print_error(f"Failed to stop stack!")
    print_success(f"Successfully stopped stack!")


def destroy_compose_stack(args):
    print_info(f"Destroying stack...")
    result = subprocess.run(["docker", "compose", "down"],
                            capture_output=not args.debug)
    if result.returncode != 0:
        print_error(f"Failed to destroy stack!")
    print_success(f"Successfully destroyed stack!")


def ssh_application(args):
    result = subprocess.run(["docker", "compose", "exec", get_application_name(
    ), "/bin/bash"], capture_output=False)
    if result.returncode == 1:
        print_error(f"Failed to SSH into application")


def deploy_compose_stack(args):
    build_compose_stack(args)
    start_compose_stack(args)


def logs_from_application(args):
    result = subprocess.run(["docker", "compose", "logs",
                            "--follow", get_application_name()], capture_output=False)
    if result.returncode != 0:
        print_error(f"Failed to get logs from application")


def get_remote_location(config):
    directory = get_application_name()
    if config["username"] == "root":
        directory = "/root/" + directory
    else:
        directory = "/home/" + config["username"] + "/" + directory
    return config["username"] + "@" + config["address"] + ":" + directory


def cloudpush(args):
    if not config_file_exists():
        print_error("QuickStack config file is required for cloudpush")
    config = get_config()["cloudpush"]
    remote_location = get_remote_location(config)
    print_info("Pushing to " + remote_location)
    result = subprocess.run(["rsync", "-avzP", "--stats", "./", remote_location,
                            "--exclude", "target", "--exclude", "venv", "--exclude", "node_modules"], capture_output=not args.debug)
    if result.returncode != 0:
        print_error(f"Failed to push to " + remote_location)
    print_success("Pushed files to " + remote_location)


def get_parser():
    parser = argparse.ArgumentParser(prog="quickstack")
    subparsers = parser.add_subparsers()

    build_command = subparsers.add_parser(
        'build', help="Builds the application image")
    build_command.add_argument(
        "-d", "--debug", action="store_true", help="Enable debugging output")
    build_command.set_defaults(func=build_compose_stack)
    build_command.add_argument(
        "-c", "--clean", action="store_true", help="Build application image without cache")

    start_command = subparsers.add_parser('start', help="Starts the stack")
    start_command.add_argument(
        "-d", "--debug", action="store_true", help="Enable debugging output")
    start_command.add_argument(
        "-a", "--attach", action="store_true", help="Attach to logging output from application")
    start_command.set_defaults(func=start_compose_stack)

    deploy_command = subparsers.add_parser(
        'deploy', help="Builds the application image and then immediately starts the stack")
    deploy_command.add_argument(
        "-d", "--debug", action="store_true", help="Enable debugging output")
    deploy_command.add_argument(
        "-a", "--attach", action="store_true", help="Attach to logging output from application")
    deploy_command.add_argument(
        "-c", "--clean", action="store_true", help="Build application image without cache")
    deploy_command.set_defaults(func=deploy_compose_stack)

    stop_command = subparsers.add_parser('stop', help="Stops the stack")
    stop_command.add_argument(
        "-d", "--debug", action="store_true", help="Enable debugging output")
    stop_command.set_defaults(func=stop_compose_stack)

    ssh_command = subparsers.add_parser(
        'ssh', help="SSH into an application container in the Docker stack")
    ssh_command.set_defaults(func=ssh_application)

    logs_command = subparsers.add_parser('logs', help="View application logs")
    logs_command.set_defaults(func=logs_from_application)

    restart_command = subparsers.add_parser(
        'restart', help="Restarts the entire stack")
    restart_command.add_argument(
        "-d", "--debug", action="store_true", help="Enable debugging output")
    restart_command.add_argument(
        "-a", "--attach", action="store_true", help="Attach to logging output from application")
    restart_command.set_defaults(func=restart_compose_stack)

    destroy_command = subparsers.add_parser(
        'destroy', help="Destroys the stack")
    destroy_command.add_argument(
        "-d", "--debug", action="store_true", help="Enable debugging output")
    destroy_command.set_defaults(func=destroy_compose_stack)

    cloudpush_command = subparsers.add_parser(
        'cloudpush', help="Deploys the stack to the cloud")
    cloudpush_command.add_argument(
        "-d", "--debug", action="store_true", help="Enable debugging output")
    cloudpush_command.set_defaults(func=cloudpush)

    return parser, subparsers


def main():
    try:
        is_docker_running()
        create_network()
        parser, subparsers = get_parser()
        args = parser.parse_args()
        args.func(args)
    except KeyboardInterrupt:
        exit(0)


if __name__ == "__main__":
    main()
