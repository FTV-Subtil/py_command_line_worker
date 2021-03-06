
import os
import logging
import configparser
import subprocess


class ProcessError(Exception):

    def __init__(self, returned_code, message):
        super().__init__(message)
        self.returned_code = returned_code

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

    def launch(self, program: str, inputs: list, output_path: str, threads_number: int, lib_path: list, exec_dir: str = None):

        if program.startswith("/") or program.startswith("./"):
            self.command_path = program
        else:
            self.command_path = os.path.join(self.command_bin_path, program)

        if "LD_LIBRARY_PATH" not in self.env:
            self.env["LD_LIBRARY_PATH"] = ""

        for path in lib_path:
            self.env["LD_LIBRARY_PATH"] += ":" + path
        self.env["LD_LIBRARY_PATH"] += ":" + self.command_lib_path

        if exec_dir and not os.path.exists(exec_dir):
            raise FileNotFoundError("The expected execution directory does not exists: " + exec_dir)

        command = [self.command_path]

        for input_path in inputs:
            command.append(input_path)

        command.append(output_path)
        command.append(str(threads_number))

        # Process command
        logging.debug("Launching process command: %s", ' '.join(command))
        command_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=exec_dir, env=self.env)
        stdout, stderr = command_process.communicate()
        self.log_subprocess(stdout, stderr)

        if stderr:
            message = "An error occurred processing "
            message += inputs + ": "
            message += stderr.decode("utf-8")
            raise ProcessError(command_process.returncode, message)
        if command_process.returncode != 0:
            message = "Process returned with error "
            message += "(code: " + str(command_process.returncode) + ")"
            raise ProcessError(command_process.returncode, message)

        return [output_path]

    def log_subprocess(self, stdout, stderr):
        if stdout:
            for line in stdout.decode("utf-8").split("\n"):
                logging.info("[Command Worker] " + line)
        if stderr:
            for line in stderr.decode("utf-8").split("\n"):
                logging.error("[Command Worker] " + line)
