
import os
import logging
import configparser
import subprocess

class Process():

    def __init__(self):
        self.load_configuration()

    def get_parameter(self, key, default):
        key = "COMMAND_" + key
        if key in os.environ:
            return os.environ.get(key)
        return default

    def load_configuration(self):
        self.command_bin_path = self.get_parameter('BIN_PATH', '/usr/bin')
        self.command_lib_path = self.get_parameter('LIB_PATH', '/usr/lib')
        self.env = os.environ.copy()

    def launch(self, program: str, inputs: list, outputs: list, lib_path: list):

        if program.startswith("/"):
            self.command_path = program
        else:
            self.command_path = os.path.join(self.command_bin_path, program)

        if "LD_LIBRARY_PATH" not in self.env:
            self.env["LD_LIBRARY_PATH"] = ""

        for path in lib_path:
            self.env["LD_LIBRARY_PATH"] += ":" + path
        self.env["LD_LIBRARY_PATH"] += ":" + self.command_lib_path

        command = [self.command_path]
        dst_paths = []

        for input in inputs:
            options = input["options"]
            for key, value in options.items():
                command.append(key)
                if value is not True:
                    command.append(str(value))
            command.append(input["path"])

        for output in outputs:
            options = output["options"]
            for key, value in options.items():
                command.append(key)
                if value is not True:
                    command.append(str(value))

            if "path" in output:
                dst_path = output["path"]
                command.append(dst_path)

                # Create missing output directory
                dst_dir = os.path.dirname(dst_path)
                if not os.path.exists(dst_dir):
                    logging.debug("Create output directory: %s", dst_dir)
                    os.makedirs(dst_dir)

                dst_paths.append(dst_path)

        # Process command
        logging.debug("Launching process command: %s", ' '.join(command))
        command_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=self.env)
        stdout, stderr = command_process.communicate()
        self.log_subprocess(stdout, stderr)

        if stderr:
            message = "An error occurred processing "
            message += inputs + ": "
            message += stderr.decode("utf-8")
            raise RuntimeError(message)
        if command_process.returncode != 0:
            message = "Process returned with error "
            message += "(code: " + str(command_process.returncode) + "):\n"
            message += stdout.decode("utf-8")
            raise RuntimeError(message)

        return dst_paths

    def log_subprocess(self, stdout, stderr):
        if stdout:
            for line in stdout.decode("utf-8").split("\n"):
                logging.info("[Command Worker] " + line)
        if stderr:
            for line in stderr.decode("utf-8").split("\n"):
                logging.error("[Command Worker] " + line)
