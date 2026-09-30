#!/usr/bin/env node
/** Offline installer. No downloads, credentials, shell commands or account changes. */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PROFILES = { codex: '.agents', universal: '.agents', claude: '.claude', cursor: '.cursor' };
const HELP = `BuyLess — install once, ask naturally

  node bin/buyless.mjs init --ai codex --global
  node bin/buyless.mjs init --ai claude --project /path/to/project
  node bin/buyless.mjs init --ai cursor --dry-run
  node bin/buyless.mjs doctor --ai codex --global

Commands: init, doctor
Options:
  --ai codex|claude|cursor|universal  Required host profile
  --global                          Install for this OS user, across local projects
  --project PATH                    Install in this project (default: current directory)
  --dry-run                         Preview init without writing
  --help                            Show help

Existing different files are never overwritten. Doctor checks installed files,
not host activation, model behavior, web access or ChatGPT account registration.
`;

export function parse(args) {
  if (!args.length || args.includes('--help')) return { help: true };
  const options = { command: args[0], global: false, dryRun: false };
  if (!['init', 'doctor'].includes(options.command)) throw Error('Use init or doctor.');
  for (let i = 1; i < args.length; i++) {
    const flag = args[i];
    if (flag === '--global' || flag === '--dry-run') {
      const key = flag === '--global' ? 'global' : 'dryRun';
      if (options[key]) throw Error(`Duplicate ${flag}`);
      options[key] = true;
    } else if (flag === '--ai' || flag === '--project') {
      const key = flag.slice(2);
      if (options[key] || !args[i+1] || args[i+1].startsWith('--')) throw Error(`Invalid ${flag}`);
      options[key] = args[++i];
    } else throw Error(`Unknown option: ${flag}`);
  }
  if (!Object.hasOwn(PROFILES, options.ai)) throw Error('Choose --ai codex, claude, cursor or universal.');
  if (options.global && options.project) throw Error('--global and --project cannot be combined.');
  if (options.command === 'doctor' && options.dryRun) throw Error('--dry-run is for init.');
  return options;
}

// Reject links/junctions along the path so writes cannot silently change another installation.
function noLinks(target) {
  let current = path.resolve(target);
  while (true) {
    try {
      if (fs.lstatSync(current).isSymbolicLink()) throw Error(`Linked path is not supported: ${current}`);
    } catch (error) { if (error.code !== 'ENOENT') throw error; }
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
}

function payload(root) {
  const files = new Map();
  function collect(relative) {
    const source = path.join(root, relative);
    const info = fs.lstatSync(source);
    if (info.isSymbolicLink()) throw Error(`Linked source is not supported: ${relative}`);
    if (info.isDirectory()) {
      for (const name of fs.readdirSync(source).sort()) {
        if (name === '__pycache__' || /\.py[co]$/.test(name)) continue;
        collect(path.join(relative, name));
      }
    } else if (info.isFile()) files.set(relative, fs.readFileSync(source));
    else throw Error(`Unsupported source: ${relative}`);
  }
  for (const relative of ['SKILL.md', 'LICENSE', 'agents', 'references', 'examples',
    'assets/buyless-logo.png', 'assets/buyless-icon.png',
    'scripts/compare_offers.py', 'scripts/audit_research.py']) collect(relative);
  if (!/^name: buyless\s*$/m.test(files.get('SKILL.md').toString('utf8'))) throw Error('Invalid BuyLess skill source.');
  return files;
}

export function run(options, { cwd = process.cwd(), home = os.homedir(), root = ROOT } = {}) {
  if (options.help) return { help: HELP };
  const base = path.resolve(options.global ? home : (options.project || cwd));
  const target = path.join(base, PROFILES[options.ai], 'skills', 'buyless');
  noLinks(target);
  const files = payload(root);
  const missing = [], changed = [];
  for (const [relative, content] of files) {
    const destination = path.join(target, relative);
    noLinks(destination);
    try {
      if (!fs.statSync(destination).isFile() || !fs.readFileSync(destination).equals(content)) changed.push(relative);
    } catch (error) { if (error.code === 'ENOENT') missing.push(relative); else throw error; }
  }
  if (options.command === 'doctor') return {
    status: missing.length || changed.length ? 'missing_or_different' : 'files_match', target,
    missing, changed, exitCode: missing.length || changed.length ? 1 : 0,
    note: 'File checks only. Open a new host session and check its skill selector; web access is provided by the host.'
  };
  if (changed.length) throw Error(`Existing files differ; nothing written. Preserve or move the existing BuyLess folder before installing this version: ${target}`);
  const report = { status: options.dryRun ? 'preview' : missing.length ? 'installed' : 'already_installed',
    target, filesToWrite: missing.length, filesChecked: files.size };
  if (options.dryRun) return report;
  // Preflight all collisions before writing. Exclusive writes also prevent overwrites on a race.
  for (const relative of missing) {
    const destination = path.join(target, relative);
    noLinks(destination);
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.writeFileSync(destination, files.get(relative), { flag: 'wx' });
  }
  return { ...report, note: 'Open a new session in your AI host. If BuyLess is absent, restart the host. This does not install a ChatGPT web plugin.' };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const result = run(parse(process.argv.slice(2)));
    console.log(result.help || JSON.stringify(result, null, 2));
    process.exitCode = result.exitCode || 0;
  } catch (error) {
    console.error(`BuyLess: ${error.message}`);
    process.exitCode = 2;
  }
}
