import argparse
import json
import sys

import dotenv

from llmwriter import generate_pdf_document

dotenv.load_dotenv(dotenv_path=".env")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic PDF documents based on requirements")

    # Add arguments
    parser.add_argument("--requirements", "-r", type=str, help="The document requirements text")
    parser.add_argument("--requirements-file", "-f", type=str, help="Path to a file containing document requirements")
    parser.add_argument(
        "--output", "-o", type=str, default="generated_document.pdf", help="Path for the output PDF file"
    )
    parser.add_argument("--config", "-c", type=str, help="Path to a JSON configuration file")

    args = parser.parse_args()

    # Load requirements
    requirements = None

    if args.requirements:
        requirements = args.requirements
    elif args.requirements_file:
        try:
            with open(args.requirements_file) as f:
                requirements = f.read()
        except FileNotFoundError:
            print(f"Error: Requirements file '{args.requirements_file}' not found")
            sys.exit(1)
    elif args.config:
        try:
            with open(args.config) as f:
                config = json.load(f)
                if "requirements" in config:
                    requirements = config["requirements"]
                elif "requirements_file" in config:
                    with open(config["requirements_file"]) as rf:
                        requirements = rf.read()
        except FileNotFoundError:
            print(f"Error: Config file '{args.config}' not found")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Config file '{args.config}' is not valid JSON")
            sys.exit(1)

    if not requirements:
        print("Error: No requirements provided. Use --requirements, --requirements-file, or --config")
        parser.print_help()
        sys.exit(1)

    # Generate the PDF
    try:
        output_path = generate_pdf_document(requirements, args.output)
        print(f"PDF document successfully generated at: {output_path}")
    except Exception as e:
        print(f"Error generating PDF document: {e!s}")
        sys.exit(1)


if __name__ == "__main__":
    main()
