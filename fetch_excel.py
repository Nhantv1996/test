"""Download an Excel file from a URL and read it with pandas.

Usage:
  python fetch_excel.py --url https://example.com/file.xlsx --output data.xlsx
  python fetch_excel.py --url https://example.com/file.xlsx --sheet "Sheet1" --nrows 50
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd


def download_excel(url: str, output_path: Path, timeout: int = 30) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "excel-fetcher/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response, output_path.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Failed to download {url}: {exc}") from exc
    return output_path


def read_excel(path: Path, sheet: Optional[str], nrows: Optional[int], skiprows: Optional[int]) -> pd.DataFrame:
    read_kwargs: dict[str, Any] = {}
    if sheet is not None:
        read_kwargs["sheet_name"] = sheet
    if nrows is not None:
        read_kwargs["nrows"] = nrows
    if skiprows is not None:
        read_kwargs["skiprows"] = skiprows
    return pd.read_excel(path, **read_kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and read an Excel file.")
    parser.add_argument("--url", required=True, help="URL to the .xlsx file")
    parser.add_argument("--output", default="downloads/data.xlsx", help="Local path to save the file")
    parser.add_argument("--sheet", help="Sheet name to read")
    parser.add_argument("--nrows", type=int, help="Number of rows to read")
    parser.add_argument("--skiprows", type=int, help="Rows to skip before reading")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds for the download")
    args = parser.parse_args()

    output_path = Path(args.output)
    download_excel(args.url, output_path, timeout=args.timeout)
    df = read_excel(output_path, args.sheet, args.nrows, args.skiprows)

    print("Downloaded to:", output_path)
    print("Rows:", len(df))
    print(df.head())


if __name__ == "__main__":
    main()
