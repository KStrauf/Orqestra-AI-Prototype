#!/usr/bin/env node
import fs from'node:fs/promises';import{Command}from'commander';import{agentRegistry}from'@orqestra/agents';import{paths,resolveSession}from'@orqestra/agents';import{runTaskAnalysisWorkflow}from'@orqestra/agents';
const p=new Command();p.name('orqestra').description('OrqestraAI agent communicator').version('0.1.0');
p.command('agents').action(()=>{for(const a of Object.values(agentRegistry))console.log(`${a.name.padEnd(36)} ${a.description}`)});
p.command('show').argument('<agent>').action((n)=>{const a=(agentRegistry as any)[n];if(!a)throw new Error(`Unknown agent ${n}`);console.log(JSON.stringify(a,null,2))});
p.command('analyze').argument('<task>').action(async(t)=>{const id=await runTaskAnalysisWorkflow(t);console.log(`Session: ${id}`);console.log(`Transcript: ${paths.transcript(id)}`);console.log(`Handoff: ${paths.handoff(id)}`)});
p.command('transcript').argument('<session>').action(async(s)=>{const id=await resolveSession(s);const raw=await fs.readFile(paths.transcript(id),'utf8');for(const l of raw.split('
').filter(Boolean)){const m=JSON.parse(l);console.log(`[${m.fromAgent} -> ${m.toAgent}] ${m.type}: ${m.task}`)}});
p.command('handoff').argument('<session>').action(async(s)=>{const id=await resolveSession(s);console.log(await fs.readFile(paths.handoff(id),'utf8'))});p.parse();
