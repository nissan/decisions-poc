"""Run one frozen comparator arm over the sealed private holdout and write a bound receipt."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from time import perf_counter
from urllib.request import Request, build_opener

from . import classic
from .decisions import MAX_RESPONSE, NoRedirect, advise
from .policy import eligibility, fixture, review

ARMS = ['gemini-decision-1', *classic.CONFIGS]


def classic_case(config, case, eligible, template, key, workdir):
    harness, model, effort, prefix = classic.CONFIGS[config]
    prompt, schema = classic.prompt_and_schema(case, eligible, template)
    if harness == 'claude':
        argv = ['claude', '-p', '--model', model, '--effort', effort, '--output-format', 'json',
                '--json-schema', json.dumps(schema), '--tools', '', '--strict-mcp-config',
                '--no-session-persistence', '--disable-slash-commands']
        answer, served, usage = classic.parse_claude(classic.run_cli(argv, prompt, workdir), prefix)
    elif harness == 'codex':
        path = Path(workdir) / 'schema.json'
        path.write_text(json.dumps(schema))
        argv = ['codex', 'exec', '-m', model, '-c', f'model_reasoning_effort="{effort}"', '--sandbox', 'read-only',
                '--ephemeral', '--ignore-user-config', '--ignore-rules', '--skip-git-repo-check',
                '--output-schema', str(path), '--json', prompt]
        answer, served, usage = classic.parse_codex(classic.run_cli(argv, '', workdir))
    else:
        body = {'model': model, 'messages': [{'role': 'user', 'content': prompt}],
                'provider': {'require_parameters': True, 'allow_fallbacks': False},
                'response_format': {'type': 'json_schema', 'json_schema': {'name': 'routing', 'strict': True, 'schema': schema}}}
        request = Request(classic.OPENROUTER, json.dumps(body).encode(),
                          {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}, method='POST')
        with build_opener(NoRedirect()).open(request, timeout=90) as response:
            wire = response.read(MAX_RESPONSE + 1)
        answer, served, usage = classic.parse_openrouter(wire, prefix)
    return classic.decide(answer, eligible, served, usage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arm', choices=ARMS)
    parser.add_argument('--packets', type=Path, required=True)
    parser.add_argument('--label-digest', required=True)
    parser.add_argument('--baseline-digest', required=True)
    parser.add_argument('--json', type=Path, required=True)
    args = parser.parse_args()
    packets = json.loads(args.packets.read_bytes())
    catalog, template = fixture('lanes'), fixture('questions')
    key = os.environ.get('GEMINI_API_KEY' if args.arm == 'gemini-decision-1' else 'OPENROUTER_API_KEY', '').strip()
    rows, stopped = [], False
    with args.json.open('x') as output, tempfile.TemporaryDirectory() as workdir:
        for case in packets:
            eligible, _ = eligibility(case, catalog)
            start = perf_counter()
            if not eligible:
                row = review('no eligible lane') | {'request_attempted': False}
            elif stopped:
                row = {'status': 'not-run', 'reason': 'stopped after provider failure'}
            elif args.arm == 'gemini-decision-1':
                row = advise(case, eligible, template, key)
            else:
                try:
                    row = classic_case(args.arm, case, eligible, template, key, workdir)
                except Exception as error:
                    row = {'status': 'provider-error', 'reason': type(error).__name__}
            stopped = stopped or row['status'] == 'provider-error'
            rows.append(row | {'case': case['case'], 'elapsed_ms': round((perf_counter() - start) * 1000, 3)})
        json.dump({'arm': args.arm, 'label_sha256': args.label_digest, 'baseline_sha256': args.baseline_digest,
                   'packets_sha256': hashlib.sha256(args.packets.read_bytes()).hexdigest(), 'rows': rows}, output, indent=1)
    print(args.arm, {s: sum(r['status'] == s for r in rows) for s in ('suggest', 'review', 'provider-error', 'not-run')})


if __name__ == '__main__':
    main()
