import React from 'react';
import {ShieldCheck, LayoutDashboard, Search, ListFilter, Activity, Github, Radar, Gauge, GitCompareArrows} from 'lucide-react';
const links=[['overview','Overview',LayoutDashboard],['score','Risk scoring',Search],['scenarios','What-if lab',GitCompareArrows],['transactions','Transactions',ListFilter],['analytics','Analytics',Activity],['models','Model performance',Radar],['monitoring','Monitoring',Gauge]];
export default function Navbar({page,setPage}) {return <aside className="sidebar">
  <div className="brand"><div className="brand-icon"><ShieldCheck size={27}/></div><div><strong>Transaction<span>Shield</span></strong><small>FRAUD INTELLIGENCE</small></div></div>
  <div className="sidebar-label">WORKSPACE</div><nav>{links.map(([id,name,Icon])=><button key={id} type="button" className={'nav-link '+(page===id?'active':'')} onClick={()=>setPage(id)}><Icon size={18}/><span>{name}</span></button>)}</nav>
  <div className="sidebar-spacer"/><div className="nav-footer"><div className="live-dot"/> Synthetic demo mode</div><a className="github-link" target="_blank" rel="noreferrer" href="https://github.com/harshakavali81-collab/TransactionShield-a-Real-Time-Fraud-Detection-and-Risk-Scoring-Platform."><Github size={15}/> View repository</a>
</aside>}
