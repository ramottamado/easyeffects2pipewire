import argparse, json


def main():
    try:
        from ee2pw.core import builder

        argparser = argparse.ArgumentParser(
            description="Parse EasyEffects configuration file."
        )

        argparser.add_argument(
            "filename", type=str, help="Path to the EasyEffects configuration file."
        )

        argparser.add_argument(
            "-n", "--filter-chain-name", type=str, help="Filter chain name."
        )

        argparser.add_argument(
            "-t",
            "--smart-filter-target",
            type=str,
            help="Smart filter target (if any).",
        )

        argparser.add_argument(
            "-o",
            "--output",
            type=str,
            help="File output.",
        )

        args = argparser.parse_args()

        result: dict = builder(
            args.filename, args.filter_chain_name, args.smart_filter_target
        )

        with open(args.output, "w") as out:
            json.dump(result, out, indent=2)

        return 0
    except Exception as e:
        raise e


if __name__ == "__main__":
    import sys

    sys.exit(main())
