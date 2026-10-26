import React,{useCallback,useEffect,useState} from 'react';
import {Bell,Menu,ShieldCheck, X} from 'lucide-react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Predict from './pages/Predict';
import Transactions from './pages/Transactions';
import Analytics from './pages/Analytics';
import ModelPerformance from './pages/ModelPerformance';
import {api} from './api/client';
export default function App(){const [page,setPage]=useState('overview'),[statistics,setStatistics]=useState(null),[rows,setRows]=useState([]),[analytics,setAnalytics]=useState(null),[metrics,setMetrics]=useState(null),[health,setHealth]=useState(null),[error,setError]=useState(''),[loading,setLoading]=useState(false),[menu,setMenu]=useState(false);
const refresh=useCallback(async()=>{setLoading(true);try{const [s,h,a,m,he]=await Promise.all([api.statistics(),api.history(),api.analytics(),api.metrics(),api.health()]);setStatistics(s);setRows(h);setAnalytics(a);setMetrics(m);setHealth(he);setError('')}catch(ex){setError(ex.message)}finally{setLoading(false)}},[]);
useEffect(()=>{refresh();const timer=setInterval(refresh,30000);return()=>clearInterval(timer)},[refresh]);
const navigate=x=>{setPage(x);setMenu(false)};
return <div className="app-shell"><div className={menu?'mobile-nav open':'mobile-nav'}><Navbar page={page} setPage={navigate}/></div><div className="desktop-nav"><Navbar page={page} setPage={navigate}/></div><main className="content"><header className="topbar"><button className="mobile-toggle" onClick={()=>setMenu(!menu)}>{menu?<X/>:<Menu/>}</button><span className="breadcrumb">Workspace <span>/</span> {page==='overview'?'Dashboard':page.replaceAll('_',' ')}</span><div className="top-right"><span className={'status '+(health?.model_ready?'':'disconnected')}><span/>{health?.model_ready?'Model online':'Model offline'}</span><div className="avatar">TS</div></div></header><div className="page-body"><div className="demo-banner"><ShieldCheck size={17}/> <span><b>Synthetic dataset demonstration.</b> Scores are educational and cannot be used to accept, deny, or investigate real payments without independent validation.</span></div>{error&&<div className="error" role="alert">Unable to reach the API: {error}. Start FastAPI on port 8000 and refresh.</div>}{page==='overview'&&<Dashboard statistics={statistics} rows={rows} refresh={refresh} loading={loading} setPage={navigate}/>}{page==='score'&&<Predict refresh={refresh}/>}{page==='transactions'&&<Transactions rows={rows}/>}{page==='analytics'&&<Analytics analytics={analytics}/>}{page==='models'&&<ModelPerformance metrics={metrics}/>}</div></main></div>}
