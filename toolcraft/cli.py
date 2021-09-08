"""Console script for toolcraft."""

import fire


def help():
    print("toolcraft")
    print("=" * len("toolcraft"))
    print("Create tools with ToolCraft")


def main():
    fire.Fire({"help": help})


if __name__ == "__main__":
    main()  # pragma: no cover
