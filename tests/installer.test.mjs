import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { run, parse } from '../bin/buyless.mjs';

function context(t) {
  // macOS exposes /var as a link to /private/var. Use the physical temp path
  // so the link-safety check tests our fixture, not that OS-managed alias.
  const tempRoot = fs.realpathSync(os.tmpdir());
  const temp = fs.mkdtempSync(path.join(tempRoot, 'buyless-test-'));
  t.after(() => {
    // Only the exact temporary directory created by this test is removed.
    assert.equal(path.dirname(temp), tempRoot);
    assert.ok(path.basename(temp).startsWith('buyless-test-'));
    fs.rmSync(temp, { recursive: true, force: true });
  });
  return { cwd: path.join(temp, 'project with spaces'), home: path.join(temp, 'home') };
}

for (const [ai, folder] of [['codex','.agents'],['claude','.claude'],['cursor','.cursor'],['universal','.agents']]) {
  test(`${ai}: install all resources and check from a separate session`, t => {
    const ctx = context(t);
    const result = run(parse(['init','--ai',ai]),ctx);
    assert.equal(result.target,path.join(ctx.cwd,folder,'skills','buyless'));
    assert.equal(result.status,'installed');
    assert.ok(fs.existsSync(path.join(result.target,'references','international.md')));
    assert.ok(fs.existsSync(path.join(result.target,'scripts','compare_offers.py')));
    assert.ok(!fs.existsSync(path.join(result.target,'.git')));
    assert.equal(run(parse(['doctor','--ai',ai]),ctx).status,'files_match');
  });
}
test('global scope uses home, not current project', t => {
  const ctx=context(t);
  const result=run(parse(['init','--ai','codex','--global']),ctx);
  assert.equal(result.target,path.join(ctx.home,'.agents','skills','buyless'));
  assert.equal(fs.existsSync(ctx.cwd),false);
});
test('dry run never creates directories', t => {
  const ctx=context(t);
  assert.equal(run(parse(['init','--ai','cursor','--dry-run']),ctx).status,'preview');
  assert.equal(fs.existsSync(ctx.cwd),false);
});
test('repeated install is idempotent and preserves unrelated files', t => {
  const ctx=context(t), options=parse(['init','--ai','claude']);
  const first=run(options,ctx);
  const extra=path.join(first.target,'personal-notes.txt');
  fs.writeFileSync(extra,'keep me');
  assert.equal(run(options,ctx).status,'already_installed');
  assert.equal(fs.readFileSync(extra,'utf8'),'keep me');
});
test('changed file prevents all writes, doctor detects drift', t => {
  const ctx=context(t), options=parse(['init','--ai','codex']);
  const first=run(options,ctx);
  const skill=path.join(first.target,'SKILL.md'), license=path.join(first.target,'LICENSE');
  fs.writeFileSync(skill,'my edits'); fs.unlinkSync(license);
  assert.throws(()=>run(options,ctx),/nothing written/);
  assert.equal(fs.readFileSync(skill,'utf8'),'my edits');
  assert.equal(fs.existsSync(license),false);
  assert.equal(run(parse(['doctor','--ai','codex']),ctx).exitCode,1);
});
test('doctor reports absent skill without creating one', t => {
  const ctx=context(t);
  assert.equal(run(parse(['doctor','--ai','codex']),ctx).exitCode,1);
  assert.equal(fs.existsSync(ctx.cwd),false);
});
test('explicit project is honored', t => {
  const ctx=context(t), project=path.join(ctx.home,'another project');
  const result=run(parse(['init','--ai','cursor','--project',project]),ctx);
  assert.equal(result.target,path.join(project,'.cursor','skills','buyless'));
});
test('reject invalid and conflicting arguments', () => {
  for (const args of [['init'],['init','--ai','chatgpt'],['init','--ai','codex','--global','--project','x'],['init','--ai','codex','--force'],['doctor','--ai','codex','--dry-run']]) {
    assert.throws(()=>parse(args));
  }
});
test('junctions cannot redirect installation', t => {
  const ctx=context(t);
  fs.mkdirSync(ctx.cwd,{recursive:true}); fs.mkdirSync(ctx.home,{recursive:true});
  fs.symlinkSync(ctx.home,path.join(ctx.cwd,'.agents'),process.platform==='win32'?'junction':'dir');
  assert.throws(()=>run(parse(['init','--ai','codex']),ctx),/Linked path/);
  assert.equal(fs.readdirSync(ctx.home).length,0);
});
