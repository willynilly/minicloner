import subprocess
import os
from urllib.parse import urlparse


class GitRunner:

    @staticmethod
    def get_repo_name(git_repo_url: str) -> str:
        return os.path.basename(urlparse(git_repo_url).path)

    @staticmethod
    def run(git_args: list[str], report_std_err: bool = False) -> str:
        # modified from https://www.slingacademy.com/article/python-how-to-programmatically-run-git-commands-and-parse-the-output/
        try:
            completedProcess = subprocess.run(["git"] + git_args, capture_output=True)
            if completedProcess.returncode != 0:
                raise Exception(
                    f"Git command failed with the following error:\n{completedProcess.stderr.decode()}"
                )
            result: str = ""
            if report_std_err:
                result = completedProcess.stderr.decode()
            else:
                result = completedProcess.stdout.decode()
            return result
        except Exception as e:
            print(e)
            raise e

    @staticmethod
    def minimial_clone(git_repo_url: str, working_dir_path: str):
        repo_name: str = GitRunner.get_repo_name(git_repo_url=git_repo_url)

        output: str = ""
        orig_dir = os.getcwd()
        try:
            os.chdir(working_dir_path)
            output += GitRunner.run_command(
                [
                    "clone",
                    "--no-checkout",
                    "--filter=blob:none",
                    git_repo_url,
                    repo_name,
                ],
                report_std_err=True,
            )
        except Exception as e:
            print(e)
            raise e
        finally:
            os.chdir(orig_dir)
        return output

    @staticmethod
    def checkout_files_from_minimal_clone(
        git_repo_url: str, working_dir_path: str, file_paths_from_repo_dir: list[str]
    ):
        repo_name: str = GitRunner.get_repo_name(git_repo_url=git_repo_url)

        output: str = ""
        orig_dir = os.getcwd()
        try:
            output += GitRunner.minimial_clone(
                git_repo_url=git_repo_url, working_dir_path=working_dir_path
            )
            repo_dir_path: str = os.path.join(working_dir_path, repo_name)
            os.chdir(repo_dir_path)
            for file_path_from_repo_dir in file_paths_from_repo_dir:
                output += GitRunner.run(
                    ["restore", "--staged", file_path_from_repo_dir]
                )
                output += GitRunner.run(["restore", file_path_from_repo_dir])
        except Exception as e:
            print(e)
            raise e
        finally:
            os.chdir(orig_dir)
        return output


if __name__ == "__main__":

    git_repo_url: str = "https://github.com/willynilly/cff2toml"
    working_dir_path: str = os.getcwd()
    file_paths_from_repo_dir: str = ["CITATION.cff", "pyproject.toml", "catf"]
    output: str = GitRunner.checkout_files_from_minimal_clone(
        git_repo_url=git_repo_url,
        working_dir_path=working_dir_path,
        file_paths_from_repo_dir=file_paths_from_repo_dir,
    )
    print(output)
