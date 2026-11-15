#!/usr/bin/env python3
"""DeepSeek 또는 OpenAI-compatible vLLM의 연결을 비밀 저장 없이 확인한다."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import urllib.error
import urllib.request


def endpoint(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def request_json(url: str, key: str, method: str = "GET", body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            payload = response.read().decode("utf-8")
            print(f"HTTP {response.status} {url}")
            return json.loads(payload)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise SystemExit(f"HTTP {exc.code} {url}\n{detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"연결 실패: {url}\n{exc.reason}") from exc


def get_key(provider: str) -> str:
    if provider == "vllm":
        return os.getenv("VLLM_API_KEY", "not-required")
    key = os.getenv("DEEPSEEK_API_KEY", "")
    if not key and sys.stdin.isatty():
        key = getpass.getpass("DeepSeek API Key: ")
    if not key:
        raise SystemExit("DEEPSEEK_API_KEY가 없고 대화형 입력도 사용할 수 없습니다.")
    return key


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", choices=["deepseek", "vllm"])
    parser.add_argument("action", choices=["balance", "models", "chat"])
    parser.add_argument("--base-url")
    parser.add_argument("--model")
    args = parser.parse_args()

    if args.provider == "deepseek":
        base_url = args.base_url or "https://api.deepseek.com"
        model = args.model or "deepseek-flash"
    else:
        if not args.base_url:
            parser.error("vllm에는 --base-url이 필요합니다.")
        base_url = args.base_url
        model = args.model

    key = get_key(args.provider)

    if args.action == "balance":
        if args.provider != "deepseek":
            parser.error("balance는 DeepSeek에서만 지원합니다.")
        result = request_json(endpoint(base_url, "user/balance"), key)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.action == "models":
        result = request_json(endpoint(base_url, "models"), key)
        models = [item.get("id", "") for item in result.get("data", [])]
        print("models:")
        for item in models:
            print(f"- {item}")
        if not models:
            raise SystemExit("모델 목록이 비어 있습니다.")
        return

    if not model:
        parser.error("chat에는 --model이 필요합니다.")
    result = request_json(
        endpoint(base_url, "chat/completions"),
        key,
        method="POST",
        body={
            "model": model,
            "messages": [{"role": "user", "content": "Reply with API_OK only."}],
            "max_tokens": 32,
            "stream": False,
        },
    )
    message = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    print(f"model: {result.get('model', model)}")
    print(f"message: {message}")
    print(f"usage: {json.dumps(result.get('usage', {}), ensure_ascii=False)}")


if __name__ == "__main__":
    main()
