#!/usr/bin/env python
"""Manage multiple batches on OpenAI"""

import json
import hashlib
import os
import sys
import time
from typing import Literal, Optional, TypedDict

from dotenv import load_dotenv
import openai


def sha256sum(filename: str):
    with open(filename, "rb", buffering=0) as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


STATUS_FILE = "/tmp/batch-status.json"

# TODO: any way to not repeat this?
BatchStatus = Literal[
    "validating",
    "failed",
    "in_progress",
    "finalizing",
    "completed",
    "expired",
    "cancelling",
    "cancelled",
]
# openai.types.Batch.__annotations__['status']


class FileStatus(TypedDict):
    filename: str
    sha256: str
    file_id: Optional[str]
    batch_id: Optional[str]
    batch_status: Optional[BatchStatus]
    batch: dict  # TODO: any way to say "JSON version of openai.types.Batch?"
    output_file_sha256: Optional[str]


def load_status(sha256: str) -> FileStatus | None:
    if not os.path.exists(STATUS_FILE):
        return None
    with open(STATUS_FILE) as f:
        statuses = json.load(f)
        return statuses.get(sha256)


def dump_status(sha256: str, status: FileStatus):
    cache = {}
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE) as f:
            cache = json.load(f)
    cache[sha256] = status
    with open(STATUS_FILE, "w") as f:
        json.dump(cache, f)


def is_failed_batch(status: BatchStatus):
    return (
        status == "cancelled"
        or status == "cancelling"
        or status == "expired"
        or status == "failed"
    )


def is_in_progress_batch(status: BatchStatus):
    return status == "finalizing" or status == "in_progress" or status == "validating"


def is_done_batch(status: BatchStatus):
    return status == "completed"


if __name__ == "__main__":
    load_dotenv()
    batch_files = sys.argv[1:]
    client = openai.OpenAI()

    # For each file:
    # - Check if we've already uploaded it to OpenAI
    # - Upload it if necessary, save file ID to cache
    # - Create the batch (if no successful or pending batch for this file ID)
    # - Monitor the batch status
    # - Retrieve the batch output when done

    for batch_file in batch_files:
        assert batch_file.endswith(".jsonl")
        sha256 = sha256sum(batch_file)
        print(f"{batch_file}: {sha256}")
        status = load_status(sha256)

        if not status:
            status: FileStatus = {"filename": batch_file, "sha256": sha256}
            dump_status(sha256, status)

        file_id = status.get("file_id")
        if not file_id:
            print(f"{batch_file}: uploading to OpenAI")
            f = client.files.create(file=open(batch_file, "rb"), purpose="batch")
            file_id = f.id
            status["file_id"] = file_id
            dump_status(sha256, status)
            print(f"{batch_file}: {file_id=}")
        else:
            print(f"{batch_file}: using previously-uploaded {file_id=}")

        batch_id = status.get("batch_id")
        if not batch_id:
            print(f"{batch_file}: creating batch")
            r = client.batches.create(
                input_file_id=file_id,
                completion_window="24h",
                endpoint="/v1/chat/completions",
                metadata={
                    "filename": batch_file,
                    "sha256": sha256,
                },
            )
            batch_id = r.id
            batch_status = r.status
            status["batch_id"] = batch_id
            status["batch_status"] = batch_status
            print(f"{batch_file}: created batch {batch_id=}, {batch_status=}")
            dump_status(sha256, status)
        else:
            print(f"{batch_file}: using previously-created {batch_id=}")

        did_fetch_status = False

        def fetch_batch_status():
            global batch_status, did_fetch_status
            did_fetch_status = True
            r = client.batches.retrieve(batch_id=batch_id)
            batch_status = r.status
            status["batch"] = r.to_dict(mode="json")
            status["batch_status"] = batch_status
            dump_status(sha256, status)
            print(f"{batch_file}: retrieved batch status {batch_status} {batch_id=}")

        batch_status = status.get("batch_status")
        if not batch_status:
            fetch_batch_status()

        def check_fail_status():
            if is_failed_batch(batch_status):
                sys.stderr.write(
                    f"{batch_file}: {batch_id} batch failed: {batch_status}\n"
                )
                sys.stderr.write(
                    f"Check https://platform.openai.com/batches/{batch_id}\n"
                )
                sys.exit(1)

        check_fail_status()

        while is_in_progress_batch(batch_status):
            if did_fetch_status:
                time.sleep(5)
            # TODO: reduce repetition
            fetch_batch_status()

            if is_done_batch(batch_status) or is_failed_batch(batch_status):
                break

        check_fail_status()

        # batch must be done!
        r = status["batch"]
        assert r is not None
        out_file_id = r["output_file_id"]

        out_path = batch_file.replace(".jsonl", ".output.jsonl")
        output_file_sha256 = status.get("output_file_sha256")
        if (
            output_file_sha256
            and os.path.exists(out_path)
            and sha256sum(out_path) == output_file_sha256
        ):
            print(f"{batch_file}: output already exists at {out_path} and matches SHA")
        else:
            counts = r["request_counts"]
            completed = counts["completed"]
            failed = counts["failed"]
            created_at_s = r["created_at"]
            completed_at_s = r["completed_at"]
            elapsed_s = completed_at_s - created_at_s
            print(
                f"{batch_file}: {completed} completed / {failed} failed in {elapsed_s:.0f}s"
            )

            r = client.files.content(file_id=out_file_id)
            with open(out_path, "wb") as out:
                out.write(r.content)
            output_file_sha256 = sha256sum(out_path)
            status["output_file_sha256"] = output_file_sha256
            dump_status(sha256, status)
            print(f"{batch_file}: downloaded output to {out_path}")
